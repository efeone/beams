// Copyright (c) 2026, efeone and contributors
// For license information, please see license.txt


frappe.ui.form.on('Monthly Consolidated Trip Sheet', {
    onload(frm) {
        set_yeat(frm);
        set_supplier_filter(frm);
        add_fetch_trip_sheets_button(frm);
        add_create_purchase_invoice_button(frm);
    },
    refresh(frm) {
        add_fetch_trip_sheets_button(frm);
        add_create_purchase_invoice_button(frm);
        calculate_batta_totals(frm);
    },
    fuel_rate__litre: function(frm) {
        calculate_fuel_expense(frm);
    },
    monthly_consolidated_trip_sheet_details_on_form_rendered: function(frm, cdt, cdn) {
        calculate_batta_totals(frm);
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
                    calculate_batta_totals(frm);
                    calculate_fuel_expense(frm);
                    frappe.show_alert({ message: __("Fetched {0} trip sheet(s).", [r.message.length]), indicator: "green" });
                } else {
                    frappe.msgprint(__("No trip sheets found for the selected criteria."));
                }
            }
        });
    });
}

// Create Purchase Invoice: open popup with items/rates from Beams Accounts Settings and doc totals
function add_create_purchase_invoice_button(frm) {
    frm.add_custom_button(__("Create Purchase Invoice"), function() {
        if (frm.is_dirty()) {
            frappe.msgprint(__("Please save the document first."));
            return;
        }
        if (!frm.doc.name) {
            frappe.msgprint(__("Please save the document first."));
            return;
        }
        frappe.call({
            method: "beams.beams.doctype.monthly_consolidated_trip_sheet.monthly_consolidated_trip_sheet.get_purchase_invoice_details",
            args: { monthly_consolidated_trip_sheet_name: frm.doc.name },
            callback: function(r) {
                if (r.message && r.message.items && r.message.items.length) {
                    show_create_pi_dialog(frm, r.message);
                } else {
                    frappe.msgprint(
                        __("No expense items to show. Open Beams Accounts Settings, go to the Bureau Trip Sheet Settings tab, and set at least one of: Batta Expense Item, Fuel Expense Item, Rent Expense Item, Batta Ot Expense Item. Save the settings and try again."),
                        __("Settings required")
                    );
                }
            }
        });
    });
}

function show_create_pi_dialog(frm, details) {
    var table_data = (details.items || []).map(function(row) {
        return {
            expense_type: row.label || "",
            item: row.item_name || row.item_code || "",
            rate: flt(row.rate)
        };
    });

    var d = new frappe.ui.Dialog({
        title: __("Create Purchase Invoice"),
        size: "medium",
        fields: [
            {
                fieldtype: "Table",
                fieldname: "items_table",
                label: __("Invoice lines (from Bureau Trip Sheet Settings)"),
                cannot_add_rows: true,
                in_list_view: 1,
                fields: [
                    {
                        fieldtype: "Data",
                        fieldname: "expense_type",
                        label: __("Expense"),
                        read_only: 1,
                        in_list_view: 1
                    },
                    {
                        fieldtype: "Data",
                        fieldname: "item",
                        label: __("Item"),
                        read_only: 1,
                        in_list_view: 1
                    },
                    {
                        fieldtype: "Currency",
                        fieldname: "rate",
                        label: __("Rate"),
                        read_only: 1,
                        in_list_view: 1
                    }
                ],
                data: table_data
            }
        ],
        primary_action_label: __("Create"),
        primary_action: function() {
            d.hide();
            // Open new Purchase Invoice with data pre-filled; user saves manually
            frappe.model.with_doctype("Purchase Invoice", function() {
                var doc = frappe.model.get_new_doc("Purchase Invoice");
                doc.supplier = details.supplier;
                doc.bureau = details.bureau || "";
                doc.company = details.company || frappe.defaults.get_default("company");
                doc.cost_center = details.cost_center || "";
                doc.set_posting_time = 1;
                doc.posting_date = details.posting_date || frappe.datetime.get_today();
                (details.items || []).forEach(function(row) {
                    if (flt(row.rate) === 0) return;
                    var child = frappe.model.add_child(doc, "Purchase Invoice Item", "items");
                    child.item_code = row.item_code;
                    child.qty = 1;
                    child.rate = flt(row.rate);
                });
                frappe.set_route("Form", "Purchase Invoice", doc.name);
            });
        }
    });
    d.show();
}

// Sum total_batta, total_ot_batta and amount_received_driver from child rows
function calculate_batta_totals(frm) {
    var total_batta = 0;
    var total_ot_batta = 0;
    var total_amount_received_driver = 0;
    (frm.doc.monthly_consolidated_trip_sheet_details || []).forEach(function(row) {
        total_batta += flt(row.total_batta);
        total_ot_batta += flt(row.total_ot_batta);
        total_amount_received_driver += flt(row.amount_received_driver);
    });
    frm.set_value("total_batta", total_batta);
    frm.set_value("total_ot_batta", total_ot_batta);
    frm.set_value("total_amount_received_driver", total_amount_received_driver);
    frm.refresh_field("total_batta");
    frm.refresh_field("total_ot_batta");
    frm.refresh_field("total_amount_received_driver");
}

// Calculate fuel expense of monthly_consolidated_trip_sheet_details
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