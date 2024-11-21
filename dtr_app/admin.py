from django.contrib import admin
from .models import TimeRecord, EmployeeProfile

# Register your models here.

@admin.register(TimeRecord)
class TimeRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'time_in', 'time_out', 'status')
    list_filter = ('date', 'status')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    date_hierarchy = 'date'

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'position')
    search_fields = ('user__username', 'employee_id', 'department')
