// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.query_reports["Fuel and Mileage Monitoring"] = {
    "filters": [
        {
            "fieldname": "vehicle",
            "label": "Vehicle",
            "fieldtype": "Link",
            "options": "Vehicle",
            "width": 120
        },
        {
            "fieldname": "driver",
            "label": "Driver",
            "fieldtype": "Link",
            "options": "Driver",
            "width": 120
        },
        {
            "fieldname": "fuel_consumed",
            "label": "Fuel Consumed",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "mileage",
            "label": "Mileage (km/L)",
            "fieldtype": "Float",
            "width": 120
        }
    ]
};
