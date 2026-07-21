import requests
import calendar
import os
import shutil

from utilities import sendMessage, sortByAttr, getCanvasData, checkFolders, getPagedData
from datetime  import datetime, timezone, timedelta
from colors    import x

courseId  = ""
canvasURL = ""      # attn:
headers   = ""      # attn:
basePath = ""


_announcements = {}
_assignments   = {}
_assignmentsById = {}
_overrides     = {}
_allOverridesById = {}
_categories    = {}
_enrollments   = {}         #   the whole works which we do not need
_groupMembers  = {}
_groups        = {}
_missing       = {}
_studentList   = {}
_studentsById  = {}
_submissionsByStudent = {}
_submissionsByAssignment = {}
_submissionsLookup = {}
_unassigned    = {}

def clearCache():
    global _announcements
    global _assignments
    global _assignmentsById
    global _overrides
    global _allOverridesById
    global _categories
    global _enrollments
    global _groupMembers
    global _groups
    global _missing
    global _studentList
    global _studentsById
    global _submissionsByStudent
    global _submissionsByAssignment
    global _submissionsLookup
    global _unassigned

    _announcements      = {}
    _assignments        = {}
    _assignmentsById    = {}
    _overrides          = {}
    _allOverridesById   = {}
    _categories         = {}
    _enrollments        = {}
    _groupMembers       = {}
    _groups             = {}
    _missing            = {}
    _studentList        = {}
    _studentsById       = {}
    _submissionsByStudent    = {}
    _submissionsByAssignment = {}
    _submissionsLookup       = {}
    _unassigned         = {}

def listTeamMembersByGroup():

#  show members in all groups, groups of one or not affiliated with a group
    categories = getStudentGroups(courseId)
    grpType = input("(1) Solo, (A) All, (U) Unassigned: ")

    while len(grpType) > 0:
        grpType = grpType.upper()
        cnt = 0

        for category in categories:
            if category["name"][0] == " ":
                continue
            print(f"{category["name"]}")
            # if we are only interested in "U"nassigned this is the route to take
            if grpType == "U":
                members = getUnassigned(category["id"])
                for member in members:
                    showStudent(member["id"], member["name"])
                print(f"{len(members)} - unassigned")
                if input("Email the Unassigned?: ") == "y":
                    studentIds = [student["id"] for student in members]
                    sendMessage(courseId, studentIds, "You have not yet found a team", "Please identify a team that works for your schedule and add your name to the group")
            else:
                # if we want the group membership this is the place
                groups = getGroups(category["id"])
                for group in groups:
                    if group["members_count"] == 0:
                        # print(f"{group["name"]}")
                        continue

                    if (group["members_count"] == 1 and grpType == "1") or grpType == "A":
                        cnt = listMembers(group, grpType) + cnt
                print(f"Members: {cnt}")
        grpType = input("(1) Solo, (A) All, (U) Unassigned: ")

def getCourseId():
    return courseId

