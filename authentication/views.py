from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from employees.models import employee

from .forms import LoginForm
from django.contrib.auth import login

def login_view(request):

    if request.user.is_authenticated:

        if request.user.is_superuser:
            return redirect("admin_dashboard")

        return redirect("employee_dashboard")

    form = LoginForm(request, data=request.POST)
    error = None

    if request.method == "POST":

        if form.is_valid():

            user = form.get_user()

            if user.is_superuser:

                login(request, user)
                return redirect("admin_dashboard")

            try:

                emp = employee.objects.get(user=user)

                if not emp.is_active:

                    error = "Your account has been disabled."

                else:

                    login(request, user)
                    return redirect("employee_dashboard")

            except employee.DoesNotExist:

                error = "Employee profile not found."

        else:

            error = "Invalid Employee ID or Password."

    return render(
        request,
        "authentication/login.html",
        {
            "form": form,
            "error": error,
        },
    )



@login_required
def logout_view(request):

    logout(request)

    return redirect("login")