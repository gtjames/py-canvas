import sys
import requests
import json
import calendar

from utilities import sendMessage, sortByAttr, getCanvasData
from datetime  import datetime, timezone, timedelta
from colors    import x, rowColor

school   = ""
courseId  = ""
canvasURL = ""      # attn: 
headers   = ""      # attn: 

_announcements = {}
_assignments   = {}
_categories    = {}
_enrollments   = {}         #   the whole works which we do not need
_groupMembers  = {}
_groups        = {}
_lastLogin     = {}
_missing       = {}
_studentList   = {}
_studentsById  = {}
_studentAssignments = {}
_studentAllAssignments = {}
_submissionsByStudent = {}
_allSubmission = {}
_unassigned    = {}

def clearCache():
    global _announcements
    global _assignments
    global _categories
    global _enrollments
    global _groupMembers
    global _groups
    global _lastLogin
    global _missing
    global _studentList
    global _studentsById
    global _studentAssignments
    global _studentAllAssignments
    global _allSubmission
    global _unassigned

    _announcements      = {}
    _assignments        = {}
    _categories         = {}
    _enrollments        = {}
    _groupMembers       = {}
    _groups             = {}
    _lastLogin          = {}
    _missing            = {}
    _studentList        = {}
    _studentsById       = {}
    _studentAssignments = {}
    _studentAllAssignments = {}
    _allSubmission = {}
    _unassigned         = {}

def listTeamMembersByGroup():

#  show members in all groups, groups of one or not affiliated with a group
    categories = getStudentGroups(courseId)
    grpType = input("(1) Solo, (0) All, (u) Unassigned: ")

    while len(grpType) > 0:
        cnt = 0

        for category in categories:
            if category["name"][0] == " ":
                continue
            print(f"{x.reset}{category["name"]}")
            # if we are only interestin "U"nassigned this is the route to take
            if grpType == "u":
                members = getUnassigned(category["id"])
                for member in members:
                    showStudent(member["id"], member["name"])
                print(f"{len(members)} - unassigned")
                if input("Email the Unassigned?: ") == "y":
                    studentIds = [student["id"] for student in members]
                    sendMessage(studentIds, "You have not yet found a team", "Please identify a team that works for your schedule and add your name to the group")
            else:
                # if we want the group membership this is the place
                groups = getGroups(category["id"])
                for group in groups:
                    if group["members_count"] == 0:
                        print(f"{group["name"]}")
                        continue

                    if (group["members_count"] == 1 and grpType == "1") or grpType == "0":
                        cnt = listMembers(group, grpType) + cnt
                print(f"Members: {cnt}")
        grpType = input("(1) Solo, (0) All, (u) Unassigned: ")

