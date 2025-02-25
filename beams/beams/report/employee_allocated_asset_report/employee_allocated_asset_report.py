# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 200},
        {"label": "Asset", "fieldname": "asset", "fieldtype": "Link", "options": "Asset", "width": 200},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "Location", "fieldname": "location", "fieldtype": "Data", "width": 200},
        {"label": "Total Asset Cost", "fieldname": "total_asset_cost", "fieldtype": "Currency", "width": 150}
    ]

def get_data(filters):
    data = []
    asset_filters = {}

    if filters.get("employee"):
        asset_filters["custodian"] = filters["employee"]

    assets = frappe.get_all(
        "Asset",
        fields=[
            "custodian as employee",
            "name as asset",
            "item_code",
            "item_name",
            "location",
            "total_asset_cost"
        ],
        filters=asset_filters if asset_filters else None
    )

    for asset in assets:
        row = {
            "employee": asset["employee"],
            "asset": asset["asset"],
            "item_code": asset.get("item_code"),
            "item_name": asset.get("item_name"),
            "location": asset["location"],
            "total_asset_cost": asset["total_asset_cost"]
        }
        data.append(row)

    return data
