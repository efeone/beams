// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.query_reports["Budget Allocation"] = {
    filters: get_filters(),
    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname.includes(__("variance"))) {
            if (data[column.fieldname] < 0) {
                value = "<span style='color:red'>" + value + "</span>";
            } else if (data[column.fieldname] > 0) {
                value = "<span style='color:green'>" + value + "</span>";
            }
        }

        return value;
    },
    after_datatable_render: function (datatable) {
        let data = frappe.query_report.data;
        if (!data || !data.length) return;

        let columns = frappe.query_report.columns;
        let total_row = {};

        // Check if total row already exists
        let first_column = columns[0]?.fieldname;
        let total_row_exists = data.some(row => row[first_column] === __("Total"));
        if (total_row_exists) return;

        columns.forEach((col) => {
            if (col.fieldtype === "Currency" || col.fieldtype === "Float") {
                total_row[col.fieldname] = data.reduce((sum, row) => sum + (row[col.fieldname] || 0), 0);
            } else {
                total_row[col.fieldname] = col.fieldname === first_column ? __("Total") : "";
            }
        });

        data.push(total_row);
        datatable.refresh(data);
    }
};

function get_filters() {
    function get_dimensions() {
        let result = [];
        frappe.call({
            method: "erpnext.accounts.doctype.accounting_dimension.accounting_dimension.get_dimensions",
            args: {
                with_cost_center_and_project: true,
            },
            async: false,
            callback: function (r) {
                if (!r.exc) {
                    result = r.message[0].map((elem) => elem.document_type);
                }
            },
        });
        return result;
    }

    let budget_against_options = get_dimensions();

    let filters = [
        {
            fieldname: "from_fiscal_year",
            label: __("From Fiscal Year"),
            fieldtype: "Link",
            options: "Fiscal Year",
            default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
            reqd: 1,
        },
        {
            fieldname: "to_fiscal_year",
            label: __("To Fiscal Year"),
            fieldtype: "Link",
            options: "Fiscal Year",
            default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
            reqd: 1,
        },
        {
            fieldname: "period",
            label: __("Period"),
            fieldtype: "Select",
            options: [
                { value: "Monthly", label: __("Monthly") },
                { value: "Quarterly", label: __("Quarterly") },
                { value: "Half-Yearly", label: __("Half-Yearly") },
                { value: "Yearly", label: __("Yearly") },
            ],
            default: "Yearly",
            reqd: 1,
        },
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1,
        },
        {
            fieldname: "budget_against",
            label: __("Budget Against"),
            fieldtype: "Select",
            options: budget_against_options,
            default: "Cost Center",
            reqd: 1,
            on_change: function () {
                frappe.query_report.set_filter_value("budget_against_filter", []);
                frappe.query_report.refresh();
            },
        },
        {
            fieldname: "budget_against_filter",
            label: __("Dimension Filter"),
            fieldtype: "MultiSelectList",
            get_data: function (txt) {
                if (!frappe.query_report.filters) return;

                let budget_against = frappe.query_report.get_filter_value("budget_against");
                if (!budget_against) return;

                return frappe.db.get_link_options(budget_against, txt);
            },
        },
        {
            fieldname: "finance_group",
            label: __("Finance Group"),
            fieldtype: "Link",
            options: "Finance Group"
        },
        {
            fieldname: "cost_head",
            label: __("Cost Head"),
            fieldtype: "Link",
            options: "Cost Head"
        },
        {
            fieldname: "cost_subhead",
            label: __("Cost Subhead"),
            fieldtype: "Link",
            options: "Cost Subhead"
        },
        {
            fieldname: "cost_category",
            label: __("Cost Category"),
            fieldtype: "Link",
            options: "Cost Category"
        }
    ];

    return filters;
}