import frappe

fields_to_remove = [
	{
		'dt':'Customer',
		'fieldname':'albatross_customer_id'
	},
	{
		'dt':'Job Opening',
		'fieldname':'expected_compensation'
	},
	{
		'dt':'Job Opening',
		'fieldname':'job_requisition'
	},
	{
		'dt':'Job Opening',
		'fieldname':'no_of_positions'
	},
	{
		'dt':'Job Opening',
		'fieldname':'location'
	},
	{
		'dt':'Job Opening',
		'fieldname':'skill_proficiency_description'
	},
	{
		'dt':'Job Opening',
		'fieldname':'skill_proficiency_break'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'applicant_interview_round'
	},
	{
		'dt':'Interview Round',
		'fieldname':'expected_question_set'
	},
	{
		'dt':'Quotation',
		'fieldname':'executive_name_'
	},
	{
		'dt':'Quotation',
		'fieldname':'albatross_invoice_number'
	},
	{
		'dt':'Quotation',
		'fieldname':'albatross_ref_number'
	},
	{
		'dt':'Quotation',
		'fieldname':'client_name'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'current_mobile_no'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'permananet_email_id'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'email_id_1'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'willing_to_work_on_location'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'employee_code'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'first_salary_drawn'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'last_salary_drawn'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'telephone_no'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'permanent_address'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'current_address'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'current_residence_no'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'permanent_period_from'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'permanent_period_to'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'permanent_residence_no'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'current_period_from'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'current_period_to'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'current_designation'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'current_department'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'manager_name'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'manager_contact_no'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'manager_email'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'employment_period_from'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'employment_period_to'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'reference_taken'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'was_this_position'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'duties_and_reponsibilities'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'reason_for_leaving'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'address_of_employer'
	},
	{
		'dt':'Job Applicant',
		'fieldname':'telephone_number'
	},
	{
		'dt':'Interview',
		'fieldname':'final_score'
	},
	{
		'dt':'Job Applicant',
		'fieldname': 'department'
	},
	{
		'dt':'Employee',
		'fieldname': 'emergency_contact_name'
	},
	{
		'dt':'Employee',
		'fieldname': 'emergency_phone'
	},
	{
		'dt':'Employee',
		'fieldname': 'relation_emergency'
	},
	{
		'dt':'Employee',
		'fieldname': 'physical_disabilities'
	},
	{
		'dt':'Employee',
		'fieldname': 'disabilities'
	},
	{
		'dt':'Employee',
		'fieldname': 'marital_indebtness'
	},
	{
		'dt':'Employee',
		'fieldname': 'court_proceedings'
	},
	{
		'dt':'Employee',
		'fieldname': 'are_you_willing_to_travel'
	},
	{
		'dt':'Employee',
		'fieldname': 'places_to_travel'
	},
	{
		'dt':'Employee',
		'fieldname': 'are_you_related_to_employee'
	},
	{
		'dt':'Employee Advance',
		'fieldname': 'purpose'
	},
	{
		'dt':'HD Settings',
		'fieldname': 'escalation_notifications_templates'
	},
	{
		'dt':'Department',
		'fieldname': 'finance_group'
	},
	{
		'dt':'Budget',
		'fieldname': 'finance_group'
	},
	{
		'dt':'Budget',
		'fieldname': 'rejection_feedback'
	},
	{
		'dt':'Budget',
		'fieldname': 'budget_accounts_custom'
	},
	{
		'dt':'Budget',
		'fieldname': 'budget_accounts_hr'
	},
	{
		'dt':'Budget Account',
		'fieldname': 'cost_head'
	},
	{
		'dt':'Budget Account',
		'fieldname': 'cost_subhead'
	},
	{
		'dt':'Budget Account',
		'fieldname': 'cost_category'
	},
	{
		'dt':'Budget Account',
		'fieldname': 'column_break_cd'
	},
	{
		'dt':'Budget Account',
		'fieldname': 'cost_description'
	},
	{
		'dt':'Budget Account',
		'fieldname': 'equal_monthly_distribution'
	},
	{
		'dt':'Expense Claim',
		'fieldname': 'budget_exceeded'
	},
	{
		'dt':'Journal Entry',
		'fieldname': 'budget_exceeded'
	},
	{
		'dt':'Material Request',
		'fieldname': 'budget_exceeded'
	},
	{
		'dt':'Purchase Invoice',
		'fieldname': 'budget_exceeded'
	},
	{
		'dt':'Purchase Order',
		'fieldname': 'is_budget_exceed'
	},
	{
		'dt':'Budget',
		'fieldname': 'column_break_ab'
	}
]

def execute():
	for field in fields_to_remove:
		if frappe.db.exists('Custom Field', field):
			frappe.db.delete('Custom Field', field)
	frappe.db.commit()
