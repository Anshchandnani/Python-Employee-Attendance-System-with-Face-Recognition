from django.shortcuts import render


def page_not_found(request, exception):

    if request.user.is_authenticated:

        if request.user.is_superuser:
            return render(request, "errors/404_admin.html", status=404)

        return render(request, "errors/404_employee.html", status=404)

    return render(request, "errors/404_guest.html", status=404)


def permission_denied(request, exception):

    if request.user.is_authenticated:

        if request.user.is_superuser:
            return render(request, "errors/403_admin.html", status=403)

        return render(request, "errors/403_employee.html", status=403)

    return render(request, "errors/403_guest.html", status=403)


def server_error(request):

    if request.user.is_authenticated:

        if request.user.is_superuser:
            return render(request, "errors/500_admin.html", status=500)

        return render(request, "errors/500_employee.html", status=500)

    return render(request, "errors/500_guest.html", status=500)