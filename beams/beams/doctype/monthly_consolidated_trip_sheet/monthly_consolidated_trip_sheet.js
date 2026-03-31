// Copyright (c) 2026, efeone and contributors
// For license information, please see license.txt


frappe.ui.form.on('Monthly Consolidated Trip Sheet', {
    onload(frm) {
        set_yeat(frm);
        set_supplier_filter(frm);
        add_create_journal_entry_button(frm);
    },
    refresh(frm) {
        add_create_journal_entry_button(frm);
        calculate_batta_totals(frm);
    },
    fetch_trip_sheets_btn: function(frm) {
        run_fetch_trip_sheets(frm);
    },
    fuel_rate__litre: function(frm) {
        calculate_fuel_expense(frm);
    },
    monthly_consolidated_trip_sheet_details_on_form_rendered: function(frm, cdt, cdn) {
        calculate_batta_totals(frm);
        calculate_fuel_expense(frm);
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

// Fetch Bureau Trip Sheets (used by the Fetch Trip Sheets button below Month field)
function run_fetch_trip_sheets(frm) {
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

                let existing = (frm.doc.monthly_consolidated_trip_sheet_details || [])
                    .map(d => d.bureau_trip_sheet);

                let added_count = 0;

                (r.message || []).forEach(function(row) {
                    if (!existing.includes(row.bureau_trip_sheet)) {

                        let child = frm.add_child("monthly_consolidated_trip_sheet_details");

                        Object.assign(child, row);
                        child.is_processed = 0;

                        added_count++;
                    }
                });

                frm.refresh_field("monthly_consolidated_trip_sheet_details");

                calculate_batta_totals(frm);
                calculate_fuel_expense(frm);

                frappe.show_alert({
                    message: __("Added {0} new trip sheet(s).", [added_count]),
                    indicator: "green"
                });

            } else {
                frappe.msgprint(__("No new trip sheets found."));
            }
        }
    });
}

// Create Journal Entry: debits batta/OT after advances + fuel expense; credit fuel log only (advance netted in batta/OT)
function add_create_journal_entry_button(frm) {
    if (!frm.is_new()) {
        frm.add_custom_button(__("Create Journal Entry"), function() {
            frappe.call({
                method: "beams.beams.doctype.monthly_consolidated_trip_sheet.monthly_consolidated_trip_sheet.create_journal_entry",
                args: { monthly_consolidated_trip_sheet_name: frm.doc.name },
                callback: function(r) {
                    if (r.message) {
                        frappe.set_route("Form", "Journal Entry", r.message);
                    }
                }
            });
        });
    }
}

// Sum totals; per row: deduct amount_received_driver from batta first, then from OT
function calculate_batta_totals(frm) {
    var total_batta = 0;
    var total_ot_batta = 0;
    var total_amount_received_driver = 0;
    var total_batta_after = 0;
    var total_ot_after = 0;
    (frm.doc.monthly_consolidated_trip_sheet_details || []).forEach(function(row) {
        var batta = flt(row.total_batta);
        var ot = flt(row.total_ot_batta);
        var advance = flt(row.amount_received_driver);
        total_batta += batta;
        total_ot_batta += ot;
        total_amount_received_driver += advance;
        var remaining_after_batta = Math.max(0, advance - batta);
        var batta_after = Math.max(0, batta - advance);
        var ot_after = Math.max(0, ot - remaining_after_batta);
        frappe.model.set_value(
            row.doctype,
            row.name,
            "total_batta_amount_after_advances",
            batta_after
        );
        frappe.model.set_value(
            row.doctype,
            row.name,
            "total_ot_amount_after_advances",
            ot_after
        );
        total_batta_after += batta_after;
        total_ot_after += ot_after;
    });
    frm.set_value("total_batta", total_batta);
    frm.set_value("total_ot_batta", total_ot_batta);
    frm.set_value("total_amount_received_driver", total_amount_received_driver);
    frm.set_value("total_batta_amount_after_advances", total_batta_after);
    frm.set_value("total_ot_amount_after_advances", total_ot_after);
    frm.refresh_field("total_batta");
    frm.refresh_field("total_ot_batta");
    frm.refresh_field("total_amount_received_driver");
    frm.refresh_field("total_batta_amount_after_advances");
    frm.refresh_field("total_ot_amount_after_advances");
}

// Calculate fuel expense of monthly_consolidated_trip_sheet_details
function calculate_fuel_expense(frm) {

    let fuel_rate__litre = frm.doc.fuel_rate__litre || 0;
    let total_fuel = 0;
    let total_distance_travelledkm = 0;
    let avg_mileage = 0;

    (frm.doc.monthly_consolidated_trip_sheet_details || []).forEach(row => {
        total_fuel += row.fuel_consumption_l || 0;
        total_distance_travelledkm += row.distance_travelledkm || 0;
        avg_mileage = row.average_mileage_kmpl;
    });

    frm.set_value("total_fuel_consumed", total_fuel);
    frm.set_value("total_distance_travelled", total_distance_travelledkm);

    let total_expense = fuel_rate__litre * total_fuel;

    frm.set_value("total_fuel_expense", total_expense);
    frm.set_value("avg_mileage", avg_mileage)

    frm.refresh_field("total_distance_travelled");
    frm.refresh_field("total_fuel_consumed");
    frm.refresh_field("total_fuel_expense");
    frm.refresh_field("avg_mileage");
}