frappe.ui.form.on('Purchase Invoice', {
  setup: function(frm) {
    handle_workflow_button(frm);
  },
  invoice_type: function(frm) {
    if (frm.doc.invoice_type === 'Stringer Bill') {
      frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
        return {
          filters: [
            ["is_stock_item", "=", 0]
          ]
        };
      };
      frm.set_query('supplier', function() {
        return {
          filters: {
            is_stringer: 1
          }
        };
      });
    } else if (frm.doc.invoice_type === 'General') {
      // Clear filters when 'General' is selected
      frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
        return {};
      };
      frm.set_query('supplier', function() {
        return {};
      });
    }

    frm.clear_table('stringer_work_details');
    frm.clear_table('items');
    frm.refresh_field('stringer_work_details');
    frm.refresh_field('items');
    frm.set_value('supplier', '');
  },
  supplier: function(frm) {
    if (frm.doc.supplier) {
      frappe.db.get_value('Supplier', frm.doc.supplier, ['is_stringer', 'bureau'], function(r) {
        frm.doc.supplier_bureau = r.bureau;
        frm.refresh_field('supplier_bureau');

        frm.doc.stringer_work_details.forEach(row => {
          if (r.is_stringer && frm.doc.supplier_bureau) {
            frappe.model.set_value(row.doctype, row.name, 'bureau', frm.doc.supplier_bureau);
          }
        });

        frm.refresh_field('stringer_work_details');
      });
    }
  },
  onload: function(frm) {
    // Set the supplier as read-only when reference_id is present (e.g., from Quotation)
    if (frm.doc.quotation) {
      frm.set_df_property('supplier', 'read_only', 1);
    }
  }
});

frappe.ui.form.on('Stringer Work Details', {
  from_time: function(frm, cdt, cdn) {
    validate_time_and_calculate_hours(frm, cdt, cdn);
    validate_row_dates(frm, cdt, cdn);
  },
  to_time: function(frm, cdt, cdn) {
    validate_time_and_calculate_hours(frm, cdt, cdn);
    validate_row_dates(frm, cdt, cdn);
  },
  stringer_work_details_add: function(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (frm.doc.supplier_bureau) {
      frappe.model.set_value(cdt, cdn, 'bureau', frm.doc.supplier_bureau);
    }
  }
});

function validate_time_and_calculate_hours(frm, cdt, cdn) {
  var row = locals[cdt][cdn];
  if (row.from_time && row.to_time) {
    var from_time = new Date(row.from_time);
    var to_time = new Date(row.to_time);

    if (from_time >= to_time) {
      frappe.msgprint(__('From Date and Time cannot be after or equal to To Date and Time.'));
      frappe.model.set_value(cdt, cdn, 'to_time', null);
      frappe.model.set_value(cdt, cdn, 'hrs', 0);
    } else {
      var diff = (to_time - from_time) / (1000 * 60 * 60);
      frappe.model.set_value(cdt, cdn, 'hrs', diff.toFixed(2));
    }
  } else {
    frappe.model.set_value(cdt, cdn, 'hrs', 0);
  }
}

function validate_row_dates(frm, cdt, cdn) {
  var row = locals[cdt][cdn];

  if (row.from_time) {
    let first_row_date = null;
    let current_row_date = new Date(row.from_time).toDateString();

    frm.doc.stringer_work_details.forEach(existing_row => {
      if (existing_row.from_time && !first_row_date) {
        first_row_date = new Date(existing_row.from_time).toDateString();
      }
    });

    if (first_row_date && current_row_date !== first_row_date) {
      frappe.msgprint(__('All rows must have the same date'));
      frappe.model.set_value(cdt, cdn, 'from_time', null);
      frappe.model.set_value(cdt, cdn, 'to_time', null);
    }
  }
}

function handle_workflow_button(frm) {
  //Function to handle the visibility or behavior of workflow buttons
  if (frm.doc.purchase_order_id) {
    $(document).ready(function () {
      var workflow_button = $(".btn.btn-primary.btn-sm[data-toggle='dropdown']");
      workflow_button.html('<span>S<span class="alt-underline">u</span>bmit</span>');
      workflow_button.find("svg").remove();
      workflow_button.on("click", function () {
        frm.savesubmit();
      });
    });
  }
}
