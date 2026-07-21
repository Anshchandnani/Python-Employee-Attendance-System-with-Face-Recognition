from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from authentication.decorators import admin_required,employee_required

from employees.models import employee
from leave.models import Leave

from .recognize import start_recognition

from django.shortcuts import redirect
from .capture import capture_faces

@admin_required
def capture_face(request, employee_id):

    capture_faces(employee_id)

    return redirect(
        "employee_profile",
        employee_id=employee_id
    )

@login_required
@employee_required
def recognize_face(request):

    emp = request.employee

    if not emp.is_active:

        messages.error(
            request,
            "Your account has been disabled."
        )

        return redirect("logout")

    today = timezone.localdate()

    approved_leave = Leave.objects.filter(
        employee=emp,
        status="Approved",
        start_date__lte=today,
        end_date__gte=today
    ).exists()

    if approved_leave:

        messages.warning(
            request,
            "Attendance is disabled because you are on approved leave."
        )

        return redirect("employee_dashboard")

    try:

        start_recognition(emp.employee_id)

        messages.success(
            request,
            "Attendance processed successfully."
        )

    except Exception as e:

        messages.error(
            request,
            str(e)
        )

    return redirect("employee_dashboard")