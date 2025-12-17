frappe.ui.form.on('HD Ticket', {
	onload(frm) {
		hide_edit_coment_btn(frm);
		if (frm.is_new() && !frm.doc.requested_employee) {
			frappe.db.get_value("Employee", { "user_id": frappe.session.user }, "name").then(r => {
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
		hide_edit_coment_btn(frm);
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'HD Agent',
				fieldname: ['name', 'is_l2_user'],
				filters: {
					user: frappe.session.user
				}
			},
			callback: function (r) {
				if (r.message && r.message.name) {
					const current_agent = r.message ? r.message.name : null;
					const is_l2 = r.message ? r.message.is_l2_user : 0;

					if (!current_agent) {
						hide_assignment_btn(frm);
						return;
					}

					add_working_button(frm);
					add_reopen_button(frm);
					add_hold_button(frm);

					// Transfer / Resolved logic
					if (is_l2 || frm.doc.assigned_agent === current_agent) {
						add_transfer_button(frm);
						add_resolved_button(frm);
					}

					add_request_buttons(frm);
					hide_assignment_btn(frm);
				}
			}
		});

		if (frm.is_new()) {
			frm.set_df_property("ticket_subcategory", "hidden", 1)
		} else {
			frm.set_df_property("ticket_subcategory", "hidden", 0)
		}
	},
	ticket_type(frm) {
		if (!frm.doc.ticket_type) return frm.set_value('agent_group', '');

		frappe.db.get_value('HD Ticket Type', frm.doc.ticket_type, 'team_name')
			.then(r => frm.set_value('agent_group', r.message?.team_name || ''))
			.catch(() => frm.set_value('agent_group', ''));
	},
});


/*
* Assign ticket to current user on clicking Accept Button
 */
function add_working_button(frm) {
	if (frm.doc.status == 'Open') {
		const btn = frm.add_custom_button(__('Accept'), () => {
			frappe.call({
				method: "beams.beams.custom_scripts.hd_ticket.hd_ticket.assign_ticket_to_agent",
				args: {
					ticket_id: frm.doc.name,
					agent: frappe.session.user
				},
				callback: function (r) {
					if (r && r.message) {
						frappe.show_alert({
							message: __(r.message),
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
* Open dialog to transfer ticket to any HD Agent
*/
function add_transfer_button(frm) {
	if (!frm.is_new() && frm.doc.status == 'Working') {
		const btn = frm.add_custom_button(__('Transfer'), async () => {
			if (!frm.doc.agent_group) {
				frappe.msgprint(__('Please select a Team (Agent Group) first'));
				return;
			}
			// Fetch the HD Team document to get the agents
			let team = await frappe.db.get_doc('HD Team', frm.doc.agent_group);
			let agent_users = (team.agents || []).map(a => a.user);
			let l2_users = (team.escalation_to || []).map(a => a.user);
			let team_users = [...new Set(
				[...agent_users, ...l2_users]
			)].filter(user => user && user !== frappe.session.user);

			let d = new frappe.ui.Dialog({
				title: 'Transfer Ticket',
				fields: [
					{
						label: 'Agent/L2 User',
						fieldname: 'agent',
						fieldtype: 'Link',
						options: 'HD Agent',
						get_query: () => {
							return {
								filters: {
									user: ['in', team_users]
								}
							};
						}
					}
				],
				size: 'small',
				primary_action_label: 'Assign',
				primary_action(values) {
					frappe.call({
						method: 'beams.beams.custom_scripts.hd_ticket.hd_ticket.assign_ticket_to_agent',
						args: {
							ticket_id: frm.doc.name,
							agent: values.agent
						},
						callback: function (r) {
							if (!r.exc) {
								frappe.show_alert({
									message: __('Ticket transferred successfully'),
									indicator: 'orange'
								});
								frm.reload_doc();
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
function add_resolved_button(frm) {
	if (!frm.is_new() && !['Closed', 'Open', 'Hold'].includes(frm.doc.status)) {

		const btn = frm.add_custom_button(__('Resolved'), () => {
			handle_status_change(frm, 'Closed');
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
 * Set ticket status to Hold
 */
function add_hold_button(frm) {
	if (!frm.is_new() && !['Closed', 'Hold'].includes(frm.doc.status)) {
		const btn = frm.add_custom_button(__('Hold'), () => {
			handle_status_change(frm, 'Hold');
		});

		btn.css({
			backgroundColor: '#e303fc',
			color: 'white',
			border: 'none',
			fontWeight: '500'
		});
	}
}

/**
 * Option to Re-Open the Closed Ticket
 */
function add_reopen_button(frm) {
	if (!frm.is_new() && ['Closed', 'Hold'].includes(frm.doc.status)) {
		const btn = frm.add_custom_button(__('Re-Open'), () => {
			handle_status_change(frm, 'Open');
		});

		btn.css({
			backgroundColor: '#f23346',
			color: 'white',
			border: 'none',
			fontWeight: '500'
		});
	}
}

/**
 * Add Asset Request + Material Request Buttons
 */
function add_request_buttons(frm) {
	if (!frm.is_new()) {
		frm.add_custom_button(__('Asset Request'), () => {
			frappe.new_doc('Asset Request', {
				'requested_by': frm.doc.requested_employee
			});
		}, __('Create'));

		frm.add_custom_button(__('Material Request'), () => {
			frappe.new_doc('Material Request', {
				'requested_by': frm.doc.requested_employee
			});
		}, __('Create'));
	}
}

/*
	hide assignment button
*/
function hide_assignment_btn(frm) {
	$(".add-assignment-btn").hide();
}

/*
	hide edit comment button
*/
function hide_edit_coment_btn(frm) {
	$(".btn.btn-link.action-btn").hide();
}


function handle_status_change(frm, new_status) {
	let d = new frappe.ui.Dialog({
		title: 'Update Ticket Status',
		fields: [
			{
				label: 'Reason for Status Change',
				fieldname: 'reason',
				fieldtype: 'Small Text',
				reqd: 1
			}
		],
		primary_action_label: 'Update',
		primary_action(values) {
			frappe.call('beams.beams.custom_scripts.hd_ticket.hd_ticket.handle_reason_for_status_change', {
				ticket_id: frm.doc.name,
				status: new_status,
				reason: values.reason,
			}).then(r => {
				d.hide();
				frappe.show_alert({
					message: __('Ticket status updated successfully'),
					indicator: 'green'
				});
				frm.reload_doc();
			})
		}
	});
	d.show();
}