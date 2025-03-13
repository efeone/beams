import frappe
import re

def validate_training_program(doc, method):
    """ Validation for Email and Contact Number"""
    
    if doc.trainer_email and not frappe.utils.validate_email_address(doc.trainer_email):
        frappe.throw("Please enter a valid email address.")

    if doc.contact_number and not re.fullmatch(r"^\d{10}$", doc.contact_number):
        frappe.throw("Please enter a valid 10-digit contact number.")
