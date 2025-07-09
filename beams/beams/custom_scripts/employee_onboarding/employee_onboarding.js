frappe.ui.form.on('Employee Onboarding', {
    refresh: function(frm) {
        // Check if CPAL already exists for the employee
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: 'Company Policy Acceptance Log',
                filters: {
                    'employee': frm.doc.employee
                },
                fields: ['name']
            },
            callback: function(response) {
                // If CPAL exists, move the button under the 'View' button group
                if (response.message && response.message.length > 0) {
                    frm.add_custom_button(__('Company Policy Acceptance Log'), function () {
                        frappe.set_route('Form', 'Company Policy Acceptance Log', response.message[0].name);
                    }, __('View'));
                } else if (frm.doc.docstatus === 1) {
                    // Only proceed with CPAL button creation if the document is submitted and no CPAL exists
                    frm.add_custom_button(__('Company Policy Acceptance Log'), function () {
                        frappe.call({
                            method: "beams.beams.custom_scripts.employee_onboarding.employee_onboarding.create_cpal",
                            args: {
                                source_name: frm.doc.name  // Ensure source_name is passed correctly
                            },
                            callback: function(response) {
                                if (response.message) {
                                    // Route to CPAL document form
                                    frappe.set_route('Form', 'Company Policy Acceptance Log', response.message);
                                }
                            },
                        });
                    }, __('Create'));
                }
            }
        });

        frappe.call({
            method: "beams.beams.custom_scripts.employee_onboarding.employee_onboarding.get_excluded_job_applicants",
            callback: function (r) {
                if (r.message) {
                    let excluded_applicants = r.message;

                    frm.set_query("job_applicant", function () {
                        let filters = {
                            name: ["not in", excluded_applicants]
                        };
                        if (frm.doc.designation) {
                            filters["designation"] = frm.doc.designation;
                        }
                        if (frm.doc.department) {
                            filters["department"] = frm.doc.department;
                        }

                        return { filters };
                    });
                }
            }
        });
        apply_template_filter(frm);
    },

    employee: function(frm) {
        // If employee is selected, fetch employee details
        if (frm.doc.employee) {
            frappe.call({
                method: 'beams.beams.custom_scripts.employee_onboarding.employee_onboarding.get_employee_details',
                args: {
                    employee_id: frm.doc.employee
                },
                callback: function(response) {
                    if (response.message) {
                        let employee = response.message;
                        // Set the fetched values in the Employee Onboarding form
                        frm.set_value('department', employee.department);
                        frm.set_value('designation', employee.designation);
                        frm.set_value('date_of_joining', employee.date_of_joining);
                        frm.set_value('holiday_list', employee.holiday_list);
                        frm.set_value('employee_grade', employee.employee_grade);
                        frm.refresh_fields();
                    }
                }
            });
        }
    },

    job_applicant: function(frm) {
        if (frm.doc.job_applicant) {
            frappe.db.get_value('Job Offer', { 'job_applicant': frm.doc.job_applicant }, 'name', function(value) {
                if (value) {
                    // If the value is returned, set the job_offer field with the name of the job offer
                    frm.set_value('job_offer', value.name);
                    frm.refresh_fields();
                }
            });
        }
    },
    department: function(frm) {
        apply_template_filter(frm);
    },

    designation: function(frm) {
        apply_template_filter(frm);
    },
});


function apply_template_filter(frm) {
    /**
    * Applies a dynamic filter to the "employee_onboarding_template" field,
    * showing only templates that match the current department and designation.
    */
    if (frm.doc.department && frm.doc.designation) {
        frm.set_query("employee_onboarding_template", function () {
            return {
                filters: {
                    department: frm.doc.department,
                    designation: frm.doc.designation
                }
            };
        });
    }
}


