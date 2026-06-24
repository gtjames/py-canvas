import requests
import os

from datetime import datetime, timedelta


courseId = os.getenv("courseId")
byupw = os.getenv("byupw")
headers = { "Authorization": f"Bearer {byupw}" }

canvasURL = "https://byupw.instructure.com/api/v1"

# --------------------------------------------------
# Get all students in the course
# --------------------------------------------------

def getStudents():
    url = f"{canvasURL}/courses/{courseId}/users"

    params = { "enrollment_type[]": "student", "per_page": 100 }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()

# --------------------------------------------------
# Get all assignments
# --------------------------------------------------

def getAssignments():
    url = f"{canvasURL}/courses/{courseId}/assignments"

    params = { "per_page": 100 }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()

# --------------------------------------------------
# Get student submissions
# --------------------------------------------------

def getStudentSubmissions(studentId):
    url = f"{canvasURL}/courses/{courseId}/students/submissions"

    params = { "student_ids[]": studentId, "per_page": 100 }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()

# --------------------------------------------------
# Create assignment override for a student
# --------------------------------------------------

def extendAssignment(assignmentId, studentId, daysExtension=7):
    url = (
        f"{canvasURL}/courses/{courseId}"
        f"/assignments/{assignmentId}/overrides"
    )

    newDueDate = (
        datetime.utcnow() + timedelta(days=daysExtension)
    ).strftime("%Y-%m-%dT23:59:00Z")

    payload = {
        "assignment_override": {
            "student_ids": [studentId],
            "title": f"Extension for student {studentId}",
            "until_at": newDueDate
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        print(f"    Extended assignment {assignmentId} until {newDueDate}")
    else:
        print(f"    Failed to extend assignment {assignmentId}")
        print(response.text)

# --------------------------------------------------
# Main processing
# --------------------------------------------------

def main():
    students = getStudents()
    assignments = getAssignments()

    assignmentMap = {
        assignment["id"]: assignment #{"name": assignment["name"], "due_at": assignment["due_at"], "points_possible": assignment["points_possible"], "lock_at": assignment["lock_at"]}
        for assignment in assignments
    }

    submissions = {}
    for student in students:
        studentId = student["id"]
        studentName = student["name"]

        submissions[studentId] = getStudentSubmissions(studentId)

        missingAssignments = []
        submittedAssignments = []

        for submission in submissions[studentId]:
            if submission.get("missing"):
                assignmentId = submission["assignment_id"]
                assignment = assignmentMap.get(assignmentId)
                assignmentName = assignment["name"]
                missingAssignments.append((assignmentId, assignmentName))
            else:
                assignmentId = submission["assignment_id"]
                assignment = assignmentMap.get( assignmentId)
                submission["name"] = assignment["name"]
                submittedAssignments.append((assignmentId, submission))

        print("=" * 60)
        print(studentName)
        if not missingAssignments:
            print("  No missing assignments")
        else:
            print("  Missing Assignments:")

            for assignmentId, assignmentName in missingAssignments:
                print(f"    - {assignmentName}   {assignmentMap[assignmentId].get("due_at")} {assignmentMap[assignmentId].get("lock_at")} {assignmentMap[assignmentId].get("points_possible")}")

        print("  Submitted Assignments:")
        for assignmentId, submission in submittedAssignments:
            print(f"    - {submission.get("name")} {submission.get("score")}  {submission.get("due_at")}  {submission.get("lock_at")} {assignmentMap[assignmentId].get("points_possible")}")

            # --------------------------------------------------
            # OPTIONAL:
            # Automatically extend due dates
            # --------------------------------------------------

            # extendAssignment( assignmentId, studentId, daysExtension=7 )

main()