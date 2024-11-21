from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import TimeRecord, EmployeeProfile
from django.contrib import messages
from django.http import FileResponse, HttpResponse
from .pdf_generator import generate_dtr_pdf
import os
from datetime import datetime, timedelta
from calendar import monthrange
import io

# Create your views here.

@login_required
def dashboard(request):
    today = timezone.now().date()
    try:
        current_record = TimeRecord.objects.get(user=request.user, date=today)
    except TimeRecord.DoesNotExist:
        current_record = None
    
    recent_records = TimeRecord.objects.filter(user=request.user).order_by('-date')[:7]
    
    context = {
        'current_record': current_record,
        'recent_records': recent_records,
    }
    return render(request, 'dtr_app/dashboard.html', context)

@login_required
def time_in(request):
    today = timezone.now().date()
    current_time = timezone.now()
    
    record, created = TimeRecord.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={'time_in': current_time}
    )
    
    if not created and not record.time_in:
        record.time_in = current_time
        record.save()
        messages.success(request, 'Time-in recorded successfully!')
    else:
        messages.info(request, 'You have already timed in today.')
    
    return redirect('dashboard')

@login_required
def time_out(request):
    today = timezone.now().date()
    current_time = timezone.now()
    
    try:
        record = TimeRecord.objects.get(user=request.user, date=today)
        if record.time_in and not record.time_out:
            record.time_out = current_time
            record.save()
            messages.success(request, 'Time-out recorded successfully!')
        else:
            messages.warning(request, 'Cannot time-out without timing in first.')
    except TimeRecord.DoesNotExist:
        messages.error(request, 'No time record found for today.')
    
    return redirect('dashboard')

@login_required
def dtr_form(request):
    # Get the current date or the requested month
    requested_date = request.GET.get('date', timezone.now().date().strftime('%Y-%m'))
    try:
        year, month = map(int, requested_date.split('-'))
        current_date = datetime(year, month, 1).date()
    except (ValueError, TypeError):
        current_date = timezone.now().date().replace(day=1)
    
    # Get all time records for the month
    month_records = TimeRecord.objects.filter(
        user=request.user,
        date__year=current_date.year,
        date__month=current_date.month
    ).order_by('date')
    
    context = {
        'user': request.user,
        'current_month': current_date.strftime('%B %Y'),
        'time_records': month_records,
    }
    return render(request, 'dtr_app/dtr_form_new.html', context)

@login_required
def export_dtr_pdf(request):
    # Get the current date or the requested month
    requested_date = request.GET.get('date', timezone.now().date().strftime('%Y-%m'))
    try:
        year, month = map(int, requested_date.split('-'))
        current_date = datetime(year, month, 1).date()
    except (ValueError, TypeError):
        current_date = timezone.now().date().replace(day=1)
    
    # Get employee profile for additional details
    try:
        employee = EmployeeProfile.objects.get(user=request.user)
        employee_id = employee.employee_id
    except EmployeeProfile.DoesNotExist:
        employee_id = "N/A"

    # Get all time records for the month
    month_records = TimeRecord.objects.filter(
        user=request.user,
        date__year=current_date.year,
        date__month=current_date.month
    ).order_by('date')

    # Create a dictionary of time records keyed by day
    time_records_dict = {record.date.day: record for record in month_records}
    
    # Calculate total undertime
    total_undertime = timedelta()
    for record in month_records:
        if record.time_in and record.time_out:
            # You can customize this calculation based on your working hours
            expected_hours = timedelta(hours=8)
            actual_hours = record.time_out - record.time_in
            if actual_hours < expected_hours:
                total_undertime += expected_hours - actual_hours

    # Create a buffer for the PDF
    buffer = io.BytesIO()
    
    # Format the period string
    period = f"{current_date.strftime('%B')} 1-{monthrange(current_date.year, current_date.month)[1]}, {current_date.year}"
    
    # Generate the PDF with all the data
    generate_dtr_pdf(
        buffer,
        f"{request.user.first_name} {request.user.last_name}".upper(),
        period,
    )
    
    # FileResponse sets the Content-Disposition header
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="DTR_{current_date.strftime("%Y_%m")}.pdf"'
    
    # Clean up
    buffer.close()
    
    return response
