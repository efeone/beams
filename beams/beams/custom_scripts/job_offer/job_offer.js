frappe.ui.form.on("Job Offer", {
	job_applicant: function(frm) {
		if (frm.doc.job_applicant) {
			frappe.db.get_value('Job Applicant', frm.doc.job_applicant, 'salutation', (r) => {
				if (r && r.salutation) {
					frm.set_value('salutation', r.salutation);
				}
			});
		}
	},
	refresh: function (frm) {
		if (
			!frm.doc.__islocal &&
			frm.doc.status == "Accepted" &&
			frm.doc.docstatus === 1 &&
			(!frm.doc.__onload || !frm.doc.__onload.employee)
		) {
			frm.remove_custom_button(__("Create Employee"));
			frm.add_custom_button(__("Create Employee"), function () {
				make_employee(frm);
			});
		}

		// Ensure CTC is editable even if it has fetch_from property
		if (frm.doc.docstatus === 0) {
			frm.set_df_property('ctc', 'read_only', 0);
		}
		
		check_ctc_mismatch(frm);
	},
	validate: function(frm) {
		if (frm.doc.ctc) {
			if (frm.doc.ctc < 0) {
				frappe.msgprint(__('CTC cannot be a Negative  Value'));
				frappe.validated = false;
			}
		}
		// Ensure totals are calculated before sending to server
		calculate_all_totals(frm);
	},
	ctc: function(frm) {
		check_ctc_mismatch(frm);
	},
	salary_details_add: function(frm) {
		calculate_all_totals(frm);
	},
	salary_details_remove: function(frm) {
		calculate_all_totals(frm);
	},
	other_contribution_details_add: function(frm) {
		calculate_all_totals(frm);
	},
	other_contribution_details_remove: function(frm) {
		calculate_all_totals(frm);
	}
});

frappe.ui.form.on("Job Offer Salary Detail", {
	amount: function(frm, cdt, cdn) {
		calculate_all_totals(frm);
	}
});

function calculate_all_totals(frm) {
	let gross = 0;
	(frm.doc.salary_details || []).forEach(d => {
		gross += flt(d.amount);
	});
	if (flt(frm.doc.gross_monthly_salary) !== gross) {
		frm.doc.gross_monthly_salary = gross;
		frm.refresh_field('gross_monthly_salary');
	}

	let other = 0;
	(frm.doc.other_contribution_details || []).forEach(d => {
		other += flt(d.amount);
	});

	let total_ctc = gross + other;
	if (flt(frm.doc.total_ctc_per_month) !== total_ctc) {
		frm.doc.total_ctc_per_month = total_ctc;
		frm.refresh_field('total_ctc_per_month');
	}

	if (!frm.doc.ctc || flt(frm.doc.ctc) === 0) {
		frm.doc.ctc = total_ctc;
		frm.refresh_field('ctc');
	}

	check_ctc_mismatch(frm);
}

function check_ctc_mismatch(frm) {
	if (!frm || !frm.dashboard) return;

	let total = flt(frm.doc.total_ctc_per_month);
	let ctc = flt(frm.doc.ctc);

	if (ctc > 0 && Math.abs(ctc - total) > 0.01) {
		// Use doc currency, or fallback to system default if not available
		let currency = frm.doc.currency || (frappe.boot && frappe.boot.sysdefaults && frappe.boot.sysdefaults.currency);
		let formatted_total = format_currency(total, currency);
		let formatted_ctc = format_currency(ctc, currency);

		frm.dashboard.set_headline(
			__('Total CTC per month ({0}) does not match CTC ({1})', [formatted_total, formatted_ctc]), 
			'orange'
		);
	} else {
		frm.dashboard.clear_headline();
	}
}

function make_employee(frm) {
	frappe.model.open_mapped_doc({
		method: "beams.beams.custom_scripts.job_offer.job_offer.make_employee",
		frm: frm,
	});
}
