from django.contrib import admin

from .models import Ausgabe


@admin.register(Ausgabe)
class AusgabenAdmin(admin.ModelAdmin):
    pass
