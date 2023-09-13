from rest_framework.serializers import ModelSerializer, SerializerMethodField
from django.contrib.auth.models import User

from .models import *


class OTPSerializer(ModelSerializer):
    class Meta:
        model = OTP
        fields = "__all__"

    def create(self, validated_data):
        otp = OTP.objects.update_or_create(
            email=validated_data["email"],
            defaults=validated_data
            )
        return otp

class AuthUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'is_superuser')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class OrganisationSerializer(ModelSerializer):
    class Meta:
        model = Organisation
        fields = "__all__"

class MembersUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user.id

class MembersSerializer(ModelSerializer):
    class Meta:
        model = Members
        fields = "__all__"

    def create(self, validated_data):
        users = validated_data.pop('users', [])
        member = Members.objects.get_or_create(org_fk=validated_data["org_fk"])
        member = member[0]
        users += list(member.users.values_list('id', flat=True))
        member.users.set(users)
        return member

class PasswordSerializer(ModelSerializer):
    class Meta:
        model = Passwords
        fields = "__all__"

class PasswordsListingSerializer(ModelSerializer):
    organisation = SerializerMethodField()
    class Meta:
        model = Passwords
        exclude = ('raw_password',)

    def get_organisation(self, obj):
        return {'name' : obj.org_fk.name, 'email' : obj.org_fk.email, 'created_by' : obj.org_fk.created_by.username}
    

class SharePasswordSerializer(ModelSerializer):
    class Meta:
        model = SharedPasswords
        fields = "__all__"

class SharePasswordsListSerializer(ModelSerializer):
    
    password = SerializerMethodField()
    class Meta:
        model = SharedPasswords
        fields = "__all__"
    
    def get_password(self, obj):
        password = PasswordsListingSerializer(obj.password).data
        password["raw_password"] = obj.password.raw_password
        if not obj.view:
            password.pop("hashed_password", None)
            password.pop("raw_password", None)
        return password
