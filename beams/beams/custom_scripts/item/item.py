import frappe

@frappe.whitelist()
def before_insert(doc, method):
    """Before inserting an Item, fetch 'Hireable' from Item Group if not set and create a Service Item if required."""

    if not doc.hireable and doc.item_group:
        doc.hireable = frappe.db.get_value("Item Group", doc.item_group, "hireable")

    if doc.hireable and "-Service" not in doc.item_code:
        service_item = create_service_item(doc)
        doc.service_item = service_item

def create_service_item(doc):
    """Creates a Service Item and ensures 'Hireable' is disabled."""

    service_item_code = f"{doc.item_code}-Service"
    if frappe.db.exists("Item", service_item_code):
        return service_item_code


    service_item = frappe.get_doc({
        "doctype": "Item",
        "item_code": service_item_code,
        "item_name": f"{doc.item_name} (Service)",
        "description": doc.description,
        "item_group": doc.item_group,
        "stock_uom": doc.stock_uom,
        "is_stock_item": 0,
        "is_sales_item": 1,
        "is_service_item": 1,
        "hireable": 0
    })

    service_item.insert(ignore_permissions=True)
    frappe.db.set_value("Item", service_item.name, "hireable", 0)
    return service_item.name
