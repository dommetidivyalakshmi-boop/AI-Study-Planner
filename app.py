import streamlit as st
import pandas as pd
from datetime import date, timedelta

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------

st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Study Planner")
st.write(
    "Create a personalized weekly study schedule based on "
    "subjects, available hours, exam dates and priority topics."
)

# ---------------------------------------------------
# SIDEBAR - INPUT CONSTRAINTS
# ---------------------------------------------------

st.sidebar.header("📌 Study Constraints")

start_date = st.sidebar.date_input(
    "Start Date",
    value=date.today()
)

available_hours = st.sidebar.number_input(
    "Available Study Hours Per Day",
    min_value=1.0,
    max_value=12.0,
    value=4.0,
    step=0.5
)

subjects_text = st.sidebar.text_area(
    "Enter Subjects",
    value="Python, Database, AI, Blockchain"
)

priority_text = st.sidebar.text_area(
    "Priority Topics",
    value="AI, Python"
)

exam_date = st.sidebar.date_input(
    "Exam Date",
    value=date.today() + timedelta(days=7)
)

generate_button = st.sidebar.button(
    "🚀 Generate Study Plan"
)

# ---------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------

def get_priority(subject, priority_topics):
    """
    Assign priority to each subject.
    """

    subject = subject.strip().lower()

    for topic in priority_topics:
        if topic.strip().lower() in subject:
            return "High"

    return "Normal"


def get_task_count(priority):
    """
    Decide number of study sessions based on priority.
    """

    if priority == "High":
        return 3

    return 2


def create_tasks(subjects, priority_topics):
    """
    Task Decomposition:
    Divide every subject into smaller study tasks.
    """

    tasks = []

    for subject in subjects:

        subject = subject.strip()

        if not subject:
            continue

        priority = get_priority(
            subject,
            priority_topics
        )

        task_count = get_task_count(priority)

        for i in range(1, task_count + 1):

            task = {
                "Subject": subject,
                "Task": f"{subject} - Study Part {i}",
                "Priority": priority
            }

            tasks.append(task)

    return tasks


def generate_schedule(
    start_date,
    exam_date,
    available_hours,
    tasks
):
    """
    Schedule Generation.
    Assign tasks to available days and hours.
    """

    if exam_date <= start_date:
        return []

    number_of_days = (
        exam_date - start_date
    ).days

    # Limit to one week for weekly planner
    number_of_days = min(number_of_days, 7)

    if number_of_days <= 0:
        return []

    schedule = []

    # High priority tasks first
    tasks = sorted(
        tasks,
        key=lambda x: 0 if x["Priority"] == "High" else 1
    )

    # Maximum number of sessions per day
    max_sessions = max(
        1,
        int(available_hours // 1)
    )

    task_index = 0

    for day_number in range(number_of_days):

        current_date = (
            start_date +
            timedelta(days=day_number)
        )

        daily_hours = 0

        while (
            daily_hours < available_hours
            and task_index < len(tasks)
            and daily_hours < max_sessions
        ):

            task = tasks[task_index]

            schedule.append({
                "Date": current_date,
                "Day": current_date.strftime("%A"),
                "Subject": task["Subject"],
                "Task": task["Task"],
                "Priority": task["Priority"],
                "Hours": 1
            })

            daily_hours += 1
            task_index += 1

    return schedule


def evaluate_schedule(
    schedule,
    available_hours
):
    """
    Evaluation:
    Check whether daily study hours exceed
    available hours.
    """

    if not schedule:
        return False, "No schedule was generated."

    df = pd.DataFrame(schedule)

    daily_hours = (
        df.groupby("Date")["Hours"]
        .sum()
    )

    violations = daily_hours[
        daily_hours > available_hours
    ]

    if len(violations) > 0:

        return (
            False,
            "Available time constraint is violated."
        )

    return (
        True,
        "Schedule satisfies the available-time constraint."
    )


# ---------------------------------------------------
# GENERATE PLAN
# ---------------------------------------------------

if generate_button:

    subjects = [
        subject.strip()
        for subject in subjects_text.split(",")
        if subject.strip()
    ]

    priority_topics = [
        topic.strip()
        for topic in priority_text.split(",")
        if topic.strip()
    ]

    if not subjects:

        st.error(
            "Please enter at least one subject."
        )

    elif exam_date <= start_date:

        st.error(
            "Exam date must be after the start date."
        )

    else:

        # -------------------------------------------
        # TASK DECOMPOSITION
        # -------------------------------------------

        st.subheader("🧩 Task Decomposition")

        tasks = create_tasks(
            subjects,
            priority_topics
        )

        task_df = pd.DataFrame(tasks)

        st.dataframe(
            task_df,
            use_container_width=True
        )

        # -------------------------------------------
        # SCHEDULE GENERATION
        # -------------------------------------------

        st.subheader("📅 Generated Weekly Schedule")

        schedule = generate_schedule(
            start_date,
            exam_date,
            available_hours,
            tasks
        )

        if schedule:

            schedule_df = pd.DataFrame(schedule)

            st.dataframe(
                schedule_df,
                use_container_width=True
            )

            # ---------------------------------------
            # SUMMARY
            # ---------------------------------------

            st.subheader("📊 Study Summary")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Total Tasks",
                    len(tasks)
                )

            with col2:
                st.metric(
                    "Study Sessions",
                    len(schedule)
                )

            with col3:
                st.metric(
                    "Total Hours",
                    schedule_df["Hours"].sum()
                )

            # ---------------------------------------
            # EVALUATION
            # ---------------------------------------

            st.subheader("✅ Plan Evaluation")

            valid, message = evaluate_schedule(
                schedule,
                available_hours
            )

            if valid:
                st.success(message)
            else:
                st.warning(message)

            # ---------------------------------------
            # PRIORITY ANALYSIS
            # ---------------------------------------

            st.subheader("⭐ Priority Analysis")

            priority_count = (
                schedule_df["Priority"]
                .value_counts()
            )

            st.bar_chart(priority_count)

            # ---------------------------------------
            # DOWNLOAD
            # ---------------------------------------

            csv_data = schedule_df.to_csv(
                index=False
            )

            st.download_button(
                label="⬇️ Download Study Plan",
                data=csv_data,
                file_name="study_plan.csv",
                mime="text/csv"
            )

        else:

            st.warning(
                "Not enough available days to create a plan."
            )

# ---------------------------------------------------
# INFORMATION
# ---------------------------------------------------

else:

    st.info(
        "Enter your subjects, available hours, "
        "priority topics and exam date, then click "
        "'Generate Study Plan'."
    )

    st.markdown(
        """
        ### How the system works

        1. **Input Constraints** – Collects subjects,
           available study hours and exam date.

        2. **Task Decomposition** – Divides subjects
           into smaller study tasks.

        3. **Priority Handling** – Gives more study
           sessions to priority subjects.

        4. **Schedule Generation** – Creates a weekly
           timetable.

        5. **Evaluation** – Checks whether the schedule
           satisfies available-time constraints.

        6. **Regeneration** – User can generate the
           schedule again after changing inputs.
        """
    )