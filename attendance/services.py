from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from attendance.models import Attendance
from employees.models import employee
from leave.models import Leave


# =====================================================
# SETTINGS
# =====================================================

CHECK_IN_START = 9          # 09:00 AM
LATE_AFTER = 10              # 08:00 AM
HALF_DAY_AFTER = 12         # 12:00 PM
CHECK_OUT_ALLOWED = 18     # 05:00 PM
STANDARD_WORK_MINUTES = 8 * 60

# =====================================================


def get_today():
    return timezone.localdate()


def get_now():
    return timezone.localtime()


# =====================================================
# VALIDATIONS
# =====================================================

def get_employee(employee_id):
    try:
        return employee.objects.get(employee_id=employee_id)
    except employee.DoesNotExist:
        return None


def employee_active(emp):
    return emp.is_active


def employee_on_leave(emp, today):
    return Leave.objects.filter(
        employee=emp,
        status="Approved",
        start_date__lte=today,
        end_date__gte=today
    ).exists()


def today_attendance(emp, today):
    return Attendance.objects.filter(
        employee=emp,
        date=today
    ).first()


# =====================================================
# TIME HELPERS
# =====================================================

def check_checkin_allowed(now):
    return now.hour >= CHECK_IN_START


def check_checkout_allowed(now):
    return now.hour >= CHECK_OUT_ALLOWED


def attendance_status(hour):

    if hour >= HALF_DAY_AFTER:
        return "Half Day"

    if hour >= LATE_AFTER:
        return "Late"

    return "Present"


def calculate_working_hours(check_in, check_out):

    if not check_out:
        return None

    start = timedelta(
        hours=check_in.hour,
        minutes=check_in.minute,
        seconds=check_in.second
    )

    end = timedelta(
        hours=check_out.hour,
        minutes=check_out.minute,
        seconds=check_out.second
    )

    total = end - start

    hours = total.seconds // 3600
    minutes = (total.seconds % 3600) // 60

    return f"{hours:02d}:{minutes:02d}"


def total_minutes(check_in, check_out):

    start = timedelta(
        hours=check_in.hour,
        minutes=check_in.minute
    )

    end = timedelta(
        hours=check_out.hour,
        minutes=check_out.minute
    )

    return (end - start).seconds // 60


def calculate_late_minutes(check_in):

    office = timedelta(hours=LATE_AFTER)

    arrival = timedelta(
        hours=check_in.hour,
        minutes=check_in.minute
    )

    if arrival <= office:
        return 0

    return (arrival - office).seconds // 60


def calculate_overtime(check_in, check_out):

    worked = total_minutes(check_in, check_out)

    if worked <= STANDARD_WORK_MINUTES:
        return 0

    return worked - STANDARD_WORK_MINUTES


# =====================================================
# REMARKS
# =====================================================

def generate_remarks(status, check_in, check_out):

    remarks = []

    if status == "Late":
        remarks.append("Late Arrival")

    elif status == "Half Day":
        remarks.append("Half Day")

    if check_out:

        worked = total_minutes(check_in, check_out)

        if worked < STANDARD_WORK_MINUTES:
            remarks.append("Early Checkout")

        overtime = calculate_overtime(check_in, check_out)

        if overtime > 0:
            remarks.append(f"Overtime {overtime} mins")

    if not remarks:
        remarks.append("Present")

    return ", ".join(remarks)


# =====================================================
# CHECK IN
# =====================================================

def create_checkin(emp, today, now):

    status = attendance_status(now.hour)

    Attendance.objects.create(
        employee=emp,
        date=today,
        check_in=now.time(),
        status=status,
        remarks=generate_remarks(
            status,
            now.time(),
            None
        )
    )

    return f"Check In Successful ({status})"


# =====================================================
# CHECK OUT
# =====================================================

def create_checkout(attendance, now):

    attendance.check_out = now.time()

    attendance.working_hours = calculate_working_hours(
        attendance.check_in,
        attendance.check_out
    )

    attendance.remarks = generate_remarks(
        attendance.status,
        attendance.check_in,
        attendance.check_out
    )

    attendance.save()

    return (
        f"Check Out Successful "
        f"({attendance.working_hours} hrs)"
    )


# =====================================================
# MAIN SERVICE
# =====================================================

def mark_attendance(employee_id):

    emp = get_employee(employee_id)

    if not emp:
        return "Employee Not Found"

    today = get_today()

    now = get_now()

    if not employee_active(emp):
        return "Employee Account Disabled"

    if employee_on_leave(emp, today):
        return "Attendance Blocked (Approved Leave)"

    attendance = today_attendance(emp, today)

    # ------------------------
    # CHECK IN
    # ------------------------

    if attendance is None:

        if not check_checkin_allowed(now):
            return (
                f"Check In Allowed After "
                f"{CHECK_IN_START}:00 AM"
            )

        return create_checkin(
            emp,
            today,
            now
        )

    # ------------------------
    # CHECK OUT
    # ------------------------

    if attendance.check_out:
        return "Attendance Already Completed"

    if not check_checkout_allowed(now):
        return (
            f"Check Out Allowed After "
            f"{CHECK_OUT_ALLOWED}:00 PM"
        )

    return create_checkout(
        attendance,
        now
    )


# =====================================================
# MONTHLY SUMMARY
# =====================================================

def employee_summary(emp):

    records = Attendance.objects.filter(
        employee=emp
    )

    total = records.count()

    present = records.filter(
        status="Present"
    ).count()

    late = records.filter(
        status="Late"
    ).count()

    half_day = records.filter(
        status="Half Day"
    ).count()

    leave_days = Leave.objects.filter(
        employee=emp,
        status="Approved"
    ).count()

    attendance_percent = 0

    if total:
        attendance_percent = round(
            ((present + late + half_day) / total) * 100,
            2
        )

    return {
        "total_days": total,
        "present": present,
        "late": late,
        "half_day": half_day,
        "leave": leave_days,
        "attendance_percent": attendance_percent
    }


# =====================================================
# DASHBOARD
# =====================================================

def dashboard_statistics():

    today = get_today()

    records = Attendance.objects.filter(
        date=today
    )

    return {
        "today_present": records.filter(
            status="Present"
        ).count(),

        "today_late": records.filter(
            status="Late"
        ).count(),

        "today_half_day": records.filter(
            status="Half Day"
        ).count(),

        "total_attendance": records.count(),

        "active_employees": employee.objects.filter(
            is_active=True
        ).count(),

        "inactive_employees": employee.objects.filter(
            is_active=False
        ).count(),

        "approved_leave": Leave.objects.filter(
            status="Approved",
            start_date__lte=today,
            end_date__gte=today
        ).count()
    }


# =====================================================
# STATUS COUNTS
# =====================================================

def attendance_status_counts():

    return (
        Attendance.objects
        .values("status")
        .annotate(total=Count("status"))
        .order_by("status")
    )

def next_attendance_action(emp):

    today = get_today()
    now = get_now()

    attendance = today_attendance(emp, today)

    if attendance is None:

        status = attendance_status(now.hour)

        if status == "Present":
            return "CHECK IN"

        if status == "Late":
            return "LATE CHECK IN"

        return "HALF DAY"

    if attendance.check_out:
        return "ATTENDANCE COMPLETED"

    return "CHECK OUT"