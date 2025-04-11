import frappe
from frappe import _

@frappe.whitelist()
def fetch_asset_bundles_for_employee(employee):
    atrs = frappe.get_all(
        "Asset Transfer Request",
        filters={"employee": employee, "workflow_state": "Transferred"},
        fields=["name", "bundle", "posting_date", "creation"],
        order_by="posting_date desc, creation desc"
    )
    
    bundles = {}
    for atr in atrs:
        if atr.bundle:
            if atr.bundle not in bundles:
                bundles[atr.bundle] = atr
            else:
                current_latest = bundles[atr.bundle]
                if atr.posting_date > current_latest.posting_date or (atr.posting_date == current_latest.posting_date and atr.creation > current_latest.creation):
                    bundles[atr.bundle] = atr

    result = []
    for bundle, latest_atr in bundles.items():
        result.append({
            "asset_transfer_request": latest_atr.name,
            "asset_bundle": bundle,
            "date": latest_atr.posting_date,
            "description": f"Bundle linked to ATR {latest_atr.name}"
        })

    return result
