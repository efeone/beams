// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Tool", {
    onload: function (frm) {
        $('.indicator-pill').hide();
        if (!frm.doc.budget) {
            var prev_route = frappe.get_prev_route();
            if (prev_route[1] === 'Budget') {
                frm.set_value('budget', prev_route[2]);
            }
        }
    },
    refresh: function (frm) {
        $('.menu-btn-group').hide();
        $('.indicator-pill').hide();
        frm.disable_save();
        if (!frm.doc.budget) {
            let $el = cur_frm.fields_dict.budget.$wrapper;
            $el.find('input').focus();
        }
        frm.add_custom_button('Reload', () => {
            localStorage.clear();
            frappe.ui.toolbar.clear_cache();
        }).addClass('btn-primary');
    },
    budget: function (frm) {
        if (frm.doc.budget) {
            set_budget_html(frm, frm.doc.budget);
        }
        else {
            frm.clear_custom_buttons();
            $(frm.fields_dict['budget_html'].wrapper).html('');
            frm.set_value('has_unsaved_changes', 0);
            refresh_field('budget_html');
        }
    },
    has_unsaved_changes: function (frm) {
        make_buttons(frm);
    },
    add_row: function (frm) {
        show_add_row_popup(frm);
    }
});

function set_budget_html(frm, budget) {
    frappe.call({
        method: 'beams.beams.doctype.budget_tool.budget_tool.get_budget_html',
        args: {
            'budget': frm.doc.budget
        },
        freeze: true,
        freeze_message: __('Loading......'),
        callback: (r) => {
            if (r.message) {
                var data = r.message;
                $(frm.fields_dict['budget_html'].wrapper).html(data.html);
                frm.set_value('has_unsaved_changes', 0);
                frm.set_value('is_editable', data.is_editable);
                frm.refresh_fields();
                make_buttons(frm);
            }
        }
    });
}

function make_buttons(frm) {
    frm.clear_custom_buttons();
    if (frm.doc.budget) {
        if (frm.doc.has_unsaved_changes) {
            frm.add_custom_button('Save', () => {
                saveData(frm);
            }).addClass('btn-primary saveBtn');
        }
        frm.add_custom_button('Open Budget', () => {
            frappe.set_route('Form', 'Budget', frm.doc.budget);
        }).addClass('btn-primary saveBtn');
    }
    frm.add_custom_button('Reload', () => {
        localStorage.clear();
        frappe.ui.toolbar.clear_cache();
    }).addClass('btn-primary saveBtn');
}

function saveData(frm) {
    var table = document.getElementById("data-table").getElementsByTagName('tbody')[0];
    var data = [];
    for (var i = 0; i < table.rows.length; i++) {
        var row = table.rows.item(i).cells;
        var data_row = []
        for (var j = 0; j < row.length; j++) {
            var val = row.item(j).innerHTML;
            //Remove html tags from primary columns
            if (j > 0 && j < 5) {
                var div = document.createElement("div");
                div.innerHTML = val;
                var text = div.textContent || div.innerText || "";
                data_row.push(text)
            }
            else {
                data_row.push(val)
            }
        }
        if (data_row[1]) {
            data.push(data_row)
        }
    }
    var jsonData = JSON.stringify(data);
    frappe.call({
        method: 'beams.beams.doctype.budget_tool.budget_tool.save_budget_data',
        args: {
            'budget': frm.doc.budget,
            'data': jsonData
        },
        freeze: true,
        freeze_message: __("Saving..."),
        callback: (r) => {
            if (r.message) {
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __('Data updated successfully')
                });
                set_budget_html(frm, frm.doc.budget);
            }
        }
    });
}

frappe.ui.keys.on("ctrl+s", function (frm) {
    if (cur_frm.doc.budget) {
        if (cur_frm.doc.has_unsaved_changes) {
            saveData(cur_frm);
        }
    }
    else {
        frappe.show_alert({
            message: __('Nothing to save, Please select Budget'),
            indicator: 'red'
        }, 5);
    }
});

frappe.ui.keys.on("ctrl+i", function (frm) {
    if (cur_frm.doc.budget) {
        show_add_row_popup(cur_frm);
    }
    else {
        frappe.show_alert({
            message: __('Please select Budget'),
            indicator: 'red'
        }, 5);
    }
});

function show_add_row_popup(frm) {
    let d = new frappe.ui.Dialog({
        title: 'Add Budget Row',
        fields: [
            {
                label: 'Cost Head',
                fieldname: 'cost_head',
                fieldtype: 'Link',
                options: 'Cost Head',
                reqd: 1
            },
            {
                label: 'Cost Sub Head',
                fieldname: 'cost_subhead',
                fieldtype: 'Link',
                options: 'Cost Subhead',
                get_query: function () {
                    return {
                        filters: {
                            "cost_head": d.get_value('cost_head')
                        }
                    };
                },
                reqd: 1
            },
            {
                label: 'Cost Category',
                fieldname: 'cost_category',
                fieldtype: 'Link',
                options: 'Cost Category',
                reqd: 1
            }
        ],
        primary_action_label: 'Add',
        primary_action(values) {
            add_row_primary_action(frm, values);
            d.hide();
        }
    });
    d.show();
}

function add_row_primary_action(frm, values) {
    if (frm.doc.budget && values.cost_head && values.cost_subhead && values.cost_category) {
        frappe.call({
            method: 'beams.beams.doctype.budget_tool.budget_tool.add_budget_row',
            args: {
                'budget': frm.doc.budget,
                'cost_head': values.cost_head,
                'cost_subhead': values.cost_subhead,
                'cost_category': values.cost_category,
            },
            freeze: true,
            freeze_message: __("Adding row..."),
            callback: (r) => {
                if (r.message) {
                    frappe.msgprint({
                        title: __('Notification'),
                        indicator: 'green',
                        message: __('Row added successfully')
                    });
                    set_budget_html(frm, frm.doc.budget);
                }
            }
        });
    }
}