// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.query_reports["Detailed Budget Allocation Report"] = {
    filters: [
        {
            fieldname: "fiscal_year",
            label: "Fiscal Year",
            fieldtype: "Link",
            options: "Fiscal Year",
            reqd: 1
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
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: "\nJan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
            depends_on: "eval: doc.period == 'Monthly'",
        },
        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company")
        },
        {
            fieldname: "region",
            label: "Region",
            fieldtype: "Select",
            options: "\nNational\nGCC"
        },
        {
            fieldname: "department",
            label: "Department",
            fieldtype: "MultiSelectList",
            options: "Department",
            get_data: function (txt) {
                let dept_mult_filters = {}
                if (frappe.query_report.get_filter_value('company')) {
                    dept_mult_filters['company'] = frappe.query_report.get_filter_value('company');
                }
                return frappe.db.get_link_options("Department", txt, dept_mult_filters);
            },
            on_change: function () {
                frappe.query_report.set_filter_value("division", [])
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "division",
            label: "Division",
            fieldtype: "Link",
            options: "Division",
            get_query: function () {
                let div_filters = {}
                if (frappe.query_report.get_filter_value('department').length) {
                    div_filters['department'] = ['in', frappe.query_report.get_filter_value('department')]
                }
                if (frappe.query_report.get_filter_value('company')) {
                    div_filters['company'] = frappe.query_report.get_filter_value('company');
                }
                return {
                    filters: div_filters
                }
            }
        },
        {
            fieldname: "cost_head",
            label: "Cost Head",
            fieldtype: "Link",
            options: "Cost Head",
        },
        {
            fieldname: "cost_subhead",
            label: "Cost Subhead",
            fieldtype: "Link",
            options: "Cost Subhead",
            get_query: function () {
                let csh_filters = {}
                if (frappe.query_report.get_filter_value('cost_head')) {
                    csh_filters['cost_head'] = frappe.query_report.get_filter_value('cost_head');
                }
                return {
                    filters: csh_filters
                }
            }
        },
        {
            fieldname: "cost_category",
            label: "Cost Category",
            fieldtype: "Select",
            options: "\nHR Overheads\nOperational Exp",
        },
        {
            fieldname: "sort_by",
            label: "Sort By",
            fieldtype: "Select",
            options: "ASC\nDESC",
            default: "DESC"
        }
    ],
    tree: true,
    treeView: true,
    name_field: "id",
    parent_field: "parent",
    initial_depth: 4,
    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (data && data.indent < 4) {
            value = $(`<span>${value}</span>`);
            var $value = $(value).css("font-weight", "bold");
            value = $value.wrap("<p></p>").parent().html();
        }
        return value;
    }
};
