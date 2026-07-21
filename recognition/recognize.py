import json
import os
import time
from employees.models import employee
import cv2
from attendance.services import today_attendance
from django.utils import timezone
from attendance.services import (
    mark_attendance,
    get_employee,
    next_attendance_action,
)
from recognition.utils import confirm_recognition


# =====================================================
# PATHS
# =====================================================

MODEL_PATH = os.path.join(
    "recognition",
    "trainer",
    "trainer.yml"
)

LABELS_PATH = os.path.join(
    "recognition",
    "trainer",
    "labels.json"
)


# =====================================================
# CAMERA SETTINGS
# =====================================================

CAMERA_INDEX = 0

FRAME_WIDTH = 1000
FRAME_HEIGHT = 600

FACE_WIDTH = 200
FACE_HEIGHT = 200


# =====================================================
# RECOGNITION SETTINGS
# =====================================================

CONFIDENCE_THRESHOLD = 65

UNKNOWN_TIMEOUT = 10

AUTO_CLOSE_DELAY = 2


# =====================================================
# UI COLORS
# =====================================================

GREEN = (0, 255, 0)

RED = (0, 0, 255)

YELLOW = (0, 255, 255)

BLUE = (255, 0, 0)

WHITE = (255, 255, 255)

BLACK = (40, 40, 40)


# =====================================================
# GLOBALS
# =====================================================

attendance_marked = False

unknown_start = None


# =====================================================
# HELPERS
# =====================================================

def file_exists():

    if not os.path.exists(MODEL_PATH):
        return False, "Trainer model not found."

    if not os.path.exists(LABELS_PATH):
        return False, "Labels file not found."

    return True, ""


def load_model():

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    recognizer.read(MODEL_PATH)

    with open(LABELS_PATH, "r") as file:

        labels = json.load(file)

    detector = cv2.CascadeClassifier(

        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"

    )

    return recognizer, detector, labels


def open_camera():

    camera = cv2.VideoCapture(
        CAMERA_INDEX,
        cv2.CAP_DSHOW
    )

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        FRAME_WIDTH
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        FRAME_HEIGHT
    )

    return camera


