frappe.ui.form.on('Voucher Entry', {
    bureau: function(frm) {
      // Triggered when the 'bureau' field is updated
        if (frm.doc.bureau) {
            frappe.db.get_value('Bureau', frm.doc.bureau, ['cost_center', 'company'], function(r) {
                if (r) {
                    frm.set_value('cost_center', r.cost_center);
                    frm.set_value('company', r.company);
                }
            });
        }
    }
});

frappe.ui.form.on("Voucher Entry", {
    refresh: function (frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Petty Cash Request'), function () {
                show_petty_cash_dialog(frm);
            });
        }
    }
});

function show_petty_cash_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: __("Petty Cash Request"),
        fields: [
            {
                fieldname: "bureau",
                label: __("Bureau"),
                fieldtype: "Link",
                options: "Bureau",
                reqd: 1,
                default: frm.doc.bureau
            },
            {
                fieldname: "mode_of_payment",
                label: __("Mode of Payment"),
                fieldtype: "Link",
                options: "Mode of Payment",
                reqd: 1,
                default: frm.doc.mode_of_payment
            },
            {
                fieldname: "account",
                label: __("Account"),
                fieldtype: "Link",
                options: "Account",
                reqd: 1,
                default: frm.doc.account
            },
            {
                fieldname: "requested_amount",
                label: __("Requested Amount"),
                fieldtype: "Currency",
                reqd: 1,
                read_only: 1,
                default: frm.doc.total_amount - frm.doc.balance
            },
            {
                fieldname: "reason",
                label: __("Reason"),
                fieldtype: "Small Text",
                reqd: 1
            },
        ],
        primary_action_label: __("Submit"),
        primary_action(values) {
            if (values.requested_amount <= 0) {
                frappe.throw({
                    title: __("Invalid Amount"),
                    message: __("Requested Amount should be greater than 0. Please enter a valid amount."),
                    indicator: "red"
                });
            }
            submit_petty_cash_request(frm, values, d);
        }
    });

    d.show();
}

function submit_petty_cash_request(frm, values, dialog) {
    frappe.call({
        method: "beams.beams.custom_scripts.voucher_entry.voucher_entry.create_petty_cash_request",
        args: {
            voucher_entry_name: frm.doc.name,
            bureau: values.bureau,
            mode_of_payment: values.mode_of_payment,
            account: values.account,
            requested_amount: values.requested_amount,
            reason: values.reason
        },
        callback: function (response) {
            if (response.message.status === "success") {
                frappe.msgprint(__("Petty Cash Request Created Successfully!"));
                dialog.hide();
            } else {
                frappe.msgprint(__("Error: " + response.message));
            }
        }
    });
}
