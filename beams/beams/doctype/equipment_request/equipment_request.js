// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Request', {
    bureau: function (frm) {
        if (frm.doc.bureau) {
            // Fetch all assets with the same bureau
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Asset',
                    filters: {
                        bureau: frm.doc.bureau // Match the bureau in the parent Equipment Request
                    },
                    fields: ['item_code'], // Fetch the item codes from assets
                    limit_page_length: 0
                },
                callback: function (response) {
                    if (response.message && response.message.length > 0) {
                        const item_codes = response.message.map(asset => asset.item_code);

                        // Set the filter for the child table's Required Item field
                        frm.fields_dict['required_equipments'].grid.get_field('required_item').get_query = function () {
                            return {
                                filters: {
                                    name: ['in', item_codes] // Filter items based on the fetched item codes
                                }
                            };
                        };
                    }
                }
            });
        }
    }
});
