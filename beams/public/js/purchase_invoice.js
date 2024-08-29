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
          "filters": {
            is_stringer: 1
          }
        };
      });
    }
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
  }
});

frappe.ui.form.on('Stringer Work Details', {
  from_time: function (frm, cdt, cdn) {
    calculate_hours(frm, cdt, cdn);
  },
  to_time: function (frm, cdt, cdn) {
    calculate_hours(frm, cdt, cdn);
  },
  stringer_work_details_add: function(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (frm.doc.supplier_bureau) {
      frappe.model.set_value(cdt, cdn, 'bureau', frm.doc.supplier_bureau);
    }
  }
});

function calculate_hours(frm, cdt, cdn) {
  /**
  * Function to calculate hours based on from time and to time.
  */
  var row = locals[cdt][cdn];
  if (row.from_time && row.to_time) {
    var from_time = new Date(row.from_time);
    var to_time = new Date(row.to_time);
    var diff = (to_time - from_time) / (1000 * 60 * 60);
    frappe.model.set_value(cdt, cdn, 'hrs', diff.toFixed(2));
  } else {
    frappe.model.set_value(cdt, cdn, 'hrs', 0);
  }
}

function handle_workflow_button(frm) {
  if (frm.doc.purchase_order_id) {
    $(document).ready(function () {
        var workflow_button = $(".btn.btn-primary.btn-sm[data-toggle='dropdown']");
           workflow_button
           .html('<span>S<span class="alt-underline">u</span>bmit</span>');
        workflow_button.find("svg").remove();
        workflow_button.on("click", function () {
          frm.savesubmit();
        });
    });
  }
}
