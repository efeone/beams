frappe.ui.form.on("Appraisal Template", {
    refresh: function(frm) {
        hide_marks_field(frm);
    }
});

function hide_marks_field(frm) {
   /**
   * Dynamically updates the "rating" and "marks" fields to be hidden 
   * for multiple child tables in the Appraisal  Template doctype.
   */
    ["company_rating_criteria", "department_rating_criteria", "rating_criteria"].forEach(table_name => {
        if (frm.fields_dict[table_name]) {
            frm.fields_dict[table_name].grid.update_docfield_property("marks", "hidden", 1);
            frm.fields_dict[table_name].grid.update_docfield_property("marks", "in_list_view", 0);
            frm.fields_dict[table_name].grid.update_docfield_property("rating", "hidden", 1);
            frm.fields_dict[table_name].grid.update_docfield_property("rating", "in_list_view", 0);
            frm.refresh_field(table_name);
        }
    });
}
