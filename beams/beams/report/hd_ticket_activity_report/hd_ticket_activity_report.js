// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt


frappe.query_reports["HD Ticket Activity Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "ticket_id",
            "label": __("Ticket ID"),
            "fieldtype": "Link",
            "options": "HD Ticket",
            "reqd": 0
        },
        {
            "fieldname": "user",
            "label": __("User"),
            "fieldtype": "Link",
            "options": "User",
            "reqd": 0
        }
    ]
};