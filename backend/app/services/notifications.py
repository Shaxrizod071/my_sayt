from typing import Optional


def send_notification(student_id: int, message: str) -> bool:
    """Stub function to simulate sending a notification."""
    # In a real implementation, integrate with email/SMS/push service
    print(f"Sending to {student_id}: {message}")
    return True
