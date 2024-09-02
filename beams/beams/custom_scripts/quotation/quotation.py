import frappe
from frappe.model.mapper import get_mapped_doc
from frappe import _
from frappe.utils import nowdate
from frappe.desk.form.assign_to import add as add_assign
from frappe.utils.user import get_users_with_role
from frappe.model.naming import make_autoname
from datetime import datetime

def autoname(doc, method=None):
    """Automatically generate a name for the Quotation document based on custom naming rules defined
    in the 'Beams Accounts Settings' doctype."""
    beams_accounts_settings = frappe.get_doc("Beams Accounts Settings")
    quotation_naming_series = ''

     # Iterate through the naming rules
    for rule in beams_accounts_settings.beams_naming_rule:
        # Check if the rule applies to the "Quotation" doctype
        if rule.doc_type == "Quotation" and rule.naming_series:
            quotation_naming_series = rule.naming_series
            if quotation_naming_series:
            # Replace date placeholders with current date values
                if "{MM}" in quotation_naming_series or "{DD}" in quotation_naming_series or "{YY}" in quotation_naming_series:
                    quotation_naming_series = quotation_naming_series.replace("{MM}", datetime.now().strftime("%m"))
                    quotation_naming_series = quotation_naming_series.replace("{DD}", datetime.now().strftime("%d"))
                    quotation_naming_series = quotation_naming_series.replace("{YY}", datetime.now().strftime("%y"))

                # Generate the name using the updated naming series
                doc.name = frappe.model.naming.make_autoname(quotation_naming_series )
            else:
                frappe.throw(_("No valid naming series found for Quotation doctype"))

@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None, ignore_permissions=False):
    """
    Method: Creates a Sales Invoice from a Quotation document.
    Output: A new or updated Sales Invoice document mapped from the Quotation.
    """

    def set_missing_values(source, target):
        target.customer = source.party_name
        target.expected_total = source.rounded_total  # Ensure expected_total is set

        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    doclist = get_mapped_doc(
        "Quotation",
        source_name,
        {
            "Quotation": {
                "doctype": "Sales Invoice",
                "validation": {"docstatus": ["=", 1]},
                "field_map": {
                    "party_name": "customer",
                    "rounded_total": "expected_total"  # Map total to expected_total
                }
            },
            "Quotation Item": {
                "doctype": "Sales Invoice Item",
                "field_map": {
                    "parent": "quotation",
                    "name": "quotation_item"
                },
            },
            "Sales Taxes and Charges": {
                "doctype": "Sales Taxes and Charges",
                "add_if_empty": True
            },
            "Sales Team": {
                "doctype": "Sales Team",
                "add_if_empty": True
            },
            "Payment Schedule": {
                "doctype": "Payment Schedule",
                "add_if_empty": True
            },
        },
        target_doc,
        set_missing_values,
        ignore_permissions=ignore_permissions,
    )

    # Manually trigger validation
    # if doclist:
    #     doclist.run_method("validate")

    return doclist



def get_party_link_if_exist(party_type, party):
    ''' Method to get Common Party Link if exists '''
    query = """
        SELECT
            CASE
                WHEN primary_role = %(party_type)s THEN secondary_party
                WHEN secondary_role = %(party_type)s THEN primary_party
            END AS party
        FROM
            `tabParty Link`  # Adjusted to use backticks for the table name
        WHERE
            (primary_role = %(party_type)s AND primary_party = %(party)s )
            OR (secondary_role = %(party_type)s AND secondary_party = %(party)s )
    """
    party_link = frappe.db.sql(query, { 'party_type': party_type, 'party': party }, as_dict=1)

    if not party_link:
        return None
    else:
        return party_link[0].party


