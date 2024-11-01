//Copyright (c) 2024, efeone and contributors
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
      frm.add_custom_button(__('Leave Application List'), function() {
          if (!frm.doc.substitution_bill_date || frm.doc.substitution_bill_date.length === 0) {
              frappe.msgprint(__('No dates found in Substitution Bill Date child table.'));
              return;
          }

          // Collect dates from the child table
          let dates = frm.doc.substitution_bill_date.map(row => row.date);
          if (dates.length === 0) {
              frappe.msgprint(__('Please enter at least one date in the Substitution Bill Date table.'));
              return;
          }

          frappe.call({
              method: 'beams.beams.doctype.substitute_booking.substitute_booking.check_leave_application',
              args: {
                  employee: frm.doc.substituting_for,
                  dates: JSON.stringify(dates)
              },
              callback: function(r) {
                  if (r.message) {
                      let { leave_applications, missing_dates } = r.message;

                      if (missing_dates && missing_dates.length > 0) {
                          frappe.msgprint(__('No approved leave applications found for these dates: {0}', [missing_dates.join(', ')]));
                      }

                      // Display approved leave applications
                      if (leave_applications && Object.keys(leave_applications).length > 0) {
                          let leaveDetails = Object.entries(leave_applications).map(([date, applications]) => {
                              return `For date ${date}: ` + applications.map(leave =>
                                  `Leave Application ${leave.name} from ${leave.from_date} to ${leave.to_date}`
                              ).join(', ');
                          }).join('<br>');

                          frappe.msgprint(__('Approved Leave Applications:<br>{0}', [leaveDetails]));

                          // Navigate to Leave Application list view with filters
                          frappe.set_route('List', 'Leave Application', {
                              employee: frm.doc.substituting_for,
                              status: 'Approved',
                              from_date: ['<=', dates[0]],
                              to_date: ['>=', dates[dates.length - 1]]
                          });
                      } else {
                          frappe.msgprint(__('No approved leave applications found for the specified dates.'));
                      }
                  } else {
                      frappe.msgprint(__('Error: No response received from the server.'));
                  }
              }
          });
      }, __("View"));





        // Check for payment button visibility
        if (!frm.is_new() && !frm.doc.is_paid && frm.doc.workflow_state === "Approved") {
            frm.add_custom_button(__('Make Payment'), function() {
                frm.set_value("is_paid", 1); // Set payment status
                frm.remove_custom_button(__('Make Payment')); // Remove button after setting paid

                frm.call({
                    doc: frm.doc,
                    method: "create_journal_entry_from_substitute_booking",
                });
            });
        }

        // disabled '+' icon in connections for creating journal entry manually
        if (frm.doc.status === 'Approved') {
            frm.fields_dict['connections'].grid.wrapper.find('.grid-add').hide();
        } else {
            frm.fields_dict['connections'].grid.wrapper.find('.grid-add').show();
        }
    },

    // Triggered when the 'substituting_for' field is changed
    substituting_for: function(frm) {
        if (!frm.is_dirty() && frm.doc.substituting_for) {
            frm.add_custom_button(__('Leave Application List'), function() {
              const employee = frm.doc.substituting_for;
                if (employee) {
                    frappe.set_route('List', 'Leave Application', { employee: employee });
                } else {
                    frappe.msgprint(__('Please specify an employee in the "Substituting For" field.'));
                }
            }, __("View"));
        }
    },
    is_paid: function(frm) {
        if (frm.doc.is_paid) {
            frm.set_value('paid_amount', frm.doc.total_wage); // Set paid amount to total wage
        } else {
            frm.set_value('paid_amount', null); // Clear paid amount if not paid
        }
    }
});



frappe.ui.form.on('Substitution Bill Date', {
	date: function(frm, cdt, cdn) {
		// Validate dates and update no_of_days when a date is entered or changed
		validate_dates(frm);
	},
	substitution_bill_date_remove: function(frm) {
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
