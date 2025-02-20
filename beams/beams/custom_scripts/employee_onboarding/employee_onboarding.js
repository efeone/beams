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

        // Fetch excluded job applicants and set filter for job_applicant field
        frappe.call({
            method: "beams.beams.custom_scripts.employee_onboarding.employee_onboarding.get_job_applicants_with_employee_and_onboarding",
            callback: function (r) {
                if (r.message) {
                    let excluded_applicants = r.message;
                    frm.fields_dict["job_applicant"].get_query = function () {
                        return {
                            filters: {
                                name: ["not in", " "]
                            }
                        };
                    };
                }
            }
        });
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
    }
});
