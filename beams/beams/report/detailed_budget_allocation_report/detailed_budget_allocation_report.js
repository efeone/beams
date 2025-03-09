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
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company",
        },
        {
            fieldname: "finance_group",
            label: "Finance Group",
            fieldtype: "Link",
            options: "Finance Group",
        },
        {
            fieldname: "department",
            label: "Department",
            fieldtype: "Link",
            options: "Department",
            get_query: function () {
                let dept_filters = {}
                if (frappe.query_report.get_filter_value('finance_group')) {
                    dept_filters['finance_group'] = frappe.query_report.get_filter_value('finance_group');
                }
                if (frappe.query_report.get_filter_value('company')) {
                    dept_filters['company'] = frappe.query_report.get_filter_value('company');
                }
                return {
                    filters: dept_filters
                }
            }
        },
        {
            fieldname: "division",
            label: "Division",
            fieldtype: "Link",
            options: "Division",
            get_query: function () {
                let div_filters = {}
                if (frappe.query_report.get_filter_value('department')) {
                    div_filters['department'] = frappe.query_report.get_filter_value('department');
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
            fieldtype: "Link",
            options: "Cost Category",
        }
    ],
    tree: true,
    treeView: true,
    name_field: "id",
    parent_field: "parent",
    initial_depth: 1,
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