def studentSearch():
    studentList = getStudentList()

    notifyNonParticipating =  input("Email Non Participating?(y/n): ") == "y"

    emailTZ = 'n'
    group = ""
    sortBy = input("Sort By (first, last, group, score, login, tz, email, id): ")

    while len(sortBy) > 0:
        sortBy, students = sortByAttr(studentList, sortBy)
        print(f"# of Students: {len(students)}")

        size = 0
        match sortBy:
            case "group":                       #   sorting by group
                print(f"{"first":10} {"last":15} : {"login":11} : {"email":36} : {"tz"}")
            case "login" | "lastActivity" | "lastLogin":
                print(f"{"first":10} {"last":15} : {"login":11} : {"group":7} : {"lastActivity"}");
            case "id":
                print(f"{"first":10} {"last":15} : {"email":36} : {"login":11} : {"id"}");
            case "score" | "activityTime" | "grade":
                print(f"{"first":10} {"last":15} : {"Pts"} : {"grade":3} : {"activityTime"}");
            case "tz":
                print(f"{"first":10} {"last":15} : {"Pts"} : {"grade":3} : {"activityTime"}: {"tz"} ");
                emailTZ = input("Email Time Zone? (y/n): ")
            case "first":
                print(f"{"  "} {"first":10} {"last":15} : {"group":7} : {"email":36} : {"tz"}")
            case _:
                print(f"{"first":10} {"last":15} : {"email":36} : {"id"}")

        for student in students:
            match sortBy:
                case "group":                       #   sorting by group
                    if group != student["group"]:           #   did the group change?
                        if size > 0:                        #   if so, print the group size
                            print(f"Members in Group {size}")
                        print(f"\t\t{student["group"]}\t\t\t")    #   print the group name
                        group = student["group"]            #   save current group
                        size = 0                            #   reset the group size
                    size += 1                               #   increment the group size
                    print(f"{student["first"]} {student["last"]} : {student["login"]} : {student["email"]} : {student["tz"]}")

                case "login" | "lastActivity" | "lastLogin":
                    print(f"{student["first"]} {student["last"]} : {student["login"]} : {student["group"]} : {student["lastActivity"]}");

                    lastLogin = datetime.fromisoformat(student["lastLogin"])
                    aWeekAgo = datetime.now(lastLogin.tzinfo) - timedelta(days=7)
                    if lastLogin < aWeekAgo and notifyNonParticipating:
                        sendMessage(courseId, [student["id"]], "You have not participated in the class this week",
                            "Please let me know if you are having trouble with the class")

                case "id":
                    print(f"{student["first"]} {student["last"]} : {student["email"]} : {student["login"]} : {student["id"]}");

                case "score" | "activityTime" | "grade":
                    print(f"{student["first"]} {student["last"]} : {student["score"]} : {student["grade"]} : {student["activityTime"]}");

                case "tz":
                    print(f"{student["first"]} {student["last"]} : {student["score"]} : {student["grade"]} : {student["activityTime"]} : {student["tz"]}");
                    # if the first 6 characters of the time zone is "Etc/UTC" then email the student to set their time zone
                    if emailTZ == "y" and student["tz"].startswith("Etc/UTC"):  # if the student has no time zone set, send them a message
                        sendMessage(courseId, [student["id"]], "Time Zone Missing", f"Your time zone is {student["tz"]}. Please update your profile to reflect your current time zone.")

                case "first":
                    size += 1
                    print(f"{size:2d} {student["first"]} {student["last"]} : {student["group"]} : {student["email"]} : {student["tz"]}")

                case _:
                    print(f"{student["first"]} {student["last"]} : {student["email"]} : {student["id"]}")

        sortBy = input(f"Sort By (first, last, group, score, login, tz, email, id): ")

def searchStudentByName():
    studentList = getStudentList()

    name = input("Enter First or Last Name: ")
    students = [s for s in studentList if name.lower() in s["name"].lower()]

    for student in students:

        studentSubmissions = getSubmissions(courseId).get(student["id"], [])
        _, studentSubmissions = sortByAttr(studentSubmissions, "title")

        missed         = [s for s in studentSubmissions if     s["missed"] and datetime.fromisoformat(s["lock_at"]) < datetime.now(timezone.utc)]
        submitted      = [s for s in studentSubmissions if not s["missed"]]
        print(f"{student["first"]} {student["last"]}\nEmail:\t\t{student["email"]}\nGroup:\t\t{student["group"]}\n"
                f"Time Zone:\t{student["tz"]}\nLast Login:\t{student["login"]}\nID:\t\t{student["id"]}\n"
                f"Score:\t\t{student["score"]}\nGrade:\t\t{student["grade"]}\nTime Active:\t{student["activityTime"]}")
        for overrides in _overrides.values():          # list of overrides
            for ovr in overrides:                 # each override object
                if student["id"] in (ovr.get("studentIds") or []):
                    print(f"        {x.fgYellow}{_assignmentsById.get(ovr.get("assignmentId"), {}).get("title")}  {ovr["dueAt"]} {ovr["lockAt"]}{x.reset}")
        if( len(missed) > 0):
            # ask to advance due datetime
            newLockAt  = input("New Due Date (MM-DD) or Enter to skip: ")

            if len(newLockAt) != 0:
                # // for each missed assignment call extendDueDates
                for ovr in missed:
                    # // if assignment Due Date is passed and student is missing it, then extend the due date for that student
                    if datetime.fromisoformat(ovr["lock_at"]) < datetime.now(timezone.utc):
                        extendDueDates(student["id"], ovr["assignmentId"], _assignmentsById.get(ovr["assignmentId"]).get("dueDate"), newLockAt)
                for ovr in _overrides.values():          # list of overrides
                    if student["id"] in ovr.get("studentIds", []):
                        print(f"    {x.fgGreen}{ovr.get("title")}  {ovr["dueAt"]} {ovr["lockAt"]}{x.reset}")
        if not missed:
            print(f"None Missing")
        else:
            # // if there are missed assignments show the current due dates and ask if they want to extend them
            for ovr in missed:
                if (ovr.get("assignmentId") in _overrides.keys()):          # list of overrides
                    overs = _overrides.get(ovr.get("assignmentId"), [])                 # each override object
                    for ovr in overs:
                        if student["id"] in ovr.get("studentIds", []):
                            print(f"Ovr/Mis {x.fgBBlue}{ovr.get("title")}  {ovr["dueAt"]} {ovr["lockAt"]}{x.reset}")
                else:
                    print(f"Missed  {x.fgBGreen}{ovr.get("title")}  {_assignmentsById.get(ovr.get("assignmentId")).get("dueDate")}  {_assignmentsById.get(ovr.get("assignmentId")).get("lockDate")}{x.reset}")
        print("\n".join(f"        {a["title"]}\t{a["grade"]}/{a["points"]}\t{a["submittedAt"]}"
            for a in submitted) if submitted else "")

    return students

