import frappe
from frappe import _
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
def login(login_id, password):
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

def strip_html_tags(text):
	'''
		Helper function to strip HTML tags from a string
	'''
	from bs4 import BeautifulSoup
	return BeautifulSoup(text, "html.parser").text

@frappe.whitelist()
def get_region_list(start=0, page_length=20, region=None):
	'''
		API to get List of Region
	'''
	region_fields = ['name as region_id', 'region']
	if region:
		region_list = frappe.db.get_all('Region', filters={ 'region':['like', '%{0}%'.format(region)] }, fields=region_fields, start=start, page_length=page_length)
	else:
		region_list = frappe.db.get_all('Region', fields=region_fields, start=start, page_length=page_length)
	if region_list:
		return response('Data get successfully', region_list, True, 200)
	else:
		return response('No Regions found', region_list, True, 200)

@frappe.whitelist()
def get_agency_list(start=0, page_length=20, agency_name=None):
	'''
		API to get List of Agency
	'''
	agency_fields = ['name as agency_id', 'customer_name as agency_name', 'region', 'gstin', 'pan as pan_no', 'default_currency as currency']
	filters = { 'is_agent':1 }
	if agency_name:
		filters = { 'is_agent':1, 'customer_name':['like', '%{0}%'.format(agency_name)] }
	agency_list = frappe.db.get_all('Customer', filters=filters, fields=agency_fields, start=start, page_length=page_length)
	if agency_list:
		return response('Data get successfully', get_customer_address(agency_list, 1), True, 200)
	else:
		return response('No Agencies found', agency_list, True, 200)

@frappe.whitelist()
def get_client_list(start=0, page_length=20, client_name=None):
	'''
		API to get List of Client
	'''
	client_fields = ['name as client_id', 'customer_name as client_name', 'region', 'gstin', 'pan as pan_no', 'default_currency as currency']
	filters = { 'is_agent':0 }
	if client_name:
		filters = { 'is_agent':0, 'customer_name':['like', '%{0}%'.format(client_name)] }
	client_list = frappe.db.get_all('Customer', filters=filters, fields=client_fields, start=start, page_length=page_length)
	if client_list:
		return response('Data get successfully', get_customer_address(client_list), True, 200)
	else:
		return response('No Clients found', client_list, True, 200)

@frappe.whitelist()
def get_customer_address(customer_list, agency=0):
	'''
		Method fetches address of customer and add it to the list
		Args:
			customer_list (list): list of dicts fo customers
			agency (int, optional): denotes whether the customer list of agents or not. Defaults to 0.
		Returns:
			list of dicts: customer list of dicts with address keys
	'''
	for customer in customer_list:
		dynamic_link = frappe.db.exists('Dynamic Link', { 'parenttype':'Address', 'link_doctype':'Customer', 'link_name':customer.get('client_id') if not agency else customer.get('agency_id')})
		address = "" if not dynamic_link else frappe.db.get_value('Dynamic Link', dynamic_link, 'parent')
		address_data = {
			"address_line_1": "",
			"address_line_2": "",
			"address_line_3": "",
			"address_line_4": "",
			"pincode": ""
		}
		if address:
			address_data = frappe.db.get_all('Address', filters={ 'name':address }, fields=['address_line1 as address_line_1', 'address_line2 as address_line_2', 'city as address_line_3', 'state as address_line_4', 'pincode'])[0]
		customer["address_line_1"] = address_data.get('address_line_1')
		customer["address_line_2"] = address_data.get('address_line_2')
		customer["address_line_3"] = address_data.get('address_line_3')
		customer["address_line_4"] = address_data.get('address_line_4')
		customer["pincode"] = address_data.get('pincode')
	return customer_list

