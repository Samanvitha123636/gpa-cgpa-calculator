import streamlit as st
import pandas as pd
import json
import os

# GPA calculator

st.title("Gradeline")

SAVE_FILE = "gradeline_data.json"

def convert_for_json(value):
    if hasattr(value, "item"):
        return value.item()
    else:
        return str(value)

def save_progress():
    data = {
        "courses": st.session_state.courses.to_dict(orient="records"),
        "plan_courses": st.session_state.plan_courses.to_dict(orient="records") if "plan_courses" in st.session_state else [],
        "semester_history": st.session_state.get("semester_history", []),
        "prev_cgpa": st.session_state.get("prev_cgpa_input", 0.0),
        "prev_credits": st.session_state.get("prev_credits_input", 0.0),
        "current_cgpa": st.session_state.get("current_cgpa_input", 0.0),
        "current_credits": st.session_state.get("current_credits_input", 0.0),
        "aim_cgpa": st.session_state.get("aim_cgpa_input", 0.0),
        "next_credits": st.session_state.get("next_credits_input", 0.0),
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, default=convert_for_json)

def load_progress():
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    st.session_state.courses = pd.DataFrame(data["courses"], columns=["Name", "Credit", "Grade"])
    st.session_state.plan_courses = pd.DataFrame(data["plan_courses"], columns=["Name", "Credit", "Grade"])
    st.session_state.semester_history = data.get("semester_history", [])
    st.session_state["prev_cgpa_input"] = data["prev_cgpa"]
    st.session_state["prev_credits_input"] = data["prev_credits"]
    st.session_state["current_cgpa_input"] = data["current_cgpa"]
    st.session_state["current_credits_input"] = data["current_credits"]
    st.session_state["aim_cgpa_input"] = data["aim_cgpa"]
    st.session_state["next_credits_input"] = data["next_credits"]

if "data_loaded" not in st.session_state:
    if os.path.exists(SAVE_FILE):
        load_progress()
    st.session_state.data_loaded = True


st.header("This Semester")

GRADE_POINTS = {
    "S (10)": 10, "A+ (9)": 9, "A (8)": 8, "B+ (7)": 7, "B (6.5)": 6.5,
    "C+ (6)": 6, "C (5)": 5, "U (0)": 0, "SA (0)": 0, "WC (0)": 0
}

if "courses" not in st.session_state:
    st.session_state.courses = pd.DataFrame(columns=["Name", "Credit", "Grade"])

edited = st.data_editor(
    st.session_state.courses,
    num_rows="dynamic",
    column_config={
        "Credit": st.column_config.NumberColumn(min_value=0.0, step=0.5),
        "Grade": st.column_config.SelectboxColumn(options=list(GRADE_POINTS.keys())),
    },
    use_container_width=True,
    key="course_editor",
)

valid_rows = edited.dropna(subset=["Credit", "Grade"])
valid_rows = valid_rows[valid_rows["Credit"] > 0]

if len(valid_rows) > 0:
    points = valid_rows["Grade"].map(GRADE_POINTS)
    total_credits = valid_rows["Credit"].sum()
    total_points = (valid_rows["Credit"] * points).sum()
    gpa = total_points / total_credits

    st.metric("Semester GPA", f"{gpa:.2f}")
else:
    st.write("Add at least one complete course to see your GPA.")


# --- Semester History ---

if "semester_history" not in st.session_state:
    st.session_state.semester_history = []

semester_label = st.text_input("Semester label", placeholder="e.g. Semester 3", key="semester_label_input")

if st.button("Save this semester to history"):
    if len(valid_rows) == 0:
        st.warning("Add at least one complete course before saving.")
    elif semester_label.strip() == "":
        st.warning("Give this semester a label first.")
    else:
        st.session_state.semester_history.append({
            "label": semester_label,
            "gpa": gpa,
            "credits": total_credits,
            "courses": valid_rows.to_dict(orient="records"),
        })
        st.success(f"Saved {semester_label} to history.")

st.divider()
st.header("Semester History")

if len(st.session_state.semester_history) == 0:
    st.write("No semesters saved yet.")
else:
    index_to_delete = None

    for i, entry in enumerate(st.session_state.semester_history):
        with st.expander(f"{entry['label']} — GPA: {entry['gpa']:.2f} ({entry['credits']} credits)"):
            history_table = pd.DataFrame(entry["courses"])
            st.dataframe(history_table, use_container_width=True)

            if st.button("Delete", key=f"delete_{i}"):
                index_to_delete = i

    if index_to_delete is not None:
        st.session_state.semester_history.pop(index_to_delete)
        st.rerun()


# CGPA calculator

st.divider()
st.header("Cumulative Record")

