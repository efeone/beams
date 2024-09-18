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

frappe.ui.form.on('Voucher Account', {
    voucher_entry_type: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.voucher_entry_type) {
          if (!frm.doc.company) {
              frappe.model.set_value(cdt, cdn, 'voucher_entry_type', );
              frappe.msgprint(__('Please set the company'));
              return;
          }
          // Validate if the company is associated with the selected voucher entry type
            frappe.call({
                method: 'beams.beams.custom_scripts.voucher_entry.voucher_entry.validate_company_for_voucher_entry_type',
                args: {
                    voucher_entry_type: row.voucher_entry_type,
                    company: frm.doc.company
                },
                callback: function(response) {
                    if (!response.message) {
                    }
                },
                error: function(err) {
                }
            });
            // Fetch and set the default account after validation
            frappe.call({
                method: 'beams.beams.custom_scripts.voucher_entry.voucher_entry.get_default_account',
                args: {
                    voucher_entry_type: row.voucher_entry_type,
                    company: frm.doc.company
                },
                callback: function(response) {
                    if (response.message) {
                        let default_account = response.message;
                        frappe.model.set_value(cdt, cdn, 'account', default_account);
                    }
                }
            });
        }
    }
});
