from frappe import _
from erpnext.stock.doctype.material_request.material_request_dashboard import get_data as original_get_data

def get_data(data=None):
	# Call the original dashboard function
	dashboard_data = original_get_data()
	dashboard_data["transactions"].append(
		{
			"label": _("Assets"),
			"items": ["Asset Movement"]
		}
	)
	return dashboard_data
