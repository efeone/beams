import frappe
from frappe import _
from frappe.model.document import Document

class ProvidentFund(Document):
    def validate(self):
        '''
        This method is triggered before saving the document to check if
        the Provident Fund record already exists for the employee.
        '''
        self.check_existing_provident_fund()

    def check_existing_provident_fund(self):
        '''
        Checks if a Provident Fund record already exists for the employee.
        If it exists, raises an error to prevent duplication.
        '''
        if not self.employee_name:
            frappe.throw(_("Employee Name is required"))

        # Check if Provident Fund record already exists for the employee
        existing_record = frappe.db.get_value(
            "Provident Fund",
            {"employee_name": self.employee_name},
            "name"
        )

        if existing_record:
            frappe.throw(_("A Provident Fund record already exists for this employee."))

@frappe.whitelist()
def get_employee_by_name(employee_name):
    '''
    Fetch employee details based on employee_name.
    '''
    if not employee_name:
        frappe.throw(_("Employee Name is required"))

    employee = frappe.db.get_value(
        "Employee",
        {"employee_name": employee_name},
        [
            "employee_number",
            "employee_name",
            "department",
            "designation",
            "cell_number",
            "personal_email",
            "company_email",
            "user_id",
            "name_of_father",
            "gender",
            "date_of_birth",
            "permanent_address",
            "current_address",
        ],
        as_dict=True,
    )

    if not employee:
        frappe.throw(_("No Employee found with the given Name"))

    return employee

@frappe.whitelist()
def get_or_create_provident_fund(employee_name):
    '''
    Fetch or create a Provident Fund record for the employee.
    '''
    if not employee_name:
        frappe.throw(_("Employee Name is required"))

    # Check if Provident Fund record already exists for the employee
    existing_record = frappe.db.get_value(
        "Provident Fund",
        {"employee_name": employee_name},
        "name"
    )

    if existing_record:
        return frappe.get_doc("Provident Fund", existing_record)

    provident_fund = frappe.new_doc("Provident Fund")
    provident_fund.employee_name = employee_name
    provident_fund.insert()

    return provident_fund
