// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trip Sheet', {
	posting_date: function (frm) {
		frm.call("validate_posting_date");
	},
	starting_date_and_time: function (frm) {
		frm.call({
			method: "validate_start_datetime_and_end_datetime",
			doc: frm.doc,
		});
	},
	ending_date_and_time: function (frm) {
		frm.call({
			method: "validate_start_datetime_and_end_datetime",
			doc: frm.doc,
		});
	},
	final_odometer_reading: function (frm) {
		frm.call("calculate_and_validate_fuel_data");
	},
	fuel_consumed: function (frm) {
		frm.call("calculate_and_validate_fuel_data");
	},

	refresh: function (frm) {
		if (!frm.is_new() && frm.doc.workflow_state !== "Closed"){
			frm.add_custom_button(__('Vehicle Incident Record'), function () {
				frappe.call({
					method: "beams.beams.doctype.trip_sheet.trip_sheet.create_vehicle_incident_record",
					args: {
						trip_sheet: frm.doc.name
					},
					callback: function (r) {
						if (r.message) {
							frappe.new_doc("Vehicle Incident Record", r.message);
						}
					}
				});
			}, __("Create"));
		}

		frm.set_query('travel_requests', function () {
			return {
				query: 'beams.beams.doctype.trip_sheet.trip_sheet.get_filtered_travel_requests',
				filters: {
					driver: frm.doc.driver
				}
			};
		});

	},

	onload: function (frm) {
			// Get Employee linked to current user
			frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
				.then(r => {
					if (r.message && r.message.name) {
						const employee_id = r.message.name;
						frappe.db.get_list('Driver', {
							filters: { employee: employee_id },
							fields: ['name'],
							limit: 1
						}).then(driver_list => {
							if (driver_list.length > 0) {
								frm.set_value('driver', driver_list[0].name);
							}
						});
					}
				});

		frm.set_query('transportation_requests', function () {
			return {
				filters: {
					name: ['not in', get_selected_requests('Transportation Request Details', 'transportation_request')]
				}
			};
		});
		frm.set_query('travel_requests', function () {
			return {
				filters: {
					name: ['not in', get_selected_requests('Employee Travel Request Details', 'employee_travel_request')]
				}
			};
		});


		function get_selected_requests(child_table, fieldname) {
			let selected_requests = [];
			frappe.call({
				method: 'beams.beams.doctype.trip_sheet.trip_sheet.get_selected_requests',
				args: {
					child_table: child_table,
					fieldname: fieldname
				},
				async: false,
				callback: function (response) {
					if (response && response.message) {
						selected_requests = response.message;
					}
				}
			});

			return selected_requests;
		}
	},
	driver: function (frm) {
		frm.set_query('travel_requests', function () {
			return {
				query: 'beams.beams.doctype.trip_sheet.trip_sheet.get_filtered_travel_requests',
				filters: {
					driver: frm.doc.driver
				}
			};
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
					frm.set_value("initial_odometer_reading", r.message || 0);
				}
			});

			frappe.db.get_list('Vehicle Safety Inspection', {
				filters: {
					vehicle: frm.doc.vehicle
				},
				fields: ['name'],
				limit: 1
			}).then(result => {
				if (result && result.length > 0) {
					frm.set_value('vehicle_template', result[0].name);
				} else {
					frm.set_value('vehicle_template', null);
					frm.clear_table('vehicle_safety_inspection_details');
					frm.refresh_field('vehicle_safety_inspection_details');
				}
			});

		} else {
			frm.set_value("initial_odometer_reading", null);
			frm.set_value('vehicle_template', null);
			frm.clear_table('vehicle_safety_inspection_details');
			frm.refresh_field('vehicle_safety_inspection_details');
		}
	},

	// Updates the vehicle safety inspection details based on the vehicle template
	vehicle_template(frm) {
		let template = frm.doc.vehicle_template;

		if (!template) {
			frm.clear_table('vehicle_safety_inspection_details');
			frm.refresh_field('vehicle_safety_inspection_details');
			return;
		}

		frappe.db.get_doc('Vehicle Safety Inspection', template)
			.then(doc => {
				frm.clear_table('vehicle_safety_inspection_details');

				doc.vehicle_safety_inspection.forEach(d => {
					frm.add_child('vehicle_safety_inspection_details', {
						item: d.item,
						fit_for_use: null, // Leave for manual input
						remarks: ""        // Leave for manual input
					});
				});

				frm.refresh_field('vehicle_safety_inspection_details');
				frm.set_value('safety_inspection_completed', 0); // Default to incomplete
			});
	},
	// Trigger when vehicle_safety_inspection_details table is modified
	vehicle_safety_inspection_details: function(frm) {
		let all_fit_for_use = frm.doc.vehicle_safety_inspection_details.every(row => row.fit_for_use === 1);
		frm.set_value('safety_inspection_completed', all_fit_for_use ? 1 : 0);
	}
});

frappe.ui.form.on('Trip Details', {
	from_time: function (frm, cdt, cdn) {
		frm.call('calculate_hours').then(() => {
			frm.refresh_field('trip_details');
			return frm.call('validate_trip_times');
		});
	},
	to_time: function (frm, cdt, cdn) {
		frm.call('calculate_hours').then(() => {
			frm.refresh_field('trip_details');
			return frm.call('validate_trip_times');
		});
	}
});
