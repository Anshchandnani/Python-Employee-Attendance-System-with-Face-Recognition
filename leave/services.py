from datetime import timedelta

from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from attendance.models import Attendance
from employees.models import employee
from django.db.models import Q
from .models import Leave


class LeaveService:

    # ==========================================
    # EMPLOYEE VALIDATION
    # ==========================================

    @staticmethod
    def get_employee(employee_id):

        try:

            return employee.objects.get(
                employee_id=employee_id
            )

        except employee.DoesNotExist:

            return None

    # ==========================================
    # LEAVE VALIDATION
    # ==========================================

    @staticmethod
    def has_overlapping_leave(emp, start_date, end_date, leave_id=None):

        queryset = Leave.objects.filter(

            employee=emp,

            status__in=[
                "Pending",
                "Approved"
            ],

            start_date__lte=end_date,

            end_date__gte=start_date

        )

        if leave_id:

            queryset = queryset.exclude(
                id=leave_id
            )

        return queryset.exists()

    # ==========================================
    # LEAVE DAYS
    # ==========================================

    @staticmethod
    def calculate_leave_days(start_date, end_date):

        return (

            end_date - start_date

        ).days + 1

    # ==========================================
    # APPLY LEAVE
    # ==========================================

    @staticmethod
    @transaction.atomic
    def apply_leave(emp, form):

        if LeaveService.has_overlapping_leave(

            emp,

            form.cleaned_data["start_date"],

            form.cleaned_data["end_date"]

        ):

            return False, "Leave already exists for selected dates."

        leave = form.save(

            commit=False

        )

        leave.employee = emp

        leave.save()

        return True, "Leave Applied Successfully."

    # ==========================================
    # EDIT LEAVE
    # ==========================================

    @staticmethod
    @transaction.atomic
    def edit_leave(leave, form):

        if leave.status != "Pending":

            return False, "Only pending leave can be edited."

        if LeaveService.has_overlapping_leave(

            leave.employee,

            form.cleaned_data["start_date"],

            form.cleaned_data["end_date"],

            leave.id

        ):

            return False, "Leave already exists for selected dates."

        form.save()

        return True, "Leave Updated Successfully."

    # ==========================================
    # ATTENDANCE CREATION
    # ==========================================

    @staticmethod
    def create_leave_attendance(leave):

        current_date = leave.start_date

        while current_date <= leave.end_date:

            Attendance.objects.get_or_create(

                employee=leave.employee,

                date=current_date,

                defaults={

                    "status": "Leave",

                    "check_in": "00:00"

                }

            )

            current_date += timedelta(days=1)

    # ==========================================
    # REMOVE LEAVE ATTENDANCE
    # ==========================================

    @staticmethod
    def remove_leave_attendance(leave):

        Attendance.objects.filter(

            employee=leave.employee,

            status="Leave",

            date__gte=leave.start_date,

            date__lte=leave.end_date

        ).delete()

    # ==========================================
    # APPROVE LEAVE
    # ==========================================

    @staticmethod
    @transaction.atomic
    def approve_leave(leave, remarks=""):

        if leave.status == "Approved":

            return False, "Leave already approved."

        leave.status = "Approved"

        leave.admin_remarks = remarks

        leave.approved_at = timezone.now()

        leave.save()

        LeaveService.create_leave_attendance(
            leave
        )

        return True, "Leave Approved Successfully."

    # ==========================================
    # REJECT LEAVE
    # ==========================================

    @staticmethod
    @transaction.atomic
    def reject_leave(leave, remarks=""):

        if leave.status == "Rejected":

            return False, "Leave already rejected."

        LeaveService.remove_leave_attendance(
            leave
        )

        leave.status = "Rejected"

        leave.admin_remarks = remarks

        leave.save()

        return True, "Leave Rejected Successfully."

    # ==========================================
    # CANCEL LEAVE
    # ==========================================

    @staticmethod
    @transaction.atomic
    def cancel_leave(leave):

        if leave.status != "Pending":

            return False, (
                "Only pending leave can be cancelled."
            )

        leave.delete()

        return True, "Leave Cancelled Successfully."

    # ==========================================
    # DELETE LEAVE
    # ==========================================

    @staticmethod
    @transaction.atomic
    def delete_leave(leave):

        LeaveService.remove_leave_attendance(
            leave
        )

        leave.delete()

        return True, "Leave Deleted Successfully."

    # ==========================================
    # CHANGE STATUS
    # ==========================================

    @staticmethod
    @transaction.atomic
    def change_status(leave, status, remarks=""):

        status = status.title()

        if status == "Approved":

            return LeaveService.approve_leave(
                leave,
                remarks
            )

        if status == "Rejected":

            return LeaveService.reject_leave(
                leave,
                remarks
            )

        return False, "Invalid Status."

    # ==========================================
    # TODAY'S LEAVES
    # ==========================================

    @staticmethod
    def todays_leaves():

        today = timezone.localdate()

        return Leave.objects.filter(

            status="Approved",

            start_date__lte=today,

            end_date__gte=today

        ).select_related(
            "employee"
        )

    # ==========================================
    # PENDING LEAVES
    # ==========================================

    @staticmethod
    def pending_leaves():

        return Leave.objects.filter(

            status="Pending"

        ).select_related(

            "employee"

        ).order_by(

            "-created_at"

        )

    # ==========================================
    # RECENT LEAVES
    # ==========================================

    @staticmethod
    def recent_leaves(limit=10):

        return Leave.objects.select_related(

            "employee"

        ).order_by(

            "-created_at"

        )[:limit]

    # ==========================================
    # EMPLOYEE SUMMARY
    # ==========================================

    @staticmethod
    def employee_summary(emp):

        leaves = Leave.objects.filter(
            employee=emp
        )

        total = leaves.count()

        pending = leaves.filter(
            status="Pending"
        ).count()

        approved = leaves.filter(
            status="Approved"
        ).count()

        rejected = leaves.filter(
            status="Rejected"
        ).count()

        total_days = sum(
            leave.total_days
            for leave in leaves
            if leave.status == "Approved"
        )

        return {

            "total": total,

            "pending": pending,

            "approved": approved,

            "rejected": rejected,

            "approved_days": total_days

        }

    # ==========================================
    # DASHBOARD SUMMARY
    # ==========================================

    @staticmethod
    def dashboard_summary():

        today = timezone.localdate()

        return {

            "pending": Leave.objects.filter(
                status="Pending"
            ).count(),

            "approved": Leave.objects.filter(
                status="Approved"
            ).count(),

            "rejected": Leave.objects.filter(
                status="Rejected"
            ).count(),

            "today_leave": Leave.objects.filter(

                status="Approved",

                start_date__lte=today,

                end_date__gte=today

            ).count()

        }

    # ==========================================
    # MONTHLY SUMMARY
    # ==========================================

    @staticmethod
    def monthly_summary(month, year):

        queryset = Leave.objects.filter(

            created_at__month=month,

            created_at__year=year

        )

        return {

            "total": queryset.count(),

            "approved": queryset.filter(
                status="Approved"
            ).count(),

            "pending": queryset.filter(
                status="Pending"
            ).count(),

            "rejected": queryset.filter(
                status="Rejected"
            ).count()

        }

    # ==========================================
    # STATUS COUNTS
    # ==========================================

    @staticmethod
    def status_counts():

        return (

            Leave.objects

            .values("status")

            .annotate(

                total=Count("status")

            )

            .order_by("status")

        )

    # ==========================================
    # SEARCH
    # ==========================================

    @staticmethod
    def search(search="", status="", leave_type=""):

        queryset = Leave.objects.select_related(
            "employee"
        )

        if search:
            queryset = queryset.filter(

                Q(employee__employee_id__icontains=search) |

                Q(employee__first_name__icontains=search) |

                Q(employee__last_name__icontains=search)

            )

        if status:

            queryset = queryset.filter(
                status=status
            )

        if leave_type:

            queryset = queryset.filter(
                leave_type=leave_type
            )

        return queryset.order_by(
            "-created_at"
        )

    # ==========================================
    # DEPARTMENT SUMMARY
    # ==========================================

    @staticmethod
    def department_summary():

        return (

            Leave.objects

            .values(

                "employee__department__department_name"

            )

            .annotate(

                total=Count("id")

            )

            .order_by(

                "employee__department__department_name"

            )

        )

    # ==========================================
    # CALENDAR EVENTS
    # ==========================================

    @staticmethod
    def calendar_events():

        events = []

        for leave in Leave.objects.filter(
            status="Approved"
        ).select_related("employee"):

            events.append({

                "title": (
                    f"{leave.employee.employee_id}"
                ),

                "start": leave.start_date,

                "end": leave.end_date,

                "status": leave.status,

                "type": leave.leave_type

            })

        return events

    # ==========================================
    # DASHBOARD RECENT
    # ==========================================

    @staticmethod
    def recent(limit=5):

        return Leave.objects.select_related(

            "employee"

        ).order_by(

            "-created_at"

        )[:limit]