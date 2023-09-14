import random
from datetime import datetime, timedelta

from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .serializers import *
from .models import *
from .permissions import IsSuperUser, IsOrgSuperUser, PasswordPermission
from .cron import expire_passwords

from common import send_notification

from django.conf import settings
from django.contrib.auth.models import User



# Create your views here.
from password_strength import PasswordPolicy

policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 2 uppercase letters
    numbers=1,  # need min. 2 digits
    special=1,  # need min. 2 special characters
    nonletters=1,  # need min. 2 non-letter characters (digits, specials, anything)
)



@api_view(['POST'])
def send_otp(request):
    data = {
        "message": "Ok",
        "code": HTTP_200_OK,
        "data": {}
    }
    status_code = HTTP_200_OK
    try:
        otp = random.randint(1000, 9999)
        data_dict = {
            'email': request.data["email"],
            'number': otp
        }
        serializer = OTPSerializer(data=data_dict)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            send_notification(request.data["email"], "Password manager otp", f"password manager otp is {otp}")
    except Exception as err:
        data["message"] = str(err)
        status_code = data["code"] = HTTP_400_BAD_REQUEST
    return Response(data, status=status_code)


class SignUpViewset(ModelViewSet):
    queryset = User.objects.all()

    def create(self, request):
        data = {
            "message": "Ok",
            "code": HTTP_200_OK,
            "data": {}
        }
        status_code = HTTP_200_OK
        try:
            username = request.data["username"]
            password = request.data["password"]
            re_password = request.data["repassword"]
            user_email = request.data["email"]
            signup_otp = request.data["otp"]

            if password != re_password:
                raise Exception("Both passwords are not same")
            if not OTP.objects.filter(email=user_email, number=signup_otp).exists():
                raise Exception("Invalid OTP")

            auth_user_data = {
                'username': username,
                'password': password,
                'email': user_email,
                'is_superuser': True
            }
            auth_user = AuthUserSerializer(data=auth_user_data)
            user = None
            if auth_user.is_valid(raise_exception=True):
                auth_user.save()

        except Exception as err:
            data["message"] = str(err)
            status_code = data["code"] = HTTP_400_BAD_REQUEST
        return Response(data, status=status_code)


