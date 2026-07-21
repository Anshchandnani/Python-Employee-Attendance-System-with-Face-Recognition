from django.urls import path

from . import views

urlpatterns = [

    # ==========================================
    # Employee
    # ==========================================

    path(
        "",
        views.leave_list,
        name="leave_list"
    ),

    path(
        "apply/",
        views.apply_leave,
        name="apply_leave"
    ),

    path(
        "<int:leave_id>/",
        views.leave_detail,
        name="leave_detail"
    ),

    path(
        "<int:leave_id>/edit/",
        views.edit_leave,
        name="edit_leave"
    ),

    path(
        "<int:leave_id>/cancel/",
        views.cancel_leave,
        name="cancel_leave"
    ),

    path(
        "summary/",
        views.employee_leave_summary,
        name="employee_leave_summary"
    ),

    path(
        "calendar-events/",
        views.leave_calendar_events,
        name="leave_calendar_events"
    ),

    # ==========================================
    # Admin
    # ==========================================

    path(
        "<int:leave_id>/approve/",
        views.approve_leave,
        name="approve_leave"
    ),

    path(
        "<int:leave_id>/reject/",
        views.reject_leave,
        name="reject_leave"
    ),

    path(
        "<int:leave_id>/delete/",
        views.delete_leave,
        name="delete_leave"
    ),

    path(
        "dashboard/",
        views.dashboard_leave_summary,
        name="dashboard_leave_summary"
    ),

    path(
        "reports/monthly/",
        views.monthly_leave_report,
        name="monthly_leave_report"
    ),

    path(
        "reports/department/",
        views.department_leave_report,
        name="department_leave_report"
    ),

    path(
        "reports/status/",
        views.leave_status_report,
        name="leave_status_report"
    ),
    
    path(
        "my-leaves/",
        views.my_leaves,
        name="my_leaves"
    ),

]