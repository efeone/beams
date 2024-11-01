frappe.listview_settings["Local Enquiry Report"] = {
    has_indicator_for_draft: 1,
    add_fields: ["status", "workflow_state"],
    get_indicator: function (doc) {
        if (doc.status === "Overdue") {
            return [__("Overdue"), "red", "status,=,Overdue"];
        }
        else {
            if (doc.workflow_state === "Pending Approval") {
                return [__("Pending Approval"), "orange", "status,=,Pending Approval"];
            } else if (doc.workflow_state === "Draft") {
                return [__("Draft"), "blue", "status,=,Draft"];
            } else if (doc.workflow_state === "Assigned to Admin") {
                return [__("Assigned to Admin"), "purple", "status,=,Assigned to Admin"];
            } else if (doc.workflow_state === "Assigned to Enquiry Officer") {
                return [__("Assigned to Enquiry Officer"), "cyan", "status,=,Assigned to Enquiry Officer"];
            } else if (doc.workflow_state === "Enquiry on Progress") {
                return [__("Enquiry on Progress"), "yellow", "status,=,Enquiry on Progress"];
            } else if (doc.workflow_state === "Approved") {
                return [__("Approved"), "green", "status,=,Approved"];
            } else if (doc.workflow_state === "Rejected") {
                return [__("Rejected"), "red", "status,=,Rejected"];
            }
        }
    }
};
