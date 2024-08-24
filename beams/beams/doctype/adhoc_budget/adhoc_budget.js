  frappe.ui.form.on('Adhoc Budget', {
      onload: function(frm) {
          if (!frm.doc.posting_date) {
            // Set the posting date to today if not already set
              frm.set_value('posting_date', frappe.datetime.nowdate());
          }

      },
      refresh: function(frm) {
          if (!frm.doc.posting_date) {
              frm.set_value('posting_date', frappe.datetime.nowdate());
          }
      },
      project: function(frm) {
         // Fetch expected start date and end date from the selected project
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
        // Validate expected revenue against the criteria
          check_expected_revenue_reached(frm, true);
      },
      total_budget_amount: function(frm) {
          check_expected_revenue_reached(frm, false);

          frm.refresh_fields()

      }
  });

  frappe.ui.form.on('Budget Expense', {
      budget_amount: function(frm, cdt, cdn) {
          calculate_total_budget_amount(frm);
      }
  });

  function calculate_total_budget_amount(frm) {
      let total = 0;
      // Sum all budget amounts from the Budget Expense child table
      frm.doc.budget_expense.forEach(function(row) {
          if (row.budget_amount) {
              total += row.budget_amount;
          }
      });
      // Set the total budget amount field with the calculated sum
      frm.set_value('total_budget_amount', total);
  }

  function check_expected_revenue_reached(frm) {
     // Fetch the adhoc_budget_revenue_expectation from Additional Account Settings
      frappe.db.get_single_value('Additional Account Settings', 'adhoc_budget_revenue_expectation')
          .then(value => {
              frm.set_df_property("expected_revenue", "description", `Expected Revenue should be greater than ${value * frm.doc.total_budget_amount}`)
              if (value) {
                // Check if the expected revenue meets both criteria
                  let revenue_expectation = parseFloat(value);
                  frm.set_intro('');
                  if (frm.doc.expected_revenue && frm.doc.total_budget_amount)
                    {
                    if (frm.doc.expected_revenue >=  frm.doc.total_budget_amount * revenue_expectation) {
                          // If criteria met, check the expected_revenue_reached checkbox
                        frm.set_value('expected_revenue_reached', 1);
                        // Set an intro message to indicate success
                        frm.set_intro('Expected Revenue has reached the total budget amount and is within the allowed expectation.', 'blue');
                    } else {
                      // If criteria not met, uncheck the expected_revenue_reached checkbox
                        frm.set_intro('')
                        frm.set_value('expected_revenue_reached', 0);
                        frm.set_intro('Expected Revenue does not meet the Required Criteria', 'orange');

                    }
                  }
              } else {
                  console.error('Failed to fetch Additional Account Settings');
              }
          });
  }
