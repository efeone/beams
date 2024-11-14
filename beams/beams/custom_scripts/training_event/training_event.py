import frappe

@frappe.whitelist()
def get_open_training_requests():
    return frappe.get_all(
        "Training Request",
        filters={"status": "Open"},
        fields=["name", "employee", "employee_name"]
    )

def on_update(doc,method):
    '''
    Updates the status of linked Training Requests when a Training Event is saved,
    based on the event's status.
    '''
    status_mapping = {
        "Scheduled": "Training Scheduled",
        "Completed": "Training Completed",
        "Cancelled": "Open"
    }

    if doc.event_status in status_mapping:
        for row in doc.employees:
            frappe.db.set_value("Training Request", row.training_request, "status", status_mapping[doc.event_status])
