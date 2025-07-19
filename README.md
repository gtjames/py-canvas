# canvas
##  A set of Python scripts to read the student information
###     all options ask for the option, the university and the course id
*   you can just time option space university space CourseId
*   and I will parse them to the three params
*   for instance 5 byupw XXXX will list the teams for class XXXX
*   You can also use option space space CourseId
*   and it will default to byupw
##  Main Menu
##  1. Team Members
        (1) Solo                Students alone in group
        (0) All                 All teams with team members
        (u) Unassigned          People not yet in a group

##  2. Students in Teams
        Sort students in class by:
                first, last, group, score, login, tz, email, id, 
        If you enter in 'search'
                you will be asked to endter part of the students name
                then everything about the student will be retrieved

##  3. List Unsubmitted
        Notify?         'Y' if you want to message them
        Message?        Subject line if you want to send students a message
        (A)ll           Send students or show all assignments
        (M)issing       Only send/show missing assignments

##  4.  Missing Assignment Letters
        Groups students by score and send different letters to the
        90% or better
        70 - 89%
        < 70$
        go/no go?       go to send letter
        Show Missed?    'y' to include missing assignments

##  5. Message 1 student
        Student Id:     Need the student Id
        Subject:        Message subject
        Body:           Message body

##  6. Message class
        Sends everyone in the class the same message
        Subject:        Message subject
        Body:           Message body

##  7.Show Assignment Dates
        Submission dates for all assignments
        sort by title, dueDate, lockDate, points

##  r. Rename Groups
        I think the groups should have other names
        This renames the groups to my liking
        Team 00 Tuesday 14:00 UTC --  08:00 Mtn
        Team 01 Tuesday 16:00 UTC --  10:00 Mtn
        Team 02 Tuesday 18:00 UTC --  12:00 Mtn
        Team 03 Tuesday 20:00 UTC --  14:00 Mtn
        Team 04 Tuesday 22:00 UTC --  16:00 Mtn
        Team 05 Tuesday 00:00 UTC --  18:00 Mtn
        Team 06 Tuesday 02:00 UTC --  20:00 Mtn
        Team 07 Tuesday 03:00 UTC --  21:00 Mtn

        Team 10 Wednesday 14:00 UTC --  08:00 Mtn
        Team 11 Wednesday 16:00 UTC --  10:00 Mtn
        Team 12 Wednesday 18:00 UTC --  12:00 Mtn
        Team 13 Wednesday 20:00 UTC --  14:00 Mtn
        Team 14 Wednesday 22:00 UTC --  16:00 Mtn
        Team 15 Wednesday 00:00 UTC --  18:00 Mtn
        Team 16 Wednesday 02:00 UTC --  20:00 Mtn
        Team 17 Wednesday 03:00 UTC --  21:00 Mtn

##  x. Exit