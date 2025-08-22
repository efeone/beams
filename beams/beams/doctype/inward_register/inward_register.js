// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt
frappe.ui.form.on('Inward Register', {
	refresh: function (frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Outward Register'), function () {
				frappe.new_doc("Outward Register", {
					inward_register: frm.doc.name,
				});
			}, __("Create"));

			if (!frappe.user.has_role('Security') || frappe.user.has_role('Administrator')) {
				frm.add_custom_button(__(' Visitor Pass'), function () {
					frappe.new_doc("Visitor Pass", {
						inward_register: frm.doc.name,
						issued_date: frappe.datetime.now_date(),
						issued_time: frappe.datetime.now_time(),
						issued_to: frm.doc.visitor_name
					});
				}, __("Create"));
				if (frm.doc.visitor_type === 'Courier') {
					frm.add_custom_button(__('Courier Log'), function () {
						frappe.model.with_doctype("Courier Log", function () {
							let doc = frappe.model.get_new_doc("Courier Log");

							doc.courier_service = frm.doc.courier_service;
							doc.date = frm.doc.visit_date;
							doc.status = "Received";

							let inward_row = frappe.model.add_child(doc, "inward_register");
							inward_row.inward_register = frm.doc.name;

							let recipient_row = frappe.model.add_child(doc, "recipients");
							recipient_row.recepient = frm.doc.received_by;

							frappe.set_route("Form", "Courier Log", doc.name);
						});
					}, __("Create"));
				}
			}
		}
	},
	posting_date: function (frm) {
	frm.call("validate_posting_date");
	}
});
