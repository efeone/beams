frappe.ui.form.on('Purchase Invoice', {
    refresh(frm) {
        handle_workflow_button(frm);
    }
});

function handle_workflow_button(frm) {
  // Check if the 'purchase_order_id' field exists in the form
  if (frm.doc.purchase_order_id) {
    $(document).ready(function () {
        // Select the workflow button based on its class and data attributes
        var workflow_button = $(".btn.btn-primary.btn-sm[data-toggle='dropdown']");

        // Modify the workflow button: remove unnecessary attributes and update it to a submit button
        workflow_button
          .removeAttr("data-toggle")
          .removeAttr("aria-expanded")
          .attr("data-label", "Submit")
          .addClass("primary-action")
          .html('<span>S<span class="alt-underline">u</span>bmit</span>');

        // Remove any SVG elements (e.g., icons) from the button
        workflow_button.find("svg").remove();
        workflow_button.on("click", function () {
          frm.savesubmit();
        });
    });
  }
}
