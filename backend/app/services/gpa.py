from typing import List


def calculate_gpa(scores: List[float]) -> float:
    """Simple GPA calculation: average of scores."""
    if not scores:
        return 0.0
    return sum(scores) / len(scores)
