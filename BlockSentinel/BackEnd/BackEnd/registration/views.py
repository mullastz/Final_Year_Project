from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisteredSystemSerializer
from .models import RegisteredSystem
from rest_framework.parsers import MultiPartParser, FormParser
import json
import logging
from .services import install_agent, discover_databases, extract_data_from_system, fetch_database_names, generate_table_summaries, get_table_data_by_table_id, fetch_table_data
from blockchain.blockchain_client import store_table_data
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from datetime import datetime
from .sync_engine import start_sync
from blockchain.ledger_index import LEDGER_INDEX



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

                    # ✅ Start syncing for Orion 1 demo tables
                    orion_demo_tables = [
                        'evaluation_app_student',
                        'evaluation_app_lecturer',
                        'evaluation_app_superadmin',
                        'evaluation_app_module',
                        'evaluation_app_lecturerfeedback',
                        'evaluation_app_assignedlecmodules'
                    ]

                    try:
                        system_id = str(system.system_id)
                        start_sync(system_id, orion_demo_tables)
                        print(f"[✔] Sync tracking started for {system_id} on tables: {orion_demo_tables}")
                    except Exception as e:
                        print(f"[ERROR] Failed to start sync tracking: {e}")

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
        from auditlog.monitoring_engine import start_monitoring_agent  # safe to import inside method

        url = request.data.get('url')
        dbs = request.data.get('db_name')  # List of {"name": "...", "type": "..."}
        credentials_map = request.data.get('credentials')  # Dict of db_name -> credentials
        system_id = request.data.get('system_id')

        if not url or not dbs or not credentials_map or not system_id:
            return Response({'error': 'Missing required fields'}, status=400)

        all_data = extract_data_from_system(url, dbs, credentials_map, system_id)

        for sys_id, sys_data in all_data.items():
            batch_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
                            rows,
                            timestamp,
                            user=request.user
                        )

                        print(f"[✔] Stored table {table_name} from {db_name}")

                    except Exception as e:
                        print(f"[ERROR] Failed storing table {table_key}: {e}")

        # ✅ Start MonitoringAgent here
        try:
            db_configs = {}

            for db in dbs:
                db_name = db['name']
                if db_name in credentials_map:
                    db_info = credentials_map[db_name]
                    db_type = db_info.get("type")
                    db_info_cleaned = {
                        "host": db_info["host"],
                        "port": int(db_info["port"]),
                        "user": db_info["user"],
                        "password": db_info["password"],
                        "database": db_info["dbname"]
                    }
                    db_configs[db_type] = db_info_cleaned

            backend_url = "http://127.0.0.1:8000"  # or use settings.BACKEND_URL
            start_monitoring_agent(system_id, backend_url, db_configs)
            print(f"[✔] Monitoring agent started for {system_id}")
        except Exception as e:
            print(f"[ERROR] Failed to start monitoring agent: {e}")

        return Response({
            "message": "Data extracted and stored on blockchain. Monitoring agent started.",
            "data": all_data
        }, status=200)

    
    
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
    Filters out entries without valid ledger hashes and removes duplicates.
    """
    try:
        summaries = generate_table_summaries(sys_id)

        # Filter out entries without ledger_hash or with placeholder ledger_hash
        filtered = [
            entry for entry in summaries
            if entry.get("ledger_hash") and not entry["ledger_hash"].startswith("<")
        ]

        # Remove duplicates based on table_id and batch_id (if batch_id is in entries)
        seen = set()
        unique_summaries = []
        for entry in filtered:
            key = entry.get("table_id", None)  # use table_id as unique key
            if key and key not in seen:
                unique_summaries.append(entry)
                seen.add(key)

        print(f"[DEBUG] Ledger summaries for system {sys_id} (filtered): {unique_summaries}")
        return Response({"status": "success", "data": unique_summaries})

    except Exception as e:
        print(f"[ERROR] Failed to fetch ledger summary: {e}")
        return Response({"status": "error", "message": str(e)}, status=500)

@api_view(['GET'])  # ✅ THIS IS THE FIX
def get_ledger_detail(request, sys_id, table_id):
    """
    API endpoint to return full ledger table data for a given system and table id.
    """
    try:
        data = fetch_table_data(sys_id, table_id)

        if not data:
            return Response({"status": "error", "message": "Ledger data not found"}, status=404)

        return Response({"status": "success", "data": data})

    except Exception as e:
        print(f"[ERROR] Failed to fetch ledger detail: {e}")
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

class SyncStatusView(APIView):
    def get(self, request):
        try:
            summary = {
                "syncsToday": 0,
                "pendingSyncs": 0,
                "successful": 0,
                "failed": 0,
            }

            today = datetime.now().date()

            for system_id, entries in LEDGER_INDEX.items():
                for entry in entries:
                    timestamp = datetime.fromisoformat(entry['timestamp'])
                    if timestamp.date() == today:
                        summary["syncsToday"] += 1
                    summary["successful"] += 1

            # Set pending and failed (0 for now)
            summary["pendingSyncs"] = 0
            summary["failed"] = 0

            return Response(summary, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SyncDetailView(APIView):
    def get(self, request):
        try:
            details = []
            seen_ledger_hashes = set()  # to track unique ledger hashes

            for system_display_id, entries in LEDGER_INDEX.items():
                try:
                    system = RegisteredSystem.objects.get(display_id=system_display_id)
                    system_name = system.name
                except RegisteredSystem.DoesNotExist:
                    system_name = system_display_id

                for entry in entries:
                    try:
                        ledger_hash = entry.get("ledger_hash", "")
                        # Filter out empty or placeholder ledger hashes
                        if not ledger_hash or ledger_hash == "<hash unavailable post-restart>":
                            continue
                        # Skip duplicates
                        if ledger_hash in seen_ledger_hashes:
                            continue

                        timestamp = datetime.fromisoformat(entry["timestamp"])
                        details.append({
                            "id": entry["batch_id"],
                            "dateTime": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            "system": system_name,
                            "recordsSynced": len(entry.get("rows", [])),
                            "status": "Success",
                            "ledgerHash": ledger_hash,
                            "syncedBy": "System",
                            "affectedTables": entry.get("table_key", ""),
                            "notes": ""
                        })
                        seen_ledger_hashes.add(ledger_hash)  # mark this hash as seen

                    except Exception as inner:
                        print(f"[ERROR] Skipping entry due to: {inner}")

            return Response(details, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"[FATAL ERROR] SyncDetailView failed: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
