const canvasBaseUrl = "https://byui.instructure.com/api/v1";

let allRows = [];
let baseURL = "http://localhost:3000";

function authHeaders(token) {
    return {
        "Authorization": `Bearer ${token}`
    };
}

async function canvasGet(url, token) {
    url = "http://localhost:3000/api/canvas/" + url;
    console.log("Fetching URL:", url);
try {
    const response = await fetch(url, {
        method: "GET",
        headers: authHeaders(token)
    });
    console.log("Status:", response.status);
    if (!response.ok) {
        const text = await response.text();
        throw new Error(
            `HTTP ${response.status}: ${text}`
        );
    }
    return await response.json();
}

catch (error) {
    console.error("Fetch failed", error);
    throw error;
}}

async function loadCourseData() {

    const token = document.getElementById("apiToken").value.trim();
    const courseId = document.getElementById("courseId").value.trim();

    if (!token || !courseId) {
        alert("Token and Course ID are required");
        return;
    }

    document.getElementById("loading").style.display = "block";

    fetch(baseURL + "users/self", { headers: { Authorization: `Bearer ${token}` } }
)
.then(r => r.text())
.then(console.log)
.catch(console.error);

    try {
        const submissions = await canvasGet(
            `courses/${courseId}/students/submissions?student_ids[]=all&grouped=true&per_page=100`);
            console.log("Submissions:", submissions);
    //     const students = await canvasGet(
    //         `/courses/${courseId}/users?enrollment_type[]=student&per_page=100`,
    //         token
    //     );

    //     const assignments = await canvasGet(
    //         `courses/${courseId}/assignments?per_page=100`,
    //         token
    //     );

    //     buildTable(
    //         students,
    //         assignments,
    //         submissions,
    //         courseId,
    //         token
    //     );

    } catch (error) {
        console.error(error);
        alert(error.message);
    }

    document.getElementById("loading").style.display = "none";
}

function buildTable(
    students,
    assignments,
    submissions,
    courseId,
    token
) {

    const tbody = document.querySelector("#resultsTable tbody");
    tbody.innerHTML = "";

    allRows = [];

    for (const studentRecord of submissions) {

        const studentId = studentRecord.user_id;

        const student =
            students.find(s => s.id === studentId);

        if (!student) continue;

        for (const submission of studentRecord.submissions) {

            const assignment =
                assignments.find(a => a.id === submission.assignment_id);

            if (!assignment) continue;

            const submitted =
                !!submission.submitted_at;

            let status = "Missing";

            if (submitted) {
                status = submission.late ? "Late" : "Submitted";
            }

            const row = document.createElement("tr");

            row.dataset.status =
                status.toLowerCase();

            if (status === "Submitted") {
                row.classList.add("status-submitted");
            }

            if (status === "Missing") {
                row.classList.add("status-missing");
            }

            if (status === "Late") {
                row.classList.add("status-late");
            }

            row.innerHTML = `
                <td class="student-name">
                    ${student.name}
                </td>

                <td>
                    ${assignment.name}
                </td>

                <td>
                    ${submitted ? "✅" : "❌"}
                </td>

                <td>
                    ${submission.submitted_at || ""}
                </td>

                <td>
                    ${assignment.due_at || ""}
                </td>

                <td>
                    ${assignment.lock_at || ""}
                </td>

                <td>
                    ${status}
                </td>

                <td>
                    <input
                        type="datetime-local"
                        class="form-control extendDate">
                </td>

                <td>
                    <button
                        class="btn btn-sm btn-warning">
                        Extend
                    </button>
                </td>
            `;

            const extendButton =
                row.querySelector("button");

            extendButton.addEventListener(
                "click",
                () => extendUntilDate(
                    courseId,
                    assignment.id,
                    student.id,
                    row.querySelector(".extendDate").value,
                    token
                )
            );

            tbody.appendChild(row);
            allRows.push(row);
        }
    }
}

async function extendUntilDate(
    courseId,
    assignmentId,
    studentId,
    newDate,
    token
) {

    if (!newDate) {
        alert("Select a new Until Date");
        return;
    }

    try {

        const response = await fetch(
            `${canvasBaseUrl}/courses/${courseId}/assignments/${assignmentId}/overrides`,
            {
                method: "POST",
                headers: {
                    ...authHeaders(token),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    assignment_override: {
                        student_ids: [studentId],
                        due_at: newDate,
                        lock_at: newDate
                    }
                })
            }
        );

        if (!response.ok) {
            throw new Error(await response.text());
        }

        alert("Extension created.");

    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}

document
    .getElementById("loadBtn")
    .addEventListener("click", loadCourseData);

document
    .getElementById("filterStatus")
    .addEventListener("change", function() {

        const filter = this.value;

        for (const row of allRows) {

            if (filter === "all") {
                row.style.display = "";
                continue;
            }

            row.style.display =
                row.dataset.status === filter
                    ? ""
                    : "none";
        }
    });
