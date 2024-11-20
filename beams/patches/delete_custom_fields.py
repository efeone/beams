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
    }
]

def execute():
    for field in fields_to_remove:
        if frappe.db.exists('Custom Field', field):
            frappe.db.delete('Custom Field', field)
    frappe.db.commit()
