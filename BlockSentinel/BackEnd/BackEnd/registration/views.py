from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisteredSystemSerializer
from .models import RegisteredSystem
from rest_framework.parsers import MultiPartParser, FormParser
import json
import logging
from .services import install_agent, discover_databases

logger = logging.getLogger(__name__)  # optional logger for production use

class RegisterSystemView(APIView):
    def post(self, request):
        try:
            # Directly extract fields from request.POST
            name = request.POST.get('name')
            url = request.POST.get('url')
            data_type = request.POST.get('data_type')
            system_type = request.POST.get('system_type')
            display_id = request.POST.get('display_id')
            num_admins = int(request.POST.get('num_admins', 0))
            profile_photo = request.FILES.get('profile_photo')

            # Build admin list
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

                # Automatically try to install agent
                system_url = system.url  # e.g. http://192.168.10.100:8000
                success = install_agent(system_url)
                print(f"[INFO] Agent installation status for {system_url}: {success}")

            # 2. Discover databases (optional — only if agent installed successfully)
                discovered_dbs = []
            if success:
                discovered_dbs = discover_databases(system_url)
                # You can log/store them, or return them to the frontend
                print(f"[INFO] Databases discovered: {discovered_dbs}")


                return Response({
                    "message": "System registered successfully",
                    "system_id": str(system.system_id),
                    "display_id": system.display_id,
                    "discovered_databases": discovered_dbs
                }, status=status.HTTP_201_CREATED)
            else:
                print("[DEBUG] Serializer errors:", serializer.errors)  # 👈 Add this
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON in "data" field'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

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
