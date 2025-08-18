// Copyright (c) 2025, efeone and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset Transfer Request", {
  refresh: function (frm) {
	  // Initialize QR Scanner only once
	if (!frm._qr_scanner_initialized) {
		frm._qr_scanner_initialized = true;

		// QR Scanner for Single Asset
		frm.fields_dict.scan_qr_code.$wrapper.on("click", function () {
			if (!frm.doc.asset_type) {
				frappe.msgprint(__("Please select an Asset Type before scanning."));
				return;
			}
			if (frm.doc.asset_type === "Single Asset") {
				start_qr_scanner(frm, "scan_qr_code");
			}
		});

		// QR Scanner for Bundle
		frm.fields_dict.scan_bundle.$wrapper.on("click", function () {
			if (!frm.doc.asset_type) {
				frappe.msgprint(__("Please select an Asset Type before scanning."));
				return;
			}
			if (frm.doc.asset_type === "Bundle") {
				start_qr_scanner(frm, "scan_bundle");
			}
		});
	}

	frappe.db.get_list("Asset Transfer Request", {
		fields: ["asset", "bundle"],
		filters: { workflow_state: "Transferred" }
	}).then(res => {
		frm.set_query("asset", () => ({
			filters: [
				["Asset", "status", "!=", "Transferred"],
				["Asset", "name", "not in", res.map(a => a.asset)],
				["Asset", "docstatus", "=", 1],
				["Asset", "location", "!=", frm.doc.location]
			]
		}));
	frm.set_query("bundle", () => ({
	filters: [
	["Asset Bundle", "name", "not in", res.map(a => a.bundle)]
	]
	}));
	}).catch(err => console.error("Error:", err));
	frm.set_df_property("asset_return_checklist", "cannot_add_rows", true);
	frm.fields_dict.asset_return_checklist.grid.update_docfield_property(
	'checklist_item', 'read_only', 1
	);

	if (["Rejected", "Pending Approval"].includes(frm.doc.workflow_state)) {
		frm.set_df_property("reason_for_rejection", "hidden", 0);
	} else {
		frm.set_df_property("reason_for_rejection", "hidden", 1);
	}

  },

  scan_qr_code: function (frm) {
	  if (!frm.doc.scan_qr_code || frm.doc.asset_type !== "Single Asset") return;

	  let scanned_value = frm.doc.scan_qr_code.trim();

	  // Check if Asset is already set
	  if (frm.doc.asset) {
		 frappe.msgprint(__("An asset is already selected: {0}. Please clear it before scanning again.", [frm.doc.asset]));
		  return;
	  }

	  frappe.call({
		  method: "frappe.client.get_value",
		  args: {
			  doctype: "Asset",
			  filters: { name: scanned_value },
			  fieldname: ["name", "asset_name"]
		  },
		  callback: function (r) {
			  if (r.message) {
				  frm.set_value("asset", r.message.name); // Set scanned asset
			  } else {
				  frappe.msgprint(__('No asset found with this QR code!'));
				  frappe.validated = false;
			  }
			  frm.set_value("scan_qr_code", ""); // Clear scan field
		  }
	  });
  },

  scan_bundle: function (frm) {
	  if (!frm.doc.scan_bundle || frm.doc.asset_type !== "Bundle") return;

	  let scanned_value = frm.doc.scan_bundle.trim();

	  // Check if Bundle is already set
	  if (frm.doc.bundle) {
		  frappe.msgprint(__("A bundle is already selected: {0}. Please clear it before scanning again.", [frm.doc.bundle]));
		  return;
	  }

	  frappe.call({
		  method: "frappe.client.get_value",
		  args: {
			  doctype: "Asset Bundle",
			  filters: { name: scanned_value },
			  fieldname: ["name"]
		  },
		  callback: function (r) {
			  if (r.message) {
				  frm.set_value("bundle", r.message.name); // Set scanned bundle
			  } else {
				  frappe.msgprint(__('No bundle found with this QR code!'));
				  frappe.validated = false;
			  }
			  frm.set_value("scan_bundle", ""); // Clear scan field
		  }
	  });
  },

  posting_date: function(frm) {
	  frm.call("validate_posting_date");
  },
  bundle: function(frm) {
	  if (frm.doc.asset_type === "Bundle" && frm.doc.bundle) {
		  fetch_stock_items(frm);
		  fetch_bundle_assets(frm);
	  } else {
		  frm.clear_table('items');
		  frm.refresh_field('items');
		  frm.set_value('assets', []);
		  frm.refresh_field('assets');
	  }
  },
  before_workflow_action: function (frm) {
	if (frm.selected_workflow_action == 'Reject' && !frm.doc.reason_for_rejection) {
			frm.scroll_to_field('reason_for_rejection');
			frappe.dom.unfreeze();
			frappe.throw({ message: __("Please fill the rejection reason."), title: __("Missing fields") });
		}
	}
});

function fetch_stock_items(frm) {
	frappe.call({
		method: "beams.beams.doctype.asset_transfer_request.asset_transfer_request.get_stock_items_from_bundle",
		args: {
			bundle: frm.doc.bundle
		},
		callback: function(response) {
			if (response.message) {
				frm.clear_table('items');
				let asset_values = [];
				let bundle_values = [];
				response.message.forEach(function(item) {
					var row = frm.add_child('items');
					row.item = item.item;
					row.uom = item.uom;
					row.qty = item.qty;
					asset_values.push(item.assets);
					bundle_values.push(item.bundles);
				});
				frm.refresh_field('items');
				frm.set_value('assets', asset_values);
				frm.refresh_field('assets');
				frm.set_value('bundles', bundle_values);
				frm.refresh_field('bundles');
			}
		}
	});
}



function fetch_bundle_assets(frm) {
  frappe.call({
	  method: "beams.beams.doctype.asset_transfer_request.asset_transfer_request.get_bundle_assets",
	  args: { bundle: frm.doc.bundle },
	  callback: function(response) {
		  if (response.message && response.message.assets && response.message.bundles) {
			  frm.set_value('assets', response.message.assets);
			  frm.set_value('bundles', response.message.bundles);
		  } else {
			  frm.set_value('assets', []);
			  frm.set_value('bundles', []);
		  }
		  frm.refresh_field('assets');
		  frm.refresh_field('bundles');
	  }
  });
}


// Function to Start QR Scanner
function start_qr_scanner(frm, fieldname) {
	let scanner = new frappe.ui.Scanner({
		multiple: false,
		on_success: function (result) {
			let scanned_value = result.text.trim();
			if (!scanned_value) {
				frappe.msgprint(__("Invalid QR Code scanned. Please try again."));
				return;
			}
			frm.set_value(fieldname, scanned_value);
			frm.trigger(fieldname); // Trigger corresponding processing
		},
		on_error: function (error) {
			frappe.msgprint(__('Failed to scan QR Code. Try again!'));
		}
	});
	scanner.show();
}
