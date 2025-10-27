from datetime import datetime
import pytz


def budget_calculation() -> str:
    """
    Returns the current local time in Singapore as a formatted string.
    """
    # TODO: Get singapore_time
    singapore_tz = pytz.timezone("Asia/Singapore")
    sg_time = datetime.now(singapore_tz)
    return f"Time in Singapore now: {sg_time.strftime('%Y-%m-%d %H:%M:%S')}"
