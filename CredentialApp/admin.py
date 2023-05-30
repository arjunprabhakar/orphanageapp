from django.contrib import admin

from CredentialApp.models import tbl_login

# Register your models here.
# admin.site.register(tbl_login)



from django.http import HttpResponse
from .views import donation_analysys

def donation_analysys(request):
    return HttpResponse(donation_analysys(request))