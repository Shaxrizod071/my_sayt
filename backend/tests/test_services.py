from app.services import gpa, grants, ratings


def test_calculate_gpa():
    assert gpa.calculate_gpa([4.0, 3.0, 3.5]) == (4.0 + 3.0 + 3.5) / 3
    assert gpa.calculate_gpa([]) == 0.0


def test_determine_grant_status():
    assert grants.determine_grant_status(3.5) == "grant"
    assert grants.determine_grant_status(2.9) == "contract"


def test_calculate_rankings():
    students = [{"id": 1, "gpa": 3.2}, {"id": 2, "gpa": 3.8}]
    ranked = ratings.calculate_rankings(students)
    assert ranked[0]["id"] == 2
    assert ranked[0]["rank"] == 1
    assert ranked[1]["rank"] == 2
