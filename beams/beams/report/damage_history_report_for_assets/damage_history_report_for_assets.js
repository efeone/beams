// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.query_reports["Damage History Report for Assets"] = {
	"filters": [
				{
						fieldname: "asset",
						label: __("Asset"),
						fieldtype: "Link",
						options: "Asset"
				},
				{
						fieldname: "location",
						label: __("Location"),
						fieldtype: "Data",
				},
				{
						fieldname: "audit_id",
						label: __("Audit ID"),
						fieldtype: "Link",
						options: "Asset Auditing",
				},
				{
						fieldname: "repair_status",
						label: __("Repair Status"),
						fieldtype: "Select",
						options: ["", "Pending", "Completed", "cancelled"],
				},
				{
						fieldname: "repair_id",
						label: __("Asset Repair ID"),
						fieldtype: "Link",
						options: "Asset Repair",
				},
				{
						fieldname: "employee",
						label: __("Employee"),
						fieldtype: "Link",
						options: "Employee",
				}
	]
};
