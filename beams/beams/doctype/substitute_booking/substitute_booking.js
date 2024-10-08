//Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Substitute Booking", {
    refresh: function(frm) {
        // Add custom button to view leave applications under "View"
        frm.add_custom_button(__('Leave Application List'), function() {
            if (!frm.doc.substitution_bill_date || frm.doc.substitution_bill_date.length === 0) {
                frappe.msgprint(__('No dates found in Substitution Bill Date child table.'));
                return;
            }

            // Collect dates from child table and convert them to JSON
            let dates = frm.doc.substitution_bill_date.map(row => row.date);
            if (dates.length === 0) {
                frappe.msgprint(__('Please enter at least one date in the Substitution Bill Date table.'));
                return;
            }

            // Call server-side method to check leave applications
            frappe.call({
                method: 'beams.beams.doctype.substitute_booking.substitute_booking.check_leave_application',
                args: {
                    employee: frm.doc.substituting_for,
                    dates: JSON.stringify(dates) // Convert dates array to JSON string
                },
                callback: function(r) {
                    if (r.message) {
                        let { leave_applications, missing_dates } = r.message;

                        // If there are missing dates, show a message
                        if (missing_dates && missing_dates.length > 0) {
                            frappe.msgprint(__('No Approved Leave Applications found for the following dates: {0}', [missing_dates.join(', ')]));
                        }

                        // If there are approved leave applications
                        if (leave_applications && Object.keys(leave_applications).length > 0) {
                            let leaveDetails = Object.entries(leave_applications).map(([date, applications]) => {
                                return `For date ${date}: ` + applications.map(leave =>
                                    `Leave Application ${leave.name} from ${leave.from_date} to ${leave.to_date}`
                                ).join(', ');
                            }).join('<br>');

                            frappe.msgprint(__('Approved Leave Applications: <br>{0}', [leaveDetails]));

                            // Redirect to Leave Application list with filters for approved leave dates
                            frappe.set_route('List', 'Leave Application', {
                                employee: frm.doc.substituting_for,
                                from_date: ['in', Object.keys(leave_applications)],  // Dates with leave applications
                                to_date: ['in', Object.keys(leave_applications)]
                            });
                        } else if (missing_dates.length === 0) {
                            frappe.msgprint(__('No approved leave applications found for the provided dates.'));
                        }
                    } else {
                        frappe.msgprint(__('No leave applications found.'));
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

        // Disable '+' icon in connections for creating journal entry manually
        if (frm.doc.status === 'Approved') {
            frm.fields_dict['connections'].grid.wrapper.find('.grid-add').hide();
        } else {
            frm.fields_dict['connections'].grid.wrapper.find('.grid-add').show();
        }
    },

    // Triggered when the 'substituting_for' field is changed
    substituting_for: function(frm) {
        if (!frm.is_dirty() && frm.doc.substituting_for) {
            frm.page.add_action_item(__('Leave Application List'), function() {
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
        validate_dates(frm);
    },
    substitution_bill_date_remove: function(frm) {
        validate_dates(frm);
    }
});

function validate_dates(frm) {
    let dates = frm.doc.substitution_bill_date.map(row => row.date).filter(date => date); // Get valid dates

    let unique_dates = [...new Set(dates)]; // Ensure unique dates
    if (unique_dates.length !== dates.length) {
        frappe.msgprint({
            title: __('Message'),
            message: __('Dates should be unique.'),
            indicator: 'red'
        });
        frm.refresh_field('substitution_bill_date');
        return;
    }

    // Set the number of unique days
    let unique_dates_count = unique_dates.length;
    frm.set_value('no_of_days', unique_dates_count);

    calculate_total_wage(frm);
}

function calculate_total_wage(frm) {
    let no_of_days = frm.doc.no_of_days;
    let daily_wage = frm.doc.daily_wage;

    if (no_of_days && daily_wage) {
        let total_wage = no_of_days * daily_wage;
        frm.set_value('total_wage', total_wage); // Update total wage based on number of days and daily wage
    }
}
