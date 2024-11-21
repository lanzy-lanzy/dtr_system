from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class TimeRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day')
    ], default='present')
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date', '-time_in']

    def __str__(self):
        return f"{self.user.username} - {self.date}"

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
