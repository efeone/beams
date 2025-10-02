// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Safety Inspection", {
    refresh(frm) {
        frm.set_query("vehicle", () => {
            return {
                filters: {
                    vehicle_safety_inspection: "",
                }
            };
        });
    }
});

