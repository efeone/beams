import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, nowtime
from frappe.utils.user import get_users_with_role
from frappe.desk.form.assign_to import add as add_assign


class InwardRegister(Document):



	def on_submit(self, method=None):
	    """
	    Creates a ToDo task for the driver when the 'vehicle_key' checkbox is checked.
	    The notification message will be "Vehicle key handed over in Inward."
	    """
	    if self.vehicle_key:
	        driver_users = get_users_with_role("Driver")
	        if driver_users:
	            description = f"Vehicle key handed over in Inward for {self.vistor_name}."
	            if not frappe.db.exists('ToDo', {
	                'reference_name': self.name,
	                'reference_type': 'Inward Register',
	                'description': description
	            }):
	                add_assign({
	                    "assign_to": driver_users,
	                    "doctype": "Inward Register",
	                    "name": self.name,
	                    "description": description
	                })
