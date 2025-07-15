frappe.ui.form.on("Appraisal Template", {
    refresh: function(frm) {
        hide_marks_field(frm);
        make_rating_criteria_readonly(frm);

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
function make_rating_criteria_readonly(frm) {
    /**
     * Makes the rating_criteria table read-only in the Appraisal Template doctype.
     */
    if (frm.fields_dict["rating_criteria"]) {
        frm.fields_dict["rating_criteria"].grid.cannot_add_rows = true;
        frm.fields_dict["rating_criteria"].grid.cannot_delete_rows = true;
        frm.fields_dict["rating_criteria"].grid.df.read_only = 1;
        frm.refresh_field("rating_criteria");
    }
}