def studentSearch():
    studentList = getStudentList(courseId)

    notifyNoneParticipating = False
    if input("Email Non Participating?: ") == "y":
        notifyNoneParticipating = True

    group = ""
    sortBy = input("Sort By (first, last, group, score, login, tz, email, id, search): ")

    while len(sortBy) > 0:
        if sortBy == "search":
            name = input("Enter First or Last Name: ")
            students = [s for s in studentList if name in s["name"]]
        else:
            sortBy, students = sortByAttr(studentList, sortBy)
        print(f"# of Students: {len(students)}")

        size = 0
        for student in students:
            match sortBy:
                case    "search"    :
                    allAssignments = getAllSubmissions(courseId)[student["id"]];
                    missed         = [s for s in allAssignments["submissions"] if     s["missed"]]
                    submitted      = [s for s in allAssignments["submissions"] if not s["missed"]]

                    print(f"{student["first"]} {student["last"]}\nEmail:\t\t{student["email"]}\nGroup:\t\t{student["group"]}\nTime Zone:\t{student["tz"]}\nLast Login:\t{student["login"]}\nID:\t\t{student["id"]}\nScore:\t\t{student["score"]}\nGrade:\t\t{student["grade"]}\nTime Active:\t{student["activityTime"]}{x.reset}")
                    print("\n".join(f"{rowColor()}{x.fgBRed}Missed{rowColor(-1)}\t{a['title']}{x.reset}"                          
                        for a in missed)    if missed else f"{x.fgGreen}None Missing{x.reset}")
                    print("\n".join(f"{rowColor()}\t{a["title"]}\t{a["grade"]}/{a["possiblePts"]}\t{a["submittedAt"]}{x.reset}" 
                        for a in submitted) if submitted else "")
                case "group":                       #   sorting by group
                    if group != student["group"]:           #   did the group change?
                        if size > 0:                        #   if so, print the group size
                            print(f"Members in Group {size}")
                        print(f"\t\t{student["group"]}")    #   print the group name
                        group = student["group"]            #   save current group
                        size = 0                            #   reset the group size
                    size += 1                               #   increment the group size
                    print(f"{rowColor()}{student["first"]} {student["last"]} : {student["login"]} : {student["email"]} : {student["tz"]}{x.reset}")
                case "login" | "lastActivity" | "lastLogin":
                    print(f"{rowColor()}{student["first"]} {student["last"]} : {student["login"]} : {student["group"]} : {student["lastActivity"]}{x.reset}");
                    lastLogin = datetime.fromisoformat(student["lastLogin"])
                    aWeekAgo = datetime.now(lastLogin.tzinfo) - timedelta(days=7)
                    if lastLogin < aWeekAgo and notifyNoneParticipating:
                        sendMessage([student["id"]], "You have not participated in the class this week",
                            "Please let me know if you are having trouble with the class")
                case "id":
                    print(f"{rowColor()}{student["first"]} {student["last"]} : {student["email"]} : {student["id"]}{x.reset}");
                case "score" | "activityTime" | "grade":
                    print(f"{rowColor()}{student["first"]} {student["last"]} : {student["score"]} : {student["grade"]} : {student["activityTime"]}{x.reset}");
                case "first" | "tz":
                    size += 1
                    print(f"{rowColor()}{size:2d} {student["first"]} {student["last"]} : {student["group"]} : {student["email"]} : {student["tz"]}{x.reset}")
                case _:
                    print(f"{rowColor()}{student["first"]} {student["last"]} : {student["email"]} : {student["id"]}{x.reset}")
        sortBy = input(f"{x.reset}Sort By (first, last, group, score, login, tz, email, id, search): ")

def getAllStudentDetails(courseId):
    global _studentList
    global _studentsById

    if courseId not in _studentList:
        params = {
            "enrollment_type[]": "student",
            "per_page": 100,  # Maximum allowed per page
        }
        _studentList[courseId] = getCanvasData(f"/courses/{courseId}/users", params, "students")
        _studentsById = {}
        _studentsById[courseId] = {}

        scores = getCourseActivity(courseId)

        tmp = {
            student["id"]: {
        } for student in _studentList[courseId]}

        for student in _studentList[courseId]:
            profile   = getStudentProfile(student["id"])
            lastLogin = getLastLogin(student["id"])

            lastLogin = lastLogin if lastLogin else "2025-01-01T00:00:00-05:00"

            lastName, rest = student["sortable_name"].split(", ")
            firstName = rest.split(" ")[0].ljust(10)[:10]
            tm  = scores[student["id"]]["activityTime"]

            student["activityTime"] = f"{int(tm/60):4d}.{tm%60:02d}"
            student["email"]        = student["email"].ljust(36)
            student["first"]        = firstName.ljust(10)[:10]
            student["grade"]        = scores[student["id"]]["grade"]
            student["group"]        = "Team XX"
            student["last"]         = lastName.ljust(15)[:15]
            student["lastActivity"] = scores[student["id"]]["lastActivity"]
            student["lastLogin"]    = lastLogin
            student["login"]        = lastLogin.replace("T", " ")[5:16]
            student["name"]         = student["sortable_name"]
            student["score"]        = scores[student["id"]]["score"]
            student["tz"]           = profile["time_zone"].ljust(20)
            _studentsById[courseId][student.get("id")] = student

    return _studentsById[courseId]

