import frappe
from frappe.model.document import Document
from frappe import _


@frappe.whitelist()
def validate_event_conflict(doc, method):
    '''
    checks for conflicting events in the same meeting room
    by comparing the event's start and end times. If another event exists
    in the same room during the selected time, it displays a warning message.
    '''
    if doc.meeting_room and doc.starts_on and doc.ends_on and doc.workflow_state == "Draft":
        conflicting_events = frappe.get_all("Event", filters={
            "meeting_room": doc.meeting_room,
            "starts_on": ["<=", doc.ends_on],
            "ends_on": [">=", doc.starts_on],
            "name": ["!=", doc.name]
        }, fields=["name", "starts_on", "ends_on"])
        if conflicting_events:
            frappe.msgprint(_(f"The selected Service Unit <b>{doc.meeting_room}</b> is already assigned to another Event during this time. Send to Admin for Approval."), title="Warning", indicator="red")


@frappe.whitelist()
def validate_event_before_approval(doc, method):
    '''
    Ensure that before approving an event, no other 'Open' events exist
    with the same service unit (meeting room) at the same time.
    '''
    if doc.workflow_state == "Approved" and doc.status == "Open":
        conflicting_events = frappe.get_all(
            "Event",
            filters={
                "meeting_room": doc.meeting_room,
                "starts_on": ["<=", doc.ends_on],
                "ends_on": [">=", doc.starts_on],
                "status": "Open",
                "name": ["!=", doc.name],
            },
            fields=["name", "starts_on", "ends_on"]
        )
        if conflicting_events:
            frappe.throw(_("Cannot approve this event because another 'Open' event exists in the same Service Unit at the same time."))

@frappe.whitelist()
def validate_reason_for_rejection(doc, method):
    '''
    checks if the workflow state of the document is "Rejected"
    and if a reason for rejection has not been provided. If no reason is provided,
    it raises an error with a message to prompt the user to provide one.
    '''
    if doc.workflow_state == "Rejected" and not doc.reason_for_rejection:
        frappe.throw(_("Provide a Reason for Rejection before Rejecting this Event."))
