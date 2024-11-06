frappe.listview_settings["Job Applicant"] = {
    add_fields: ["status"],
    get_indicator: function (doc) {
        if (doc.status === "Selected") {
            return [__("Selected"), "green", "status,=,Selected"];
        } else if (doc.status === "Accepted") {
            return [__("Accepted"), "green", "status,=,Accepted"];
        } else if (doc.status === "Replied") {
            return [__("Replied"), "blue", "status,=,Replied"];
        } else if (doc.status === "Hold") {
            return [__("Hold"), "red", "status,=,Hold"];
        }
    }
};