def get_sales_taxes_and_charges_template(tax_rate, tax_category):
	'''
		Method to get Sales Taxes and Charges Template
		args:
			tax_rate : Tax Percentage
			tax_category : Tax Category
	'''
	tax_template = None
	tax_row = frappe.db.exists('Albatross GST Mapping', {
		"parent": "Albatross Settings",
		"tax_rate": int(tax_rate),
		"tax_category": tax_category,
	})
	if tax_row:
		tax_template = frappe.db.get_value('Albatross GST Mapping', tax_row, 'tax_template')
	return tax_template

@frappe.whitelist()
def get_currency_list(start=0, page_length=20, currency=None):
	'''
		API to get List of Currency
	'''
	currency_fields = ['currency_name', 'symbol']
	if currency:
		currency_list = frappe.db.get_all('Currency', filters={ 'currency_name':['like', '%{0}%'.format(currency)], 'enabled':1 }, fields=currency_fields, start=start, page_length=page_length)
	else:
		currency_list = frappe.db.get_all('Currency', filters={ 'enabled':1 }, fields=currency_fields, start=start, page_length=page_length)
	if currency_list:
		return response('Data get successfully', currency_list, True, 200)
	else:
		return response('No Currency found', currency_list, True, 200)

@frappe.whitelist()
def get_employee_list(start=0, page_length=20, employee_name=None):
	'''
		API to get List of Employee
	'''
	employee_fields = ['name as employee_id', 'employee_name']
	if employee_name:
		employee_list = frappe.db.get_all('Employee', filters={ 'employee_name':['like', '%{0}%'.format(employee_name)], 'status':'Active' }, fields=employee_fields, start=start, page_length=page_length)
	else:
		employee_list = frappe.db.get_all('Employee', filters={ 'status':'Active' }, fields=employee_fields, start=start, page_length=page_length)
	if employee_list:
		return response('Data get successfully', employee_list, True, 200)
	else:
		return response('No Employees found', employee_list, True, 200)

