# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import cstr, strip_html
import json



def execute(filters=None):
    return get_columns(), get_data(filters or {})



def get_columns():
    return [
        {
            "label": _("Ticket ID"),
            "fieldname": "ticket_id",
            "fieldtype": "Link",
            "options": "HD Ticket",
            "width": 150
        },
        {
            "label": _("Date and Time"),
            "fieldname": "timestamp",
            "fieldtype": "Datetime",
            "width": 200
        },
        {
            "label": _("User"),
            "fieldname": "user",
            "fieldtype": "Link",
            "options": "User",
            "width": 220
        },
        {
            "label": _("Activity Type"),
            "fieldname": "activity_type",
            "fieldtype": "Data",
            "width": 170
        },
        {
            "label": _("Activity Details"),
            "fieldname": "activity",
            "fieldtype": "Data",
            "width": 1000
        }
    ]



def get_data(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    ticket_id = filters.get("ticket_id")
    user_filter = filters.get("user")

    activity_log = []

    # date range filter
    date_filter = ["between", [from_date, f"{to_date} 23:59:59"]]

    # Ticket Creation Logs

    ticket_filters = {"creation": date_filter}
    if ticket_id:
        ticket_filters = {"name": ticket_id}

    tickets = frappe.get_all(
        "HD Ticket",
        filters=ticket_filters,
        fields=["name", "owner", "creation"]
    )

    for ticket in tickets:
        if user_filter and ticket.owner != user_filter:
            continue

        activity_log.append({
            "ticket_id": ticket.name,
            "timestamp": ticket.creation,
            "user": ticket.owner,
            "activity_type": "Creation",
            "activity": "Created the Ticket"
        })

    # Version Logs

    version_filters = {
        "ref_doctype": "HD Ticket",
        "creation": date_filter
    }

    if ticket_id:
        version_filters["docname"] = ticket_id
    if user_filter:
        version_filters["owner"] = user_filter

    versions = frappe.get_all(
        "Version",
        filters=version_filters,
        fields=["docname", "owner", "creation", "data"],
        order_by="creation asc"
    )

    for version in versions:
        if not version.data:
            continue

        change_data = json.loads(version.data)
        messages = []

        if change_data.get("added"):
            messages.append(
                f"Added rows: {parse_row_changes(change_data['added'])}"
            )

        if change_data.get("changed"):
            messages.append(
                f"Changed values: {parse_field_changes(change_data['changed'])}"
            )

        if change_data.get("removed"):
            messages.append(
                f"Removed rows: {parse_row_changes(change_data['removed'])}"
            )

        if change_data.get("row_changed"):
            messages.append(
                f"Row values changed: {parse_row_changes(change_data['row_changed'])}"
            )

        if messages:
            activity_log.append({
                "ticket_id": version.docname,
                "timestamp": version.creation,
                "user": version.owner,
                "activity_type": "Update",
                "activity": "; ".join(messages)
            })

    # Comments

    comment_filters = {
        "reference_doctype": "HD Ticket",
        "creation": date_filter
    }

    if ticket_id:
        comment_filters["reference_name"] = ticket_id
    if user_filter:
        comment_filters["owner"] = user_filter

    comments = frappe.get_all(
        "Comment",
        filters=comment_filters,
        fields=[
            "reference_name",
            "owner",
            "creation",
            "comment_type",
            "content"
        ],
        order_by="creation asc"
    )

    for comment in comments:
        content = strip_html(cstr(comment.content))

        activity_log.append({
            "ticket_id": comment.reference_name,
            "timestamp": comment.creation,
            "user": comment.owner,
            "activity_type": comment.comment_type or "Comment",
            "activity": f"{comment.comment_type or 'Comment'}: {content}"
        })


    activity_log.sort(key=lambda x: x["timestamp"], reverse=True)
    return activity_log



def parse_field_changes(changes):
    """
    Formats field-level changes from Version.data['changed']
    Format: [[field, old, new], ...]
    """
    messages = []

    for field, old, new in changes:
        field_label = frappe.unscrub(field)
        messages.append(
            f"{field_label} from '{old or ''}' to '{new or ''}'"
        )

    return ", ".join(messages)


def parse_row_changes(rows):
    """
    Formats child table row changes
    """
    return f"affected {len(rows)} row(s)"
