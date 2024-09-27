// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Substitute Booking", {
    daily_wage: function(frm) {
        calculate_total_wage(frm);
    },

    onload: function(frm) {
      if (frm.is_new() && !frm.doc.expense_account) {  // Check if it's a new form and the field is empty
      // Fetch the default debit account from Beams Account Settings
        frappe.db.get_single_value('Beams Accounts Settings', 'default_debit_account')
          .then(default_account => {
            if (default_account) {
              frm.set_value('expense_account', default_account);
            } else {
              frappe.msgprint(__('Default Debit Account is not set in Beams Account Settings.'));
                    }
               });
      }
},

    refresh: function(frm) {
        // Remove the "Leave Application List" button if the form is dirty (unsaved changes)
        if (frm.is_dirty()) {
            frm.remove_custom_button(__('Leave Application List'), __("View"));
        }

        // Add "Leave Application List" button only if the form is saved and "Substituting For" has a value
        if (!frm.is_new() && frm.doc.substituting_for) {
            frm.add_custom_button(__('Leave Application List'), function () {
                const employee = frm.doc.substituting_for;
                if (employee) {
                    // Navigate to the Leave Application List filtered by the employee
                    frappe.set_route('List', 'Leave Application', { employee: employee });
                } else {
                    frappe.msgprint(__('Please specify an employee in the "Substituting For" field.'));
                }
            }, __("View"));
        }

        // Add "Make Payment" button if is_paid is not checked
        if (!frm.is_new() && !frm.doc.is_paid && frm.doc.workflow_state === "Approved") {
            frm.add_custom_button(__('Make Payment'), function() {
                // Mark the booking as paid
                frm.set_value("is_paid", 1);
                // Hide the "Make Payment" button
                frm.remove_custom_button(__('Make Payment'));

                // Call the server-side method to create the journal entry
                frm.call({
                    doc: frm.doc,
                    method: "create_journal_entry_from_substitute_booking",
                });
            });
        }
    },

    // Triggered when the 'substituting_for' field is changed
    substituting_for: function(frm) {
        // Ensure the button is only shown when the form is saved
        if (!frm.is_dirty() && frm.doc.substituting_for) {
            frm.add_custom_button(__('Leave Application List'), function() {
                const employee = frm.doc.substituting_for;
                if (employee) {
                    frappe.set_route('List', 'Leave Application', { employee: employee });
                } else {
                    frappe.msgprint(__('Please specify an employee in the "Substituting For" field.'));
                }
            }, __("View"));
        } else {
            frm.remove_custom_button(__('Leave Application List'), __("View"));
        }
    },
		is_paid: function(frm) {
		    if (frm.doc.is_paid) {
		        frm.set_value('paid_amount', frm.doc.total_wage);
		    } else {
		        frm.set_value('paid_amount', null);  // Clear the field by setting it to null
		    }
		}
});



frappe.ui.form.on('Substitution Bill Date', {
	date: function(frm, cdt, cdn) {
		// Validate dates and update no_of_days when a date is entered or changed
		validate_dates(frm);
	}
});

function validate_dates(frm) {
	let dates = frm.doc.substitution_bill_date.map(row => row.date).filter(date => date);

	// Check for duplicate dates
	let unique_dates = [...new Set(dates)];
	if (unique_dates.length !== dates.length) {
		frappe.msgprint({
			title: __('Message'),
			message: __('Dates should be unique.'),
			indicator: 'red'
		});
		frm.refresh_field('substitution_bill_date');
		return;
	}

	let unique_dates_count = unique_dates.length;
	frm.set_value('no_of_days', unique_dates_count);

	// Calculate the total wage after updating no_of_days
	calculate_total_wage(frm);
}

function calculate_total_wage(frm) {
	let no_of_days = frm.doc.no_of_days;
	let daily_wage = frm.doc.daily_wage;

	if (no_of_days && daily_wage) {
		// Calculate total wage
		let total_wage = no_of_days * daily_wage;
		frm.set_value('total_wage', total_wage);
	}
}
