// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.query_reports["Budget Allocation"] = {
    "filters": [
        {
            "fieldname": "fiscal_year",
            "label": __("Fiscal Year"),
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "default": "",
            "width": "100px"
        }
    ],
    onload: function(report) {
        get_current_fiscal_year(report);
    }
};

// Function to get the current fiscal year
async function get_current_fiscal_year(report) {
    const today = frappe.datetime.get_today();

    try {
        const r = await frappe.db.get_value('Fiscal Year', {
            year_start_date: ["<=", today],
            year_end_date: [">=", today]
        }, 'name');

        // Check if a valid fiscal year is returned
        if (r && r.message && r.message.name) {
            report.filters[0].default = r.message.name;
            report.filters[0].set_input(r.message.name);
            report.refresh();
        } else {
            console.warn("No fiscal year found for today's date:", today); // Warning if no fiscal year is found
        }
    } catch (err) {
        console.error("Error fetching fiscal year:", err); // Log any errors
    }
}
