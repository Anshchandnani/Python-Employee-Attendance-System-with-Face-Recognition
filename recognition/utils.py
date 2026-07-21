import time
from collections import defaultdict

# =====================================================
# SETTINGS
# =====================================================

FRAME_THRESHOLD = 5
FACE_TIMEOUT = 5

# =====================================================
# GLOBAL VARIABLES
# =====================================================

frame_counter = defaultdict(int)

last_person = None
locked_person = None

last_seen = time.time()

# =====================================================
# HELPERS
# =====================================================

def reset_recognition():
    """
    Reset the recognition session.
    """

    global last_person
    global locked_person

    frame_counter.clear()

    last_person = None
    locked_person = None


def recognition_progress(employee_id):
    """
    Returns current progress.
    """

    return frame_counter.get(employee_id, 0)


def unlock_recognition():
    """
    Unlock after attendance completes.
    """

    global locked_person

    locked_person = None


def is_locked(employee_id):
    """
    Check whether employee is already processed.
    """

    return locked_person == employee_id


# =====================================================
# MAIN FUNCTION
# =====================================================

def confirm_recognition(employee_id):

    global last_person
    global locked_person
    global last_seen

    current_time = time.time()

    # ---------------------------------------
    # Unknown Face
    # ---------------------------------------

    if employee_id == "Unknown":

        if current_time - last_seen >= FACE_TIMEOUT:

            reset_recognition()

        return False

    last_seen = current_time

    # ---------------------------------------
    # Already Confirmed
    # ---------------------------------------

    if is_locked(employee_id):
        return False

    # ---------------------------------------
    # New Face
    # ---------------------------------------

    if employee_id != last_person:

        frame_counter.clear()

        last_person = employee_id

    frame_counter[employee_id] += 1

    # ---------------------------------------
    # Recognition Complete
    # ---------------------------------------

    if frame_counter[employee_id] >= FRAME_THRESHOLD:

        locked_person = employee_id

        return True

    return False