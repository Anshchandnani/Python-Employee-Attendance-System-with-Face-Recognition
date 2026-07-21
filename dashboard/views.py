#Employee Dashboard in employees/views.py file

from django.shortcuts import render
from django.utils import timezone
from employees.models import employee, department
from attendance.models import Attendance
from leave.models import Leave

from django.contrib.auth.decorators import login_required
from authentication.decorators import admin_required, employee_required

@login_required
@admin_required
def admin_dashboard(request):

    today = timezone.localdate()

    total_employees = employee.objects.filter(is_active=True).count()

    present_today = Attendance.objects.filter(
        date=today,
        status="Present"
    ).count()

    absent_today = total_employees - present_today
    recent_employees = employee.objects.order_by("-created_at")[:5]
    if total_employees > 0:
        attendance_percentage = round((present_today / total_employees) * 100, 2)
    else:
        attendance_percentage = 0

    context = {
        "total_employees": employee.objects.count(),
        "recent_employees": recent_employees,
        "attendance_percentage": attendance_percentage,

        "active_employees": employee.objects.filter(
            is_active=True
        ).count(),

        "inactive_employees": employee.objects.filter(
            is_active=False
        ).count(),

        "departments": department.objects.count(),

        "present_today": present_today,
        "absent_today": absent_today,

        "pending_leave": Leave.objects.filter(
            status="Pending"
        ).count(),

        "recent_attendance":
        Attendance.objects.select_related(
            "employee"
        ).order_by(
            "-check_in"
        )[:10],

    }

    return render(
        request,
        "dashboard/admin_dashboard.html",
        context,
    )
