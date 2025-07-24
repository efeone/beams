from frappe import _

def get_data(data=None):
    return {
        "fieldname": "job_applicant",  
        "non_standard_fieldnames": {
            "Compensation Proposal": "job_applicant",  
            "Job Offer": "job_applicant",
            "Appointment Letter": "job_applicant",
            "Interview": "job_applicant",
            "Employee Onboarding": "job_applicant",
            "Employee": "job_applicant",
        },
        "transactions": [

            {
                "label": _("Job Process"),
                "items": ["Job Offer", "Appointment Letter", "Interview"],
            },
            {
                "label": _("Proposals"),
                "items": ["Compensation Proposal "],
            },
            {
                "label": _("Onboarding"),
                "items": ["Employee Onboarding", "Employee"],
            },
            
        ],
    }
