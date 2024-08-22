frappe.ui.form.on('Adhoc Budget', {
    onload: function(frm) {
        if (!frm.doc.posting_date) {
            frm.set_value('posting_date', frappe.datetime.nowdate());
        }
        check_expected_revenue_reached(frm, false);
    },
    refresh: function(frm) {
        if (!frm.doc.posting_date) {
            frm.set_value('posting_date', frappe.datetime.nowdate());
        }
        check_expected_revenue_reached(frm, false);
    },
    project: function(frm) {
        if (frm.doc.project) {
            frappe.db.get_value('Project', frm.doc.project, ['expected_start_date', 'expected_end_date'], function(r) {
                if (r) {
                    frm.set_value('expected_start_date', r.expected_start_date);
                    frm.set_value('expected_end_date', r.expected_end_date);
                }
            });
        } else {
            frm.set_value('expected_start_date', null);
            frm.set_value('expected_end_date', null);
        }
    },
    expected_revenue: function(frm) {
        check_expected_revenue_reached(frm, true);
    },
    total_budget_amount: function(frm) {
        check_expected_revenue_reached(frm, false);
    }
});

frappe.ui.form.on('Budget Expense', {
    budget_amount: function(frm, cdt, cdn) {
        calculate_total_budget_amount(frm);
    }
});

function calculate_total_budget_amount(frm) {
    let total = 0;
    frm.doc.budget_expense.forEach(function(row) {
        if (row.budget_amount) {
            total += row.budget_amount;
        }
    });
    frm.set_value('total_budget_amount', total);
    check_expected_revenue_reached(frm, false);
}

function check_expected_revenue_reached(frm, show_warning) {
    frappe.db.get_single_value('Additional Account Settings', 'adhoc_budget_revenue_expectation')
        .then(value => {
            if (value) {
                let revenue_expectation = parseFloat(value);
                if (frm.doc.expected_revenue >= 3 * frm.doc.total_budget_amount &&
                    frm.doc.expected_revenue <= revenue_expectation) {
                    frm.set_value('expected_revenue_reached', 1);
                    frm.set_intro('Expected Revenue has reached three times the total budget amount and is within the allowed expectation.', 'blue');
                } else {
                    frm.set_value('expected_revenue_reached', 0);
                    frm.set_intro('');
                    if (show_warning) {
                        frappe.msgprint({
                            title: __('Warning'),
                            indicator: 'orange',
                            message: __('Expected Revenue does not meet the Required Criteria.')
                        });
                    }
                }
            } else {
                console.error('Failed to fetch Additional Account Settings');
            }
        });
}
