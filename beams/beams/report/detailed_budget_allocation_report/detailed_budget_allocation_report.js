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
                return {
                    filters: {
                        'finance_group': frappe.query_report.get_filter_value('finance_group'),
                        'company': frappe.query_report.get_filter_value('company')
                    }
                }
            }
        },
        {
            fieldname: "cost_category",
            label: "Cost Category",
            fieldtype: "Link",
            options: "Cost Category",
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
                return {
                    filters: {
                        'cost_head': frappe.query_report.get_filter_value('cost_head')
                    }
                }
            }
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