def create_common_party_and_supplier(customer):
    ''' Method to create Supplier against customer and link as Common Party '''
    common_party = get_party_link_if_exist('Customer', customer)
    if not common_party:
        # Create supplier for common party
        supplier_doc = frappe.new_doc('Supplier')
        customer_name = frappe.db.get_value('Customer', customer, 'customer_name')
        supplier_doc.supplier_name = customer_name
        supplier_group = frappe.db.get_single_value('Buying Settings', 'supplier_group')
        if not supplier_group:
            frappe.throw('Default Supplier Group is not configured in Buying Settings!')
        supplier_doc.supplier_group = supplier_group
        supplier_doc.insert()

        # Link common party
        if supplier_doc.name:
            link_doc = frappe.new_doc('Party Link')
            link_doc.primary_role = 'Customer'
            link_doc.primary_party = customer
            link_doc.secondary_role = 'Supplier'
            link_doc.secondary_party = supplier_doc.name
            link_doc.insert()

        frappe.msgprint('Common Party and Supplier Created and Linked', indicator="green", alert=1)
        common_party = supplier_doc.name

    return common_party

@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None, ignore_permissions=False):
    '''
    Method: Maps the Quotation ID to the quotation field in Purchase Invoice.
    Output: A new Purchase Invoice document with the Quotation ID mapped to quotation.
    '''

    customer = frappe.db.get_value("Quotation", source_name, "party_name")

    supplier = create_common_party_and_supplier(customer)

    def set_missing_values(source, target):
        target.quotation = source.name
        target.supplier = supplier

    doclist = get_mapped_doc(
        "Quotation",
        source_name,
        {
            "Quotation": {
                "doctype": "Purchase Invoice",
                "validation": {"docstatus": ["=", 1]},
                "field_map": {
                    "name": "quotation"
                }
            }
        },
        target_doc,
        set_missing_values,
        ignore_permissions=ignore_permissions,
    )

    return doclist

@frappe.whitelist()
def get_total_sales_invoice_amount(quotation_name):
    '''
    Method: Calculates the total amount of all Sales Invoices linked to the Quotation using rounded_total.
    '''
    total_amount = frappe.db.sql("""
        SELECT SUM(rounded_total) FROM `tabSales Invoice`
        WHERE reference_id = %s AND docstatus = 1
    """, quotation_name)[0][0]

    return total_amount or 0

@frappe.whitelist()
def validate_is_barter(quotation,method=None):
    '''
    Method: Checking Whether enable_common_party_accounting checked or not.
    '''
    # Fetch the setting from the Account Setting DocType
    enable_common_party_accounting = frappe.db.get_single_value('Accounts Settings', 'enable_common_party_accounting')

    # Check if 'is_barter' is checked
    if quotation.is_barter and not enable_common_party_accounting:
        frappe.throw("Please enable 'Common Party Accounting' in the Accounts Settings to proceed with barter transactions.")


@frappe.whitelist()
def create_tasks_for_production_items(doc, method):
    '''
    Method: Creating task for production items.
    '''

    if doc.docstatus == 1:  # Ensure it's only triggered on submit
        for item in doc.items:
            # Fetch `is_production_item` from the Item DocType using item_code from the child table
            is_production_item = frappe.db.get_value('Item', item.item_code, 'is_production_item')

            if is_production_item:
                quantity = item.qty
                for _ in range(int(quantity)):
                    create_task(item.item_code, doc.name)

def create_task(item_code, quotation_name):

    '''
    Method: Task Creation and Assigning to Production Manager.
    '''
    # Check if the task already exists
    if frappe.db.exists("Task", {"description": f'Production task for item {item_code} in Quotation {quotation_name}'}):
        return False

    # Create a new task document
    task = frappe.get_doc({
        'doctype': 'Task',
        'subject': f'Production Task for {item_code}',
        'description': f'Production task for item {item_code} in Quotation {quotation_name}.',
        'status': 'Open',
        'exp_start_date': nowdate(),
        'exp_end_date': nowdate(),  # Adjust the end date as needed
        'assigned_by': frappe.session.user,
    })

    # Insert the Task into the database
    task.insert(ignore_permissions=True)

    # Fetch Production Managers and assign the Task
    production_managers = get_users_with_role("Production Manager")
    if production_managers:
        add_assign({
            "assign_to": production_managers,
            "doctype": "Task",
            "name": task.name,
            "description": f'You are assigned a production task for item {item_code} in Quotation {quotation_name}.'
        })
    return True