def showAssignmentDates():
    assignments = getAssignments(courseId)
    print(f"{'Title':<55} {'Due Date':<10} {'Lock Date':<10} {'Points':>7} {'Has Submissions?':<15}")
    print("-" * 100)
    for assignment in assignments:
        print(f"{assignment['title']:<55} {assignment['dueAt']}     {assignment['lockAt']} {assignment['possiblePts']:>7}     {str(assignment['hasSubmissions']):<15}")

def listAssignments():
    row = 0
    submissionsByStudent = getAllSubmissions(courseId)

    notify = input("Notify?: ")
    msg = input("Message?: ")
    msg = msg if msg else "\tThe Following assignments have not been submitted.\n\tThese can all be submitted up to the end of Week 4."
    missing = input("(A)ll / (M)issing?: ")

    for studentId, unsub in submissionsByStudent.items():
        row += 1
        displayList = unsub["submissions"]
        _ ,displayList = sortByAttr(displayList, "title")
        if missing == "m":
            missingWork = [asgn for asgn in displayList if asgn.get("missed")]
            missingList = "\n".join(f"{rowColor()}\t{a["title"]}" for a in missingWork) if missingWork else "\tAll Assignments are Submitted"                                          
            print(f"{unsub["name"].ljust(50)[:50]}  `Missing:` {len(missingWork)}")
            print(missingList);
            if notify == "y" and len(missingWork) > 0:
                missed = "\n\t".join(map(str,submissionsByStudent[studentId]["unsubmitted"]))  # Convert each number to a string
                sendMessage([studentId], "Missing Assignments", f"{msg}\n\n\t{missed}")
        else:
            print(f"{unsub["name"].ljust(50)[:50]}")
            for assignment in displayList:
                if assignment["missed"]:
                    print(f"{rowColor()}{x.fgGreen} Missing       {assignment["title"]}{x.reset}")
                else:
                    print(f"{rowColor()} {assignment.get("score", 0)}/{assignment.get("possiblePts")}  {assignment.get("submittedAt")} \033[1;34m{assignment.get("title", "Untitled")}\033[0m")

# Get group categories
def getStudentGroups(courseId):
    global _categories

    studentsById = getAllStudentDetails(courseId)

    if courseId not in _categories:
        _categories[courseId] = getCanvasData(f"/courses/{courseId}/group_categories", {}, "categories")

        for category in _categories[courseId]:
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

    return _categories[courseId]

# Get members not in a group
def getUnassigned(groupId):
    global _unassigned

    if groupId not in _unassigned:
        _unassigned[groupId] = getCanvasData(f"/group_categories/{groupId}/users", {"unassigned": True, "per_page": 100}, "unassigned")
    return _unassigned[groupId]

def getAssignments(courseId):
    global _assignments
    
    if courseId not in _assignments:
        tmp = getCanvasData(f"/courses/{courseId}/assignments", {"per_page": 100}, "assignments")

        sub = [        {
            "id"             : a["id"],
            "dueAt"          : calendar.month_abbr[int(a["due_at"][5:7])]  + " " + a["due_at"][8:10],
            "dueDate"        : a["due_at"][5:7],
            "lockAt"         : calendar.month_abbr[int(a["lock_at"][5:7])] + " " + a["lock_at"][8:10],
            "possiblePts"    : f"{a["points_possible"]:2.0f}",
            "title"          : a["name"].ljust(55),
            "hasSubmissions" : a["has_submitted_submissions"]
        } for a in tmp]

        _, sub = sortByAttr(sub, "title")
        _assignments[courseId] = sub;

    return _assignments[courseId]

def getStudentList(courseId):
    global _studentList
    return _studentList[courseId]

def getStudentProfile(studentId):
    return getCanvasData(f"/users/{studentId}/profile", {}, "st-"+str(studentId))

