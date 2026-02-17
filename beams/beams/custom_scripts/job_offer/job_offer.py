import frappe
import json
from frappe import _
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
						"salutation": "salutation",
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
				"salutation": applicant_data.get("salutation"),
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


def validate_ctc(doc, method=None):
	"""
	Validate that the CTC value is not negative.
	Calculate totals for salary and other contribution details.
	Ensure CTC matches Total CTC per month.
	"""
	if not doc.salutation and doc.job_applicant:
		doc.salutation = frappe.db.get_value("Job Applicant", doc.job_applicant, "salutation")

	if doc.ctc and frappe.utils.flt(doc.ctc) < 0:
		frappe.throw("CTC cannot be a Negative Value")

	doc.gross_monthly_salary = sum(frappe.utils.flt(d.amount) for d in doc.get("salary_details") or [])
	other_contribution = sum(frappe.utils.flt(d.amount) for d in doc.get("other_contribution_details") or [])
	doc.total_ctc_per_month = doc.gross_monthly_salary + other_contribution

	if not doc.ctc or frappe.utils.flt(doc.ctc) == 0:
		doc.ctc = doc.total_ctc_per_month

	# Validation logic strictly enforce only on submission.
	if doc.docstatus == 1:
		if not doc.get("salary_details") and not doc.get("other_contribution_details"):
			frappe.throw(_("Please add Salary Details or Other Contribution Details before submitting."))

		ctc_diff = abs(frappe.utils.flt(doc.ctc) - frappe.utils.flt(doc.total_ctc_per_month))
		if ctc_diff > 0.01:
			currency = getattr(doc, "currency", None)
			if not currency and doc.company:
				currency = frappe.get_cached_value('Company', doc.company, 'default_currency')

			msg = _("Total CTC per month ({0}) does not match CTC ({1})").format(
				frappe.utils.fmt_money(doc.total_ctc_per_month, currency=currency),
				frappe.utils.fmt_money(doc.ctc, currency=currency)
			)
			frappe.throw(msg)
