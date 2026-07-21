from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),



    path(
        "employees/",
        views.employee_list,
        name="employee_list",
    ),

    path(
        "add/",
        views.add_employee,
        name="add_employee",
    ),

    path(
        "profile/<str:employee_id>/",
        views.employee_profile,
        name="employee_profile",
    ),

    path(
        "update/<str:employee_id>/",
        views.update_employee,
        name="update_employee",
    ),

    path(
        "delete/<str:employee_id>/",
        views.delete_employee,
        name="delete_employee",
    ),

    path(
        "employee-created/<str:employee_id>/",
        views.employee_created,
        name="employee_created",
    ),

path(
    "employee-dashboard/",
    views.employee_dashboard,
    name="employee_dashboard"
),

path(
        "change-password/",
        auth_views.PasswordChangeView.as_view(
            template_name="employees/change_password.html",
            success_url=reverse_lazy("employee_dashboard"),
        ),
        name="employee_change_password",
    ),

]