def determine_grant_status(gpa: float, threshold: float = 3.0) -> str:
    """Return 'grant' if gpa >= threshold else 'contract'"""
    return "grant" if gpa >= threshold else "contract"
