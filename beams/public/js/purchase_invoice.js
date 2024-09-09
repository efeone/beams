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
    }else if (frm.doc.invoice_type === 'Normal') {
      // Clear filters when 'General' is selected
      frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
        return {};
      };
      frm.set_query('supplier', function() {
        return {};
      });
    }

    frm.clear_table('items');
    frm.refresh_field('items');
    frm.set_value('supplier', '');
  },
  supplier: function(frm) {
    if (frm.doc.supplier) {
      frappe.db.get_value('Supplier', frm.doc.supplier, ['is_stringer', 'bureau'], function(r) {
        frm.doc.supplier_bureau = r.bureau;
        frm.refresh_field('supplier_bureau');
      });
    }
  }
});

function handle_workflow_button(frm) {
  // Function to handle the visibility or behavior of workflow buttons
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
