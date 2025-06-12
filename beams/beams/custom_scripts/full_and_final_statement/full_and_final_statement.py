import frappe
from frappe import _

@frappe.whitelist()
def fetch_asset_bundles_for_employee(employee):
    '''
        Fetches the latest asset bundles for a given employee.

        This function retrieves all Asset Transfer Requests (ATR)for the employee
        that are marked as "Transferred". It keeps only the latest ATR for each asset
        bundle based on the posting date and creation date.

        Parameters:
            employee (str): The Employee ID for which to fetch asset bundles.

        Returns:
            list: A list of dictionaries containing the following fields:
                - asset_transfer_request: The name of the ATR.
                - asset_bundle: The asset bundle ID.
                - date: The posting date of the ATR.
                - description: A description linking the bundle to the ATR.
    '''
    
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
