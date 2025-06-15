from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisteredSystemSerializer
from .models import RegisteredSystem
from rest_framework.parsers import MultiPartParser, FormParser
import json
import logging
from .services import install_agent, discover_databases, extract_data_from_system, fetch_database_names, generate_table_summaries, get_table_data_by_table_id
from blockchain.blockchain_client import store_table_data
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view


logger = logging.getLogger(__name__)  # optional logger for production use

class RegisterSystemView(APIView):
   def post(self, request):
    success = False  # Initialize early to avoid UnboundLocalError

    try:
        # Extract form data
        name = request.POST.get('name')
        url = request.POST.get('url')
        data_type = request.POST.get('data_type')
        system_type = request.POST.get('system_type')
        display_id = request.POST.get('display_id')
        num_admins = int(request.POST.get('num_admins', 0))
        profile_photo = request.FILES.get('profile_photo')

        admins = []
        for i in range(num_admins):
            admin_name = request.POST.get(f'admins[{i}][name]')
            admin_email = request.POST.get(f'admins[{i}][email]')
            if admin_name and admin_email:
                admins.append({'name': admin_name, 'email': admin_email})

        data = {
            'name': name,
            'url': url,
            'data_type': data_type,
            'system_type': system_type,
            'display_id': display_id,
            'num_admins': num_admins,
            'profile_photo': profile_photo,
            'admins': admins
        }

        serializer = RegisteredSystemSerializer(data=data)
        if serializer.is_valid():
            system = serializer.save()

            # Install agent
            system_url = system.url
            success = install_agent(system_url)
            print(f"[INFO] Agent installation status for {system_url}: {success}")

            if success:
                discovered_dbs = discover_databases(system_url)
                print(f"[INFO] Databases discovered: {discovered_dbs}")

                return Response({
                    "message": "System registered successfully",
                    "system_id": str(system.system_id),
                    "display_id": system.display_id,
                    "discovered_databases": discovered_dbs
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Agent installation failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON in "data" field'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("Unexpected error during system registration")
        return Response({'error': f'Unexpected error: {str(e)}', 'success': success}, status=status.HTTP_400_BAD_REQUEST)

class RegisteredSystemListView(APIView):
    def get(self, request):
        systems = RegisteredSystem.objects.all()
        serialized = RegisteredSystemSerializer(systems, many=True, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)

class RegisteredSystemDetailView(APIView):
    def get(self, request, display_id):
        try:
            system = RegisteredSystem.objects.get(display_id=display_id)
            serializer = RegisteredSystemSerializer(system)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except RegisteredSystem.DoesNotExist:
            return Response({'error': 'System not found'}, status=status.HTTP_404_NOT_FOUND)

class AgentInstallView(APIView):
    def post(self, request):
        url = request.data.get('url')
        if not url:
            return Response({'error': 'Missing URL'}, status=status.HTTP_400_BAD_REQUEST)

        success = install_agent(url)
        if success:
            return Response({'status': 'Agent installed'})
        return Response({'error': 'Installation failed'}, status=500)


class DiscoverDatabasesView(APIView):
    def get(self, request):
        url = request.query_params.get('url')
        if not url:
            return Response({'error': 'Missing URL'}, status=status.HTTP_400_BAD_REQUEST)

        dbs = discover_databases(url)
        return Response({'databases': dbs}) 

    
class FetchDatabaseNamesView(APIView):
    def post(self, request):
        data = request.data
        ip = data.get('ip_address')
        db_type = data.get('db_type')
        credentials = data.get('credentials')

        if not all([ip, db_type, credentials]):
            return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

        database_names = fetch_database_names(ip, db_type, credentials)
        if not database_names:
            return Response({'error': 'Could not fetch databases'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'database_names': database_names})


class ExtractDataView(APIView):
    def post(self, request):
        url = request.data.get('url')
        dbs = request.data.get('db_name')
        credentials_map = request.data.get('credentials')
        system_id = request.data.get('system_id')

        if not url or not dbs or not credentials_map or not system_id:
            return Response({'error': 'Missing required fields'}, status=400)

        all_data = extract_data_from_system(url, dbs, credentials_map, system_id)

        for sys_id, sys_data in all_data.items():
            batch_id = str(uuid.uuid4())

            for db_name, db_content in sys_data.items():
                tables_data = db_content.get("data", {})

                for table_key, table_obj in tables_data.items():
                    try:
                        schema_name = table_obj.get("schema_name", "")
                        table_name = table_obj.get("table_name", "")
                        data_section = table_obj.get("data", {})
                        schema = data_section.get("schema", [])
                        rows = data_section.get("rows", [])

                        if not schema or not rows:
                            print(f"[WARN] No data for table {table_key}")
                            continue

                        receipt = store_table_data(
                            sys_id,
                            batch_id,
                            db_name,
                            table_key,
                            schema_name,
                            table_name,
                            schema,
                            rows
                        )

                        print(f"[✔] Stored table {table_name} from {db_name}")

                    except Exception as e:
                        print(f"[ERROR] Failed storing table {table_key}: {e}")

        return Response({"message": "Data extracted and stored on blockchain", "data": all_data}, status=200)

class GetLedgerDataView(APIView):
    def get(self, request, system_id):
        from .services import get_ledger_data
        data = get_ledger_data(system_id)
        if data:
            return Response({
                "status": "success",
                "ledger_data": data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to retrieve data from blockchain"}, status=500)

@api_view(["GET"])
def get_ledger_summary(request, sys_id):
    """
    Endpoint to return the Data Record summary for a system.
    """
    try:
        summaries = generate_table_summaries(sys_id)
        return Response({"status": "success", "data": summaries})
    except Exception as e:
        print(f"[ERROR] Failed to fetch ledger summary: {e}")
        return Response({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def get_ledger_table_summaries(request, sys_id):
    if request.method == 'GET':
        try:
            summaries = generate_table_summaries(sys_id)
            return JsonResponse({"status": "success", "data": summaries}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
def get_full_table_data(request, sys_id, table_id):
    if request.method == 'GET':
        try:
            table_data = get_table_data_by_table_id(sys_id, table_id)
            return JsonResponse({"status": "success", "data": table_data}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
