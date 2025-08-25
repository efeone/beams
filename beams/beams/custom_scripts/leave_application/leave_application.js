frappe.ui.form.on('Leave Application', {
	leave_type: function(frm) {
		validate_from_date(frm);
		validate_medical_certificate(frm);
	},
	from_date: function(frm) {
		validate_from_date(frm);
		frm.trigger('leave_type');
		check_holidays(frm);
	},
	to_date: function(frm) {
		frm.trigger('leave_type');
		check_holidays(frm);
	}
});

function validate_from_date(frm) {
	if (!frm.doc.from_date || !frm.doc.leave_type) {
		return;
	}

	frappe.call({
		method: 'beams.beams.custom_scripts.leave_application.leave_application.validate_leave_advance_days',
		args: {
			from_date: frm.doc.from_date,
			leave_type: frm.doc.leave_type
		},
		callback: function(response) {
			if (response.exc) {
				frm.set_value('from_date', '');
			}
		}
	});
}

function validate_medical_certificate(frm) {
	if (!frm.doc.leave_type || !frm.doc.from_date || !frm.doc.to_date) {
		hide_medical_certificate(frm);
		return;
	}

	frappe.db.get_value('Leave Type', frm.doc.leave_type, ['is_proof_document', 'medical_leave_required'])
		.then(r => {
			let value = r.message || {};

			if (!value.is_proof_document) {
				hide_medical_certificate(frm);
				return;
			}

			let from_date = frappe.datetime.str_to_obj(frm.doc.from_date);
			let to_date = frappe.datetime.str_to_obj(frm.doc.to_date);

			if (!from_date || !to_date) {
				hide_medical_certificate(frm);
				return;
			}

			let duration = frappe.datetime.get_day_diff(to_date, from_date) + 1;
			let medical_leave_required = parseInt(value.medical_leave_required) || 0;

			if (medical_leave_required > 0 && duration > medical_leave_required) {
				show_medical_certificate(frm);
			} else {
				hide_medical_certificate(frm);
			}
		})
		.catch(err => {
			hide_medical_certificate(frm);
		});
}

function show_medical_certificate(frm) {
	frm.set_df_property('medical_certificate', 'hidden', false);
	frm.set_df_property('medical_certificate', 'reqd', true);
	frm.refresh_field('medical_certificate');
}

function hide_medical_certificate(frm) {
	frm.set_df_property('medical_certificate', 'hidden', true);
	frm.set_df_property('medical_certificate', 'reqd', false);
	frm.refresh_field('medical_certificate');
}

/**
 * Check if the selected leave dates overlap with holidays.
 * Calls the server-side method `validate_holiday_overlap`
 * and shows a message if overlaps are found.
 */
function check_holidays(frm) {
	if (!frm.doc.from_date || !frm.doc.to_date) return;
	frappe.call({
		method: 'beams.beams.custom_scripts.leave_application.leave_application.validate_holiday_overlap',
		args: {
			doc: frm.doc   
		},
		callback: function(r) {
			if (r.message) {
				frappe.msgprint(r.message);
			}
		}
	});
}