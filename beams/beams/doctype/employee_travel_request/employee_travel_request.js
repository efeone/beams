// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Travel Request', {
    onload(frm) {
        if (!frm.doc.requested_by) {
            frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
                .then(r => {
                    if (r.message) frm.set_value('requested_by', r.message.name);
                });
        }
    },
    refresh: function (frm) {
        if (!frm.is_new() && frappe.user.has_role("Admin")) {
            frm.add_custom_button(__('Journal Entry'), function () {
                let journal_entry = frappe.model.get_new_doc("Journal Entry");
                journal_entry.voucher_type = "Journal Entry";
                journal_entry.posting_date = frm.doc.posting_date;
                journal_entry.employee_travel_request = frm.doc.name;
                journal_entry.user_remark = "Journal Entry for Travel Request " + frm.doc.name;
                frappe.model.set_value("Journal Entry", journal_entry.name, "employee_travel_request", frm.doc.name);
                frappe.set_route("form", "Journal Entry", journal_entry.name);
            }, __("Create"));
        }

        if (frm.doc.is_unplanned === 1 ) {
            frm.add_custom_button(__('Expense Claim'), function () {
                const dialog = new frappe.ui.Dialog({
                    title: 'Travel Claim Expenses',
                    fields: [
                        {
                            fieldtype: 'Table',
                            label: 'Expenses',
                            fieldname: 'expenses',
                            reqd: 1,
                            fields: [
                                {
                                    label: 'Expense Date',
                                    fieldtype: 'Date',
                                    fieldname: 'expense_date',
                                    in_list_view: 1,
                                    reqd: 1
                                },
                                {
                                    label: 'Expense Claim Type',
                                    fieldtype: 'Link',
                                    options: 'Expense Claim Type',
                                    fieldname: 'expense_type',
                                    in_list_view: 1,
                                    reqd: 1
                                },
                                {
                                    label: 'Description',
                                    fieldtype: 'Small Text',
                                    fieldname: 'description',
                                    in_list_view: 1
                                },
                                {
                                    label: 'Amount',
                                    fieldtype: 'Currency',
                                    fieldname: 'amount',
                                    in_list_view: 1,
                                    reqd: 1
                                }
                            ]
                        }
                    ],
                    size: 'large',
                    primary_action_label: 'Submit',
                    primary_action(values) {
                        const expenses = values.expenses || [];
                        if (!expenses.length) {
                            frappe.msgprint(__('Please enter at least one expense item.'));
                            return;
                        }
                        frappe.call({
                            method: 'beams.beams.doctype.employee_travel_request.employee_travel_request.create_expense_claim',
                            args: {
                                employee: frm.doc.requested_by,
                                travel_request: frm.doc.name,
                                expenses: expenses
                            },
                            callback: function (r) {
                                if (!r.exc) {
                                    dialog.hide();
                                    frappe.set_route('Form', 'Expense Claim', r.message);
                                }
                            }
                        });
                    }
                });
                dialog.show();
            }, __('Create'));
        }

        if (frm.doc.workflow_state === "Approved by HOD" && frm.doc.is_vehicle_required) {
            frm.set_df_property("travel_vehicle_allocation", "read_only", 0);
        } else {
            frm.set_df_property("travel_vehicle_allocation", "read_only", 1);
        }

        if (frm.doc.is_unplanned === 1) {
            frm.set_df_property("attachments", "read_only", 0);
        } else if (frm.doc.workflow_state === "Approved by HOD") {
            frm.set_df_property("attachments", "read_only", 0);
        } else {
            frm.set_df_property("attachments", "read_only", 1);
        }
    },

    requested_by: function (frm) {
        apply_travellers_filter(frm);
        frappe.call({
            method: "beams.beams.doctype.employee_travel_request.employee_travel_request.get_batta_policy",
            args: { requested_by: frm.doc.requested_by },
            callback: function (response) {
                if (response.message) {
                    let batta_policy = response.message;
                    frm.set_value("batta_policy", batta_policy.name);

                    if (frm.doc.accommodation_required) {
                        set_room_criteria_filter(frm);
                    }
                } else {
                    frm.set_value("batta_policy", "");
                }
            }
        });
    },

    accommodation_required: function (frm) {
        set_room_criteria_filter(frm);
    },

    batta_policy: function (frm) {
        set_mode_of_travel_filter(frm);
    },

    posting_date: function (frm) {
        frm.call("validate_posting_date");
    },

    start_date: function (frm) {
        calculate_days(frm);
    },

    end_date: function (frm) {
        calculate_days(frm);
        update_number_of_travellers_visibility(frm);
    },

    is_group: function (frm) {
        update_number_of_travellers_visibility(frm);
        if (!frm.doc.is_group) {
            frm.set_value("travellers", []);
            frm.set_value("number_of_travellers", 1);
        }
    },

    travellers: function (frm) {
        if (frm.doc.is_group && frm.doc.travellers) {
            frm.set_value("number_of_travellers", frm.doc.travellers.length + 1);
        }
        update_number_of_travellers_visibility(frm);
    },

    is_unplanned: function (frm) {
        update_number_of_travellers_visibility(frm);
    }
});
// Toggles visibility of 'number_of_travellers' field based on 'is_group' status and 'travellers' table length.

