import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def create_adhoc_budget(source_name, target_doc=None):
    """
    Maps fields from the Project doctype to the Adhoc Budget doctype, including the
    selected values from the 'budget_expense_types' field into the child table 'Budget Expense'.
    """
    project_doc = frappe.get_doc('Project', source_name)
    adhoc_budget = get_mapped_doc("Project", source_name, {
        "Project": {  
                "doctype": "Adhoc Budget",  
                "field_map": {
                    "name": "project",  
                    "expected_start_date": "expected_start_date",
                    "expected_end_date": "expected_end_date",
                    "generates_revenue": "generates_revenue"
                }
            }
    }, target_doc)

    for expense_type in project_doc.budget_expense_types:
        adhoc_budget.append('budget_expense', {
            'budget_expense_type': expense_type.budget_expense_type
        })
    return adhoc_budget

