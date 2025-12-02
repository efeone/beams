frappe.listview_settings["HD Ticket"] = {
    add_fields: ["status"],
    onload: function (listview) {
        frappe.route_options = { "status": "Open" };
    }
};
