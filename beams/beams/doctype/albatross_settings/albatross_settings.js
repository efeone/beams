// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Albatross Settings', {
   /*
   *  Applies a filter on `albatross_service_item` where is_stock_item'checkbox is unchecked in item doctype.
   * Applies a filter to the `albatross_service_item` field based on the fetched Sales Types where is_time_sales
    checkbox is checked in item doctype.
   */
    onload: function (frm) {
        // Initialize the list for filtering
        frm.albatross_service_item_sales_types = [];
        // Fetch Sales Types where is_time_sales is checked
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Sales Type',
                filters: {
                    'is_time_sales': 1
                },
                fields: ['name']
            },
            callback: function (data) {
                if (data.message) {
                    frm.albatross_service_item_sales_types = data.message.map(sales_type => sales_type.name);
                    // Set query for the albatross_service_item field
                    frm.fields_dict['albatross_service_item'].get_query = function () {
                        return {
                            filters: {
                                'is_stock_item': 0, // Filter for is_stock_item being unchecked
                                'sales_type': ['in', frm.albatross_service_item_sales_types] // Filter based on sales types
                            }
                        };
                    };
                    frm.refresh_field('albatross_service_item');
                }
            }
        });
    }
});