prev_cgpa = st.number_input("CGPA before this semester", min_value=0.0, max_value=10.0, step=0.01, key="prev_cgpa_input")
prev_credits = st.number_input("Credits completed before this semester", min_value=0.0, step=1.0, key="prev_credits_input")
if st.button("Update CGPA with this semester"):
    if len(valid_rows) > 0:
        new_cgpa = (prev_cgpa * prev_credits + gpa * total_credits) / (prev_credits + total_credits)
        st.session_state.new_cgpa = new_cgpa
    else:
        st.warning("Add at least one complete course above first.")

if "new_cgpa" in st.session_state:
    st.metric("New CGPA", f"{st.session_state.new_cgpa:.2f}")


# GPA predictor (standalone — Section A)

st.divider()
st.header("Plan Next Semester")

current_cgpa = st.number_input("Your current CGPA", min_value=0.0, max_value=10.0, step=0.01, key="current_cgpa_input")
current_credits = st.number_input("Total credits completed so far", min_value=0.0, step=1.0, key="current_credits_input")
aim_cgpa = st.number_input("Aim CGPA", min_value=0.0, max_value=10.0, step=0.01, key="aim_cgpa_input")
next_credits = st.number_input("Total credits next semester", min_value=0.0, step=1.0, key="next_credits_input")

if st.button("Calculate required GPA"):
    if next_credits > 0:
        required_gpa = (aim_cgpa * (current_credits + next_credits) - current_cgpa * current_credits) / next_credits
        st.session_state.required_gpa = required_gpa
    else:
        st.warning("Next semester's credits can't be 0.")

if "required_gpa" in st.session_state:
    req = st.session_state.required_gpa
    if req > 10:
        st.error(f"Required GPA: {req:.2f} — not achievable even with all S grades next semester.")
    elif req <= 0:
        st.success("You've already secured this CGPA — any passing semester keeps you there.")
    else:
        st.metric("Required GPA next semester", f"{req:.2f}")


# Required grade per course (Section B — depends on Section A)

st.divider()
st.header("Required Grade Per Course")

PLAN_GRADE_OPTIONS = ["Unsure"] + list(GRADE_POINTS.keys())

if "plan_courses" not in st.session_state:
    st.session_state.plan_courses = pd.DataFrame(columns=["Name", "Credit", "Grade"])

st.write("Upcoming courses — pick a grade for the ones you're confident about, leave the rest as 'Unsure':")

plan_edited = st.data_editor(
    st.session_state.plan_courses,
    num_rows="dynamic",
    column_config={
        "Credit": st.column_config.NumberColumn(min_value=0.0, step=0.5),
        "Grade": st.column_config.SelectboxColumn(options=PLAN_GRADE_OPTIONS),
    },
    use_container_width=True,
    key="plan_course_editor",
)

if st.button("Calculate required grades"):
    if "required_gpa" not in st.session_state:
        st.warning("Calculate your required GPA above first.")
    else:
        plan_valid = plan_edited.dropna(subset=["Credit", "Grade"])
        plan_valid = plan_valid[plan_valid["Credit"] > 0]

        if len(plan_valid) == 0:
            st.warning("Add at least one upcoming course above first.")
        else:
            required_gpa = st.session_state.required_gpa
            total_plan_credits = plan_valid["Credit"].sum()
            sum_needed = required_gpa * total_plan_credits

            locked = plan_valid[plan_valid["Grade"] != "Unsure"]
            unsure = plan_valid[plan_valid["Grade"] == "Unsure"]

            sum_locked = (locked["Credit"] * locked["Grade"].map(GRADE_POINTS)).sum()
            unsure_credits = unsure["Credit"].sum()

            st.session_state.plan_result = {
                "locked": locked,
                "unsure": unsure,
                "sum_needed": sum_needed,
                "sum_locked": sum_locked,
                "unsure_credits": unsure_credits,
            }

def nearest_grade(point):
    sorted_grades = sorted(GRADE_POINTS.items(), key=lambda item: item[1])
    for label, value in sorted_grades:
        if value >= point - 1e-9:
            return label
    return None

if "plan_result" in st.session_state:
    r = st.session_state.plan_result

    if r["unsure_credits"] == 0:
        st.write("You've set a grade for every course — no unsure courses to solve for.")
    else:
        needed_avg_point = (r["sum_needed"] - r["sum_locked"]) / r["unsure_credits"]

        if needed_avg_point > 10:
            st.error(f"Needed average: {needed_avg_point:.2f} — not achievable even with S in every unsure course.")
        elif needed_avg_point <= 0:
            st.success("Your locked-in grades already cover the target — any passing grade works for the rest.")
        else:
            suggested = nearest_grade(needed_avg_point)
            st.metric("Needed average grade point (unsure courses)", f"{needed_avg_point:.2f}")
            st.write(f"Suggested minimum grade for each unsure course: **{suggested}**")
            st.write("Unsure courses:")
            st.dataframe(r["unsure"][["Name", "Credit"]], use_container_width=True)
save_progress()