def getStudents(courseId):
    global _studentList
    global _studentsById

    if _studentsById:
        return _studentsById

    params = { "enrollment_type[]": "student", "per_page": 100 }
    _studentList = getCanvasData(f"/courses/{courseId}/users", params, "students", "students")
    _studentsById = {}

    scores = getCourseActivity(courseId)

    for student in _studentList:
        profile   = getStudentProfile(student["id"])
        lastLogin = getLastLogin(student["id"])

        lastName, rest = student["sortable_name"].split(", ", 1)
        firstName = rest.split(" ")[0].ljust(10)[:10]
        tm  = scores[student["id"]]["activityTime"] if student["id"] in scores else 0

        student["activityTime"] = f"{int(tm/60):4d}.{tm%60:02d}"
        student["email"]        = student["email"].ljust(36)
        student["first"]        = firstName.ljust(10)[:10]
        student["grade"]        = scores[student["id"]]["grade"] if student["id"] in scores else "--"
        student["group"]        = "Team XX"
        student["last"]         = lastName.ljust(15)[:15]
        student["lastActivity"] = scores[student["id"]]["lastActivity"] if student["id"] in scores else "No activity"
        student["lastLogin"]    = lastLogin
        student["login"]        = lastLogin.replace("T", " ")[5:16]
        student["name"]         = student["sortable_name"]
        student["score"]        = scores[student["id"]]["score"] if student["id"] in scores else "  0"
        student["tz"]           = profile["time_zone"].ljust(20)
        _studentsById[student.get("id")] = student

    return _studentsById

def showAssignmentDates():
    assignments = getAssignments(courseId)
    sortBy = input("Sort By (title, dueDate, lockDate, points): ")
    exten = input("With Extensions? (y/n): ")
    sortBy = sortBy if sortBy in ["title", "dueDate", "lockDate", "points"] else "title"
    while len(sortBy) > 0:
        _, assignments = sortByAttr(assignments, sortBy)

        print(f"{'Title':<55} {'Due Date':<10} {'Lock Date':<10} {'Points':>7} {'Has Submissions?':<15}")
        print("-" * 102)
        for assignment in assignments:
            print(f"{assignment['title']:<55} {assignment['dueAt']}     {assignment['lockAt']} {assignment['points']:>7}     {str(assignment['hasSubmissions']):<15}")
            if exten == "y" and assignment["hasOverrides"]:
                for overRide in _overrides.get(assignment["id"], []):
                    for student in overRide["studentIds"]:
                        print(f"{x.fgBBlue}    { _studentsById.get(student).get("name"):<51} {overRide['dueAt'] }     {overRide['lockAt']}  {overRide['id']}  {overRide['assignmentId']}{x.reset}")

        deleteId = input("Enter Override Id to delete: ")
        deleteId = int(deleteId) if deleteId.isdigit() else 0
        if deleteId > 0:
            # look for the assignment that has this override id
            if _allOverridesById[deleteId] is not None:
                assignmentId = _allOverridesById[deleteId].get("assignment_id")
                requests.delete(f"{canvasURL}/courses/{courseId}/assignments/{assignmentId}/overrides/{deleteId}", headers=headers)
                print(f"Deleting Override {deleteId} for Assignment {assignment['title']}")
                del _allOverridesById[deleteId]
                for ovr in _overrides.get(assignmentId, []):
                    if deleteId == ovr.get("id"):
                        _overrides[assignmentId].remove(ovr)
                        if _overrides.get(assignmentId) == []:
                            file = f"{basePath}/ovr/{assignmentId}.json"
                            os.remove(file)

        sortBy = input("Sort By (title, dueDate, lockDate, points): ")

