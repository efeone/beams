import frappe
from frappe import _
import json
from frappe.utils import getdate

@frappe.whitelist(allow_guest=True)
def response(message, data, success, status_code):
    '''
        method to generates responses of an API
        args:
            message : response message string
            data : json object of the data
            success : True or False depending on the API response
            status_code : status of the request
    '''
    frappe.clear_messages()
    frappe.local.response["message"] = message
    frappe.local.response["data"] = data
    frappe.local.response["success"] = success
    frappe.local.response["http_status_code"] = status_code
    return

@frappe.whitelist(allow_guest=True)
def login(login_id, password, device_token=None):
    '''
        API for user login
        args:
            login_id : username/email of the user
            password : user password
    '''
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=login_id, pwd=password)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        return response( "Authentication Error!",{},False,400)

    api_generate = generate_keys(frappe.session.user)
    user = frappe.get_doc("User", frappe.session.user)
    roles = frappe.get_roles(frappe.session.user)

    if device_token:
        add_new_device(login_id, device_token)

    frappe.local.response["message"] = {
            "success_key":1,
            "sid": frappe.session.sid,
            "api_key": user.api_key,
            "api_secret": api_generate,
            "is_active": user.enabled,
            "user_id": user.username,
            "name": user.full_name,
            "roles": roles,
            "msg": "Authentication Success"
        }

def generate_keys(user):
    '''
        method generates api secret for a user
        args:
            user : username of the user
    '''
    user_details = frappe.get_doc("User", user)
    api_secret =  frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.save()

    return api_secret

@frappe.whitelist()
def create_release_order():
    '''
        API to create Release Order
        args:
            JSON string of Release Order data
    '''
    try:
        # Get JSON data
        input_data = frappe.request.json

        # Validate mandatory fields
        mandatory_fields = ['Quotation To', 'Date', 'Order Type', 'Series']
        for field in mandatory_fields:
            if field not in input_data:
                return {
                    "status": "error",
                    "message": f'Missing mandatory field: {field}'
                }

        albatross_settings = frappe.get_single('Albatross Settings')
        if not albatross_settings.albatross_service_item:
            return {
                "status": "error",
                "message": 'Albatross service item not found in settings'
            }

        # Create new Quotation document
        quotation_doc = frappe.get_doc({
            "doctype": "Quotation",
            "transaction_date": input_data.get("Date"),
            "party_name": input_data.get("Invoice To (Party Name)"),
            "client_name": input_data.get("Client Name"),
            "executive_name": input_data.get("Executive Name"),
            "albatross_ref_number": input_data.get("Ref No"),
            "albatross_ro_id": input_data.get("RO No."),
            "region": input_data.get("Region"),
            "order_type": input_data.get("Order Type"),
            "series": input_data.get("Series"),
            "sales_type": input_data.get("Service Type"),
            "albatross_invoice_number": input_data.get("Invoice No."),
        })

        # Add items to the quotation
        quotation_doc.append('items', {
            'item_code': albatross_settings.albatross_service_item,
            'qty': 1,
            'rate': input_data.get('Taxable Value')
        })

        # Add taxes based on GST Rate
        gst_rate = input_data.get('GST Rate')
        if gst_rate:
            if input_data.get('CGST'):
                quotation_doc.append('taxes', {
                    'charge_type': 'On Net Total',
                    'account_head': 'Output Tax CGST - E',
                    'rate': gst_rate / 2,
                    'tax_amount': input_data['CGST'],
                    'description': 'CGST'
                })
            if input_data.get('SGST'):
                quotation_doc.append('taxes', {
                    'charge_type': 'On Net Total',
                    'account_head': 'Output Tax SGST - E',
                    'rate': gst_rate / 2,
                    'tax_amount': input_data['SGST'],
                    'description': 'SGST'
                })
            if input_data.get('IGST'):
                quotation_doc.append('taxes', {
                    'charge_type': 'On Net Total',
                    'account_head': 'Input Tax IGST - E',
                    'rate': gst_rate,
                    'tax_amount': input_data['IGST'],
                    'description': 'IGST'
                })

        quotation_doc.save(ignore_permissions=True)
        frappe.clear_messages()
        return response('Created Release Order Successfully', quotation_doc.as_dict(), True, 201)

    except frappe.exceptions.CharacterLengthExceededError as e:
        frappe.log_error("Character Length Exceeded", "Error in Release Order creation: " + str(e)[:120])
        return response('Character Length Exceeded in Error Log', {}, False, 400)

    except Exception as exception:
        frappe.log_error(frappe.get_traceback(), "Release Order Creation Error")
        clean_exception_message = strip_html_tags(str(exception))
        return response(f"An error occurred: {clean_exception_message}", {}, False, 400)

def strip_html_tags(text):
    '''
        Helper function to strip HTML tags from a string
    '''
    from bs4 import BeautifulSoup
    return BeautifulSoup(text, "html.parser").text
