import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()

from attendance.services import mark_attendance

print(mark_attendance("EMP001"))