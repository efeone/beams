import frappe
from frappe import _

@frappe.whitelist()
def create_feedback_criteria(doc, method=None):

	doc.rating_criteria = []

	for goal in doc.goals:
		# Fetch existing KRA records
		existing_kra = frappe.get_all(
			'KRA',
			filters={'title': goal.key_result_area},
			fields=['title', 'description']
		)

		if existing_kra:
			for kra in existing_kra:
				existing_criteria = frappe.get_all(
					'Employee Feedback Criteria',
					filters={'criteria': kra['title']},
					fields=['name']
				)

				if not existing_criteria:
					# Create a new Employee Feedback Criteria
					new_criteria = frappe.get_doc({
						'doctype': 'Employee Feedback Criteria',
						'criteria': kra['title']
					}).insert(ignore_permissions=True)

				else:
					new_criteria = frappe.get_doc('Employee Feedback Criteria', existing_criteria[0]['name'])

				# Add a new row to the rating_criteria child table
				doc.append('rating_criteria', {
					'criteria': new_criteria.name,
					'per_weightage': goal.per_weightage
				})

def validate_rating_criteria(doc, method=None):
	"""
	validate department and company rating criteria
	"""
	department_rating_total_weight = sum([row.per_weightage or 0 for row in doc.get("department_rating_criteria", [])])
	if department_rating_total_weight != 100:
		frappe.throw("Total weightage in department rating criteria must be 100%.")

	company_rating_total_weight = sum([row.per_weightage for row in doc.get("company_rating_criteria", [])])
	if company_rating_total_weight != 100:
		frappe.throw("Total weightage in Company rating criteria must be 100%.")
