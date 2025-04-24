# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class NightPatrolLog(Document):

	def validate(self):
		if self.start_time and self.end_time:
			if self.start_time >= self.end_time:
				frappe.throw(_("Start Time must be earlier than End Time."))

