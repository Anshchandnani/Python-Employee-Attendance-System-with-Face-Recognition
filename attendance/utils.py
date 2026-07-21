from datetime import timedelta

from django.utils import timezone


def get_today():
    return timezone.localdate()


def get_now():
    return timezone.localtime()


def calculate_working_hours(check_in, check_out):

    if not check_out:
        return None

    start = timedelta(
        hours=check_in.hour,
        minutes=check_in.minute,
        seconds=check_in.second
    )

    end = timedelta(
        hours=check_out.hour,
        minutes=check_out.minute,
        seconds=check_out.second
    )

    total = end - start

    hours = total.seconds // 3600
    minutes = (total.seconds % 3600) // 60

    return f"{hours:02d}:{minutes:02d}"


def late_minutes(check_in):

    office_hour = 9
    office_minute = 0

    office = timedelta(
        hours=office_hour,
        minutes=office_minute
    )

    current = timedelta(
        hours=check_in.hour,
        minutes=check_in.minute
    )

    if current <= office:
        return 0

    late = current - office

    return late.seconds // 60


def overtime_minutes(check_in, check_out):

    office_hours = 8 * 60

    start = timedelta(
        hours=check_in.hour,
        minutes=check_in.minute
    )

    end = timedelta(
        hours=check_out.hour,
        minutes=check_out.minute
    )

    worked = (end - start).seconds // 60

    if worked <= office_hours:
        return 0

    return worked - office_hours