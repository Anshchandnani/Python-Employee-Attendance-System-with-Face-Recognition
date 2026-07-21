from django import forms
from django.utils import timezone

from .models import Leave


class LeaveForm(forms.ModelForm):

    class Meta:

        model = Leave

        fields = [

            "leave_type",

            "start_date",

            "end_date",

            "reason"

        ]

        widgets = {

            "leave_type": forms.Select(

                attrs={

                    "class": "form-select"

                }

            ),

            "start_date": forms.DateInput(

                attrs={

                    "type": "date",

                    "class": "form-control"

                }

            ),

            "end_date": forms.DateInput(

                attrs={

                    "type": "date",

                    "class": "form-control"

                }

            ),

            "reason": forms.Textarea(

                attrs={

                    "class": "form-control",

                    "rows": 4,

                    "placeholder": "Enter the reason for leave..."

                }

            )

        }

    def __init__(self, *args, **kwargs):

        self.employee = kwargs.pop(
            "employee",
            None
        )

        super().__init__(*args, **kwargs)

        today = timezone.localdate().isoformat()

        self.fields["start_date"].widget.attrs["min"] = today
        self.fields["end_date"].widget.attrs["min"] = today

    def clean(self):

        cleaned_data = super().clean()

        start_date = cleaned_data.get(
            "start_date"
        )

        end_date = cleaned_data.get(
            "end_date"
        )

        # -----------------------------
        # Required
        # -----------------------------

        if not start_date or not end_date:

            return cleaned_data

        # -----------------------------
        # End Date Validation
        # -----------------------------

        if end_date < start_date:

            raise forms.ValidationError(

                "End Date cannot be before Start Date."

            )

        # -----------------------------
        # Past Date
        # -----------------------------

        if start_date < timezone.localdate():

            raise forms.ValidationError(

                "Past leave requests are not allowed."

            )

        # -----------------------------
        # Overlapping Leave
        # -----------------------------

        if self.employee:


            overlap = Leave.objects.filter(

                employee=self.employee,

                status__in=[

                    "Pending",

                    "Approved"

                ],

                start_date__lte=end_date,

                end_date__gte=start_date

            )

            if self.instance.pk:

                overlap = overlap.exclude(
                    pk=self.instance.pk
                )

            if overlap.exists():

                raise forms.ValidationError(

                    "A leave request already exists for the selected dates."

                )

        return cleaned_data