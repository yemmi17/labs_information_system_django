from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "middle_name", "position", "work_phone")
    search_fields = ("last_name", "first_name", "middle_name", "position", "work_phone", "personal_phone")
