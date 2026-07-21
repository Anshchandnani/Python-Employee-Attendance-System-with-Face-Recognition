from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from employees.models import employee
from django.shortcuts import get_object_or_404
from .models import Attendance
from django.contrib.auth.decorators import login_required
from authentication.decorators import admin_required, employee_required

@login_required
@admin_required
def attendance_list(request):

    search = request.GET.get("search", "")

    attendance_date = request.GET.get("date", "")

    attendance = Attendance.objects.select_related(
        "employee"
    ).order_by(
        "-date",
        "-check_in"
    )

    if search:

        attendance = attendance.filter(

            Q(employee__employee_id__icontains=search) |

            Q(employee__first_name__icontains=search) |

            Q(employee__last_name__icontains=search)

        )

    if attendance_date:

        attendance = attendance.filter(
            date=attendance_date
        )

    paginator = Paginator(
        attendance,
        10
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(

        request,

        "attendance/attendance_list.html",

        {

            "page_obj": page_obj,

            "search": search,

            "attendance_date": attendance_date,

        }

    )

@login_required
@employee_required
def attendance_history(request):

    emp = get_object_or_404(
        employee,
        user=request.user
    )

    attendance = Attendance.objects.filter(
        employee=emp
    ).order_by("-date", "-check_in")

    total_attendance = Attendance.objects.filter(
        employee=emp,
        status__in=["Present", "Half Day", "Late"]
    ).count()

    search_date = request.GET.get("date")

    if search_date:
        attendance = attendance.filter(date=search_date)

    context = {

        "attendance": attendance,

        "employee": emp,

        "search_date": search_date,

        "total_present": total_attendance,

    }

    return render(
        request,
        "attendance/attendance_history.html",
        context,
    )