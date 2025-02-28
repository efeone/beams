# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Asset", "fieldname": "asset", "fieldtype": "Link", "options": "Asset", "width": 200},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
        {"label": "Total Asset Cost", "fieldname": "total_asset_cost", "fieldtype": "Currency", "width": 150},
        {"label": "Location", "fieldname": "location", "fieldtype": "Data", "width": 200},
        {"label": "Audit ID", "fieldname": "audit_id", "fieldtype": "Link", "options": "Asset Auditing", "width": 150},
        {"label": "Has Damage", "fieldname": "has_damage", "fieldtype": "Data", "width": 100},
        {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 300},
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 200},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 200},
        {"label": "Asset Repair ID", "fieldname": "repair_id", "fieldtype": "Link", "options": "Asset Repair", "width": 150},
        {"label": "Description", "fieldname": "description", "fieldtype": "Data", "width": 250},
        {"label": "Repair Cost", "fieldname": "repair_cost", "fieldtype": "Currency", "width": 150},
        {"label": "Failure Date", "fieldname": "failure_date", "fieldtype": "Date", "width": 150},
        {"label": "Repair Status", "fieldname": "repair_status", "fieldtype": "Select", "width": 150}
    ]

def get_data(filters):
    data = []
    asset_filters = {}
    if filters.get("asset"):
        asset_filters["name"] = filters["asset"]
    if filters.get("item_code"):
        asset_filters["item_code"] = filters["item_code"]
    if filters.get("location"):
        asset_filters["location"] = filters["location"]
    asset_auditing_filters = {}
    if filters.get("employee"):
        asset_auditing_filters["employee"] = filters["employee"]
    if filters.get("audit_id"):
        asset_auditing_filters["name"] = filters["audit_id"]
    repair_filters = {}
    if filters.get("repair_status"):
        repair_filters["repair_status"] = filters["repair_status"]
    if filters.get("repair_id"):
        repair_filters["name"] = filters["repair_id"]
    assets = frappe.get_all("Asset", fields=["name as asset", "item_code", "total_asset_cost", "location"], filters=asset_filters if asset_filters else None)
    for asset in assets:
        audits = frappe.get_all(
            "Asset Auditing",
            filters={"asset": asset["asset"], **asset_auditing_filters},
            fields=["name as audit_id", "has_damage", "remarks", "employee", "posting_date"]
        )
        repairs = frappe.get_all(
            "Asset Repair",
            filters={"asset": asset["asset"], **repair_filters},
            fields=["name as repair_id", "description", "repair_cost", "failure_date", "repair_status"]
        )
        if not audits:
            audits = [{"audit_id": None, "has_damage": None, "remarks": None, "employee": None, "posting_date": None}]
        if not repairs:
            repairs = [{"repair_id": None, "description": None, "repair_cost": None, "failure_date": None, "repair_status": None}]
        for audit in audits:
            for repair in repairs:
                row = {
                    "asset": asset["asset"],
                    "item_code": asset["item_code"],
                    "total_asset_cost": asset["total_asset_cost"],
                    "location": asset["location"],
                    "audit_id": audit["audit_id"],
                    "has_damage": "Yes" if audit["has_damage"] else "No" if audit["has_damage"] is not None else None,
                    "remarks": audit["remarks"],
                    "employee": audit["employee"],
                    "posting_date": audit["posting_date"],
                    "repair_id": repair.get("repair_id"),
                    "description": repair.get("description"),
                    "repair_cost": repair.get("repair_cost"),
                    "failure_date": repair.get("failure_date"),
                    "repair_status": repair.get("repair_status")
                }
                if (filters.get("repair_id") and not row["repair_id"]) or \
                   (filters.get("repair_status") and not row["repair_status"]) or \
                   (filters.get("employee") and not row["employee"]) or \
                   (filters.get("audit_id") and not row["audit_id"]):
                    continue
                data.append(row)

    return data
