// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Allocated Asset Report"] = {
    "filters": [
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee"
        }
    ]
};
