frappe.listview_settings["Purchase Invoice"] = {
    /*
    * The code sets the list view settings for the Purchase Invoice doctype, adding custom status indicators based on
    * the invoice's status and workflow state. These indicators visually distinguish invoices as Paid, Unpaid,
    * Partly Paid, Overdue, etc.
    */
    has_indicator_for_draft: 1,
    add_fields: ["status", "workflow_state"],
    get_indicator: function (doc) {
        if (doc.workflow_state === "Approved"|| doc.workflow_state == "Submitted") {
            if (doc.status === "Paid") {
                return [__("Paid"), "green", "status,=,Paid"];
            } else if (doc.status === "Unpaid") {
                return [__("Unpaid"), "orange", "status,=,Unpaid"];
            } else if (doc.status === "Partly Paid") {
                return [__("Partly Paid"), "yellow", "status,=,Partly Paid"];
            } else if (doc.status === "Overdue") {
                return [__("Overdue"), "red", "status,=,Overdue"];
            }
        }
        else {
            if (doc.workflow_state === "Pending Approval") {
                return [__("Pending Approval"), "orange", "status,=,Pending Approval"];
            } else if (doc.workflow_state === "Draft") {
                return [__("Draft"), "blue", "status,=,Draft"];
            } else if (doc.workflow_state === "Rejected") {
                return [__("Rejected"), "red", "status,=,Rejected"];
            } else if (doc.workflow_state === "Cancelled") {
                return [__("Cancelled"), "red", "status,=,Cancelled"];
            }
        }
        return [__("No Status"), "gray", ""];
    }
};
