# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils import today, add_days
from frappe.utils import today
from frappe import _

class GuestAppointment(Document):
    def on_update_after_submit(self):
        self.validate_employee_availability()
        if self.workflow_state == "Approved":
            self.send_appointment_notifications()

    def before_save(self):
        self.validate_posting_date()

    def validate_employee_availability(self):
        '''
        Validates if the employee associated with the document is available
        on the specified appointment date.
        '''

        leave_applications = frappe.db.exists(
            "Leave Application",
            {
                "employee": self.received_by,
                "status": "Approved",
                "from_date": ["<=", self.appointment_date],
                "to_date": [">=", self.appointment_date],
            }
        )

        if leave_applications:
            frappe.throw(
                f"The employee {self.received_by} has an approved leave on {self.appointment_date}."
            )
    def send_appointment_notifications(self):
        '''
        Creates a ToDo  to the employee (received_by) when the workflow state is 'Approved'.
        '''
        if not self.received_by:
            return

        # Get the user ID and name of the employee
        employee_user = frappe.get_value("Employee", self.received_by, "user_id")
        employee_name = frappe.get_value("Employee", self.received_by, "employee_name")
        if not employee_user:
            return

        # ToDo message
        todo_message = f"An appointment with guest {self.received_by} has been scheduled on {self.appointment_date} at {self.appointment_time}."

        # Check if a ToDo already exists for the same document and message
        existing_todo = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": self.doctype,
                "reference_name": self.name,
                "status": "Open",
                "description": todo_message,
            },
        )

        if existing_todo:
            return

        add_assign({
            "assign_to": [employee_user],
            "doctype": self.doctype,
            "name": self.name,
            "description": todo_message,
        })
        
    @frappe.whitelist()
    def validate_posting_date(self):
        if self.posting_date:
            if self.posting_date > today():
                frappe.throw(_("Posting Date cannot be set after today's date."))


@frappe.whitelist()
def create_inward_register(guest_appointment):
    appointment = frappe.get_doc("Guest Appointment", guest_appointment)

    inward_register = frappe.new_doc("Inward Register")
    inward_register.visitor_name = appointment.guest_name
    inward_register.received_by = appointment.received_by
    inward_register.purpose_of_visit = appointment.purpose_of_visit
    inward_register.visit_date = appointment.appointment_date
    inward_register.visitor_type = "Guest"
    inward_register.insert(ignore_mandatory=True)

    return inward_register.name
