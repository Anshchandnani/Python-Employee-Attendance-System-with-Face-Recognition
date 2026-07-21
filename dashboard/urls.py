from django.urls import path
from employees import views as ve
from . import views

urlpatterns = [

    path(
        "admin/",
        views.admin_dashboard,
        name="admin_dashboard",
    ),

    path(
        "employee/",
        ve.employee_dashboard,
        name="employee_dashboard",
    ),

]