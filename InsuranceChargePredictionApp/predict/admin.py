from django.contrib import admin
from .models import ClientInfos, Predictions

admin.site.register(Predictions)
admin.site.register(ClientInfos)