class OrganisationViewset(ModelViewSet):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsSuperUser]

    def create(self, request):
        data = {
            "message": "Created",
            "code": HTTP_200_OK,
            "data": {}
        }
        status_code = HTTP_200_OK
        try:
            inp_data = {
                'name': request.data["name"],
                'email': request.data["email"],
                'created_by': request.user.id
            }
            serializer = self.get_serializer(data=inp_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        except Exception as err:
            data["message"] = str(err)
            status_code = data["code"] = HTTP_400_BAD_REQUEST
        return Response(data, status=status_code)


class MembersViewset(ModelViewSet):  # To add new members into a organisation
    queryset = Members.objects.all()
    permission_classes = [IsOrgSuperUser]

    def create(self, request):
        data = {
            "message": "Created",
            "code": HTTP_200_OK,
            "data": {}
        }
        status_code = HTTP_200_OK
        try:
            users = request.data["users"]
            users_serializer = MembersUserSerializer(data=users, many=True)
            if users_serializer.is_valid(raise_exception=True):
                members_id = users_serializer.save()
                members_data = {
                    'users': members_id,
                    'org_fk': request.data["org_fk"]
                }
                member_serializer = MembersSerializer(data=members_data)
                if member_serializer.is_valid(raise_exception=True):
                    member_serializer.save()

        except Exception as err:
            data["message"] = str(err)
            status_code = data["code"] = HTTP_400_BAD_REQUEST
        return Response(data, status=status_code)


class PasswordViewset(ModelViewSet):
    queryset = Passwords.objects.filter(expired=False)
    serializer_class = PasswordSerializer
    permission_classes = [PasswordPermission]

    def validate_password(self, password):
        return policy.test(password)

    def create(self, request):
        data = {
            "message": "Created",
            "code": HTTP_200_OK,
            "data": {}
        }
        status_code = HTTP_200_OK
        try:
            payload = request.data
            validates_password = self.validate_password(payload["raw_password"])
            if len(validates_password) != 0:
                raise Exception(f"Not a strong password : please provide {validates_password}")
            duration_from = datetime.now()
            input_data = {
                "org_fk" : payload["org_fk"],
                "duration" : payload["duration"],
                "raw_password" : payload["raw_password"],
                "duration_from" : duration_from,
                "duration_to" : duration_from + timedelta(seconds=int(payload["duration"]))
            }
            serializer = self.get_serializer(data=input_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                expire_passwords(schedule=duration_from + timedelta(seconds=int(payload["duration"])))
        except Exception as err:
            data["message"] = str(err)
            status_code = data["code"] = HTTP_400_BAD_REQUEST
        return Response(data, status=status_code)


    def list(self, request): #get organistions password / get shared passwords
        data = {
            "message": "Ok",
            "code": HTTP_200_OK,
            "data": {}
        }
        status_code = HTTP_200_OK        
        try:
            if request.GET.get("shared", False) == "1":
                password_ids = request.user.shared_to.values_list("password_id", flat=True)
                print("password_ids", password_ids)

                qs = self.get_queryset().filter(id__in=password_ids)
            else:
                organisations_list = request.user.organisation_set.values_list('id', flat=True)
                qs = self.get_queryset().filter(org_fk__in=organisations_list)
            data["data"] = PasswordsListingSerializer(qs, many=True).data
            
        except Exception as err:
            data["message"] = str(err)
            status_code = data["code"] = HTTP_400_BAD_REQUEST
        return Response(data, status=status_code)
    
    def retrieve(self, request, pk=None):
        data = {
            "message": "Ok",
            "code": HTTP_200_OK,
            "data": {}
        }
        status_code = HTTP_200_OK        
        try:
            qs = self.get_object()
            data["data"] = PasswordsListingSerializer(qs).data
            data["data"]["raw_password"] = qs.raw_password
            
        except Exception as err:
            data["message"] = str(err)
            status_code = data["code"] = HTTP_400_BAD_REQUEST
        return Response(data, status=status_code)
    
    def update(self, request, *args, **kwargs):
        data = {
            "message": "Updated",
            "code": HTTP_200_OK,
            "data": {}
        }
        status_code = HTTP_200_OK
        try:
            validates_password = self.validate_password(request.data["raw_password"])
            if len(validates_password) != 0:
                raise Exception(f"Not a strong password : please provide {validates_password}")
            instance = self.get_object()
            payload = {
                "duration" : request.data["duration"],
                "duration_to" : instance.duration_from + timedelta(seconds=int(request.data["duration"])),
                "raw_password" : request.data["raw_password"]
            }
            serializer = self.get_serializer(instance, data=payload, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except Exception as err:
            data["message"] = str(err)
            status_code = data["code"] = HTTP_400_BAD_REQUEST
        return Response(data, status=status_code)



class SharedPasswordsViewset(ModelViewSet):
    queryset = SharedPasswords.objects.filter(password__expired=False)
    serializer_class = SharePasswordSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        data = {
            "message": "Created",
            "code": HTTP_200_OK,
            "data": {}
        }
        status_code = HTTP_200_OK
        try:
            payload = request.data
            org = Passwords.objects.get(id=payload["password"]).org_fk
            shared_to_user = User.objects.get(id=payload["shared_to"])
            if self.get_queryset().filter(shared_to_id=payload["shared_to"], password_id=payload["password"]).exists():
                raise Exception("This password already shared with this member") 
            
            serializer = SharePasswordSerializer(data=payload)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                send_notification(org.email, f"{org.name} Password Shared", f"{org.name} Password Shared, from : {request.user.email} to : {shared_to_user.email}")

        except Exception as err:
            data["message"] = str(err)
            status_code = data["code"] = HTTP_400_BAD_REQUEST
        return Response(data, status=status_code)
    
    def list(self, request):
        data = {
            "message": "Ok",
            "code": HTTP_200_OK,
            "data": {}
        }
        status_code = HTTP_200_OK
        try:
            qs = self.get_queryset().filter(shared_to = request.user)
            serializer = SharePasswordsListSerializer(qs, many=True)
            data["data"] = serializer.data
        except Exception as err:
            data["message"] = str(err)
            status_code = data["code"] = HTTP_400_BAD_REQUEST
        return Response(data, status=status_code)
    