def draw_message(frame, text, color=YELLOW):

    cv2.rectangle(
        frame,
        (10, 10),
        (500, 60),
        BLACK,
        -1
    )

    cv2.putText(
        frame,
        text,
        (20, 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        color,
        2
    )


def draw_footer(frame):

    current_time = time.strftime("%H:%M:%S")

    cv2.putText(
        frame,
        f"Time : {current_time}",
        (15, 520),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        WHITE,
        2
    )

    cv2.putText(
        frame,
        "ESC/Q : Exit",
        (600, 520),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        WHITE,
        2
    )


def draw_employee(frame, employee_name, confidence, x, y, w, h, color):

    cv2.rectangle(
        frame,
        (x, y),
        (x + w, y + h),
        color,
        2
    )

    cv2.putText(
        frame,
        employee_name,
        (x, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        color,
        2
    )

    cv2.putText(
        frame,
        f"Recognition : {100-confidence:.1f}%",
        (x, y + h + 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2
    )


# =====================================================
# MAIN
# =====================================================

def start_recognition(logged_in_employee):
    global attendance_marked
    global unknown_start

    attendance_marked = False

    unknown_start = None

    ok, message = file_exists()

    if not ok:
        return message

    recognizer, detector, labels = load_model()

    camera = open_camera()

    if not camera.isOpened():
        return "Camera not found."

    try:
        while True:

            ret, frame = camera.read()

            if not ret:
                draw_message(
                    frame,
                    "Unable to Read Camera",
                    RED
                )
                break

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            faces = detector.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(100, 100)
            )

            # -----------------------------------
            # Multiple Faces
            # -----------------------------------

            if len(faces) > 1:

                confirm_recognition("Unknown")

                draw_info_panel(
                    frame,
                    "",
                    "",
                    "MULTIPLE FACES",
                    "Only One Face Allowed"
                )
                cv2.waitKey(300)

                draw_footer(frame)

                cv2.imshow(
                    "Face Recognition",
                    frame
                )

                if cv2.waitKey(1) & 0xFF in [27, ord("q")]:
                    break

                continue

            # -----------------------------------
            # No Face
            # -----------------------------------

            if len(faces) == 0:

                confirm_recognition("Unknown")

                if unknown_start is None:
                    unknown_start = time.time()

                elif time.time() - unknown_start >= UNKNOWN_TIMEOUT:
                    break

                draw_info_panel(
                    frame,
                    "",
                    "",
                    "WAITING...",
                    "Show Your Face"
                )

                draw_footer(frame)

            else:

                unknown_start = None

            # -----------------------------------
            # Process Face
            # -----------------------------------

            for (x, y, w, h) in faces:

                face = gray[
                    y:y + h,
                    x:x + w
                ]

                face = cv2.resize(
                    face,
                    (
                        FACE_WIDTH,
                        FACE_HEIGHT
                    )
                )

                try:

                    label, confidence = recognizer.predict(
                        face
                    )

                except Exception:

                    continue

                recognized_employee = "Unknown"

                color = RED

                # -----------------------------
                # Unknown Face
                # -----------------------------

                if confidence > CONFIDENCE_THRESHOLD:
                    draw_info_panel(
                        frame,
                        "",
                        "",
                        "UNKNOWN",
                        "Face Not Registered"
                    )

                    continue

                recognized_employee = labels.get(
                    str(label),
                    "Unknown"
                )

                try:
                    emp = employee.objects.get(
                        employee_id=recognized_employee
                    )

                    employee_name = (
                        f"{emp.first_name} {emp.last_name}"
                    )

                except employee.DoesNotExist:

                    employee_name = ""

                # -----------------------------
                # Wrong Employee
                # -----------------------------

                if recognized_employee != logged_in_employee:
                    draw_employee(
                        frame,
                        recognized_employee,
                        confidence,
                        x,
                        y,
                        w,
                        h,
                        RED
                    )

                    draw_info_panel(
                        frame,
                        recognized_employee,
                        employee_name,
                        "ACCESS DENIED",
                        "Unauthorized Face"
                    )

                    continue

                color = GREEN

                draw_employee(
                    frame,
                    recognized_employee,
                    confidence,
                    x,
                    y,
                    w,
                    h,
                    color
                )

                emp = get_employee(recognized_employee)

                action = next_attendance_action(emp)

                progress = confirm_recognition(
                    recognized_employee
                )

                if not progress:
                    draw_info_panel(
                        frame,
                        emp.employee_id,
                        employee_name,
                        action,
                        "Look at Camera"
                    )

                    draw_footer(frame)

                    cv2.imshow(
                        "Face Recognition",
                        frame
                    )

                    continue

                if attendance_marked:
                    continue

                draw_info_panel(
                    frame,
                    emp.employee_id,
                    employee_name,
                    action,
                    "Processing..."
                )

                draw_footer(frame)

                cv2.imshow(
                    "Face Recognition",
                    frame
                )

                cv2.waitKey(100)

                attendance_status = mark_attendance(
                    recognized_employee
                )

                attendance_marked = True
                draw_info_panel(
                    frame,
                    emp.employee_id,
                    employee_name,
                    action,
                    attendance_status
                )

                draw_footer(frame)

                cv2.imshow(
                    "Face Recognition",
                    frame
                )

                while True:

                    key = cv2.waitKey(1) & 0xFF

                    if key == 27:
                        return

                    if key == ord("q"):
                        return

                    if cv2.getWindowProperty(
                            "Face Recognition",
                            cv2.WND_PROP_VISIBLE
                    ) < 1:
                        return

            draw_footer(frame)

            cv2.imshow(
                "Face Recognition",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == 27:
                break

            if key == ord("q"):
                break

            if cv2.getWindowProperty(
                    "Face Recognition",
                    cv2.WND_PROP_VISIBLE
            ) < 1:
                break
        pass

    finally:
        camera.release()
        cv2.destroyAllWindows()

def draw_info_panel(
        frame,
        employee_id="",
        employee_name="",
        action="Waiting...",
        result=""
):

    cv2.rectangle(
        frame,
        (0, 0),
        (1000, 110),
        (45, 45, 45),
        -1
    )

    cv2.putText(
        frame,
        "EMPLOYEE ATTENDANCE SYSTEM",
        (15, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        WHITE,
        2
    )

    cv2.putText(
        frame,
        f"Employee : {employee_id}",
        (15, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        YELLOW,
        2
    )

    cv2.putText(
        frame,
        f"Name : {employee_name}",
        (15, 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        WHITE,
        2
    )

    cv2.putText(
        frame,
        f"Action : {action}",
        (400, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        GREEN,
        2
    )

    cv2.putText(
        frame,
        f"Result : {result}",
        (400, 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        WHITE,
        2
    )