function update_number_of_travellers_visibility(frm) {
    if (frm.doc.is_group && frm.doc.travellers && frm.doc.travellers.length > 0) {
        frm.set_df_property("number_of_travellers", "hidden", 0);
    } else {
        frm.set_df_property("number_of_travellers", "hidden", 1);
    }
}


function set_room_criteria_filter(frm) {
    if (frm.doc.batta_policy) {
        frappe.call({
            method: "beams.beams.doctype.employee_travel_request.employee_travel_request.filter_room_criteria",
            args: {
                batta_policy_name: frm.doc.batta_policy
            },
            callback: function (filter_response) {
                let room_criteria = filter_response.message || [];
                frm.set_query("room_criteria", function () {
                    return {
                        filters: {
                            name: ["in", room_criteria]
                        }
                    };
                });
            }
        });
    }
}

function set_mode_of_travel_filter(frm) {
    // Skip filter if user has "Admin" role
    if (frappe.user.has_role("Admin")) {
        frm.set_query("mode_of_travel", function () {
            return {};
        });
        return;
    }
    frappe.call({
        method: "beams.beams.doctype.employee_travel_request.employee_travel_request.filter_mode_of_travel",
        args: {
            batta_policy_name: frm.doc.batta_policy
        },
        callback: function (filter_response) {
            let mode_of_travel = filter_response.message || [];
            frm.set_query("mode_of_travel", function () {
                return {
                    filters: {
                        name: ["in", mode_of_travel]
                    }
                };
            });
        }
    });
}

function calculate_days(frm) {
    if (frm.doc.start_date && frm.doc.end_date) {
        frm.call("validate_dates")
        .then(() => {
            return frm.call("total_days_calculate");
        })
        .then(() => {
            frm.refresh_field("total_days");
        });
    } else {
        frm.set_value("total_days", null);
    }
}

function apply_travellers_filter(frm) {
    frm.set_query("travellers", function () {
        return {
            filters: [["name", "!=", frm.doc.requested_by || ""]]
        };
    });
}

frappe.ui.form.on('Vehicle Allocation', {
  driver: function(frm, cdt, cdn) {
      set_driver_filters(frm, cdt, cdn);
  },
  vehicle: function(frm, cdt, cdn) {
      set_vehicle_filters(frm, cdt, cdn);
  },
  travel_vehicle_allocation_add: function(frm, cdt, cdn) {
      set_driver_filters(frm, cdt, cdn);
      set_vehicle_filters(frm, cdt, cdn);
  }
});


// Sets filter for the `driver` field to exclude already selected drivers in other rows
function set_driver_filters(frm, cdt, cdn) {
  const current_row = locals[cdt][cdn];
  // Collect all drivers already selected in other rows
  const selected_drivers = (frm.doc.travel_vehicle_allocation || [])
      .filter(row => row.name !== current_row.name && row.driver)
      .map(row => row.driver);

  // Set query filter on the driver field to exclude selected drivers
  frm.fields_dict.travel_vehicle_allocation.grid.get_field("driver").get_query = function(doc, cdt, cdn) {
      return {
          filters: [
              ["name", "not in", selected_drivers]
          ]
      };
  };
}

// Sets filter for the `vehicle` field to exclude already selected vehicles in other rows
function set_vehicle_filters(frm, cdt, cdn) {
  const current_row = locals[cdt][cdn];
  // Collect all vehicles already selected in other rows
  const selected_vehicles = (frm.doc.travel_vehicle_allocation || [])
      .filter(row => row.name !== current_row.name && row.vehicle)
      .map(row => row.vehicle);

  // Set query filter on the vehicle field to exclude selected vehicles
  frm.fields_dict.travel_vehicle_allocation.grid.get_field("vehicle").get_query = function(doc, cdt, cdn) {
      return {
          filters: [
              ["name", "not in", selected_vehicles]
          ]
      };
  };
}
