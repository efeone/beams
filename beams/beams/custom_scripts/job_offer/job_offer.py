import frappe
import json
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_employee(source_name, target_doc=None):
	def set_missing_values(source, target):
		email, name = frappe.db.get_value(
			"Job Applicant", source.job_applicant, ["email_id", "applicant_name"]
		) or (None, None)
		if email:
			target.personal_email = email
		if name:
			target.first_name = name
	if target_doc:
		# If it's a string, try to parse it as JSON
		if isinstance(target_doc, str):
			try:
				target_doc = json.loads(target_doc)
			except json.JSONDecodeError:
				target_doc = {}
		# If it's not a dictionary, reset to empty dict
		elif not isinstance(target_doc, dict):
			target_doc = {}
	else:
		target_doc = {}

	try:
		doc = get_mapped_doc(
			"Job Offer",
			source_name,
			{
				"Job Offer": {
					"doctype": "Employee",
					"field_map": {
						"applicant_name": "employee_name",
						"offer_date": "scheduled_confirmation_date",
					},
				}
			},
			target_doc,
			set_missing_values,
		)
		job_offer = frappe.get_doc("Job Offer", source_name)

		if job_offer.job_applicant:
			appointment_date = frappe.db.get_value(
				'Appointment Letter',
				{'job_applicant':job_offer.job_applicant},
				'appointment_date'
			)
			if appointment_date:
				doc.date_of_appointment = appointment_date

		# Only proceed if Job Applicant exists
		if job_offer.job_applicant:
			applicant_data = frappe.get_doc("Job Applicant", job_offer.job_applicant)
			mapping = {
				"gender": applicant_data.get("gender"),
				"date_of_birth": applicant_data.get("date_of_birth"),
				"cell_number": applicant_data.get("phone_number"),
				"name_of_father": applicant_data.get("father_name"),
				"department": applicant_data.get("department"),
				"designation": applicant_data.get("designation"),
				"marital_status": applicant_data.get("marital_status"),
				"permanent_address": applicant_data.get("permanent_address"),
				"current_address": applicant_data.get("current_address")
			}
			# Update document with mapped fields
			for field, value in mapping.items():
				if value is not None:
					setattr(doc, field, value)
		return doc

	except Exception as e:
		frappe.log_error(message=f"Error in make_employee: {str(e)}")
		frappe.throw(f"An error occurred while creating employee: {str(e)}")


@frappe.whitelist()
def validate_ctc(doc,method):
		"""
		Validate that the  CTC value is not negative.
		"""
		if doc.ctc:
			if doc.ctc < 0:
				frappe.throw("CTC cannot be a Negative Value")