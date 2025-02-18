import frappe
from frappe.utils import fmt_money

def get_context(context):
	context.no_cache = 1
	# Get designation, location, and job_type from the request form data
	designation, location, employment_type = frappe.form_dict.get('designation'), frappe.form_dict.get('location'), frappe.form_dict.get('employment_type')

	conditions = ""
	has_filter = False

	# Check each filter value and add conditions to the list
	if designation:
		conditions += 'AND designation = "{0}"'.format(designation)
		has_filter = True
	if location:
		conditions +='AND preffered_location = "{0}"'.format(location)
		has_filter = True
	if employment_type:
		conditions +='AND employment_type = "{0}"'.format(employment_type)
		has_filter = True

	query = '''
		SELECT
			name,
			job_title,
			preffered_location as location,
			designation,
			employment_type,
			publish_applications_received,
			closes_on,
			publish_salary_range
		FROM
			`tabJob Opening`
		WHERE
			publish = 1 AND
			status = 'Open'
	'''
	if has_filter:
		query += conditions
	jobs = frappe.db.sql(query, as_dict=True)
	for job in jobs:
		job['no_of_applications'] = get_job_applicant_count(job.get('name'))
		job['salary_range'] = get_salary_range(job.get('name'))

	context.designations = get_job_designation()
	context.job_locations = get_job_locations()
	context.employment_types = get_employment_types()
	context.jobs = jobs
	context.designation = designation
	context.job_location = location
	context.employment_type = employment_type

	return {
		"context": context
	}

def get_job_designation():
	'''
		Method to get Designation specified in Job Opening
	'''
	query = '''
		SELECT
			DISTINCT designation
		FROM
			`tabJob Opening`
		WHERE
			designation IS NOT NULL AND designation != '';
	'''
	return frappe.db.sql(query, as_dict=True)

def get_job_locations():
	'''
		Method to get Locations specified in Job Opening
	'''
	query = '''
		SELECT
			DISTINCT preffered_location as location
		FROM
			`tabJob Opening`
		WHERE
			preffered_location IS NOT NULL AND preffered_location != '';
	'''
	return frappe.db.sql(query, as_dict=True)

def get_employment_types():
	'''
		Method to get Employement Types specified in Job Opening
	'''
	query = '''
		SELECT
			DISTINCT employment_type
		FROM
			`tabJob Opening`
		WHERE
			employment_type IS NOT NULL AND employment_type != '';
	'''
	return frappe.db.sql(query, as_dict=True)

def get_job_applicant_count(job_opening):
	'''
		Method to get total Job Applicant Counts on the selected Job Opening
	'''
	applicants = frappe.db.get_all('Job Applicant', { 'job_title':job_opening })
	return len(applicants)

def get_salary_range(job_opening):
	'''
		Method to get Salary Range for a Job Opening
	'''
	salary_range = ''
	if frappe.db.exists('Job Opening', job_opening):
		lower_range, upper_range = frappe.db.get_value('Job Opening', job_opening, ['lower_range', 'upper_range'])
		currency , salary_per = frappe.db.get_value('Job Opening', job_opening, ['currency', 'salary_per'])
		if currency:
			if lower_range and upper_range:
				salary_range = '{0} - {1}'.format(fmt_money(lower_range, 0, currency), fmt_money(upper_range, 0, currency))
			if lower_range:
				salary_range = '{0}'.format(fmt_money(lower_range, 0, currency))
			if upper_range:
				salary_range = '{0}'.format(fmt_money(upper_range, 0, currency))
			salary_range += ' /{0}'.format(salary_per)
	return salary_range
