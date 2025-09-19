import frappe
from frappe.model.document import Document
from frappe import _

@frappe.whitelist()
def validate_event_conflict(doc, method=None):
	"""
	Prevent saving if another event exists
	for the same meeting room in the overlapping time.
	"""

	doc = frappe.parse_json(doc)

	if not doc.get("meeting_room") or not doc.get("starts_on") or not doc.get("ends_on"):
		return

	conflict = frappe.db.exists(
		"Event",
		{
			"meeting_room": doc.get("meeting_room"),
			"starts_on": ["<=", doc.get("ends_on")],
			"ends_on": [">=", doc.get("starts_on")],
			"name": ["!=", doc.get("name")],
		}
	)

	if conflict:
		frappe.throw(
			_(f"The selected Meeting Room <b>{doc.get('meeting_room')}</b> is already booked during this time."),
			title=_("Meeting Room Conflict")
		)

@frappe.whitelist()
def validate_reason_for_rejection(doc, method):
	'''
	checks if the workflow state of the document is "Rejected"
	and if a reason for rejection has not been provided. If no reason is provided,
	it raises an error with a message to prompt the user to provide one.
	'''
	if doc.workflow_state == "Rejected" and not doc.reason_for_rejection:
		frappe.throw(_("Provide a Reason for Rejection before Rejecting this Event."))
