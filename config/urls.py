from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path("admin/", admin.site.urls),

    # Authentication (Login / Logout)
    path("", include("authentication.urls")),

    path("dashboard/", include("dashboard.urls")),

    path("employees/", include("employees.urls")),

    # Employee Management
    path("employees/", include("employees.urls")),

    # Attendance
    path("attendance/", include("attendance.urls")),

    # Face Recognition
    path("recognition/", include("recognition.urls")),

    # Leave Management
    path("leave/", include("leave.urls")),

]

from employees import error_views

handler404 = error_views.page_not_found
handler403 = error_views.permission_denied
handler500 = error_views.server_error

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )