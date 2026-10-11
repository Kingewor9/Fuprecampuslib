"""
Static taxonomy: Colleges -> Departments -> Programme length (years).

Slugs (short keys) are used in callback_data because Telegram limits
callback_data to 64 bytes and full names (with spaces) are unsafe there.

Levels are derived from a department's `years` value:
    4 years -> 100, 200, 300, 400
    5 years -> 100, 200, 300, 400, 500
"""

COLLEGES = {
    "COMP": {
        "name": "College of Computing",
        "departments": {
            "CSC": {"name": "Computer Science", "years": 4},
            "DTS": {"name": "Data Science", "years": 4},
            "INT": {"name": "Information Technology", "years": 4},
            "CYB": {"name": "Cyber Security", "years": 4},
            "SEN": {"name": "Software Engineering", "years": 4},
        },
    },
    "TECH": {
        "name": "College of Technology",
        "departments": {
            "MEE": {"name": "Mechanical Engineering", "years": 5},
            "EEE": {"name": "Electrical Engineering", "years": 5},
            "CVE": {"name": "Civil Engineering", "years": 5},
            "MAE": {"name": "Marine Engineering", "years": 5},
            "NGE": {"name": "Natural Gas Engineering", "years": 5},
            "PEE": {"name": "Petroleum Engineering", "years": 5},
            "CHE": {"name": "Chemical Engineering", "years": 5},
            "PCE": {"name": "Petrochemical Engineering", "years": 5},
            "CPE": {"name": "Computer Engineering", "years": 5},
            "EMA": {"name": "Engineering Mathematics", "years": 5},
        },
    },
    "SCI": {
        "name": "College of Science",
        "departments": {
            "GST": {"name": "General Studies", "years": 4},
            "MTH": {"name": "Mathematics", "years": 4},
            "STA": {"name": "Statistics", "years": 4},
            "SLT": {"name": "Science Laboratory Technology", "years": 5},
            "PHY": {"name": "Physics", "years": 4},
            "ESC": {"name": "Earth Science", "years": 4},
            "MAR": {"name": "Maritime Studies", "years": 5},
            "CHM": {"name": "Chemistry", "years": 4},
            "EMT": {"name": "Environmental Management Technology", "years": 5},
        },
    },
}

MATERIAL_TYPES = {
    "lecture_note": "\U0001F4D8 Lecture Notes",
    "past_question": "\U0001F4C4 Past Questions",
}


def get_college(college_slug: str) -> dict | None:
    return COLLEGES.get(college_slug)


def get_department(college_slug: str, dept_slug: str) -> dict | None:
    college = get_college(college_slug)
    if not college:
        return None
    return college["departments"].get(dept_slug)


def get_levels(college_slug: str, dept_slug: str) -> list[int]:
    dept = get_department(college_slug, dept_slug)
    if not dept:
        return []
    years = dept["years"]
    return [100 + (100 * i) for i in range(years)]


def department_name(college_slug: str, dept_slug: str) -> str:
    dept = get_department(college_slug, dept_slug)
    return dept["name"] if dept else dept_slug


def college_name(college_slug: str) -> str:
    college = get_college(college_slug)
    return college["name"] if college else college_slug
