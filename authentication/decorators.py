from functools import wraps

from django.shortcuts import redirect
from django.contrib import messages

from employees.models import employee


def admin_required(view_func):

    @wraps(view_func)

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:

            return redirect("login")

        if not request.user.is_superuser:

            messages.error(
                request,
                "Administrator access required."
            )

            return redirect("employee_dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper


def employee_required(view_func):

    @wraps(view_func)

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:

            return redirect("login")

        if request.user.is_superuser:

            return redirect("admin_dashboard")

        try:

            emp = employee.objects.get(
                user=request.user
            )

        except employee.DoesNotExist:

            messages.error(
                request,
                "Employee account not found."
            )

            return redirect("login")

        if not emp.is_active:

            messages.error(
                request,
                "Your account has been disabled."
            )

            return redirect("logout")

        request.employee = emp

        return view_func(request, *args, **kwargs)

    return wrapper