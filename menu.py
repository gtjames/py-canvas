# from  nameGroups import renameGroups
from  canvas import startUp, courseId, setParams, getStudentList, listAssignments, sendStatusLetters, sendMessage, listTeamMembersByGroup, studentSearch, renameGroups, showAssignmentDates

def main():

# Print all command-line arguments
    setParams()
    startUp();
    
    while True:
        print("\nMain Menu")
        print("1.  Team Members       2. Students in Team")
        print("3.  List Unsubmitted   4. Missing Assignment Letters")
        print("5.  Message 1 student  6. Message Class")
        print("7.  Assignment Dates  10. Set School and Class")
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
                sendStatusLetters();
            case '5':
                studentId = input("Student Id: ")
                subject   = input("Subject: ")
                body      = input("Body: ")
                sendMessage([studentId], subject, body)
            case '6':
                studentList = getStudentList(courseId)
                studentIds = [student['id'] for student in studentList]
                subject   = input("Subject: ")
                body      = input("Body: ")
                sendMessage(studentIds, subject, body)
            case '7':
                showAssignmentDates()
            case 'r':
                renameGroups()
            case '10':
                setParams()
            case 'x':
                exit()
            case _:
                print("Invalid choice, please try again.")

main()
