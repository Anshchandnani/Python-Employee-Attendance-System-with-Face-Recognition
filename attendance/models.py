from django.db import models
from employees.models import employee


class Attendance(models.Model):

    STATUS = (
        ("Present", "Present"),
        ("Late", "Late"),
        ("Half Day", "Half Day"),
        ("Leave", "Leave"),
        ("Absent", "Absent"),
    )

    employee = models.ForeignKey(
        employee,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    date = models.DateField()

    check_in = models.TimeField(
        null=True,
        blank=True
    )

    check_out = models.TimeField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Present"
    )

    working_hours = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    remarks = models.CharField(
        max_length=200,
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-date", "employee"]

        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date"],
                name="unique_daily_attendance"
            )
        ]

    def __str__(self):
        return (
            f"{self.employee.employee_id} | "
            f"{self.date} | "
            f"{self.status}"
        )