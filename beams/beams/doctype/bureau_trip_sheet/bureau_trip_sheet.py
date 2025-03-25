import frappe
from frappe.model.document import Document
from frappe import _

class BureauTripSheet(Document):
    pass




@frappe.whitelist()
def get_batta_value(driver):
    """
    Fetch the 'outside_kerala' value from Batta Policy for the given driver.
    """
    batta_value = frappe.get_value("Batta Policy", {"driver": driver}, "outside_kerala")
    return batta_value if batta_value else 0

# @frappe.whitelist()
# def update_allowance(doc_name):
#     try:
#         # Retrieve the Bureau Trip Sheet document
#         doc = frappe.get_doc("Bureau Trip Sheet", doc_name)
#
#         # Check if the document exists
#         if not doc:
#             frappe.throw(_("Bureau Trip Sheet document not found."))
#
#         # Fetch the Batta Policy document
#         if not doc.batta_policy:
#             frappe.throw(_("Batta Policy not selected for the Bureau Trip Sheet."))
#
#         policy = frappe.get_doc("Batta Policy", doc.batta_policy)
#
#         # Reset the daily batta fields to 0 initially
#         doc.daily_batta_with_overnight_stay = 0
#         doc.daily_batta_without_overnight_stay = 0
#
#         # Determine allowance based on conditions
#         if doc.is_travelling_outside_kerala and doc.is_overnight_stay:
#             doc.daily_batta_with_overnight_stay = policy.outside_kerala__
#         elif doc.is_overnight_stay:
#             doc.daily_batta_with_overnight_stay = policy.inside_kerala__
#         elif doc.is_travelling_outside_kerala:
#             doc.daily_batta_without_overnight_stay = policy.outside_kerala
#         else:
#             doc.daily_batta_without_overnight_stay = policy.inside_kerala
#
#         # Save the updated document
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()
#
#         return "Allowance Updated"
#
#     except frappe.DoesNotExistError:
#         frappe.throw(_("The document with the name '{}' was not found.").format(doc_name))
#     except Exception as e:
#         frappe.throw(_("An error occurred: {}").format(str(e)))

# @frappe.whitelist()
# def update_batta(docname):
#     doc = frappe.get_doc("Bureau Trip Sheet", docname)
#
#     # Reset the daily batta fields to 0 initially
#     doc.daily_batta_with_overnight_stay = 0
#     doc.daily_batta_without_overnight_stay = 0
#
#     # Fetch the policy document (ensure you are retrieving the correct one)
#     policy = frappe.get_doc("Batta Policy", "Policy Name")  # Replace "Policy Name" with the actual policy name or logic to fetch it
#
#     # Determine allowance based on conditions
#     if doc.is_travelling_outside_kerala and doc.is_overnight_stay:
#         doc.daily_batta_with_overnight_stay = policy.outside_kerala__
#     elif doc.is_overnight_stay:
#         doc.daily_batta_with_overnight_stay = policy.inside_kerala__
#     elif doc.is_travelling_outside_kerala:
#         doc.daily_batta_without_overnight_stay = policy.outside_kerala
#     else:
#         doc.daily_batta_without_overnight_stay = policy.inside_kerala
#
#     return {
#         "daily_batta_with_overnight_stay": doc.daily_batta_with_overnight_stay,
#         "daily_batta_without_overnight_stay": doc.daily_batta_without_overnight_stay
#     }
