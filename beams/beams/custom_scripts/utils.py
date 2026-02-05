import frappe
from beams.beams.overrides.budget import validate_expense_against_budget

budget_validation_doctypes = ["Purchase Order", "Material Request"]

def validate_budget(self, method=None):
	'''
		Custom Method trigger on on_update event of all doctypes 
	'''
	#Skip if doctype is not in budget_validation_doctypes
	if self.doctype not in budget_validation_doctypes:
		return
	
	#Apply budget validation
	if self.name:
		for data in self.get("items"):
			args = data.as_dict()
			args.update(
				{
					"object": self,
					"doctype": self.doctype,
					"company": self.company,
					"posting_date": (
						self.schedule_date
						if self.doctype == "Material Request"
						else self.transaction_date
					),
				}
			)
			validate_expense_against_budget(args, 0, 1)