def listAssignments():
    submissionsByStudent = getSubmissions(courseId)

    notify = input("Notify?: ")
    msg = input("Message?: ")
    msg = msg if msg else "\tThe Following assignments have not been submitted.\n\tThese can all be submitted up the UNTIL date. 7 days after the due date."
    missing = input("(A)ll / (M)issing?: ")
    missing = missing.lower() if missing else "m"
    for studentId, studentSubmissions in submissionsByStudent.items():
        unsubmitted = [s for s in studentSubmissions if s["missed"]]
        submitted   = [s for s in studentSubmissions if not s["missed"]]
        _ ,submitted = sortByAttr(submitted, "title")
        if missing == "m":
            if notify == "y" and len(unsubmitted) > 0:
                print(f"{_studentsById[studentId]["name"].ljust(50)[:50]}  Missing: {len(unsubmitted)}")
                missingList = "\n".join(f"\t{a["title"]}" for a in unsubmitted) if unsubmitted else f"\tAll Assignments are Submitted"
                # sendMessage(courseId, [studentId], "Missing Assignments", f"{msg}\n\n\t{missingList}")
                print(missingList);
        else:           # this would be ALL
            print(f"{_studentsById[studentId]["name"].ljust(50)[:50]}")
            print(" Points  Submitted At           Title")
            for assignment in submitted:
                if assignment["missed"]:
                    print(f"    {assignment.get("points")}  {x.fgBYellow}Missed{x.reset} {assignment["title"]}")
                else:
                    print(f" {assignment.get("score", 0)}/{assignment.get("points")}  {x.fgBBlue}{assignment.get("submittedAt")}{x.reset} {assignment.get("title", "Untitled")}")

# Get group categories
def getStudentGroups(courseId):
    global _categories

    studentsById = getStudents(courseId)

    if courseId not in _categories:
        _categories = getCanvasData(f"/courses/{courseId}/group_categories", {}, "categories", "groups")

        for category in _categories:
            if category["name"] == "Who is Here":
                continue

            groups = getGroups(category["id"])
            for group in groups:
                if group["members_count"] == 0:
                    continue

                members = getGroupMembers(group["id"])
                for member in members:
                    if member["id"] in studentsById:
                        studentsById[member["id"]]["group"]     = group["name"][:7]

    return _categories

# Get members not in a group
def getUnassigned(groupId):
    global _unassigned

    if groupId not in _unassigned:
        _unassigned[groupId] = getCanvasData(f"/group_categories/{groupId}/users", {"unassigned": True, "per_page": 100}, "unassigned", "groups")
    return _unassigned[groupId]

def cleanupAssignmentData(assignments):
    for a in assignments:
        a["due_at"]  = '2026-01-01T00:00:00-05:00' if a["due_at"]  is None else a["due_at"]
        a["lock_at"] = '2026-01-01T00:00:00-05:00' if a["lock_at"] is None else a["lock_at"]

    sub = [ {
            "id"             : a["id"],
            "dueDate"        : a["due_at"][5:10],
            "lockDate"       : a["lock_at"][5:10],
            "due_at"         : a["due_at"],
            "lock_at"        : a["lock_at"],
            "dueAt"          : calendar.month_abbr[int(a["due_at"][5:7])]  + " " + a["due_at"][8:10],
            "lockAt"         : calendar.month_abbr[int(a["lock_at"][5:7])] + " " + a["lock_at"][8:10],
            "points"         : f"{a["points_possible"]:2.0f}",
            "title"          : a["name"].ljust(55),
            "hasOverrides"   : a["has_overrides"],
            "hasSubmissions" : a["has_submitted_submissions"]
        } for a in assignments]
    return sub

