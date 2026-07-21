from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from employees.models import employee
from .forms import LeaveForm
from .models import Leave
from .services import LeaveService
from django.contrib.auth.decorators import login_required
from authentication.decorators import admin_required, employee_required


# ==========================================
# GET LOGGED-IN EMPLOYEE
# ==========================================

def get_logged_in_employee(request):

    try:

        return employee.objects.get(
            user=request.user,
            is_active=True
        )

    except employee.DoesNotExist:

        return None


# ==========================================
# LEAVE LIST
# ==========================================

@login_required
@admin_required
def leave_list(request):

    emp = get_logged_in_employee(request)

    if not emp and not request.user.is_superuser:

        messages.error(
            request,
            "Employee profile not found."
        )

        return redirect("login")

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "")
    leave_type = request.GET.get("leave_type", "")

    if request.user.is_superuser:

        queryset = LeaveService.search(
            search=search,
            status=status,
            leave_type=leave_type
        )

    else:

        queryset = Leave.objects.filter(
            employee=emp
        ).order_by("-created_at")

        if status:

            queryset = queryset.filter(
                status=status
            )

        if leave_type:

            queryset = queryset.filter(
                leave_type=leave_type
            )

    paginator = Paginator(
        queryset,
        10
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    context = {

        "page_obj": page_obj,

        "search": search,

        "status": status,

        "leave_type": leave_type

    }

    return render(

        request,

        "leave/leave_list.html",

        context

    )


# ==========================================
# APPLY LEAVE
# ==========================================

@login_required
@employee_required
def apply_leave(request):

    emp = get_logged_in_employee(request)

    if not emp:
        messages.error(
            request,
            "Employee profile not found."
        )
        return redirect("login")

    if request.method == "POST":

        form = LeaveForm(
            request.POST,
            employee=emp
        )

        if not form.is_valid():

            # Display validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)

            return render(
                request,
                "leave/apply_leave.html",
                {
                    "form": form
                }
            )

        success, message = LeaveService.apply_leave(
            emp,
            form
        )

        if success:
            messages.success(
                request,
                message
            )
            return redirect("employee_dashboard")

        messages.error(
            request,
            message
        )

        return render(
            request,
            "leave/apply_leave.html",
            {
                "form": form
            }
        )

    else:
        form = LeaveForm(employee=emp)

    return render(
        request,
        "leave/apply_leave.html",
        {
            "form": form
        }
    )

# ==========================================
# EDIT LEAVE
# ==========================================

@login_required
@admin_required
def edit_leave(request, leave_id):

    leave = get_object_or_404(
        Leave,
        id=leave_id
    )

    emp = get_logged_in_employee(request)

    if not request.user.is_superuser:

        if leave.employee != emp:

            messages.error(
                request,
                "Permission denied."
            )

            return redirect("leave_list")

    if request.method == "POST":

        form = LeaveForm(

            request.POST,

            instance=leave,

            employee=leave.employee

        )

        if form.is_valid():

            success, message = LeaveService.edit_leave(

                leave,

                form

            )

            if success:

                messages.success(
                    request,
                    message
                )

                return redirect(
                    "leave_list"
                )

            messages.error(
                request,
                message
            )

    else:

        form = LeaveForm(

            instance=leave,

            employee=leave.employee

        )

    return render(

        request,

        "leave/edit_leave.html",

        {

            "form": form,

            "leave": leave

        }

    )


# ==========================================
# APPROVE LEAVE
# ==========================================

@login_required
@admin_required
def approve_leave(request, leave_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "Permission denied."
        )

        return redirect("leave_list")

    leave = get_object_or_404(
        Leave,
        id=leave_id
    )

    remarks = request.POST.get(
        "remarks",
        ""
    )

    success, message = LeaveService.approve_leave(

        leave,

        remarks

    )

    if success:

        messages.success(
            request,
            message
        )

    else:

        messages.error(
            request,
            message
        )

    return redirect(
        "leave_list"
    )


# ==========================================
# REJECT LEAVE
# ==========================================

@login_required
@admin_required
def reject_leave(request, leave_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "Permission denied."
        )

        return redirect("leave_list")

    leave = get_object_or_404(
        Leave,
        id=leave_id
    )

    remarks = request.POST.get(
        "remarks",
        ""
    )

    success, message = LeaveService.reject_leave(

        leave,

        remarks

    )

    if success:

        messages.success(
            request,
            message
        )

    else:

        messages.error(
            request,
            message
        )

    return redirect(
        "leave_list"
    )


# ==========================================
# CANCEL LEAVE
# ==========================================

@login_required
@employee_required
@login_required
def cancel_leave(request, leave_id):

    leave = get_object_or_404(
        Leave,
        id=leave_id
    )

    emp = get_logged_in_employee(request)

    if leave.employee != emp:

        messages.error(
            request,
            "Permission denied."
        )

        return redirect("my_leaves")

    if leave.status != "Pending":

        messages.error(
            request,
            "Only pending leave requests can be cancelled."
        )

        return redirect("my_leaves")

    leave.delete()

    messages.success(
        request,
        "Leave request cancelled successfully."
    )

    return redirect("my_leaves")

# ==========================================
# DELETE LEAVE
# ==========================================

@login_required
@admin_required
def delete_leave(request, leave_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "Permission denied."
        )

        return redirect(
            "leave_list"
        )

    leave = get_object_or_404(

        Leave,

        id=leave_id

    )

    success, message = LeaveService.delete_leave(

        leave

    )

    if success:

        messages.success(
            request,
            message
        )

    else:

        messages.error(
            request,
            message
        )

    return redirect(
        "leave_list"
    )

from django.http import JsonResponse


# ==========================================
# LEAVE DETAIL
# ==========================================

@login_required
def leave_detail(request, leave_id):

    leave = get_object_or_404(
        Leave,
        id=leave_id
    )

    if not request.user.is_superuser:

        emp = get_logged_in_employee(request)

        if leave.employee != emp:

            messages.error(
                request,
                "Permission denied."
            )

            return redirect(
                "leave_list"
            )

    if request.user.is_superuser:
        template = "leave/leave_detail.html"
    else:
        template = "leave/employee_leave_detail.html"

    return render(
        request,
        template,
        {"leave": leave}
    )


# ==========================================
# ADMIN DASHBOARD SUMMARY
# ==========================================

@login_required
@admin_required
def dashboard_leave_summary(request):

    if not request.user.is_superuser:

        return redirect(
            "employee_dashboard"
        )

    summary = LeaveService.dashboard_summary()

    recent = LeaveService.recent()

    pending = LeaveService.pending_leaves()

    today = LeaveService.todays_leaves()

    context = {

        "summary": summary,

        "recent_leaves": recent,

        "pending_leaves": pending,

        "today_leaves": today

    }

    return render(

        request,

        "leave/dashboard_summary.html",

        context

    )


# ==========================================
# EMPLOYEE SUMMARY
# ==========================================

@login_required
@employee_required
def employee_leave_summary(request):

    emp = get_logged_in_employee(request)

    if not emp:

        messages.error(
            request,
            "Employee profile not found."
        )

        return redirect(
            "login"
        )

    summary = LeaveService.employee_summary(
        emp
    )

    recent = Leave.objects.filter(

        employee=emp

    ).order_by(

        "-created_at"

    )[:10]

    return render(

        request,

        "leave/employee_summary.html",

        {

            "summary": summary,

            "recent": recent

        }

    )

# ==========================================
# MY LEAVES
# ==========================================

@login_required
@employee_required
def my_leaves(request):

    emp = get_logged_in_employee(request)

    if not emp:

        messages.error(
            request,
            "Employee profile not found."
        )

        return redirect("login")

    status = request.GET.get("status", "").strip()
    leave_type = request.GET.get("leave_type", "").strip()

    queryset = Leave.objects.filter(
        employee=emp
    ).order_by("-created_at")

    if status:

        queryset = queryset.filter(
            status=status
        )

    if leave_type:

        queryset = queryset.filter(
            leave_type=leave_type
        )

    paginator = Paginator(
        queryset,
        5
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    context = {

        "leaves": page_obj,

        "status": status,

        "leave_type": leave_type,

    }

    return render(

        request,

        "leave/my_leaves.html",

        context

    )

# ==========================================
# CALENDAR EVENTS API
# ==========================================

@login_required
def leave_calendar_events(request):

    if request.user.is_superuser:

        events = LeaveService.calendar_events()

    else:

        emp = get_logged_in_employee(request)

        events = []

        for leave in Leave.objects.filter(

            employee=emp,

            status="Approved"

        ):

            events.append({

                "title": leave.leave_type,

                "start": leave.start_date,

                "end": leave.end_date,

                "status": leave.status

            })

    return JsonResponse(

        events,

        safe=False

    )


# ==========================================
# MONTHLY REPORT
# ==========================================

@login_required
def monthly_leave_report(request):

    if not request.user.is_superuser:

        return redirect(
            "employee_dashboard"
        )

    today = timezone.localdate()

    summary = LeaveService.monthly_summary(

        today.month,

        today.year

    )

    return render(

        request,

        "leave/monthly_report.html",

        {

            "summary": summary

        }

    )


# ==========================================
# DEPARTMENT REPORT
# ==========================================

@login_required
def department_leave_report(request):

    if not request.user.is_superuser:

        return redirect(
            "employee_dashboard"
        )

    departments = LeaveService.department_summary()

    return render(

        request,

        "leave/department_report.html",

        {

            "departments": departments

        }

    )


# ==========================================
# STATUS REPORT
# ==========================================

@login_required
def leave_status_report(request):

    if not request.user.is_superuser:

        return redirect(
            "employee_dashboard"
        )

    status_counts = LeaveService.status_counts()

    return render(

        request,

        "leave/status_report.html",

        {

            "status_counts": status_counts

        }

    )