from django import forms
from .models import employee


class EmployeeForm(forms.ModelForm):

    class Meta:
        model = employee

        exclude = (
            "employee_id",
            "created_at",
            "updated_at",
        )

        widgets = {
            "joining_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),

            "phone": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "designation": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "department": forms.Select(
                attrs={"class": "form-select"}
            ),

            "gender": forms.Select(
                attrs={"class": "form-select"}
            ),

            "photo": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),

            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }