import frappe
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role
from frappe.utils import get_url

def on_task_update(task_doc, method):
    """
    Triggered when a Task is updated. Checks if the task is part of the activities
    table of an Employee Separation DocType. If all tasks are completed, perform the required actions.
    """

    cdn = frappe.db.exists("Employee Boarding Activity", {"task": task_doc.name})
    if not cdn:
        return

    parent_info = frappe.db.get_value(
        "Employee Boarding Activity", cdn, ["parent", "parenttype"], as_dict=True
    )

    if not parent_info or parent_info.parenttype != "Employee Separation":
        return

    emp_separation_doc = frappe.get_doc("Employee Separation", parent_info.parent)

    all_completed = True
    for row in emp_separation_doc.activities:
        if frappe.db.get_value("Task", row.task, "status") != "Completed":
            all_completed = False
            break

    if all_completed:
        emp_separation_doc.db_set("boarding_status", "Completed")
        create_todo_for_hr_manager(emp_separation_doc)


def create_todo_for_hr_manager(emp_separation_doc):
    """
    Create a ToDo task for HR Managers when all tasks in an Employee Separation are completed.
    """
    # Fetch all HR Manager users
    hr_manager_users = get_users_with_role("HR Manager")

    if not hr_manager_users:
        frappe.msgprint("No HR Manager role user found.", alert=True)
        return

    # Format the task details for the ToDo description
    task_list = "\n".join([
        f"- {frappe.get_value('Task', row.task, 'subject')} (Status: Completed)"
        for row in emp_separation_doc.activities
    ])

    # ToDo description
    todo_description = f"""
        The Employee Separation {emp_separation_doc.name} has been marked as Completed.
        Below is the list of associated tasks:
        {task_list}
    """
    
    # Create a ToDo for each HR Manager
    for user in hr_manager_users:
        add_assign({
            "assign_to": hr_manager_users,
            "doctype": "Employee Separation",
            "name": emp_separation_doc.name,
            "description": todo_description.strip()
        })

    frappe.msgprint("ToDo created for HR Manager(s).", alert=True)
