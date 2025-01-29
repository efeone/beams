from frappe import _


def get_data(data=None):
	return {
		"heatmap": True,
		"heatmap_message": _("This is based on the Time Sheets created against this project"),
		"fieldname": "project",
		"transactions": [
			{
				"label": _("Project"),
				"items": ["Task", "Timesheet", "Issue", "Project Update"],
			},
			{"label": _("Material"), "items": ["Material Request", "BOM", "Stock Entry"]},
			{"label": _("Sales"), "items": ["Sales Order", "Delivery Note", "Sales Invoice"]},
			{"label": _("Purchase"), "items": ["Purchase Order", "Purchase Receipt", "Purchase Invoice"]},
			{"label": _("Budgets"), "items": ["Budget", "Adhoc Budget"]},
			{"label": _("Programs"), "items": ["Equipment Hire Request", "Equipment Request", "Transportation Request", "Technical Request","External Resource Request"]},

		],
	}
