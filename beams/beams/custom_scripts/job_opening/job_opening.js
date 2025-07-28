frappe.ui.form.on('Job Opening', {
	refresh: function(frm) {
		// Show the button only after the doc is saved
		if (!frm.is_new()) {
			frm.add_custom_button(__('Generate QR Code'), function() {
				if (frm.doc.qr_scan_to_apply) {
					frappe.msgprint({
						title: __('QR Code Already Generated'),
						indicator: 'blue',
						message: __('A QR Code is already generated for this Job Opening.')
					});
					return;
				}
				frappe.call({
					method: 'beams.beams.custom_scripts.job_opening.job_opening.generate_qr_for_job',
					args: {
						doc: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.success) {
							frappe.msgprint(__('QR Code generated successfully'));
							frm.reload_doc();
						} else {
							let errorMsg = r.message && r.message.error ? r.message.error : 'Unknown error';
							frappe.msgprint({
								title: __('Error'),
								indicator: 'red',
								message: __('Failed to generate QR Code: ') + errorMsg + __('. Please check the error log.')
							});
						}
					},
					error: function(err) {
						frappe.msgprint({
							title: __('Error'),
							indicator: 'red',
							message: __('Failed to generate QR Code due to a server error. Please check the error log.')
						});
					}
				});
			});
		}
	}
});
