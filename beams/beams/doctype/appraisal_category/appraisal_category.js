// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Appraisal Category", {
  validate: function(frm) {
	  if (frm.doc.appraisal_threshold < 0 || frm.doc.appraisal_threshold > 5) {
		frappe.throw({
			  title: __('Invalid Appraisal Threshold'),
			  message: __('Appraisal Threshold must be between 0 and 5.')
		  });
	  }
  }
});

frappe.ui.form.on("Payscale Details", {
	maximum_ctc: function(frm, cdt, cdn) {
		update_min_ctc(frm);
	},
	payscale_details_add: function(frm, cdt, cdn) {
		update_min_ctc(frm);
	},
	payscale_details_remove: function(frm, cdt, cdn) {
        update_min_ctc(frm);
    }
});


/**
* Updates the minimum CTC for a row in the payscale_details table.
* Sets minimum CTC to 0 for the first row.
* Sets minimum CTC of the current row to the previous row's maximum CTC + 1.
* If current row's maximum CTC is 0, clears min and max CTC for subsequent rows.
*/
function update_min_ctc(frm) {
    let grid = frm.doc.payscale_details || [];
    for (let i = 0; i < grid.length; i++) {
        if (i === 0) {
            grid[i].minimum_ctc = 0;
        } else {
            let prev_row = grid[i - 1];
            if (prev_row.maximum_ctc != null) {
                grid[i].minimum_ctc = prev_row.maximum_ctc + 1;
            }
        }
        if (grid[i].maximum_ctc === 0) {
            for (let j = i + 1; j < grid.length; j++) {
                grid[j].minimum_ctc = null;
                grid[j].maximum_ctc = null;
            }
            break; 
        }
    }
    frm.refresh_field("payscale_details");
}
