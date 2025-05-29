from frappe import _

def get_data(data=None):
    return {
        "fieldname": "vehicle",
        "non_standard_fieldnames": {
            "Vehicle Log": "license_plate"
        },
        "transactions": [
            {
                "items": ["Vehicle Log", "Delivery Trip", "Vehicle Documents Log"]
            }
        ]
    }
