// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Petty Cash Request", {
    refresh: function (frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Payment Entry'), function () {
                open_payment_entry(frm);
            }, __("Create"));
        }
    }
});

function open_payment_entry(frm) {
    frappe.new_doc("Payment Entry", {
        payment_type: "Pay",
        party_type: "Employee",
        party: frm.doc.employee,
        paid_amount: frm.doc.requested_amount,
        reference_no: frm.doc.name,
        reference_date: frappe.datetime.nowdate(),
        mode_of_payment: frm.doc.mode_of_payment,
        paid_from: frm.doc.account
    });
}