def getStudent(courseId, studentId):
    global _studentsById

    return _studentsById.get(courseId, {}).get(studentId)

# Get details on a student
def showStudent(studentId, name):
        student = getStudent(courseId, studentId)
        if student is None:
            print(f"    - {name} has dropped the course")
            return
        print(f"{rowColor()}    - {student.get("first")} {student.get("last")} {student.get("email")} - {student.get("tz")}{x.reset}")

# Get Last Login
def getCourseActivity(courseId):
    global _enrollments

    if courseId not in _enrollments:
        _enrollments[courseId] = getCanvasData(f"/courses/{courseId}/enrollments", {"per_page": 100, "type[]": "StudentEnrollment"}, "activity") 
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
            for student in _enrollments[courseId]
        }
    _enrollments[courseId] = tmp
    return _enrollments[courseId]

# traverse from the categories in a course to the groups to the members
def listMembers(group, grpType):
    print(f"{group["name"]} # in Group: {group["members_count"]} ")
    members = getGroupMembers(group["id"])
    studentIds = [student["id"] for student in members]
    for member in members:
        showStudent(member["id"], member["name"])
        
    if len(members) == 1 and grpType == "1":
        if input("Email Lonely People?: ") == "y":
            sendMessage(studentIds, "You are currently the only member of the team", 
                                "Please identify a team that has others enrolled already that works for your schedule and add your name to the group")            
    if grpType == "0" and input("Email Class?: ") == "y":
        subject = input("Subject: ")
        body    = input("What do you want to say?: ")
        sendMessage(studentIds, subject, body)
        
    return len(members)

# Get all groups within the specified group category
def getGroups(catId):
    global _groups

    if catId not in _groups:
        _groups[catId] = getCanvasData(f"/group_categories/{catId}/groups", {"per_page": 100}, "grps-"+str(catId))

    return _groups[catId]

# Get members in each group
def getGroupMembers(groupId):
    global _groupMembers

    if groupId not in _groupMembers:
        _groupMembers[groupId] = getCanvasData(f"/groups/{groupId}/users", {"per_page": 100}, "grpMbrs"+str(groupId))
    return _groupMembers[groupId]

# Get Last Login
def getLastLogin(studentId):
    global _lastLogin

    if studentId not in _lastLogin:
        _lastLogin[studentId] = getCanvasData(f"/users/{studentId}", { "include[]": "last_login" }, "ll-"+str(studentId))

    return _lastLogin[studentId]["last_login"]

def getAllSubmissions(courseId):
    if courseId not in _submissionsByStudent:

        students    = getStudentList(courseId)
        assignments = getAssignments(courseId)

        allSubmissions = {}

        submissionsByStudent = {
            student["id"]: { "name": student["name"], "submissions": [] } for student in students
        }

        # today = datetime.now(timezone.utc)  # Make "today" timezone-aware
        # assignments = [a for a in assignments if datetime.fromisoformat(a["dueAt"]) < today]
        
        for assignment in assignments:
            # Fetch all submissions for the assignment
            allSubmissions[assignment["id"]] = getSubmissions(courseId, assignment)
            
            for submission in allSubmissions[assignment["id"]]:
                studentId = submission["userId"]
                if studentId in submissionsByStudent:
                    submissionsByStudent[studentId]["submissions"].append(submission)

        _submissionsByStudent[courseId] = submissionsByStudent;

    return _submissionsByStudent[courseId]