def getAssignments(courseId):
    global _assignments
    global _overrides
    global _assignmentsById
    global _allOverridesById

    if not _assignments:
        _assignmentsById = {}

        tmp1  = getCanvasData(f"/courses/{courseId}/assignments", {"per_page": 100}, "assignments", "course")

        assignments = cleanupAssignmentData(tmp1)
        _, _assignments = sortByAttr(assignments, "title")

        for assignment in assignments:
            _assignmentsById[assignment.get("id")] = assignment

            if assignment["hasOverrides"] and assignment["id"] not in _overrides:
                overrides = getCanvasData(f"/courses/{courseId}/assignments/{assignment["id"]}/overrides", {"per_page": 100}, f"{assignment["id"]}", "ovr")
                # create a list of overrides by override id for easy lookup
                for ovr in overrides:
                    _allOverridesById[ovr["id"]] = ovr

                for a in overrides:
                    a["due_at"]  = a.get("due_at")  or "2026-12-31"
                    a["lock_at"] = a.get("lock_at") or "2026-12-31"

                overridesForAssignment = [ {
                        "id"             : ovr["id"],
                        "assignmentId"   : ovr["assignment_id"],
                        "dueAt"          : calendar.month_abbr[int(ovr["due_at"][5:7])]  + " " + ovr["due_at"][8:10],
                        "lockAt"         : calendar.month_abbr[int(ovr["lock_at"][5:7])] + " " + ovr["lock_at"][8:10],
                        "studentIds"     : ovr["student_ids"],
                    } for ovr in overrides]
                _overrides[assignment["id"]] = overridesForAssignment
                assignment["overrides"] = overridesForAssignment if overridesForAssignment else []

    return _assignments

def getStudentList():
    global _studentList
    return _studentList

def getStudentProfile(studentId):
    return getCanvasData(f"/users/{studentId}/profile", {}, str(studentId), "students")

def getStudent(studentId):
    global _studentsById

    return _studentsById.get(studentId)

# Get details on a student
def showStudent(studentId, name):
        student = getStudent(studentId)
        if student is None:
            print(f"    - {name} has dropped the course")
            return
        print(f"    - {student.get("first")} {student.get("last")} {student.get("email")} - {student.get("tz")}")

# Get Last Login
def getCourseActivity(courseId):
    global _enrollments

    if not _enrollments:
        _enrollments = getCanvasData(f"/courses/{courseId}/enrollments", {"per_page": 100, "type[]": "StudentEnrollment"}, "activity", "course")
        tmp = {
            student["user_id"]: {
                "lastActivity": (
                    student["last_activity_at"].replace("T", " ")[5:16]
                    if student.get("last_activity_at") else "No activity"
                ),
                "activityTime": student.get("total_activity_time", 0),
                "grade": (
                    student.get("grades", {}).get("current_grade", "").ljust(2)
                    if student.get("grades") and student["grades"].get("current_grade") else "--"
                ),
                "score": (
                    f'{student.get("grades", {}).get("current_score", 0):3.0f}'
                    if student.get("grades") and student["grades"].get("current_score") is not None else "  0"
                ),
            }
            for student in _enrollments
        }
        _enrollments = tmp
    return _enrollments

# traverse from the categories in a course to the groups to the members
def listMembers(group, grpType):
    print(f"{group["name"]} # in Group: {group["members_count"]} ")
    members = getGroupMembers(group["id"])
    studentIds = [student["id"] for student in members]
    for member in members:
        showStudent(member["id"], member["name"])

    if len(members) == 1 and grpType == "1":
        if input("Email single person teams (y/n)?: ") == "y":
            sendMessage(courseId, studentIds, "You are currently the only member of the team",
                                "Please identify a team that has others enrolled already that works for your schedule and add your name to the group")
    elif grpType == "a" and input("Email Team?: ") == "y":
        subject = input("Subject: ")
        body    = input("What do you want to say?: ")
        sendMessage(courseId, studentIds, subject, body)

    return len(members)

