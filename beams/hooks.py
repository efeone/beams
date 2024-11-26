app_name = "beams"
app_title = "BEAMS"
app_publisher = "efeone"
app_description = "BEAMS (Broadcast Enterprise Administration Management System)"
app_email = "info@efeone.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/beams/css/beams.css"
# app_include_js = "/assets/beams/js/beams.js"

# include js, css files in header of web template
# web_include_css = "/assets/beams/css/beams.css"
# web_include_js = "/assets/beams/js/beams.js"

# website_generators = ["Job Application"]

# website_route_rules = [
#     {"from_route": "/job_application/new", "to_route": "job_application"}
# ]


# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "beams/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Sales Invoice": "beams/custom_scripts/sales_invoice/sales_invoice.js",
    "Quotation": "beams/custom_scripts/quotation/quotation.js",
    "Purchase Invoice": "beams/custom_scripts/purchase_invoice/purchase_invoice.js",
    "Driver":"beams/custom_scripts/driver/driver.js",
    "Sales Order": "beams/custom_scripts/sales_order/sales_order.js",
    "Voucher Entry": "beams/custom_scripts/voucher_entry/voucher_entry.js",
    "Contract":"beams/custom_scripts/contract/contract.js",
    "Department":"beams/custom_scripts/department/department.js",
    "Job Requisition":"beams/custom_scripts/job_requisition/job_requisition.js",
    "Job Applicant" :"beams/custom_scripts/job_applicant/job_applicant.js",
    "Budget":"beams/custom_scripts/budget/budget.js",
    "Interview Feedback":"beams/custom_scripts/interview_feedback/interview_feedback.js",
    "Interview":"beams/custom_scripts/interview/interview.js",
    "Employee":"beams/custom_scripts/employee/employee.js",
    "Event":"beams/custom_scripts/event/event.js",
    "Training Event":"beams/custom_scripts/training_event/training_event.js",
    "Employee Onboarding":"beams/custom_scripts/employee_onboarding/employee_onboarding.js",
    "Leave Application":"beams/custom_scripts/leave_application/leave_application.js"

}
doctype_list_js = {
    "Sales Invoice" : "beams/custom_scripts/sales_invoice/sales_invoice_list.js",
    "Purchase Invoice":"beams/custom_scripts/purchase_invoice/purchase_invoice_list.js",
    "Job Applicant":"beams/custom_scripts/job_applicant/job_applicant_list.js"
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "beams/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "beams.utils.jinja_methods",
# 	"filters": "beams.utils.jinja_filters"
# }

# Installation
# ------------

after_install = "beams.setup.after_install"
after_migrate = "beams.setup.after_migrate"

# Uninstallation
# ------------

before_uninstall = "beams.setup.before_uninstall"
# after_uninstall = "beams.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "beams.utils.before_app_install"
# after_app_install = "beams.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "beams.utils.before_app_uninstall"
# after_app_uninstall = "beams.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "beams.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Job Applicant": "beams.beams.custom_scripts.job_applicant.job_applicant.get_permission_query_conditions",
}

