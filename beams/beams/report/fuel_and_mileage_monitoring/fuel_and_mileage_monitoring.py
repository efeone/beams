# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    filters = filters or {}

    conditions = {"docstatus": 1}
    
    if filters.get("vehicle"):
        conditions["vehicle"] = filters["vehicle"]
    if filters.get("driver"):
        conditions["driver"] = filters["driver"]
    if filters.get("fuel_consumed"):
        conditions["fuel_consumed"] = filters["fuel_consumed"]
    if filters.get("mileage"):
        conditions["mileage"] = filters["mileage"]

    data = frappe.get_all(
        "Trip Sheet",
        filters=conditions,
        fields=[
            "vehicle",
            "final_odometer_reading",
            "distance_traveledkm",
            "fuel_consumed",
            "mileage",
            "posting_date",
            "driver"
        ],
        order_by="posting_date desc"
    )

    columns = [
        {"label": "Vehicle", "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "width": 150},
        {"label": "Odometer Reading", "fieldname": "final_odometer_reading", "fieldtype": "Int", "width": 180},
        {"label": "Distance Traveled (km)", "fieldname": "distance_traveledkm", "fieldtype": "Float", "width": 180},
        {"label": "Fuel Consumed (L)", "fieldname": "fuel_consumed", "fieldtype": "Float", "width": 180},
        {"label": "Mileage (km/L)", "fieldname": "mileage", "fieldtype": "Float", "width": 180},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 180},
        {"label": "Driver", "fieldname": "driver", "fieldtype": "Data", "width": 180}
    ]

    return columns, data
