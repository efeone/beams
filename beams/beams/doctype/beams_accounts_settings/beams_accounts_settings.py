import frappe
from frappe.model.document import Document

class BeamsAccountsSettings(Document):
    def before_save(self):
        for rule in self.beams_naming_rule:
            if rule.doc_type and rule.naming_series:
                self.update_naming_series(rule.doc_type, rule.naming_series)

    def autoname(self):
        """Define autoname logic here if needed"""
        # You can use self.name = make_autoname(...) if you need to generate a custom name

    def update_naming_series( doc_type, naming_series,company):
        try:
            # Assuming autoname should be the naming_series itself
            frappe.db.set_value("DocType", doc_type, "autoname", naming_series)
            frappe.msgprint(f"Naming series for {doc_type} updated to {naming_series}")
        except Exception as e:
            frappe.throw(f"Error updating naming series for {doc_type}: {str(e)}")