def getSubmissions(courseId, assignment):
    global _allSubmission

    if assignment["id"] not in _allSubmission:
        tmp = getCanvasData(f"/courses/{courseId}/assignments/{assignment["id"]}/submissions", {"per_page": 100}, "sub"+str(assignment["id"]))
        _allSubmission[assignment["id"]] = []
        for s in tmp:
            b = {}
            b["assignmentId"]  = s["assignment_id"]
            b["grade"]         =(s["grade"] or "").rjust(2)
            b["gradedAt"]      = s["graded_at"]
            b["id"]            = s["id"]
            b["late"]          = s["late"]
            b["missed"]        = s["missing"]
            b["missing"]       = s["missing"] if s["missing"] else "done   "
            b["score"]         = f"{(s.get('score') or 0.0):2.0f}"
            b["secondsLate"]   = s["seconds_late"]
            b["submittedAt"]   = s["submitted_at"].replace("T", " ")[5:11] if s["submitted_at"] else "      "
            b["userId"]        = s["user_id"]
            b["workflowState"] = s["workflow_state"]
            b["dueAt"]         = assignment["dueAt"]
            b["possiblePts"]   = assignment["possiblePts"]
            b["title"]         = assignment["title"]
            _allSubmission[assignment["id"]].append(b)

    return _allSubmission[assignment["id"]]

def sendStatusLetters():
    studentList     = getStudentList(courseId)
    pastAssignments = getAllSubmissions(courseId)

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

    go         = input("go/no go? ")    == "go"
    showMissed = input("Show Missed? ") == "y"

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

        sendMessage([f"{s["id"]}"],  f"{subject} {s["score"]}",
                     f"\n{s["first"]},\n{body}\nMissing Assignments(if any)\n\t{missed}\n\nBro. James")

def getAnnouncements(courseId):
    global _announcements

    if courseId not in _announcements:
        _announcements[courseId] = getCanvasData(f"/courses/{courseId}/discussion_topics?only_announcements=true", {"per_page": 100}, "announcements")
    return _announcements[courseId]

def listAnnouncements():
    announcements = getAnnouncements(courseId)
    for announcement in announcements:
        print(f"{announcement["id"]}  {announcement["title"]}")

def setParams():
    global school
    global courseId
    if (len(school) == 0 and len(sys.argv) > 1):
        courseId = sys.argv[1]
    else:
        school   = input("Enter School: ")
        courseId = input("Enter Course: ")
    school   = "byupw"  if school   == "" else school
    courseId = "13819"  if courseId == "" else courseId

    setSchool(school)
    return courseId

# Canvas API details
def setSchool(school):
    global canvasURL
    global headers

    canvasURL = f"https://{school}.instructure.com/api/v1"

    # Load the JSON key file
    with open("keys.json", "r") as file:
        data = json.load(file)

    headers = { "Authorization": f"Bearer {data[f"{school}"]}" }

def startUp():
    getAllStudentDetails (courseId)       #   _studentList
    getStudentGroups     (courseId)       #   _categories

def renameGroups():
    times = [
        "16:00 UTC --  10:00 Mtn",      #  good for western hemisphere PM and eastern hemisphere PM
        "18:00 UTC --  12:00 Mtn",  
        "20:00 UTC --  14:00 Mtn",
        "22:00 UTC --  16:00 Mtn",      #  good for eastern hemisphere AM and western hemisphere PM
        " 0:00 UTC --  18:00 Mtn",  
        " 2:00 UTC --  20:00 Mtn",
        " 8:00 UTC --   2:00 Mtn",      #  good for eastern hemisphere PM
        "12:00 UTC --   6:00 Mtn",
        "14:00 UTC --   8:00 Mtn",
    ]

    categories = getStudentGroups(courseId)

    for category in categories:
        print(f"{category.get('name')}")
        groups = getGroups(category['id'])
        if len(groups) == 1:
            continue

        grpNum  = 0
        teamNum = 0
        first=True

        for group in groups:
            print(f"{group['name']}")
            if first:
                teamName = "People Dropping the Class",
            else:
                teamName = f"Team {teamNum:02d} WDD330 {"Tuesday" if grpNum < 8 else "Wednesday"} {times[grpNum%8]} "
            
            print(teamName)

            data = { "name": teamName, "max_membership": 7 }
            requests.put(f"{canvasURL}/groups/{group["id"]}", headers=headers, data=data)

            if first:
                first = False
                continue
            grpNum=grpNum+1
            teamNum=teamNum+1
            if teamNum == 8:
                teamNum=teamNum+2
