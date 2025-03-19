# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class Division(Document):
    def before_rename(self, old_name, new_name, merge=False):
        """
        Ensure the division field is updated when the naming series changes.
        """
        if not merge:
            division_name = new_name.split("-")[0]
            self.division = division_name
            frappe.db.set_value("Division", self.name, "division", division_name)
