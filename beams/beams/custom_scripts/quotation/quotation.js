frappe.ui.form.on('Quotation', {
    party_name: function(frm) {
        if (frm.doc.quotation_to == "Customer" and frm.doc.party_name) {
            frappe.db.get_value("Customer", frm.doc.party_name, "region", (r) => {
                if (r && r.region) {
                    frm.set_value("region", r.region);
                }
            });
        } else {
            frm.set_value("region", "");
        }
    },
    onload: function(frm) {
       if (!frm.doc.executive) {
           // Only fetch if field is empty
           let user_roles = frappe.user_roles;
           // Get roles of the logged-in user
           if (user_roles.includes("Employee")) {
                frappe.db.get_value("Employee", { user_id: frappe.session.user }, "name")
                    .then(r => {
                        if (r && r.message && r.message.name) {
                          frm.set_value("executive", r.message.name);
                      }
                });
           }
       }
    },

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
        }
    },

    is_barter: function(frm) {
        if (frm.doc.is_barter) {
            frappe.db.get_single_value('Accounts Settings', 'enable_common_party_accounting')
                .then(check => {
                    if (!check) {
                        frm.set_value('is_barter', 0); // Uncheck the checkbox if validation fails
                        frm.refresh_fields();
                        frappe.msgprint("Please enable 'Common Party Accounting' in the Accounts Settings to proceed with barter transactions.");
                    }
                });
        }
    },

    sales_type: function(frm) {
        check_sales_type(frm);
        // function to check the selected Sales Type
        frm.clear_table('items');
        frm.refresh_field('items');

        //function to check the selected Sales Type
        if (frm.doc.sales_type) {
            frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
                return {
                    filters: {
                        'sales_type': frm.doc.sales_type
                    }
                };
            };
        }
    }
});

function check_sales_type(frm) {
    // Fetch  is_time_sales field value from the linked Sales Type doctype
    if (frm.doc.sales_type) {
        frappe.db.get_value('Sales Type', frm.doc.sales_type, 'is_time_sales')
            .then(r => {
                let is_time_sales = r.message.is_time_sales;
                if (is_time_sales) {
                    frm.set_df_property('albatross_ro_id', 'reqd', true);
                } else {
                    frm.set_df_property('albatross_ro_id', 'reqd', false);
                }
            });
    } else {
        frm.set_df_property('albatross_ro_id', 'reqd', false);
    }
}

frappe.ui.form.on('Quotation Item', {
    item_code: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        if (row.item_code) {
            // Fetch sales_type from Item doctype based on selected item_code
            frappe.db.get_value('Item', {'item_code': row.item_code}, 'sales_type')
                .then(r => {
                    if (r.message) {
                        var sales_type = r.message.sales_type;

                        if (sales_type) {
                            // Set the sales_type in the child table row
                            frappe.model.set_value(cdt, cdn, 'sales_type', sales_type);
                        } else {
                            frappe.model.set_value(cdt, cdn, 'sales_type', ''); // Clear if no sales_type in Item
                        }
                    }
                });
        }
    }
});
