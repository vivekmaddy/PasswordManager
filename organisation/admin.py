from django.contrib import admin

from .models import *

# Register your models here.


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('number', 'email',)

@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email',)


@admin.register(Passwords)
class PasswordsAdmin(admin.ModelAdmin):
    list_display = ('org_fk', 'hashed_password', 'raw_password')


@admin.register(Members)
class MembersAdmin(admin.ModelAdmin):
    list_display = ('org_fk',)


@admin.register(SharedPasswords)
class SharedPasswordsAdmin(admin.ModelAdmin):
    list_display = ('shared_to', 'shared_by', 'view', 'edit')
