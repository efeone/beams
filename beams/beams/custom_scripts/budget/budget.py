import frappe

month_fields = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

def beams_budget_validate(doc, method=None):
	'''
		Method trigger on `validate` event of Budget
	'''
	update_budget_against(doc, method)
	update_total_amount(doc, method)
	convert_currency(doc, method)

def update_total_amount(doc, method):
	total = sum([row.budget_amount for row in doc.get('budget_accounts') if row.budget_amount])
	doc.total_amount = total

def populate_og_accounts(doc, method=None):
	'''
		Method trigger on `before_validate` event of Budget
		Populate OPEX budget accounts in the main table for better reporting and to avoid issues with child table data retrieval in case of large number of rows
	'''
	doc.accounts = []
	accounts_map = {}

	#Process OPEX budget accounts
	for row in doc.budget_accounts:
		#Set Company Currency in each row for reference during currency conversion in case company currency is not INR
		if doc.company_currency:
			row.company_currency = doc.company_currency

		# Accumulate amounts per account
		account = row.account
		# Initialize account if not exists
		if account not in accounts_map:
			accounts_map[account] = {
				'account': account,
				'budget_amount': 0
			}
			# Initialize all months
			for month in month_fields:
				accounts_map[account][month] = 0
		# Add monthly values
		for month in month_fields:
			month_value = row.get(month) or 0
			accounts_map[account][month] += month_value
			accounts_map[account]['budget_amount'] += month_value

	#Update accumulated amounts for each account in main table
	for account_data in accounts_map.values():
		doc.append('accounts', account_data)

def convert_currency(doc, method):
	'''
		Convert budget amounts for non-INR companies
	'''
	company_currency = frappe.db.get_value('Company', doc.company, 'default_currency')
	exchange_rate = 1

	if company_currency != 'INR':
		exchange_rate = frappe.db.get_value('Company', doc.company, 'exchange_rate_to_inr')
		if not exchange_rate:
			frappe.throw(
				f'Please set Exchange Rate from <b>{company_currency}</b> to <b>INR</b> for <b>{doc.company}</b>',
				title='Message',
			)

	months = [
		'january', 'february', 'march', 'april', 'may', 'june',
		'july', 'august', 'september', 'october', 'november', 'december'
	]

	def apply_conversion(row):
		'''
			Apply exchange rate conversion to a budget row
		'''
		row.budget_amount_inr = row.budget_amount * exchange_rate
		for month in months:
			setattr(row, f'{month}_inr', (getattr(row, month, 0) or 0) * exchange_rate)

	for row in (*doc.accounts, *doc.budget_accounts):
		apply_conversion(row)


def update_budget_against(doc, method=None):
	'''
		Set budget_against field based on budget_for selection
	'''
	if doc.budget_for:
		doc.budget_against = doc.budget_for
