from django.db import models
from django.contrib.auth.models import User

class department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class employee(models.Model):

    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=15)

    gender = models.CharField(
        max_length=10,
        choices=GENDER
    )

    department = models.ForeignKey(
        department,
        on_delete=models.CASCADE
    )

    designation = models.CharField(max_length=100)

    joining_date = models.DateField()

    photo = models.ImageField(
        upload_to="employees/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    
    must_change_password = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.employee_id:

            last_employee = employee.objects.order_by("id").last()

            if last_employee:

                number = int(last_employee.employee_id[3:]) + 1

            else:

                number = 1

            self.employee_id = f"EMP{number:03d}"

        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.employee_id} - {self.first_name} {self.last_name}"