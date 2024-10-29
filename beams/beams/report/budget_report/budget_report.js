// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.query_reports["Budget Report"] = {
    "filters": [
        {
            "fieldname": "fiscal_year",
            "label": __("Fiscal Year"),
            "fieldtype": "Link",
            "options": "Fiscal Year",
            // Default value will be set when the report is loaded
            "default": get_current_fiscal_year(),
            "width": "100px"
        }
    ]
};

// Function to get the current fiscal year
function get_current_fiscal_year() {
    let fiscal_year = "";
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Fiscal Year",
            filters: {
                year_start_date: ["<=", frappe.datetime.get_today()],
                year_end_date: [">=", frappe.datetime.get_today()]
            },
            fields: ["name"],
            limit_page_length: 1
        },
        async: false, // Make it synchronous
        callback: function(response) {
            if (response.message && response.message.length > 0) {
                fiscal_year = response.message[0].name; // Get the name of the fiscal year
            }
        }
    });
    return fiscal_year;
}
