from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisteredSystemSerializer
from .models import RegisteredSystem
from rest_framework.parsers import MultiPartParser, FormParser
import json
import logging
from .services import install_agent, discover_databases, extract_data_from_system, scan_common_db_ports, fetch_db_names

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
        db_type = request.data.get("db_type")
        credentials = request.data.get("credentials")

        if not db_type or not credentials:
            return Response({"error": "Missing db_type or credentials"}, status=400)

        db_names = fetch_db_names(db_type, credentials)
        return Response({"databases": db_names})  

class ExtractDataView(APIView):
    def post(self, request):
        url = request.data.get('url')
        db_name = request.data.get('db_name')
        credentials = request.data.get('credentials')

        if not url or not db_name or not credentials:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # This assumes extract_data_from_system handles credentials internally
        extracted = extract_data_from_system(url, db_name=db_name, credentials=credentials)

        if extracted:
            return Response({'status': 'Extraction started', 'data': extracted})
        return Response({'error': 'Extraction failed'}, status=500)

