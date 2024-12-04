frappe.ui.form.on("Job Offer", {
    refresh: function (frm) {
        if (
            !frm.doc.__islocal &&
            frm.doc.status == "Accepted" &&
            frm.doc.docstatus === 1 &&
            (!frm.doc.__onload || !frm.doc.__onload.employee)
        ) {
            frm.remove_custom_button(__("Create Employee"));
        }

        setTimeout(1000);

        if (
            !frm.doc.__islocal &&
            frm.doc.status == "Accepted" &&
            frm.doc.docstatus === 1 &&
            (!frm.doc.__onload || !frm.doc.__onload.employee)
        ) {
            frm.add_custom_button(__("Create Employee"), function () {
                make_employee(frm);
            });
        }
    },
});

function make_employee(frm) {
    frappe.model.open_mapped_doc({
        method: "beams.beams.custom_scripts.job_offer.job_offer.make_employee",
        frm: frm,
    });
}
