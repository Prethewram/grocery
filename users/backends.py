from django.contrib.auth.hashers import check_password
from .models import CoAdmin
from django.contrib.auth.backends import ModelBackend

class CoAdminBackend:
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            coadmin = CoAdmin.objects.get(email=email)
        except CoAdmin.DoesNotExist:
            return None

        # Manually check if the password is correct
        if check_password(password, coadmin.password):
            return coadmin
        return None
    

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = CoAdmin.objects.get(email=email)
            if user.check_password(password):
                return user
        except CoAdmin.DoesNotExist:
            return None