# has_permission = {
#
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Attendance Request": "beams.beams.custom_scripts.attendance_request.attendance_request.AttendanceRequestOverride",
    "Shift Type": "beams.beams.custom_scripts.shift_type.shift_type.ShiftTypeOverride"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Invoice": {
        "on_update_after_submit":"beams.beams.custom_scripts.sales_invoice.sales_invoice.on_update_after_submit",
        "autoname": "beams.beams.custom_scripts.sales_invoice.sales_invoice.autoname",
        "validate": "beams.beams.custom_scripts.sales_invoice.sales_invoice.validate_sales_invoice_for_barter"
    },
    "Quotation": {
        "validate": "beams.beams.custom_scripts.quotation.quotation.validate_is_barter",
        "on_submit": "beams.beams.custom_scripts.quotation.quotation.create_tasks_for_production_items",
        "autoname": "beams.beams.custom_scripts.quotation.quotation.autoname"
    },
    "Purchase Invoice": {
        "before_save": "beams.beams.custom_scripts.purchase_invoice.purchase_invoice.before_save"
    },
    "Account": {
        "after_insert": "beams.beams.custom_scripts.account.account.create_todo_on_creation_for_account"
    },
    "Customer": {
        "after_insert": "beams.beams.custom_scripts.account.account.create_todo_on_creation_for_customer"
    },
    "Training Event": {
         "on_update": "beams.beams.custom_scripts.training_event.training_event.on_update",
          "on_update_after_submit": "beams.beams.custom_scripts.training_event.training_event.on_update",
          "on_cancel": "beams.beams.custom_scripts.training_event.training_event.on_cancel"
    },
    "Supplier": {
        "after_insert": "beams.beams.custom_scripts.account.account.create_todo_on_creation_for_supplier"
    },
    "Purchase Order": {
        "on_update": "beams.beams.custom_scripts.purchase_order.purchase_order.create_todo_on_finance_verification",
        "after_insert": "beams.beams.custom_scripts.purchase_order.purchase_order.create_todo_on_purchase_order_creation",
        "before_save": "beams.beams.custom_scripts.purchase_order.purchase_order.validate_budget",
        "validate": "beams.beams.custom_scripts.purchase_order.purchase_order.fetch_department_from_cost_center"
    },
    "Material Request":{
        "before_save":"beams.beams.custom_scripts.purchase_order.purchase_order.validate_budget",
        "validate":"beams.beams.custom_scripts.purchase_order.purchase_order.fetch_department_from_cost_center"
    },
    "Sales Order": {
        "autoname": "beams.beams.custom_scripts.sales_order.sales_order.autoname",
        "before_save": "beams.beams.custom_scripts.sales_order.sales_order.validate_sales_order_amount_with_quotation",
        "before_insert": "beams.beams.custom_scripts.sales_order.sales_order.set_region_from_quotation"
    },
    "Contract": {
        "on_update": "beams.beams.custom_scripts.contract.contract.create_todo_on_contract_verified_by_finance",
        "after_insert": "beams.beams.custom_scripts.contract.contract.create_todo_on_contract_creation",
        "on_submit":"beams.beams.custom_scripts.contract.contract.on_submit"
    },
    "Batta Claim": {
        "onchange": "beams.beams.doctype.batta_claim.batta_claim.calculate_batta_allowance",
        "onchange": "beams.beams.doctype.batta_claim.batta_claim.calculate_batta"
    },
    "Job Requisition": {
        "on_update": [
            "beams.beams.custom_scripts.job_requisition.job_requisition.create_job_opening_from_job_requisition",
            "beams.beams.custom_scripts.job_requisition.job_requisition.on_update"
        ]
    },
    "Journal Entry": {
        "on_cancel": "beams.beams.custom_scripts.journal_entry.journal_entry.on_cancel"
    },
    "Job Applicant": {
        "validate": [
            "beams.beams.custom_scripts.job_applicant.job_applicant.validate",
            "beams.beams.custom_scripts.job_applicant.job_applicant.validate_unique_application"
            ],
        "after_insert":"beams.beams.custom_scripts.job_applicant.job_applicant.set_interview_rounds"
    },
    "Department": {
       "validate": "beams.beams.custom_scripts.department.department.validate"
    },
    "Interview": {
        "on_submit": "beams.beams.custom_scripts.interview.interview.mark_interview_completed",
        "after_insert": "beams.beams.custom_scripts.interview.interview.on_interview_creation",
        "on_update": "beams.beams.custom_scripts.interview.interview.update_applicant_interview_round"
    },
    "Interview Feedback": {
        "after_insert": "beams.beams.custom_scripts.interview_feedback.interview_feedback.after_insert",
        "validate": "beams.beams.custom_scripts.interview_feedback.interview_feedback.validate"
    },
    "Employee Checkin":{
        "after_insert":"beams.beams.custom_scripts.employee_checkin.employee_checkin.handle_employee_checkin_out"
    },
    "Leave Allocation":{
        "on_submit":"beams.beams.custom_scripts.leave_allocation.leave_allocation.create_new_compensatory_leave_log",
        "on_update_after_submit":"beams.beams.custom_scripts.leave_allocation.leave_allocation.create_new_log_on_update"

    },
    "Leave Application" : {
        "validate":[
            "beams.beams.custom_scripts.leave_application.leave_application.validate_leave_type",
            "beams.beams.custom_scripts.leave_application.leave_application.validate_leave_application"
         ]
    }
}


# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": [
        "beams.beams.doctype.local_enquiry_report.local_enquiry_report.set_status_to_overdue",
        "beams.beams.custom_scripts.attendance.attendance.send_absence_reminder",
        "beams.beams.custom_scripts.attendance.attendance.send_absent_reminder"
    ],
# 	"all": [
# 		"beams.tasks.all"
# 	],
# 	"daily": [
# 		"beams.tasks.daily"
# 	],
# 	"hourly": [
# 		"beams.tasks.hourly"
# 	],
# 	"weekly": [
# 		"beams.tasks.weekly"
# 	],
# 	"monthly": [
# 		"beams.tasks.monthly"
# 	],
  }

# Testing
# -------

# before_tests = "beams.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "beams.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
	'Item': 'beams.beams.custom_scripts.item_dashboard.item_dashboard.get_data',
    'Customer': 'beams.beams.custom_scripts.customer_dashboard.customer_dashboard.get_data',
    'Sales Invoice': 'beams.beams.custom_scripts.sales_invoice_dashboard.sales_invoice_dashboard.get_data',
    'Sales Order': 'beams.beams.custom_scripts.sales_order_dashboard.sales_order_dashboard.get_data',
    'Employee':'beams.beams.custom_scripts.employee_dashboard.employee_dashboard.get_data',
    'Job Applicant': 'beams.beams.custom_scripts.job_applicant.job_applicant_dashboard.get_data'
}

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["beams.utils.before_request"]
# after_request = ["beams.utils.after_request"]

# Job Events
# ----------
# before_job = ["beams.utils.before_job"]
# after_job = ["beams.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"beams.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
fixtures = [
    {"dt": "Workflow", "filters": [
        ["name", "in", ["Customer Approval", "Account Approval", "Adhoc Budget","Supplier Approval", "Purchase Order Approval" , "Budget Approval" , "Batta Claim Approval","Purchase Invoice Workflow","Sales Invoice Approval","Stringer Bill Approval","Material Request Approval","Substitute Booking","Contract","Job Requisition Workflow","Enquiry Workflow","Job Proposal Workflow"]]
    ]},
    {"dt": "Workflow State", "filters": [
        ["name", "in", ["Draft", "Pending Approval", "Approved", "Rejected", "Pending Finance Verification", "Verified By Finance","Rejected By Finance", "Pending Finance Approval", "Approved by Finance","Submitted","Cancelled","Completed","On Hold","Assigned to Enquiry Officer","Assigned to Admin","Enquiry on Progress","Applicant Accepted","Applicant Rejected"]]
    ]},
    {"dt": "Workflow Action Master", "filters": [
        ["name", "in", ["Submit for Approval","Reopen", "Approve", "Reject", "Send For Finance Verification", "Verify", "Send for Approval","Submit","Cancel","Send Email To Party","Put On Hold","Assign to Admin","Assign to Enquiry Officer","Start Enquiry","Enquiry Completed","Accept"]]
    ]}
]
