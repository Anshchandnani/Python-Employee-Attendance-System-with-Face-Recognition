from django.urls import path

from . import views

urlpatterns = [

    path(
        "start/",
        views.recognize_face,
        name="start_recognition"
    ),

    path(
        "capture-face/<str:employee_id>/",
        views.capture_face,
        name="capture_face",
    ),

]