// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Petty Cash Request", {
    refresh: function (frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Payment Entry'), function () {
                open_payment_entry(frm);
            }, __("Create"));
        }
        frm.set_query('petty_cash_account', function() {
            return {
                filters: {
                    type: 'Cash'
                }
            };
        });
    },
    petty_cash_account: function(frm) {
        var petty_cash_account = frm.doc.petty_cash_account;
        if (!petty_cash_account) {
            frm.set_value('account', '');
            return;
        }
        frappe.call({
            method: 'frappe.client.get',
            args: {
                'doctype': 'Mode of Payment',
                'filters': {'name': petty_cash_account},
                'fieldname': ['accounts']
            },
            callback: function(response) {
                if (response && response.message && response.message.accounts && response.message.accounts.length > 0) {
                    var defaultAccount = response.message.accounts[0].default_account;
                    frm.set_value('account', defaultAccount);
                }
            }
        });
    }
});

function open_payment_entry(frm) {
    frappe.new_doc("Payment Entry", {
        payment_type: "Internal Transfer",
        paid_amount: frm.doc.requested_amount,
        reference_date: frappe.datetime.nowdate(),
        paid_to: frm.doc.account
    });
}
