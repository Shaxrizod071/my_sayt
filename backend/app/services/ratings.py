from typing import List, Dict


def calculate_rankings(students: List[Dict]) -> List[Dict]:
    """Given a list of dicts with 'id' and 'gpa',
    return list sorted by gpa descending with rank added."""
    sorted_students = sorted(students, key=lambda s: s.get("gpa", 0), reverse=True)
    for idx, stu in enumerate(sorted_students, start=1):
        stu["rank"] = idx
    return sorted_students