@frappe.whitelist()
def create_release_order():
	'''
		API to create Release Order
		args:
			JSON string of RO data like
			{
				"ror_no": "M1/0142/2024-25",
				"ror_date": "2024-06-01",
				"ro_no": "766",
				"ro_date": "2024-05-31",
				"client_id": "Dias Idea Incubators",
				"agency_id": "efeone",
				"currency": "INR",
				"bill_to": "A",
				"option": "Associate Sponsorship",
				"product_name": "P M S College",
				"program_name": "News At 9",
				"no_of_eps": 0,
				"commission_per": 15,
				"fct_total": 50,
				"amount": 50000,
				"region": "Trivandrum",
				"executive_id": "HR-EMP-00012",
				"region_revenue_percentage": 100
			}
	'''
	try:
		input_data = frappe.form_dict
		if input_data.get('cmd'):
			input_data.pop('cmd')

		albatross_service_item = frappe.db.get_single_value('Albatross Settings', 'albatross_service_item')
		if not albatross_service_item:
			return response('`albatross_service_item` is not configured in Albatross Settings', {}, False, 400)

		if not input_data.get('bill_to'):
			return response('`bill_to` is reuqired to create Release Order', {}, False, 400)
		else:
			if not input_data.get('bill_to') in ['A', 'C']:
				return response('`bill_to` should be either `A` or `C`', {}, False, 400)

		# Checking Mandatory fields
		if not input_data.get('client_id'):
			return response('`client_id` is reuqired to create Release Order', {}, False, 400)
		else:
			if not frappe.db.exists('Customer', input_data.get('client_id')):
				return response('Client : `{0}` does not exists'.format(input_data.get('client_id')), {}, False, 404)

		if input_data.get('bill_to') == 'A':
			if not input_data.get('agency_id'):
				return response('`agency_id` is reuqired to create Release Order', {}, False, 400)
			else:
				if not frappe.db.exists('Customer', input_data.get('agency_id')):
					return response('Agency : `{0}` does not exists'.format(input_data.get('agency_id')), {}, False, 404)

		if not input_data.get('ror_no'):
			return response('`ror_no` is reuqired to create Release Order', {}, False, 400)

		if not input_data.get('ror_date'):
			return response('`ror_date` is reuqired to create Release Order', {}, False, 400)

		if not input_data.get('ro_date'):
			return response('`ror_date` is reuqired to create Release Order', {}, False, 400)

		if not input_data.get('option'):
			return response('`option` is reuqired to create Release Order', {}, False, 400)

		if input_data.get('executive_id') and not frappe.db.exists('Employee', input_data.get('executive_id')):
			return response('Employee : `{0}` does not exists'.format(input_data.get('executive_id')), {}, False, 400)

		if not input_data.get('region_revenue_percentage'):
			return response('`region_revenue_percentage` is reuqired to create Release Order', {}, False, 400)

		if input_data.get('region') and not frappe.db.exists('Region', input_data.get('region')):
			return response('Region : `{0}` does not exists'.format(input_data.get('region')), {}, False, 400)

		if input_data.get('currency') and not frappe.db.exists('Currency', input_data.get('currency')):
			return response('Currency : `{0}` does not exists'.format(input_data.get('currency')), {}, False, 400)

		# Creating Release Order
		ro_doc = frappe.new_doc('Quotation')
		ro_doc.transaction_date = getdate(input_data.get('ror_date'))
		ro_doc.quotation_to = 'Customer'
		if input_data.get('bill_to') == 'A':
			ro_doc.party_name = input_data.get('agency_id')
			ro_doc.actual_customer = input_data.get('client_id')
		elif input_data.get('bill_to') == 'C':
			ro_doc.party_name = input_data.get('client_id')
		ro_doc.region = input_data.get('region')
		ro_doc.executive = input_data.get('executive_id') or ''
		ro_doc.executive_name = input_data.get('executive_name') or ''
		ro_doc.albatross_ro_id = input_data.get('ror_no') or ''
		ro_doc.ro_no = input_data.get('ro_no') or ''
		ro_doc.ro_date = getdate(input_data.get('ro_date'))
		ro_doc.product_name = input_data.get('product_name') or ''
		ro_doc.program_name = input_data.get('program_name') or ''
		ro_doc.ro_option = input_data.get('option') or ''
		ro_doc.no_of_eps = input_data.get('no_of_eps') or 0
		ro_doc.commission_per = input_data.get('commission_per') or 0
		ro_doc.fct_total = input_data.get('fct_total') or 0
		ro_doc.region_revenue_percentage = input_data.get('region_revenue_percentage') or 0
		ro_item_row = ro_doc.append('items')
		ro_item_row.qty = 1
		ro_item_row.item_code = albatross_service_item
		ro_item_row.rate = float(input_data.get('amount') or 0)
		ro_item_row.base_rate = float(input_data.get('amount') or 0)
		ro_doc.ignore_mandatory = True
		ro_doc.save(ignore_permissions=True)
		frappe.clear_messages()
		return response('Created Release Order Successfully', ro_doc.as_dict(), True, 201)

	except frappe.exceptions.CharacterLengthExceededError as e:
		frappe.log_error("Character Length Exceeded", "Error in Release Order creation: " + str(e)[:120])
		return response('Character Length Exceeded in Error Log', {}, False, 400)

	except Exception as exception:
		frappe.log_error(frappe.get_traceback(), "Release Order Creation Error")
		clean_exception_message = strip_html_tags(str(exception))
		return response(f"An error occurred: {clean_exception_message}", {}, False, 400)

