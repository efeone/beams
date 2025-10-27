frappe.ui.form.on('HD Ticket', {
    // Called when form is loaded
    onload(frm) {
        if (frm.is_new() && !frm.doc.requested_employee) {
            frappe.db.get_value("Employee", { "user_id": frappe.session.user }, "name")
                .then(r => {
                    if (r.message && r.message.name) {
                        frm.set_value('requested_employee', r.message.name);
                    }
                });
        }

        if (frm.is_new() && !frm.doc.raised_by) {
            frm.set_value('raised_by', frappe.session.user);
        }
    },

    refresh(frm) {
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'HD Agent',
                fieldname: 'name',
                filters: {
                    user: frappe.session.user,
                    is_active: 1
                }
            },
            callback: function(r) {
                if (r.message && r.message.name) {
                    // User is an active HD Agent, show all buttons
                    working_button(frm);
                    transfer_ticket(frm);
                    resolved_button(frm);
                    add_request_buttons(frm);
                }
                hide_assignment_btn(frm);
            }
        });
    },

    ticket_type(frm) {
        if (!frm.doc.ticket_type) return frm.set_value('agent_group', '');

        frappe.db.get_value('HD Ticket Type', frm.doc.ticket_type, 'team_name')
            .then(r => frm.set_value('agent_group', r.message?.team_name || ''))
            .catch(() => frm.set_value('agent_group', ''));
    },
    
});


/**
 * Assign ticket to current user if status is Open or Transferred
 */
function working_button(frm) {
    if (['Open', 'Transferred'].includes(frm.doc.status)) {
        const btn = frm.add_custom_button(__('Working'), () => {
            frappe.call({
                method: "beams.beams.custom_scripts.hd_ticket.hd_ticket.assign_to_current_user",
                args: {
                    docname: frm.doc.name,
                    doctype: frm.doc.doctype
                },
                callback: function(r) {
                    if (!r.exc) {
                        frappe.show_alert({
                            message: __('Ticket assigned to you'),
                            indicator: 'green'
                        });

                        frm.reload_doc();
                    }
                }
            });
        });

        btn.css({
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            fontWeight: '500'
        });
    }
}



/**
 * Open dialog to transfer ticket to another active agent
 */
function transfer_ticket(frm) {
    if (!['Closed', 'Open'].includes(frm.doc.status)) {
        const btn = frm.add_custom_button(__('Transfer'), () => {
            let d = new frappe.ui.Dialog({
                title: 'Transfer Ticket',
                fields: [
                    {
                        label: 'Agent',
                        fieldname: 'agent',
                        fieldtype: 'Link',
                        options: 'HD Agent',
                        get_query: function() {
                            return { filters: { 'is_active': 1 } };
                        }
                    }
                ],
                size: 'small',
                primary_action_label: 'Assign',
                primary_action(values) {
                    frappe.call({
                        method: 'beams.beams.custom_scripts.hd_ticket.hd_ticket.assign_ticket_to_agent',
                        args: {
                            ticket_name: frm.doc.name,
                            agent: values.agent
                        },
                        callback: function(r) {
                            if (!r.exc) {
                                frappe.show_alert({ message: __('Ticket transferred successfully'), indicator: 'orange' });
                                frm.set_value('status', 'Transferred');
                                frm.save().then(() => frm.reload_doc());
                            }
                        }
                    });
                    d.hide();
                }
            });

            d.show();
        });

        btn.css({
            backgroundColor: '#fd7e14',
            color: 'white',
            border: 'none',
            fontWeight: '500'
        });
    }
}


/**
 * Set ticket status to Closed
 */
function resolved_button(frm) {
    if (!['Closed', 'Open'].includes(frm.doc.status)) {
        const btn = frm.add_custom_button(__('Resolved'), () => {

            frm.set_value('status', 'Closed');
            frm.save().then(() => {
                frappe.show_alert({ message: __('Ticket marked as closed'), indicator: 'green' });
                frm.reload_doc();
            });
        });

        btn.css({
            backgroundColor: '#1c9a68ff',
            color: 'white',
            border: 'none',
            fontWeight: '500'
        });
    }
}



/**
 * Add Asset Request and Material Request buttons if user is an active HD Agent
 */
function add_request_buttons(frm) {
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: 'HD Agent',
            fieldname: 'name',
            filters: {
                user: frappe.session.user,
                is_active: 1
            }
        },
        callback: function(r) {
            if (r.message && r.message.name) {
                // Asset Request button
                frm.add_custom_button(__('Asset Request'), () => {
                    frappe.new_doc('Asset Request', {
                        'requested_by': frm.doc.requested_employee
                    });
                }, __('Create'));

                // Material Request button
                frm.add_custom_button(__('Material Request'), () => {
                    frappe.new_doc('Material Request', {
                        'requested_by': frm.doc.requested_employee
                    });
                }, __('Create'));
            }
        }
    });
}


/**
 * hide assignment button
 */
function hide_assignment_btn(frm) {
    $(".add-assignment-btn").hide();
}
