from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from employees.models import employee


class Leave(models.Model):

    LEAVE_TYPES = (

        ("Casual", "Casual"),
        ("Sick", "Sick"),
        ("Paid", "Paid"),
        ("Emergency", "Emergency"),
        ("Work From Home", "Work From Home"),

    )

    STATUS = (

        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),

    )

    employee = models.ForeignKey(

        employee,

        on_delete=models.CASCADE,

        related_name="leave_requests"

    )

    leave_type = models.CharField(

        max_length=30,

        choices=LEAVE_TYPES

    )

    start_date = models.DateField()

    end_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(

        max_length=20,

        choices=STATUS,

        default="Pending"

    )

    admin_remarks = models.TextField(

        blank=True,

        default=""

    )

    approved_at = models.DateTimeField(

        null=True,

        blank=True

    )

    created_at = models.DateTimeField(

        auto_now_add=True

    )

    updated_at = models.DateTimeField(

        auto_now=True

    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [

            models.Index(fields=["status"]),

            models.Index(fields=["employee"]),

            models.Index(fields=["start_date"]),

            models.Index(fields=["end_date"]),

        ]

    def __str__(self):

        return (
            f"{self.employee.employee_id} - "
            f"{self.leave_type} ({self.status})"
        )

    # -----------------------------------
    # VALIDATION
    # -----------------------------------

    def clean(self):

        if self.start_date > self.end_date:

            raise ValidationError(
                "End date cannot be before start date."
            )

        if self.start_date < timezone.localdate():

            raise ValidationError(
                "Past leave requests are not allowed."
            )

    # -----------------------------------
    # PROPERTIES
    # -----------------------------------

    @property
    def total_days(self):

        return (
            self.end_date -
            self.start_date
        ).days + 1

    @property
    def is_pending(self):

        return self.status == "Pending"

    @property
    def is_approved(self):

        return self.status == "Approved"

    @property
    def is_rejected(self):

        return self.status == "Rejected"