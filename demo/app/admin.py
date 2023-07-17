from django.contrib import admin

from .models import City, Person


@admin.register(City, Person)
class Admin(admin.ModelAdmin):
    search_fields = ["name"]
