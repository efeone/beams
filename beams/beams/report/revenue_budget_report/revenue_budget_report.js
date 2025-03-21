// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.query_reports["Revenue Budget Report"] = {
    "filters": [
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
            fieldname: "revenue_region",
            label: "Revenue Region",
            fieldtype: "Select",
            options: "\nNational\nGCC"
        },
        {
            fieldname: "revenue_category",
            label: "Revenue Category",
            fieldtype: "Link",
            options: "Revenue Category"
        },
        {
            fieldname: "revenue_centre",
            label: "Revenue Centre",
            fieldtype: "Link",
            options: "Revenue Centre"
        },
        {
            fieldname: "revenue_group",
            label: "Revenue Group",
            fieldtype: "Link",
            options: "Revenue Group"
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
    initial_depth: 4
};