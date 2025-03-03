frappe.ui.form.on('Job Requisition', {
    onload: function (frm) {
        if (!frm.doc.requested_by) {
            // Fetch the Employee linked to the current User
            frappe.db.get_value('Employee', { 'user_id': frappe.session.user }, 'name').then(r => {
                if (r && r.message) {
                    frm.set_value('requested_by', r.message.name);
                }
            });
        }
    },

    refresh: function (frm) {
        // To clear all custom buttons from the form
        frm.clear_custom_buttons();
        set_filters(frm);

        if (frm.doc.status === 'Cancelled') {
            const connections = frm.dashboard.links;
            if (connections['Job Opening']) {
                connections['Job Opening'].$link.find('.btn-new-doc').hide();
            }
        }

        if (frm.doc.workflow_state === 'Pending CEO Final Approval') {
            frm.set_df_property('designation', 'reqd', 1);
            frm.set_df_property('description', 'reqd', 1);
        }
    },

    request_for: function (frm) {
        if (frm.doc.request_for) {
            frm.set_value('employee_left', '');
            frm.set_df_property('employee_left', 'reqd', 0);

            if (frm.doc.request_for === 'Employee Exit') {
                frm.set_df_property('employee_left', 'reqd', 1);
            }
        }
    },

    job_description_template: function (frm) {
        // To fetch the Template Content from master
        if (frm.doc.job_description_template) {
            frappe.call({
                method: 'beams.beams.custom_scripts.job_requisition.job_requisition.get_template_content',
                args: {
                    template_name: frm.doc.job_description_template,
                    doc: frm.doc,
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value('description', r.message);
                    }
                },
            });
        }
    },

    setup: function (frm) {
        // Set Designation filter for Job Description Template
        frm.set_query('job_description_template', function () {
            return {
                filters: {
                    'designation': frm.doc.designation
                }
            };
        });
    },

    expected_by: function(frm) {
        if (frm.doc.expected_by) {
            let expected_date = frappe.datetime.str_to_obj(frm.doc.expected_by);
            let today = frappe.datetime.str_to_obj(frappe.datetime.get_today());

            if (expected_date < today) {
                frappe.msgprint(__('Expected By date must be a future date.'));
                frm.set_value("expected_by", "");  
            }
        }
    }
    

});
    
   

    
    
    
