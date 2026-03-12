// Copyright (c) 2026, efeone and contributors
// For license information, please see license.txt


frappe.ui.form.on('Monthly Consolidated Trip Sheet', {
    onload(frm) {
        set_yeat(frm);
        set_supplier_filter(frm);
        add_fetch_trip_sheets_button(frm);
    },
    refresh(frm) {
        add_fetch_trip_sheets_button(frm);
    },
    fuel_rate__litre: function(frm) {
        calculate_fuel_expense(frm)
    }
});

// Set default year to current year on new document creation
function set_yeat(frm) {
    if (frm.is_new()) {
        frm.set_value("year", frappe.datetime.get_today().split("-")[0]);
    }
}

// Filter supplier field to show only transporters
function set_supplier_filter(frm) {
    frm.set_query("supplier", function() {
        return {
            filters: {
                is_transporter: 1
            }
        };
    });
}

// Button to fetch Bureau Trip Sheets for the selected supplier, bureau, month and year
function add_fetch_trip_sheets_button(frm) {
    frm.add_custom_button(__("Fetch Trip Sheets"), function() {
        if (!frm.doc.supplier || !frm.doc.bureau || !frm.doc.month || !frm.doc.year) {
            frappe.msgprint(__("Please set Supplier, Bureau, Month and Year first."));
            return;
        }
        frappe.call({
            method: "beams.beams.doctype.monthly_consolidated_trip_sheet.monthly_consolidated_trip_sheet.fetch_trip_sheets",
            args: {
                supplier: frm.doc.supplier,
                bureau: frm.doc.bureau,
                month: frm.doc.month,
                year: frm.doc.year
            },
            callback: function(r) {
                if (r.message && r.message.length) {
                    frm.clear_table("monthly_consolidated_trip_sheet_details");
                    (r.message || []).forEach(function(row) {
                        frm.add_child("monthly_consolidated_trip_sheet_details", row);
                    });
                    frm.refresh_field("monthly_consolidated_trip_sheet_details");
                    frappe.show_alert({ message: __("Fetched {0} trip sheet(s).", [r.message.length]), indicator: "green" });
                } else {
                    frappe.msgprint(__("No trip sheets found for the selected criteria."));
                }
            }
        });
    });
}

// calculate fuel expense of monthly_consolidated_trip_sheet_details
function calculate_fuel_expense(frm) {

    let fuel_rate__litre = frm.doc.fuel_rate__litre || 0;
    let total_fuel = 0;

    (frm.doc.monthly_consolidated_trip_sheet_details || []).forEach(row => {
        total_fuel += row.fuel_consumption_l || 0;
    });

    frm.set_value("total_fuel_consumed", total_fuel);

    let total_expense = fuel_rate__litre * total_fuel;

    frm.set_value("total_fuel_expense", total_expense);
}