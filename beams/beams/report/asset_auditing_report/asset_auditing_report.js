// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.query_reports["Asset Auditing Report"] = {
    "filters": [
        {
            fieldname: "asset",
            label: __("Asset"),
            fieldtype: "Link",
            options: "Asset"
        },
        {
            fieldname: "item_code",
            label: __("Item Code"),
            fieldtype: "Data"
        },
        {
            fieldname: "location",
            label: __("Location"),
            fieldtype: "Data"
        },
        {
            fieldname: "audit_id",
            label: __("Audit ID"),
            fieldtype: "Link",
            options: "Asset Auditing"
        },
        {
            fieldname: "repair_status",
            label: __("Repair Status"),
            fieldtype: "Select",
            options: ["", "Pending", "Completed", "Cancelled"]
        },
        {
            fieldname: "repair_id",
            label: __("Asset Repair ID"),
            fieldtype: "Link",
            options: "Asset Repair"
        },
        {
            fieldname: "employee",
            label: __("Employee"),
            fieldtype: "Link",
            options: "Employee"
        },
        {
            fieldname: "has_damage",
            label: __("Has Damage"),
            fieldtype: "Check"
        }
    ]
};