# Get all groups within the specified group category
def getGroups(catId):
    global _groups

    if catId not in _groups:
        _groups[catId] = getCanvasData(f"/group_categories/{catId}/groups", {"per_page": 100}, str(catId), "groups")

    return _groups[catId]

def extendDueDates(studentId="", assignmentId="", dueAt="", newLockAt=""):
    data = {
        "assignment_override[student_ids][]": studentId,
        "assignment_override[due_at]"   : f"2026-{dueAt}T23:59:00Z",
        "assignment_override[lock_at]"  : f"2026-{newLockAt}T23:59:00Z",
        "assignment_override[title]"    : f"Extension for student {studentId}",
        "assignment_override[until_at]" : f"2026-{newLockAt}T23:59:00Z"
    }
    response = requests.post(f"{canvasURL}/courses/{courseId}/assignments/{assignmentId}/overrides", headers=headers, data=data)
    print(response.status_code)
    if ((response.status_code >= 400) and (response.status_code < 500)):
        print(f"Error: {response.status_code} - {response.text}")
        response = requests.delete(f"{canvasURL}/courses/{courseId}/assignments/{assignmentId}/overrides/51533", headers=headers, data=data)
        print(f"Response: {response.status_code} - {response.text}")

# Get members in each group
def getGroupMembers(groupId):
    global _groupMembers

    if groupId not in _groupMembers:
        _groupMembers[groupId] = getCanvasData(f"/groups/{groupId}/users", {"per_page": 100}, str(groupId), "groups")
    return _groupMembers[groupId]

# Get Last Login
def getLastLogin(studentId):

    userData = getCanvasData(f"/users/{studentId}", { "include[]": "last_login" }, str(studentId), "lastLogin")
    lastLogin = userData.get("last_login") or "2025-01-01T00:00:00-05:00"

    return lastLogin

def getSubmissions(courseId):
    #  Get all submissions for all students in the course
    global _submissionsByStudent
    global _submissionsByAssignment
    global _submissionsLookup

    getAssignments(courseId)        #  this will populate the _assignmentsById dictionary which we need to get the due dates and points for each submission
    if not _submissionsByStudent:
        url = f"/courses/{courseId}/students/submissions"
        allSubs = getPagedData(url, {"per_page": 100, "student_ids[]": ["all"]}, "submissions", "course")

        allSubmissions = []
        for s in allSubs:
            # skip inactive students
            if s["user_id"] not in _studentsById:
                continue
            assignment = _assignmentsById.get(s["assignment_id"], {})
            b = {}
            b["assignmentId"]  = s["assignment_id"]
            b["grade"]         =(s["grade"] or "").rjust(2)
            b["gradedAt"]      = s["graded_at"]
            b["id"]            = s["id"]
            b["late"]          = s["late"]
            b["missed"]        = s["missing"]
            b["missing"]       = s["missing"] if s["missing"] else "done   "
            b["score"]         = f"{(s.get('score') or 0.0):3.0f}"
            b["submittedAt"]   = s["submitted_at"].replace("T", " ")[5:11] if s["submitted_at"] else "      "
            b["userId"]        = s["user_id"]
            b["workflowState"] = s["workflow_state"]
            b["due_at"]        =    assignment["due_at"]
            b["lock_at"]       =    assignment["lock_at"]
            b["dueAt"]         =    assignment["dueAt"]
            b["lockAt"]        =    assignment["lockAt"]
            b["points"]        = f"{assignment["points"]:>3}"
            b["title"]         =    assignment["title"]
            allSubmissions.append(b)

        #   create a dictionary of students with their submissions
        submissionsByStudent = {}
        submissionsByAssignment = {}

        for submission in allSubmissions:
            studentId = submission["userId"]
            assignmentId = submission["assignmentId"]

            submissionsByStudent.setdefault(studentId, []).append(submission)
            submissionsByAssignment.setdefault(assignmentId, []).append(submission)
        submissionLookup = { (s["userId"], s["assignmentId"]): s for s in allSubmissions }

        # today = datetime.now(timezone.utc)  # Make "today" timezone-aware
        # assignments = [a for a in assignments if datetime.fromisoformat(a["dueAt"]) < today]
        _submissionsByStudent    = submissionsByStudent;
        _submissionsByAssignment = submissionsByAssignment;
        _submissionsLookup       = submissionLookup;

    return _submissionsByStudent

