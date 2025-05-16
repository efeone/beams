import frappe
from erpnext.controllers.queries import get_fields
from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.desk.reportview import build_match_conditions, get_filters_cond

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_cost_center_list(doctype, txt, searchfield, start, page_len, filters=None, as_dict=False):
    from erpnext.controllers.queries import get_fields
    conditions = []
    fields = ["name"]

    fields = get_fields("Cost Center", fields)

    searchfields = frappe.get_meta(doctype).get_search_fields()
    searchfields = " or ".join(field + " like %(txt)s" for field in searchfields)

    bureau_user = False
    department_user = False
    departments = False
    cost_center_filter = False

    # Get permitted bureaus
    bureau_list = frappe.db.get_all(
        'User Permission',
        filters = {
            'user': frappe.session.user,
            'allow': 'Bureau'
        },
        fields = ['for_value']
    )
    if len(bureau_list) > 0:
        bureaus = tuple(d['for_value'] for d in bureau_list)
        cost_center_filter = frappe.get_all(
            'Bureau',
            filters={'name': ['in', bureaus]},
            fields=['cost_center']
        )

    else:
        department_list = frappe.db.get_all(
            'User Permission',
            filters = {
                'user': frappe.session.user, 'allow': 'Department'
            },
            fields = ['for_value']
        )
        if len(department_list) > 0:
            departments = tuple(d['for_value'] for d in department_list)
            cost_center_filter = frappe.get_all(
                'Department Cost Center',
                filters={
                    'parent': ['in', departments],
                    'parenttype': 'Department',
                },
                fields=['cost_center'],
            )

    cost_center_filter_cond = ""
    if cost_center_filter:
        cost_center_filter = ', '.join("'"+d['cost_center']+"'" for d in cost_center_filter)
        cost_center_filter_cond = " and name in ({0})".format(cost_center_filter)

    query = '''
        select
            {fields}
        from
            `tabCost Center`
        where
            docstatus < 2
            {cost_center_filter_cond}
            and ({scond}) and disabled != 1
            {fcond} {mcond}
        order by
            idx desc, name
        limit %(page_len)s offset %(start)s
    '''

    return frappe.db.sql(
        query.format(
            **{
                "fields": ", ".join(fields),
                "scond": searchfields,
                "mcond": get_match_cond(doctype),
                "cost_center_filter_cond": cost_center_filter_cond,
                "fcond": get_filters_cond(doctype, filters, conditions).replace("%", "%%")
            }
        ),
        {"txt": "%%%s%%" % txt, "_txt": txt.replace("%", ""), "start": start, "page_len": page_len},
        as_dict=as_dict,
    )
