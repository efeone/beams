// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt
frappe.ui.form.on('Trip Sheet', {
    starting_date_and_time: function(frm) {
        frm.call({
            method: "validate_start_datetime_and_end_datetime",
            doc: frm.doc,
        });
    },
    ending_date_and_time: function(frm) {
        frm.call({
            method: "validate_start_datetime_and_end_datetime",
            doc: frm.doc,
        });
    },
    vehicle: function(frm) {
        if (frm.doc.vehicle) {
            frappe.call({
                method: 'beams.beams.doctype.trip_sheet.trip_sheet.get_last_odometer',
                args: {
                    vehicle: frm.doc.vehicle
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("initial_odometer_reading", r.message);
                    } else {
                        frm.set_value("initial_odometer_reading", 0);
                    }
                }
            });
        } else {
            frm.set_value("initial_odometer_reading", null);
        }
    },
    final_odometer_reading: function (frm) {
        frm.call("calculate_and_validate_fuel_data");
    },
    fuel_consumed: function (frm) {
        frm.call("calculate_and_validate_fuel_data");
    },

    refresh: function (frm) {
      // Check if the Trip Sheet is saved
      if (!frm.is_new()) {
          // Add "Vehicle Incident Record" button
          frm.add_custom_button(__('Vehicle Incident Record'), function () {
              let vehicle_incident_record = frappe.model.get_new_doc("Vehicle Incident Record");
              vehicle_incident_record.trip_sheet = frm.doc.name; // Link the current Trip Sheet
              // Redirect to the new Vehicle Incident Record
              frappe.set_route("form", "Vehicle Incident Record", vehicle_incident_record.name);
          }, __("Create"));
      }
  }

});



// frappe.ui.form.on('Trip Sheet', {
//     refresh: function(frm) {
//         frm.fields_dict['travel_request'].get_query = function(doc) {
//             return {
//                 query: 'beams.beams.doctype.trip_sheet.trip_sheet.filter_unassigned_travel_requests',
//                 filters: {
//                     employee: frm.doc.employee  // Pass the employee to filter the Travel Requests
//                 }
//             };
//         };
//     }
// });
