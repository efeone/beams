// Copyright (c) 2024, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Local Enquiry Report', {
  setup: function(frm) {
      // Set query for the 'enquiry_officer' field
      frm.set_query('enquiry_officer', () => {
          return {
              // Define the query to get enquiry officers
              query: 'beams.beams.doctype.local_enquiry_report.local_enquiry_report.get_enquiry_officers',

              // Set the filter to only show users with the 'Enquiry Officer' role
              filters: { role: 'Enquiry Officer' }
          };
      });
  }

});
