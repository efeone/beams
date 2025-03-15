frappe.ui.form.on('Budget', {
    refresh: function (frm) {
        set_filters(frm);
        if (!frm.is_new()) {
            frm.add_custom_button('Open Budget Tool', () => {
                frappe.set_route('Form', 'Budget Tool', 'Budget Tool');
            });
        }
    },
    department: function (frm) {
        set_filters(frm);
        if (!frm.doc.department) {
            frm.set_value('division', null);
        }
    },
    company: function (frm) {
        frm.set_value('department', null);
    },
    budget_template: function (frm) {
    if (!frm.doc.budget_template) {
        frm.set_value('cost_center', null);
        frm.set_value('region', null);
        frm.clear_table('accounts');
        frm.refresh_field('accounts');
        return;
    }

    if (frm.doc.budget_template === frm._previous_budget_template) {
        return;
    }

    let previous_template = frm.doc.__last_value || frm._previous_budget_template;

    frappe.confirm(
        __('Are you sure you want to change the Budget Template? This will reset existing budget data.'),
        function () {
            frm.clear_table('accounts');

            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Budget Template',
                    name: frm.doc.budget_template
                },
                callback: function (response) {
                    if (response.message) {
                        let budget_template = response.message;
                        frm.set_value('cost_center', budget_template.cost_center);
                        frm.set_value('region', budget_template.region);

                        let budget_template_items = budget_template.budget_template_item || [];
                        budget_template_items.forEach(function (item) {
                            let row = frm.add_child('accounts');
                            row.cost_head = item.cost_head;
                            row.cost_subhead = item.cost_sub_head;
                            row.account = item.account;
                            row.cost_category = item.cost_category;
                        });
                        frm.refresh_field('accounts');
                    }
                }
            });

            frm._previous_budget_template = frm.doc.budget_template;
        },
        function () {
            frm.set_value('budget_template', previous_template);
        }
    );
}
});
// Function to apply filters in the cost subhead field in Budget Account
function set_filters(frm) {
    frm.set_query('division', function () {
        return {
            filters: {
                department: frm.doc.department,
                company: frm.doc.company
            }
        };
    });
    frm.set_query('budget_template', function () {
        return {
            filters: {
                division: frm.doc.division,
                company: frm.doc.company
            }
        };
    });
    frm.set_query('department', function () {
        return {
            filters: {
                company: frm.doc.company
            }
        };
    });
    frm.set_query('region', function () {
        return {
            filters: {
                company: frm.doc.company
            }
        };
    });
}

frappe.ui.form.on('Budget Account', {
  cost_subhead: function (frm, cdt, cdn) {
      var row = locals[cdt][cdn];

      if (row.cost_subhead && frm.doc.company) {
          frappe.db.get_doc('Cost Subhead', row.cost_subhead).then(doc => {
              if (doc.accounts && doc.accounts.length > 0) {
                  let account_found = doc.accounts.find(acc => acc.company === frm.doc.company);
                  if (account_found) {
                      frappe.model.set_value(cdt, cdn, 'account', account_found.default_account);
                  } else {
                      frappe.model.set_value(cdt, cdn, 'account', '');
                      frappe.msgprint(__('No default account found for the selected Cost Subhead and Company.'));
                  }
              } else {
                  frappe.model.set_value(cdt, cdn, 'account', '');
              }
          });
      }
  },
    budget_amount: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.equal_monthly_distribution && row.budget_amount) {
            distribute_budget_equally(frm, cdt, cdn, row.budget_amount);
        }
    },
    equal_monthly_distribution: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (!row.equal_monthly_distribution) {
            frappe.confirm(
                "Are you sure you want to uncheck Equal Monthly Distribution?",
                function() {
                    clear_monthly_values(frm, cdt, cdn);
                },
                function() {
                    frappe.model.set_value(cdt, cdn, "equal_monthly_distribution", 1);
                }
            );
        } else if (row.budget_amount) {
            distribute_budget_equally(frm, cdt, cdn, row.budget_amount);
        }
    },
    january: function (frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    february: function (frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    march: function (frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    april: function (frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    may: function (frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    june: function (frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    july: function (frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    august: function (frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    september: function (frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    october: function (frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    november: function (frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    december: function (frm, cdt, cdn) {
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

function clear_monthly_values(frm, cdt, cdn) {
    let fields = [
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december'
    ];

    fields.forEach(field => frappe.model.set_value(cdt, cdn, field, 0));

    frm.refresh_field('budget_account');
}

frappe.ui.form.on("Rejection Feedback", {
    rejection_feedback_add: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        row.user = frappe.session.user_fullname;
        frm.refresh_field("rejection_feedback");
    }
});
