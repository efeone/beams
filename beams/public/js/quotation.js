frappe.ui.form.on('Quotation', {
    refresh: function(frm) {
        if (frm.doc.docstatus == 1) {
            // Check if the is_barter checkbox is checked and show the Purchase Invoice button
            if (frm.doc.is_barter) {
                frm.add_custom_button(__('Purchase Invoice'), function() {
                    frappe.model.open_mapped_doc({
                        method: "beams.beams.custom_scripts.quotation.quotation.make_purchase_invoice",
                        frm: frm
                    });
                }, __('Create'));
            }

            // Check the total amount of linked Sales Invoices
            frappe.call({
                method: "beams.beams.custom_scripts.quotation.quotation.get_total_sales_invoice_amount",
                args: {
                    quotation_name: frm.doc.name
                },
                callback: function(r) {
                    if (r.message < frm.doc.total) {
                        frm.add_custom_button(__('Sales Invoice'), function() {
                            frappe.model.open_mapped_doc({
                                method: "beams.beams.custom_scripts.quotation.quotation.make_sales_invoice",
                                frm: frm
                            });
                        }, __('Create'));
                    } else {
                        frappe.msgprint(__('The total amount of Sales Invoices for this Quotation has reached or exceeded the limit.'));
                    }
                }
            });
        }
    },

    is_barter: function(frm) {
        if (frm.doc.is_barter) {
            frappe.db.get_single_value('Accounts Settings', 'enable_common_party_accounting')
            .then(check => {
              if (!check) {
                  frm.set_value('is_barter', 0); // Uncheck the checkbox if validation fails
                  frm.refresh_fields()
                  frappe.msgprint("Please enable 'Common Party Accounting' in the Accounts Settings to proceed with barter transactions.");
              }
            })
        }
    }
});
