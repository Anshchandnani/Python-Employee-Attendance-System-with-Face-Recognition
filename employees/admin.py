from django.contrib import admin
from .models import employee, department


@admin.register(department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "employee_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "department",
        "designation",
        "joining_date",
        "is_active",
    )

    list_filter = (
        "department",
        "designation",
        "is_active",
    )

    search_fields = (
        "employee_id",
        "first_name",
        "last_name",
        "email",
        "phone",
    )

    ordering = (
        "employee_id",
    )

    readonly_fields = (
        "employee_id",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Employee Information", {
            "fields": (
                "employee_id",
                "first_name",
                "last_name",
                "photo",
            )
        }),

        ("Contact Information", {
            "fields": (
                "email",
                "phone",
                "gender",
            )
        }),

        ("Work Information", {
            "fields": (
                "department",
                "designation",
                "joining_date",
                "is_active",
            )
        }),

        ("System Information", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )