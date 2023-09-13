from django.urls import path, include
from rest_framework.routers import DefaultRouter
from organisation import views


router = DefaultRouter()
router.register(r'users', views.SignUpViewset ,basename="user")
router.register(r'organisation', views.OrganisationViewset ,basename="organisation")
router.register(r'members', views.MembersViewset ,basename="members")
router.register(r'passwords', views.PasswordViewset ,basename="password")
router.register(r'share_password', views.SharedPasswordsViewset ,basename="share_password")




urlpatterns = [
    path('', include(router.urls)),
    path('send_otp/', views.send_otp),
]