import frappe
from frappe.utils import add_days, today, getdate, get_datetime

@frappe.whitelist()
def get_ticket_summary(filters=None):
	if filters:
		filters = frappe.parse_json(filters)
	else:
		filters = {}
	
	conds = ""
	if filters.ticket_type:
		conds += " AND ticket_type='{0}'".format(filters.get("ticket_type"))
	if filters.priority:
		conds += " AND priority='{0}'".format(filters.get("priority"))
	if filters.subcategory:
		conds += " AND ticket_subcategory='{0}'".format(filters.get("subcategory"))
	if filters.team:
		conds += " AND agent_group='{0}'".format(filters.get("team"))
	if filters.agent:
		conds += " AND assigned_agent='{0}'".format(filters.get("agent"))
	
	from_date = filters.get("from_date", frappe.utils.nowdate())
	to_date = filters.get("to_date", add_days(frappe.utils.nowdate(), -6))

	total_tickets = get_ticket_count(from_date, to_date, conds)
	open_tickets = get_ticket_count(from_date, to_date, conds+"AND status = 'Open'")
	working_tickets = get_ticket_count(from_date, to_date, conds+"AND status = 'Working'")
	pending_tickets = open_tickets + working_tickets
	hold_tickets = get_ticket_count(from_date, to_date, conds+"AND status = 'Hold'")
	closed_tickets = get_ticket_count(from_date, to_date, conds+"AND status = 'Closed'")
	email_tickets = get_ticket_count(from_date, to_date, conds+"AND email_account IS NOT NULL")
	portal_tickets = get_ticket_count(from_date, to_date, conds+"AND email_account IS NULL")
	response_breach_tickets = get_ticket_count(from_date, to_date, conds+"AND response_due_escalation_send = 1")
	resolution_breach_tickets = get_ticket_count(from_date, to_date, conds+"AND resolution_due_escalation_send = 1")
	full_breach_tickets = get_ticket_count(from_date, to_date, conds+"AND response_due_escalation_send = 1 AND resolution_due_escalation_send = 1")
	escalated_tickets = full_breach_tickets

	avg_reponse_time = get_avg_time(from_date, to_date, conds, time_field="first_response_time")
	avg_resolution_time = get_avg_time(from_date, to_date, conds, time_field="resolution_time")
	avg_hold_time = get_avg_time(from_date, to_date, conds, time_field="total_hold_time")

	return {
		'data': [
			{ "id":"total_tickets", "title":"Total Tickets", "value": total_tickets,
				"color":"#0F172A", "bg_color":"#E0F2FE"
			}, # Slate / Light Blue
			{ "id":"open_tickets", "title":"Open Tickets", "value": open_tickets,
				"color":"#7C2D12", "bg_color":"#FFEDD5"
			}, # Brown / Light Orange
			{ "id":"working_tickets", "title":"Working Tickets", "value": working_tickets,
				"color":"#4C1D95", "bg_color":"#EDE9FE"
			}, # Purple
			{ "id":"pending_tickets", "title":"Open+Working Tickets", "value": pending_tickets,
				"color":"#4C1D95", "bg_color":"#DDD6FE"
			}, # Darker Purple
			{ "id":"hold_tickets", "title":"Hold Tickets", "value": hold_tickets,
				"color":"#065F46", "bg_color":"#D1FAE5"
			}, # Green
			{ "id":"closed_tickets", "title":"Closed Tickets", "value": closed_tickets,
				"color":"#14532D", "bg_color":"#DCFCE7"
			}, # Success Green

			{ "id":"avg_reponse_time", "title":"Avg Response Time", "value": avg_reponse_time,
				"color":"#1E3A8A", "bg_color":"#DBEAFE"
			}, # Blue
			{ "id":"avg_resolution_time", "title":"Avg Resolution Time", "value": avg_resolution_time,
				"color":"#1E40AF", "bg_color":"#BFDBFE"
			}, # Strong Blue
			{ "id":"avg_hold_time", "title":"Avg Hold Time", "value": avg_hold_time,
				"color":"#92400E", "bg_color":"#FEF3C7"
			}, # Amber
			{ "id":"response_breach_tickets", "title":"Response Breached Tickets", "value": response_breach_tickets,
				"color":"#7F1D1D", "bg_color":"#FEE2E2"
			}, # Red (Warning)
			{ "id":"resolution_breach_tickets", "title":"Resolution Breached Tickets", "value": resolution_breach_tickets,
				"color":"#991B1B", "bg_color":"#FECACA"
			}, # Dark Red
			{ "id":"full_breach_tickets", "title":"Breached Tickets", "value": full_breach_tickets,
				"color":"#450A0A", "bg_color":"#FCA5A5"
			}, # Critical Red
			{ "id":"escalated_tickets", "title":"Escalated Tickets", "value": escalated_tickets,
				"color":"#78350F", "bg_color":"#FDE68A"
			}, # Yellow / Escalation
			{ "id":"email_ticket", "title":"Email Tickets", "value": email_tickets,
				"color":"#1F2937", "bg_color":"#E5E7EB"
			}, # Neutral Gray
			{ "id":"portal_tickets", "title":"Portal Tickets", "value": portal_tickets,
				"color":"#0F766E", "bg_color":"#CCFBF1"
			} # Teal
		]
	}


def get_ticket_count(from_date, to_date, conds=""):
	"""
		Get ticket data for the dashboard.
	"""
	from_datetime = get_datetime(f"{from_date} 00:00:00")
	to_datetime = get_datetime(f"{to_date} 23:59:59")
	result = frappe.db.sql(
		f"""
		SELECT
			COUNT(CASE
				WHEN creation >= %(from_datetime)s AND creation <= %(to_datetime)s
				{conds}
				THEN name
				ELSE NULL
			END) as ticket_count
		FROM `tabHD Ticket`
	""",
		{
			"from_datetime": from_datetime,
			"to_datetime": to_datetime,
		},
		as_dict=1,
	)
	ticket_count = result[0].ticket_count or 0
	return ticket_count

def get_avg_time(from_date, to_date, conds="", time_field="first_response_time"):
	"""
		Get average time for the dashboard.
		Shows minutes by default, hours if >= 60 mins.
	"""
	from_datetime = get_datetime(f"{from_date} 00:00:00")
	to_datetime = get_datetime(f"{to_date} 23:59:59")

	# Calculate average time in minutes from seconds
	result = frappe.db.sql(
		f"""
		SELECT 
			AVG(CASE 
				WHEN creation >= %(from_datetime)s
				AND creation <= %(to_datetime)s
				{conds}
				THEN ({time_field})
				ELSE NULL
			END) AS avg_seconds
		FROM `tabHD Ticket`
	""",
		{
			"from_datetime": from_datetime,
			"to_datetime": to_datetime
		},
		as_dict=1,
	)

	avg_seconds = int(result[0].avg_seconds or 0)
	return format_seconds(avg_seconds)

def format_seconds(seconds):
	"""
		Formats seconds into:
		- X Secs
		- X Mins
		- X Hrs
		- X Hrs Y Mins Z Secs
	"""
	if seconds < 60:
		return f"{seconds} Secs"

	minutes, secs = divmod(seconds, 60)

	if minutes < 60:
		return f"{minutes} Mins {secs} Secs" if secs > 0 else f"{minutes} Mins"

	hours, mins = divmod(minutes, 60)

	if mins == 0:
		return f"{hours} Hrs"

	return f"{hours} Hrs {mins} Mins {secs} Secs" if secs > 0 else f"{hours} Hrs {mins} Mins"
