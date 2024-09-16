import frappe
from frappe import _
from datetime import datetime
from frappe.model.naming import make_autoname
from beams.beams.custom_scripts.quotation.quotation import create_common_party_and_supplier
from frappe.core.doctype.communication.email import make


def autoname(doc, method=None):
    """
    Automatically generate a name for the Sales Invoice document based on custom naming rules defined
    in the 'Beams Accounts Settings' doctype.
    """
    beams_accounts_settings = frappe.get_doc("Beams Accounts Settings")
    sales_invoice_naming_series = ''

    # Iterate through the naming rules
    for rule in beams_accounts_settings.beams_naming_rule:
        # Check if the rule applies to the Sales Invoice doctype
        if rule.doc_type == "Sales Invoice" and rule.naming_series:
            sales_invoice_naming_series = rule.naming_series
            if sales_invoice_naming_series:
                # Replace date placeholders with current date values
                if "{MM}" in sales_invoice_naming_series or "{DD}" in sales_invoice_naming_series or "{YY}" in sales_invoice_naming_series:
                    sales_invoice_naming_series = sales_invoice_naming_series.replace("{MM}", datetime.now().strftime("%m"))
                    sales_invoice_naming_series = sales_invoice_naming_series.replace("{DD}", datetime.now().strftime("%d"))
                    sales_invoice_naming_series = sales_invoice_naming_series.replace("{YY}", datetime.now().strftime("%y"))

                # Generate the name using the updated naming series
                doc.name = frappe.model.naming.make_autoname(sales_invoice_naming_series)
            else:
                frappe.throw(_("No valid naming series found for Sales Invoice doctype"))

@frappe.whitelist()
def validate_sales_invoice_amount_with_quotation(doc, method):
    '''
    Method to validate the sum of total amount in Sales Invoices against the total amount in the Quotation.
    Also checks if the `is_barter` checkbox is checked and ensures that a corresponding Purchase Invoice exists with the same customer.
    Creates common party and supplier if necessary.
    '''

    if doc.reference_id:
        # Fetch the Quotation document
        quotation = frappe.get_doc('Quotation', doc.reference_id)

        # Fetch the Beams Account Settings to check if single_sales_invoice is enabled
        single_sales_invoice_enabled = frappe.db.get_single_value('Beams Accounts Settings', 'single_sales_invoice')

        # Proceed only if the single_sales_invoice checkbox is checked
        if single_sales_invoice_enabled == 1:
            # Fetch all related Sales Invoices (excluding the current one)
            sales_invoices = frappe.get_all('Sales Invoice',
                filters={'reference_id': doc.reference_id, 'docstatus': 1, 'name': ['!=', doc.name]},
                fields=['grand_total'])

            # Calculate the total grand total of existing Sales Invoices
            total_grand_total = sum(invoice.grand_total for invoice in sales_invoices)

            # Add the current Sales Invoice's grand total
            total_grand_total += doc.grand_total

            # Perform the comparison with the Quotation's grand total
            if total_grand_total > quotation.grand_total:
                frappe.throw(_(
                    "The total amount of Sales Invoices for this Quotation cannot exceed the total amount in the Quotation."
                ))

            # Optional: Inform the user if the total is less than the Quotation (if required)
            elif total_grand_total < quotation.grand_total:
                frappe.throw(_(
                    "The total amount of Sales Invoices for this Quotation is less than the total amount in the Quotation."
                ))


        # Check if `is_barter` is checked in the Quotation
        if quotation.is_barter:
            # Check if there is a Purchase Invoice for the same Quotation
            purchase_invoices = frappe.get_all('Purchase Invoice',
                filters={'quotation': doc.reference_id, 'docstatus': 1},
                fields=['supplier'])

            if purchase_invoices:
                customer = doc.customer
                for purchase_invoice in purchase_invoices:
                    supplier = purchase_invoice.supplier
                    if customer:
                        # Ensure common party accounting is enabled
                        if frappe.db.get_single_value("Accounts Settings", "enable_common_party_accounting"):
                            common_party = create_common_party_and_supplier(customer)
                            if common_party:
                                frappe.msgprint(f'Common Party and Supplier {common_party} created and linked.', indicator="green", alert=1)
            else:
                frappe.throw(_(
                    "No Purchase Invoice found for the Quotation."
                ))



@frappe.whitelist()
def on_update_after_submit(doc, method=None):
    """
    Method triggered after the document is updated and submitted.
    It checks if the workflow state has changed to "Completed".
    """
    if doc.workflow_state == "Completed":
        send_email_to_party(doc)


@frappe.whitelist()
def send_email_to_party(doc):
    """
    Method to send an email with a PDF attachment of the given document (Sales Invoice)
    to the contact associated with the customer. Also validates the existence of the
    contact for the customer and its email ID.
    """
    customer_name = doc.customer

    # Fetch contact linked to the customer
    contact_name = frappe.db.get_value("Dynamic Link", {
        "link_doctype": "Customer",
        "link_name": customer_name,
        "parenttype": "Contact"
    }, "parent")

    if not contact_name:
        frappe.msgprint(f"Please Configure a Contact for Customer {customer_name}")
        return

    contact = frappe.get_doc("Contact", contact_name)

    if not contact.email_id:
        frappe.msgprint(f"Please Configure an Email Id  {contact.first_name or contact_name}.")
        return

    email_id = contact.email_id
    subject = f"{doc.doctype} {doc.name}"
    message = f"Dear {contact.first_name or 'Customer'},<br><br>Please find the attached {doc.doctype} {doc.name}.<br><br>Thank you."

    # Fetch the print format from Beam Account Settings
    print_format = frappe.db.get_single_value("Beams Accounts Settings", "default_sales_invoice_print_format")

    if not print_format:
        frappe.msgprint("Please configure a default print format for Sales Invoice in Beam Account Settings.")
        return

    try:
        # Try to generate PDF using the selected print format
        pdf_data = frappe.attach_print('Sales Invoice', doc.name, print_format=print_format)

        # Send the email with the PDF attachment
        frappe.sendmail(
            recipients=[email_id],
            subject=subject,
            message=message,
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            attachments=[{
                'fname': pdf_data['fname'],
                'fcontent': pdf_data['fcontent'],
            }]
        )
        frappe.msgprint(f"Email sent to {email_id} successfully.")

    except Exception as e:
        # Log the error and notify the user
        frappe.log_error(f"Failed to generate PDF or send email for {doc.doctype} {doc.name}: {str(e)}", "PDF/Email Failure")
        frappe.msgprint(f"Failed to generate PDF or send email to {contact.first_name or 'Customer'} ({email_id}). Please check the system logs for more details.")
