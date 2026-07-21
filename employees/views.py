from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.crypto import get_random_string
from attendance.models import Attendance
from leave.models import Leave
from .forms import EmployeeForm
from .models import employee, department
from django.contrib.auth.decorators import login_required
from authentication.decorators import admin_required, employee_required

def dashboard(request):

    today = timezone.localdate()

    total_employees = employee.objects.count()

    active_employees = employee.objects.filter(
        is_active=True
    ).count()

    inactive_employees = employee.objects.filter(
        is_active=False
    ).count()

    total_departments = department.objects.count()

    present_today = Attendance.objects.filter(
        date=today
    ).count()

    absent_today = max(
        total_employees - present_today,
        0
    )

    attendance_percentage = 0

    if total_employees > 0:

        attendance_percentage = round(
            (present_today / total_employees) * 100,
            2
        )

    recent_employees = employee.objects.order_by(
        "-created_at"
    )[:5]

    recent_attendance = Attendance.objects.select_related(
        "employee"
    ).order_by(
        "-check_in"
    )[:5]

    context = {

        "total_employees": total_employees,

        "active_employees": active_employees,

        "inactive_employees": inactive_employees,

        "total_departments": total_departments,

        "present_today": present_today,

        "absent_today": absent_today,

        "attendance_percentage": attendance_percentage,

        "recent_employees": recent_employees,

        "recent_attendance": recent_attendance,

    }

    return render(
        request,
        "dashboard.html",
        context,
    )


@login_required
@admin_required
def employee_list(request):

    search = request.GET.get("search")

    employees = employee.objects.all().order_by("employee_id")

    if search:

        employees = employees.filter(
            Q(employee_id__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(department__name__icontains=search) |
            Q(designation__icontains=search)
        )

    context = {

        "employees": employees,

        "search": search,

        "total_employees": employee.objects.count(),

        "active_employees": employee.objects.filter(
            is_active=True
        ).count(),

        "total_departments": department.objects.count(),

    }

    return render(
        request,
        "employees/employee_list.html",
        context,
    )

@login_required
@admin_required
def employee_profile(request, employee_id):

    emp = get_object_or_404(
        employee,
        employee_id=employee_id
    )

    return render(
        request,
        "employees/employee_profile.html",
        {
            "emp": emp
        }
    )

@login_required
@admin_required
def add_employee(request):

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            try:

                with transaction.atomic():

                    emp = form.save()

                    username = emp.employee_id

                    password = get_random_string(
                        length=10,
                        allowed_chars="ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
                    )

                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        first_name=emp.first_name,
                        last_name=emp.last_name,
                        email=emp.email,
                        is_active=emp.is_active
                    )

                    emp.user = user
                    emp.save()

                    request.session["new_employee_credentials"] = {
                        "employee_id": emp.employee_id,
                        "username": username,
                        "password": password,
                    }

                    return redirect(
                        "employee_created",
                        employee_id=emp.employee_id
                    )

            except Exception as e:

                messages.error(
                    request,
                    f"Error creating employee account: {e}"
                )

    else:

        form = EmployeeForm()

    return render(
        request,
        "employees/employee_form.html",
        {
            "form": form,
            "title": "Add Employee"
        }
    )

@login_required
@admin_required
def update_employee(request, employee_id):

    emp = get_object_or_404(
        employee,
        employee_id=employee_id
    )

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            request.FILES,
            instance=emp
        )

        if form.is_valid():

            emp = form.save()

            if emp.user:
                emp.user.first_name = emp.first_name
                emp.user.last_name = emp.last_name
                emp.user.email = emp.email
                emp.user.is_active = emp.is_active
                emp.user.save()
            messages.success(
                request,
                "Employee updated successfully."
            )

            return redirect("employee_list")

    else:

        form = EmployeeForm(
            instance=emp
        )

    return render(
        request,
        "employees/employee_form.html",
        {
            "form": form,
            "title": "Update Employee"
        }
    )

@login_required
@admin_required
def delete_employee(request, employee_id):

    emp = get_object_or_404(
        employee,
        employee_id=employee_id
    )

    if emp.user:
        emp.user.delete()
    else:
        emp.delete()

    messages.success(
        request,
        "Employee deleted successfully."
    )

    return redirect("employee_list")

@login_required
@admin_required
def employee_created(request, employee_id):

    credentials = request.session.get(
        "new_employee_credentials"
    )

    if not credentials:

        messages.error(
            request,
            "Credentials are no longer available."
        )

        return redirect("employee_list")

    if credentials["employee_id"] != employee_id:

        return redirect("employee_list")

    del request.session["new_employee_credentials"]

    return render(
        request,
        "employees/employee_created.html",
        {
            "credentials": credentials
        }
    )

from django.contrib.auth.decorators import login_required

@login_required
@employee_required
def employee_dashboard(request):

    emp = get_object_or_404(
        employee,
        user=request.user
    )

    today = timezone.localdate()

    # Today's attendance
    today_attendance = Attendance.objects.filter(
        employee=emp,
        date=today
    ).first()

    # Attendance summary
    total_attendance = Attendance.objects.filter(
        employee=emp,
        status__in=["Present", "Half Day", "Late"]
    ).count()

    present_days = Attendance.objects.filter(
        employee=emp
    ).count()

    recent_attendance = Attendance.objects.filter(
        employee=emp
    ).order_by(
        "-date"
    )[:5]

    upcoming_leaves = Leave.objects.filter(
        employee=emp,
        end_date__gte=today
    ).order_by("start_date")[:5]

    context = {

        "emp": emp,

        "today": today,

        "today_attendance": today_attendance,

        "total_attendance": total_attendance,
        "recent_attendance": recent_attendance,
        "upcoming_leaves": upcoming_leaves,
        "present_days": present_days,

    }

    return render(
        request,
        "dashboard/employee_dashboard.html",
        context
    )

