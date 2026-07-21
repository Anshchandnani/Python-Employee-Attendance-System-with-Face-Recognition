from leave.models import Leave


def employee_on_leave(employee, today):

    return Leave.objects.filter(

        employee=employee,

        status="Approved",

        start_date__lte=today,

        end_date__gte=today

    ).exists()


def employee_active(employee):

    return employee.is_active


def attendance_exists(employee, today):

    from attendance.models import Attendance

    return Attendance.objects.filter(

        employee=employee,

        date=today

    ).first()