// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Incident Record", {
  posting_date:function (frm){
      frm.call("validate_posting_date");
    },
  offense_date_and_time: function (frm) {
      frm.call("validate_offense_date_and_time");
    },
    refresh: function(frm) {
      // Apply filter to the expense_type field in the Vehicle Incident Details child table
      frm.fields_dict.vehicle_incident_details.grid.get_field("expense_type").get_query = function() {
          return {
              filters: {
                  "vehicle_against": 1
              }
          };
      };
  }
});
