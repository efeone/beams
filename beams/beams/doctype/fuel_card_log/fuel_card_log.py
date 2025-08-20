# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FuelCardLog(Document):
	"""
	Reduce fuel_card_limit According to refilling_amount
	"""
	def validate(self):
		total_used = 0
		for row in self.get("recharge_history"):
			if row.recharge_amount:
				if row.recharge_amount > self.fuel_card_limit:
					frappe.throw(
						f"Refilling amount {row.refilling_amount} is more than available limit {self.fuel_card_limit}"
					)
				else:
					total_used += row.recharge_amount

		# Reduce fuel card limit
		if total_used > 0:
			self.fuel_card_limit -= total_used

