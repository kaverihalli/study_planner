"""
Smart Student Study Planner
---------------------------
A console-based study planner written in Python.

Features:
- Add subjects and link study tasks to them
- Deadline and priority for every task (tasks are kept sorted by deadline)
- Mark tasks as completed, delete tasks
- Overall and subject-wise progress report
- Data is saved to a JSON file, so nothing is lost when the program closes
- Input validation, so wrong input never crashes the program
"""

import json
import os
from datetime import datetime, date

# The data file is saved in the same folder as this program
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "study_planner_data.json")

PRIORITIES = ["High", "Medium", "Low"]
PRIORITY_RANK = {"High": 0, "Medium": 1, "Low": 2}


# ---------------------------------------------------------------
# File handling
# ---------------------------------------------------------------
def load_data():
    """Load subjects and tasks from the JSON file (if it exists)."""
    if not os.path.exists(DATA_FILE):
        return [], []

    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
        return data.get("subjects", []), data.get("tasks", [])
    except (json.JSONDecodeError, OSError):
        print("Could not read the saved data. Starting with an empty planner.")
        return [], []


def save_data(subjects, tasks):
    """Save subjects and tasks to the JSON file."""
    try:
        with open(DATA_FILE, "w") as file:
            json.dump({"subjects": subjects, "tasks": tasks}, file, indent=4)
    except OSError:
        print("Warning: could not save your data.")


# ---------------------------------------------------------------
# Input helpers (these prevent crashes on wrong input)
# ---------------------------------------------------------------
def get_number(message, low, high):
    """Keep asking until the user enters a whole number between low and high."""
    while True:
        try:
            number = int(input(message))
            if low <= number <= high:
                return number
            print(f"Please enter a number between {low} and {high}.")
        except ValueError:
            print("Invalid input! Please enter a number.")


def get_text(message):
    """Keep asking until the user enters non-empty text."""
    while True:
        text = input(message).strip()
        if text:
            return text
        print("This field cannot be empty.")


def get_deadline():
    """Ask for a deadline in YYYY-MM-DD format and validate it."""
    while True:
        text = input("Enter deadline (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(text, "%Y-%m-%d")
            return text
        except ValueError:
            print("Invalid date! Example of a valid date: 2026-12-31")


def choose_subject(subjects):
    """Show the subject list and let the user pick one by number."""
    print("\nSubjects:")
    for i, name in enumerate(subjects, start=1):
        print(f"  {i}. {name}")
    choice = get_number("Choose subject number: ", 1, len(subjects))
    return subjects[choice - 1]


def choose_priority():
    """Let the user pick High, Medium or Low priority."""
    print("\nPriority:")
    for i, level in enumerate(PRIORITIES, start=1):
        print(f"  {i}. {level}")
    choice = get_number("Choose priority number: ", 1, len(PRIORITIES))
    return PRIORITIES[choice - 1]


# ---------------------------------------------------------------
# Planner features
# ---------------------------------------------------------------
def add_subject(subjects):
    name = get_text("Enter subject name: ")

    # Avoid duplicate subjects (ignoring upper/lower case)
    if name.lower() in [s.lower() for s in subjects]:
        print("This subject already exists!")
        return

    subjects.append(name)
    print("Subject added successfully!")


def add_task(subjects, tasks):
    if len(subjects) == 0:
        print("No subjects available. Please add a subject first (option 1).")
        return

    subject = choose_subject(subjects)
    topic = get_text("Enter study topic: ")
    deadline = get_deadline()
    priority = choose_priority()

    tasks.append({
        "subject": subject,
        "topic": topic,
        "deadline": deadline,
        "priority": priority,
        "status": "Pending"
    })

    # Keep tasks sorted: earliest deadline first, then higher priority first
    tasks.sort(key=lambda t: (t["deadline"], PRIORITY_RANK[t["priority"]]))
    print("Study task added successfully!")


def view_tasks(tasks):
    if len(tasks) == 0:
        print("No tasks available.")
        return

    today = date.today().strftime("%Y-%m-%d")
    print("\nYour Study Tasks (sorted by deadline):")

    for i, task in enumerate(tasks, start=1):
        overdue = ""
        if task["status"] == "Pending" and task["deadline"] < today:
            overdue = "  <-- OVERDUE"

        print(f"\nTask {i}")
        print("Subject :", task["subject"])
        print("Topic   :", task["topic"])
        print("Deadline:", task["deadline"])
        print("Priority:", task["priority"])
        print("Status  :", task["status"] + overdue)


def mark_completed(tasks):
    if len(tasks) == 0:
        print("No tasks available!")
        return

    print("\nYour Study Tasks:")
    for i, task in enumerate(tasks, start=1):
        print(f"{i}. [{task['subject']}] {task['topic']} - {task['status']}")

    task_no = get_number("Enter task number to mark as completed: ", 1, len(tasks))

    if tasks[task_no - 1]["status"] == "Completed":
        print("This task is already completed!")
    else:
        tasks[task_no - 1]["status"] = "Completed"
        print("Task completed successfully!")


def delete_task(tasks):
    if len(tasks) == 0:
        print("No tasks available!")
        return

    print("\nYour Study Tasks:")
    for i, task in enumerate(tasks, start=1):
        print(f"{i}. [{task['subject']}] {task['topic']}")

    task_no = get_number("Enter task number to delete: ", 1, len(tasks))
    tasks.pop(task_no - 1)
    print("Task deleted successfully!")


def view_progress(subjects, tasks):
    if len(tasks) == 0:
        print("No tasks available!")
        return

    total = len(tasks)
    completed = sum(1 for t in tasks if t["status"] == "Completed")
    pending = total - completed
    progress = (completed / total) * 100

    print("\n===== Overall Study Progress =====")
    print("Total Tasks    :", total)
    print("Completed Tasks:", completed)
    print("Pending Tasks  :", pending)
    print("Progress       :", round(progress, 1), "%")

    print("\n===== Subject-wise Progress =====")
    for subject in subjects:
        subject_tasks = [t for t in tasks if t["subject"] == subject]

        if len(subject_tasks) == 0:
            print(f"{subject}: no tasks yet")
        else:
            done = sum(1 for t in subject_tasks if t["status"] == "Completed")
            percent = (done / len(subject_tasks)) * 100
            print(f"{subject}: {done} of {len(subject_tasks)} done "
                  f"({round(percent, 1)}%)")


# ---------------------------------------------------------------
# Main program
# ---------------------------------------------------------------
def show_menu():
    print("\n===============================")
    print("  SMART STUDENT STUDY PLANNER")
    print("===============================")
    print("1. Add Subject")
    print("2. Add Study Task")
    print("3. View Tasks")
    print("4. Mark Task as Completed")
    print("5. Delete Task")
    print("6. View Study Progress")
    print("7. Exit")


def main():
    subjects, tasks = load_data()

    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_subject(subjects)
        elif choice == "2":
            add_task(subjects, tasks)
        elif choice == "3":
            view_tasks(tasks)
        elif choice == "4":
            mark_completed(tasks)
        elif choice == "5":
            delete_task(tasks)
        elif choice == "6":
            view_progress(subjects, tasks)
        elif choice == "7":
            save_data(subjects, tasks)
            print("Your data has been saved. Thank you for using Study Planner!")
            break
        else:
            print("Invalid choice! Please try again.")
            continue

        # Save after every change so data is never lost
        save_data(subjects, tasks)


if __name__ == "__main__":
    main()