def sendStatusLetters():
    studentList     = getStudentList()
    pastAssignments = getSubmissions(courseId)

    _, studentList = sortByAttr(studentList, "score")

    statusLetter(studentList, 90, 101, pastAssignments,
                 "Keep up the good work!: Current Score: ",
                "\nYou are doing very well in the class keep up the good work")
    statusLetter(studentList, 70, 90, pastAssignments,
                "You are doing well but might be missing a few assignments: Current Score: ",
                "\nYou can still turn these in until the end of week four")
    statusLetter(studentList, 0, 70, pastAssignments,
                 "How are you doing in the class? It looks like you are struggling: Current Score: ",
                "\nHere is a list of your missing assignments. You can still turn these in until the end of week four\nDon't forget there is tutoring available for the class.")

def statusLetter(studentScores, lo, hi, unfinishedAssignments, subject, body):
    mailList = [ student for student in studentScores   if lo <= float(student['score']) < hi ]

    go         = input("(e)mail/not? ")   == "e"
    showMissed = input("Show Missed(y/n)? ") == "y"

    # today = datetime.now(timezone.utc)  # Make "today" timezone-aware
    for s in mailList:
        missed = "\n".join(f"\t{a['title']}" for a in unfinishedAssignments[s["id"]]["submissions"] if a.get("missed")) or ""

        # pastAssignments = [a for a in unfinishedAssignments[s["id"]]["submissions"]
        #                    if datetime.fromisoformat(a["dueAt"]) < today and a.get("missed")]

        print(f"{float(s['score']):4.0f} - {s["first"]} {s["last"]} {" dropped" if s["id"] not in unfinishedAssignments else ""}")

        if len(missed) == 0:
            continue
        if showMissed:
            print(missed)
        # Check if the student ID is in the unfinishedAssignments dictionary
        if s["id"] not in unfinishedAssignments or not go:
            continue

        sendMessage(courseId, [f"{s["id"]}"],  f"{subject} {s["score"]}",
                     f"\n{s["first"]},\n{body}\nMissing Assignments(if any)\n\t{missed}\n\nBro. James")

def getAnnouncements(courseId):
    global _announcements

    if not _announcements:
        _announcements = getCanvasData(f"/courses/{courseId}/discussion_topics?only_announcements=true", {"per_page": 100}, "announcements", "course" )
    return _announcements

def listAnnouncements():
    announcements = getAnnouncements(courseId)
    for announcement in announcements:
        print(f"{announcement["id"]:>8}  {announcement["title"]}")
        print(f"{x.fgBBlue}    {" ":>8}  {announcement["url"]}{x.reset}")

def setParams():
    global courseId
    global canvasURL
    global headers
    global basePath

    canvasURL = "https://byupw.instructure.com/api/v1"
    courseId = os.getenv("courseId")
    byupw = os.getenv("byupw")
    headers = { "Authorization": f"Bearer {byupw}" }
    basePath = f"./cache/{courseId}"

def setCourseId():
    global courseId
    global basePath

    courseId = input("Enter Course Id: ")
    basePath = f"./cache/{courseId}"

def startUp():
    checkFolders      (courseId)
    getStudents       (courseId)       #   _studentList
    getStudentGroups  (courseId)       #   _categories

