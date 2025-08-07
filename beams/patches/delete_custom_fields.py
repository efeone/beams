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
	}
]

def execute():
	for field in fields_to_remove:
		if frappe.db.exists('Custom Field', field):
			frappe.db.delete('Custom Field', field)
	frappe.db.commit()
