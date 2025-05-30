from frappe import _

def get_data(data=None):
    return {
        "fieldname": "driver",
        "non_standard_fieldnames": {
            "Vehicle Incident Record": "driver"
        },
        "transactions": [
            {
                "items": ["Vehicle Incident Record"]
            }
        ]
    }
