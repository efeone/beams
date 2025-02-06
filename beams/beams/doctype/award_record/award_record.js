// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt
//

frappe.ui.form.on('Award Record', {
    refresh: function (frm) {
        if (!frm.is_new() && frm.doc.total_amount > 0) {
            frm.add_custom_button(__('Journal Voucher'), function () {
                create_jv(frm);
            }, __('Create'));
        }

        // Show button only if workflow_state is "Awarded", "Applied", or "Nominated"
        if (["Awarded", "Applied", "Nominated"].includes(frm.doc.workflow_state)) {
            frm.add_custom_button(__('Employee Travel Request'), function() {
                create_travel_request(frm);
            }, __('Create'));
        }
    },

    posting_date: function (frm) {
        frm.call("validate_posting_date");
    }
});

function create_jv(frm) {
    // Fetch Default Award Expense Account from BEAMS Admin Settings
    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'BEAMS Admin Settings'
        },
        callback: function (r) {
            if (r.message && r.message.default_award_expense_account) {
                const default_account = r.message.default_award_expense_account;

                // Create a new Journal Entry
                frappe.new_doc('Journal Entry', {
                    voucher_type: 'Journal Entry',
                    accounts: [
                        {
                            account: default_account,
                            debit_in_account_currency: frm.doc.total_amount
                        }
                    ],
                    user_remark: `Award Record: ${frm.doc.name}`
                });
            } else {
                frappe.msgprint(__('Please set the Default Award Expense Account in BEAMS Admin Settings.'));
            }
        }
    });
}

function create_travel_request(frm) {
  frappe.model.open_mapped_doc({
          method: "beams.beams.doctype.award_record.award_record.map_award_record_to_travel_request",
          frm: frm,
  });

}

frappe.ui.form.on("Award Expense Detail", {
    amount: function (frm) {
        frm.call("update_total_amount");
    },
    expenses_remove: function(frm) {
        frm.call("update_total_amount");
    }
});
