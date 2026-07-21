from django.urls import path
from . import views
from . import exports

urlpatterns = [
    path(
        "",
        views.attendance_list,
        name="attendance_list",
    ),

    path(
        "history/",
        views.attendance_history,
        name="attendance_history",
    ),

    path(
        "excel/",
        exports.export_excel,
        name="attendance_excel"
    ),

    path(
        "pdf/",
        exports.export_pdf,
        name="attendance_pdf"
    ),
]