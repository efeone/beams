// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Travel Request', {
    refresh: function (frm) {
        if (!frm.is_new()) {
            // Add "Purchase Invoice" button
            frm.add_custom_button(__('Purchase Invoice'), function () {
                let invoice = frappe.model.get_new_doc("Purchase Invoice");
                invoice.posting_date = frm.doc.posting_date;
                frappe.set_route("form", "Purchase Invoice", invoice.name);
            }, __("Create"));

            // Add "Journal Entry" button
            frm.add_custom_button(__('Journal Entry'), function () {
                let journal_entry = frappe.model.get_new_doc("Journal Entry");
                journal_entry.voucher_type = "Journal Entry";
                journal_entry.posting_date = frm.doc.posting_date;
                journal_entry.user_remark = "Journal Entry for Travel Request " + frm.doc.name;
                frappe.set_route("form", "Journal Entry", journal_entry.name);
            }, __("Create"));
        }
    },

    requested_by: function (frm) {

        // Fetch the Batta Policy for the selected employee
        frappe.call({
            method: "beams.beams.doctype.employee_travel_request.employee_travel_request.get_batta_policy",
            args: { requested_by: frm.doc.requested_by },
            callback: function (response) {
                if (response.message) {
                    let batta_policy = response.message;
                    frm.set_value('batta_policy', batta_policy.name);

                    // If accommodation is required, fetch and apply the room criteria filter
                    if (frm.doc.accommodation_required) {
                        set_room_criteria_filter(frm)
                    }
                }
                else {
                  frm.set_value('batta_policy', '');
              }
            },
        });
    },
    accommodation_required: function(frm) {
      set_room_criteria_filter(frm)
    },
    batta_policy: function(frm) {
      set_mode_of_travel_filter(frm)
    },
    posting_date:function (frm){
      frm.call("validate_posting_date");
    }
});

function set_room_criteria_filter(frm) {
  if (frm.doc.batta_policy){
      frappe.call({
          method: "beams.beams.doctype.employee_travel_request.employee_travel_request.filter_room_criteria",
          args: {
            batta_policy_name: frm.doc.batta_policy
          },
          callback: function (filter_response) {
              let room_criteria = filter_response.message || [];
              frm.set_query("room_criteria", function() {
                return {
                  filters: {
                    name: ["in", room_criteria]
                  }
                }
              })
          },
      });
    }
}

function set_mode_of_travel_filter(frm) {
  frappe.call({
      method: "beams.beams.doctype.employee_travel_request.employee_travel_request.filter_mode_of_travel",
      args: {
        batta_policy_name: frm.doc.batta_policy
      },
      callback: function (filter_response) {
          let mode_of_travel = filter_response.message || [];
          frm.set_query("mode_of_travel", function() {
            return {
              filters: {
                name: ["in", mode_of_travel]
              }
            }
          })
      },
  });
}
