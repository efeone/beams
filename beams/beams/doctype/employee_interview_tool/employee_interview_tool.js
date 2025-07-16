// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Interview Tool', {
    refresh: function (frm) {
        // Button to fetch applicants
        frm.add_custom_button('Get Job Applicants', function () {
            const filters = {};

            if (frm.doc.job_opening) {
                filters.job_title = frm.doc.job_opening;
            }
            if (frm.doc.department) {
                filters.department = frm.doc.department;
            }
            if (frm.doc.designation) {
                filters.designation = frm.doc.designation;
            }

            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Job Applicant',
                    fields: ['name', 'applicant_name', 'designation', 'status'],
                    filters: filters,
                    limit_page_length: 50
                },
                callback: function (r) {
                    if (!r.exc) {
                        frm.clear_table('job_applicants');
                        (r.message || []).forEach(function (app) {
                            let row = frm.add_child('job_applicants');
                            row.job_applicant = app.name;
                            row.applicant_name = app.applicant_name;
                            row.status = app.status;
                            row.designation = app.designation;
                        });
                        frm.refresh_field('job_applicants');
                    }
                }
            });
        });

        // Show "Create Interview" only if form is not dirty
        if (!frm.is_dirty() && frm.doc.docstatus === 0) {
            frm.add_custom_button('Create Interview', function () {
                let selected_rows = frm.fields_dict.job_applicants.grid.get_selected_children();

                if (!selected_rows.length) {
                    frappe.msgprint(__('Please select one or more rows in the Job Applicants table.'));
                    return;
                }

                frappe.call({
                    method: 'beams.beams.doctype.employee_interview_tool.employee_interview_tool.create_bulk_interviews',
                    args: {
                        applicants: selected_rows.map(row => ({
                            job_applicant: row.job_applicant,
                            applicant_name: row.applicant_name,
                            designation: row.designation,
                            interview_round: frm.doc.interview_round,
                            scheduled_on: frm.doc.scheduled_on,
                            from_time: frm.doc.from_time,
                            to_time: frm.doc.to_time
                        }))
                    },
                    callback: function (r) {
                        if (!r.exc) {
                            const data = r.message || {};
                            let any_message = false;
                            // Show success if interviews were created
                            if (Array.isArray(data.created) && data.created.length > 0) {
                                const created_ids = data.created.map(c => c.job_applicant).join(', ');
                                frappe.msgprint(__('Interviews created successfully for: ') + created_ids);
                            }
                            // Show warning if some were skipped
                            if (Array.isArray(data.skipped_applicants) && data.skipped_applicants.length > 0) {
                                frappe.msgprint({
                                    title: __('Note'),
                                    message: __('Interviews already exist for the following applicants: ') + data.skipped_applicants.join(', '),
                                    indicator: 'orange'
                                });
                            }
                        }
                    }
                });
            });
        }
    }
});
