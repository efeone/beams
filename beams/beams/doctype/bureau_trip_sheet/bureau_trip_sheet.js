frappe.ui.form.on("Bureau Trip Sheet", {
    refresh: function (frm) {
        filter_supplier_field(frm);
    },

    is_overnight_stay: function (frm) {
        update_daily_batta(frm);
    },

    is_travelling_outside_kerala: function (frm) {
        update_daily_batta(frm);
    },

    driver: function (frm) {
        update_daily_batta(frm);
    }
});

// Function to filter the supplier field
function filter_supplier_field(frm) {
    frm.set_query("supplier", function () {
        return {
            filters: {
                is_transporter: 1
            }
        };
    });
}
