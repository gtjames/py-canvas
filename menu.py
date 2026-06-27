# from  nameGroups import renameGroups
from  canvas import setCourseId, startUp, getCourseId, setParams, getStudentList, listAssignments, sendStatusLetters, sendMessage, listTeamMembersByGroup, studentSearch, renameGroups, showAssignmentDates, reset, listAnnouncements

def main():

# Print all command-line arguments
    setParams()
    startUp()

    while True:
        print("\nMain Menu")
        print("1.  Team Members       2. Student Details")
        print("3.  List Unsubmitted   4. Missing Assignment Letters")
        print("5.  Message 1 student  6. Message Class")
        print("7.  Assignment Dates   8. List Announcements")
        print("E(x)it")

        # print("5. Rename Groups")

        choice = input("Enter your choice: ")

        match choice:
            case '1':
                listTeamMembersByGroup()

            case '2':
                studentSearch()

            case '3':
                listAssignments()

            case '4':
                sendStatusLetters()

            case '5':
                studentId = input("Student Id: ")
                subject   = input("Subject: ")
                body      = input("Body: ")
                sendMessage(getCourseId(), [studentId], subject, body)

            case '6':
                studentList = getStudentList()
                studentIds = [student['id'] for student in studentList]
                subject   = input("Subject: ")
                body      = input("Body: ")
                sendMessage(getCourseId(), studentIds, subject, body)

            case '7':
                showAssignmentDates()

            case '8':
                listAnnouncements()

            case 'change':
                setCourseId()
                startUp()

            case 'groups':
                renameGroups()

            case 'reset':
                reset()

            case 'x':
                exit()
                
            case _:
                print("Invalid choice, please try again.")

main()