@frappe.whitelist()
def create_sales_order():
	'''
		API to create Sales Order
		args:
			JSON string of Sales Order data like
			{
				"date": "30-10-2024",
				"invoice_no": "LB/138",
				"client_id": "Dias Idea Incubators",
				"currency": "INR",
				"executive_id": "HR-EMP-00012",
				"taxable_value": 170000,
				"gst_rate": 18,
				"sgst": 15300,
				"cgst": 15300,
				"igst": 0,
				"ro_no": "CCPL/32/2024-25",
				"ref_no": "M1/0139/2024-25",
				"region": "Trivandrum"
			}
	'''
	try:
		input_data = frappe.form_dict
		if input_data.get('cmd'):
			input_data.pop('cmd')

		albatross_service_item = frappe.db.get_single_value('Albatross Settings', 'albatross_service_item')
		if not albatross_service_item:
			return response('`albatross_service_item` is not configured in Albatross Settings', {}, False, 400)

		# Checking Mandatory fields
		if not input_data.get('date'):
			return response('`date` is reuqired to create Release Order', {}, False, 400)

		if not input_data.get('client_id'):
			return response('`client_id` is reuqired to create Release Order', {}, False, 400)
		else:
			if not frappe.db.exists('Customer', input_data.get('client_id')):
				return response('Client : `{0}` does not exists'.format(input_data.get('client_id')), {}, False, 404)

		if not input_data.get('taxable_value'):
			return response('`taxable_value` is reuqired to create Release Order', {}, False, 400)

		if input_data.get('currency') and not frappe.db.exists('Currency', input_data.get('currency')):
			return response('Currency : `{0}` does not exists'.format(input_data.get('currency')), {}, False, 400)

		if input_data.get('region') and not frappe.db.exists('Region', input_data.get('region')):
			return response('Region : `{0}` does not exists'.format(input_data.get('region')), {}, False, 400)

		sales_taxes_and_charges_template = None
		tax_category = None
		if input_data.get('gst_rate'):
			if input_data.get('igst_rate'):
				tax_category_field_name = 'out_state_tax_category'
			else:
				tax_category_field_name = 'in_state_tax_category'
			tax_category = frappe.db.get_single_value('Albatross Settings', tax_category_field_name)
			tax_rate = float(input_data.get('gst_rate'))
			sales_taxes_and_charges_template = get_sales_taxes_and_charges_template(tax_rate, tax_category)

		# Creating Sales Order
		ro_doc = frappe.new_doc('Sales Order')
		ro_doc.transaction_date = getdate(input_data.get('date'))
		ro_doc.delivery_date = getdate(input_data.get('date'))
		ro_doc.customer = input_data.get('client_id')
		ro_doc.region = input_data.get('region')
		ro_doc.executive = input_data.get('executive_id') or ''
		ro_doc.reference_id = get_quotation_from_ro_id(input_data.get('ref_no')) or ''
		ro_item_row = ro_doc.append('items')
		ro_item_row.qty = 1
		ro_item_row.item_code = albatross_service_item
		ro_item_row.rate = float(input_data.get('taxable_value'))
		ro_item_row.base_rate = float(input_data.get('taxable_value'))
		if sales_taxes_and_charges_template:
			ro_doc.taxes_and_charges = sales_taxes_and_charges_template
		else:
			ro_doc.taxes_and_charges = ''
		if tax_category:
			ro_doc.tax_category = tax_category
		else:
			ro_doc.tax_category = ''
		ro_doc.ignore_mandatory = True
		ro_doc.save(ignore_permissions=True)
		frappe.clear_messages()
		return response('Created Sales Order Successfully', ro_doc.as_dict(), True, 201)

	except frappe.exceptions.CharacterLengthExceededError as e:
		frappe.log_error("Character Length Exceeded", "Error in Release Order creation: " + str(e)[:120])
		return response('Character Length Exceeded in Error Log', {}, False, 400)

	except Exception as exception:
		frappe.log_error(frappe.get_traceback(), "Release Order Creation Error")
		clean_exception_message = strip_html_tags(str(exception))
		return response(f"An error occurred: {clean_exception_message}", {}, False, 400)

@frappe.whitelist()
def get_quotation_from_ro_id(albatross_ro_id):
	'''
		Method to get Quotation using albatross_ro_id
	'''
	quotation = None
	if frappe.db.exists('Quotation', { 'albatross_ro_id':albatross_ro_id }):
		quotation = frappe.db.get_value('Quotation', { 'albatross_ro_id':albatross_ro_id })
	return quotation
