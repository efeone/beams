frappe.ui.form.on('Budget', {
    division: function(frm) {
        frm.set_value('cost_center', null);
        frm.set_value('department', null);

        if (frm.doc.division) {
            // Fetch cost center and department based on selected division
            frappe.db.get_value('Division', { 'name': frm.doc.division }, ['cost_center', 'department'])
                .then(r => {
                    if (r && r.message) {
                        const { cost_center, department } = r.message;

                        if (cost_center) {
                            frm.set_value('cost_center', cost_center);
                        }
                        if (department) {
                            frm.set_value('department', department);
                        }
                    } else {
                        frappe.msgprint(__('No cost center or department found for the selected division.'));
                    }
                });
        }
    },
    refresh: function(frm) {
        set_filters(frm);
    }
});

function set_filters(frm) {
    // Apply filters in the cost subhead field in Budget Account
    frm.set_query('cost_subhead', 'accounts', (doc, cdt, cdn) => {
        var child = locals[cdt][cdn];
        return {
            filters: {
                'department': frm.doc.department || ''
            }
        };
    });
}

frappe.ui.form.on('Budget Account', {
    cost_subhead: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.cost_subhead) {
            // Fetch the related account and department from the selected cost_subhead
            frappe.db.get_value('Cost Subhead', row.cost_subhead, ['account', 'department'], function(value) {
                if (value) {
                    // Set the account in the child table
                    frappe.model.set_value(cdt, cdn, 'account', value.account);
                    // Set the department in the parent Budget form
                    frm.set_value('department', value.department);
                }
            });
        }
    },
    budget_amount: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.equal_monthly_distribution && row.budget_amount) {
            distribute_budget_equally(frm, cdt, cdn, row.budget_amount);
        }
    },
    equal_monthly_distribution: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.equal_monthly_distribution && row.budget_amount) {
            distribute_budget_equally(frm, cdt, cdn, row.budget_amount);
        }
    },
    january: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    february: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    march: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    april: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    may: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    june: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    july: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    august: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    september: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    october: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    november: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    december: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    }
});

function calculate_budget_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    // Calculate the total of all monthly amounts
    let total =
        (row.january || 0) +
        (row.february || 0) +
        (row.march || 0) +
        (row.april || 0) +
        (row.may || 0) +
        (row.june || 0) +
        (row.july || 0) +
        (row.august || 0) +
        (row.september || 0) +
        (row.october || 0) +
        (row.november || 0) +
        (row.december || 0);

    frappe.model.set_value(cdt, cdn, 'budget_amount', total);
    frm.refresh_field('budget_account');
}

function distribute_budget_equally(frm, cdt, cdn, budget_amount) {
    let row = locals[cdt][cdn];

    // Calculate equal amount for each month and rounding adjustment
    let equal_amount = Math.floor((budget_amount / 12) * 100) / 100;
    let total = equal_amount * 12;
    let difference = Math.round((budget_amount - total) * 100) / 100;

    // Distribute the amounts
    frappe.model.set_value(cdt, cdn, 'january', equal_amount);
    frappe.model.set_value(cdt, cdn, 'february', equal_amount);
    frappe.model.set_value(cdt, cdn, 'march', equal_amount);
    frappe.model.set_value(cdt, cdn, 'april', equal_amount);
    frappe.model.set_value(cdt, cdn, 'may', equal_amount);
    frappe.model.set_value(cdt, cdn, 'june', equal_amount);
    frappe.model.set_value(cdt, cdn, 'july', equal_amount);
    frappe.model.set_value(cdt, cdn, 'august', equal_amount);
    frappe.model.set_value(cdt, cdn, 'september', equal_amount);
    frappe.model.set_value(cdt, cdn, 'october', equal_amount);
    frappe.model.set_value(cdt, cdn, 'november', equal_amount);
    frappe.model.set_value(cdt, cdn, 'december', equal_amount + difference);

    frm.refresh_field('budget_account');
}