def renameGroups():
    if input("This will reset all the data in the cache. Are you sure? (y/n): ") != "y":
        return

    times = [
        "Team 00 Tues 11:00 UTC --  Tues 05:00 Mtn",
        "Team 01 Tues 18:00 UTC --  Tues 12:00 Mtn",
        "Team 02 Tues 19:00 UTC --  Tues 13:00 Mtn",
        "Team 03 Tues 20:00 UTC --  Tues 14:00 Mtn",
        "Team 04 Tues 23:00 UTC --  Tues 17:00 Mtn",  # popular time in the US
        "Team 05 Wed  01:00 UTC --  Tues 19:00 Mtn",
        "Team 06 Wed  02:00 UTC --  Tues 20:00 Mtn",
        "Team 07 Wed  03:00 UTC --  Tues 21:00 Mtn",

        "Team 10 Wed  11:00 UTC --  Wed  05:00 Mtn",
        "Team 11 Wed  18:00 UTC --  Wed  12:00 Mtn",
        "Team 12 Wed  19:00 UTC --  Wed  13:00 Mtn",
        "Team 13 Wed  20:00 UTC --  Wed  14:00 Mtn",
        "Team 14 Wed  23:00 UTC --  Wed  17:00 Mtn",
        "Team 15 Thu  01:00 UTC --  Wed  19:00 Mtn",
        "Team 16 Thu  02:00 UTC --  Wed  20:00 Mtn",
        "Team 17 Thu  03:00 UTC --  Wed  21:00 Mtn",
    ]

    categories = getStudentGroups(courseId)

    for category in categories:
        print(f"{category.get('name')}")
        groups = getGroups(category['id'])
        if len(groups) == 1:
            continue

        grpNum  = 0
        first   = True

        for group in groups:
            print(f"{group['name']}")
            if first:
                teamName = "People Dropping the Class",
            else:
                teamName = times[grpNum]
            print(teamName)

            data = { "name": teamName, "max_membership": 7 }
            requests.put(f"{canvasURL}/groups/{group["id"]}", headers=headers, data=data)

            if first:
                first = False
                continue
            grpNum=grpNum+1

def reset():
    if input("This will reset all the data in the cache. Are you sure? (y/n): ") == "y":
        clearCache()
    resetFiles()

def resetFiles():
    for subFolder in os.listdir(f"{basePath}"):
        if input(f"Remove {subFolder}. Are you sure? (y/n): ") == "y":
            subFolder = f"{basePath}/{subFolder}"
            os.remove(subFolder) if os.path.isfile(subFolder) else shutil.rmtree(subFolder)
            print(f"Deleted: {subFolder}")
        else:
            print(f"Skipped: {subFolder}")

def ask(prompt):
    response = input(f"{prompt} (y/n): ").strip().lower()
    return response in ["y", "yes"]

def test():
    # find students that have missed assignments by assignment
    getSubmissions(courseId)

    notify = input("Email Missing? (y/n): ").strip().lower() == "y"

    for assignmentId, assignmentSubmissions in sorted(
        _submissionsByAssignment.items(),
        key=lambda item: _assignmentsById.get(item[0], {}).get("title", ""),
    ):
        missed = [submission for submission in assignmentSubmissions if submission["missed"]]
        if not missed:
            continue

        assignment = _assignmentsById.get(assignmentId, {})
        title = assignment.get("title", f"Assignment {assignmentId}").strip()
        print(f"{title}")
        print(f"  Due: {assignment.get('dueAt', 'Unknown')}  Lock: {assignment.get('lockAt', 'Unknown')}  Missed: {len(missed)}")

        studentIds = []
        for submission in missed:
            student = _studentsById.get(submission["userId"])
            if student is None:
                continue

            studentIds.append(submission["userId"])
            print(f"    - {student.get('first')} {student.get('last')} {student.get('email')}")

        data = {
            "assignment_override[student_ids][]": studentIds,
            "assignment_override[due_at]"   : f"2026-{assignment.get('dueDate')}T23:59:00Z",
            "assignment_override[lock_at]"  : f"2026-{assignment.get('lockDate')}T23:59:00Z",
            "assignment_override[title]"    : f"Extension for student {studentIds}",
            "assignment_override[until_at]" : f"2026-{assignment.get('lockDate')}T23:59:00Z"
        }
        print(f"{data['assignment_override[due_at]']}\n  {data['assignment_override[lock_at]']}\n  {data['assignment_override[title]']}\n {data['assignment_override[until_at]']}")

        # if notify and studentIds:
        #     sendMessage(courseId, studentIds, f"Missing {title}", f"You have not yet submitted: {title}")
