// // Copyright (c) 2025, efeone and contributors
// // For license information, please see license.txt

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
    },
    required_from: function (frm) {
        validate_dates(frm);
    },
    required_to: function (frm) {
        validate_dates(frm);
    },
    validate: function (frm) {
        validate_dates(frm);
    }
});

// Helper function to validate dates
function validate_dates(frm) {
    if (frm.doc.required_from && frm.doc.required_to) {
        if (frm.doc.required_from > frm.doc.required_to) {
            frappe.throw(__('The "Required From" date cannot be after the "Required To" date.'));
        }
    }
}
