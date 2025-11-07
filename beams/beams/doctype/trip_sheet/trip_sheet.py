# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime
from frappe.utils import today
from frappe import _
from frappe.utils import getdate

class TripSheet(Document):
	def validate(self):
		self.validate_start_datetime_and_end_datetime()
		self.calculate_and_validate_fuel_data()
		self.calculate_hours()
		self.validate_trip_times()
		self.validate_reason_for_rejection()

	def validate_reason_for_rejection(self):
		"""
		Ensure that a Reason for Rejection is provided
		whenever the workflow state is set to 'Rejected'.
		"""
		if self.workflow_state == "Rejected" and not self.reason_for_rejection:
			frappe.throw(
				msg="Please provide a Reason for Rejection before rejecting this request.",
				title="Missing Reason for Rejection"
			)

	def before_save(self):
		self.validate_posting_date()
		# Set safety_inspection_completed based on fit_for_use are checked
		if self.vehicle_safety_inspection_details:
			all_fit_for_use = all(row.fit_for_use == 1 for row in self.vehicle_safety_inspection_details)
			self.safety_inspection_completed = 1 if all_fit_for_use else 0
		else:
			self.safety_inspection_completed = 0

	def on_submit(self):
		self.validate_final_odometer_reading()

	def validate_final_odometer_reading(self):
		if self.final_odometer_reading is None:
			frappe.throw("Please enter an integer value for Final Odometer Reading.")

		if not isinstance(self.final_odometer_reading, int):
			frappe.throw("Please enter an integer value for Final Odometer Reading.")

	@frappe.whitelist()
	def calculate_hours(self):
		'''
		Calculate hours between from_time and to_time for each trip, validating their order.
		'''
		for trip in self.trip_details:
			if trip.from_time and trip.to_time:
				from_time = frappe.utils.get_datetime(trip.from_time)
				to_time = frappe.utils.get_datetime(trip.to_time)

				if to_time > from_time:
					diff = to_time - from_time
					trip.hrs = round(diff.total_seconds() / 3600, 2)
				else:
					trip.hrs = 0
					frappe.throw(f"To Time must be after From Time for trip from {trip.departure} to {trip.destination}")
			else:
				trip.hrs = None

	@frappe.whitelist()
	def validate_trip_times(self):
		'''
		Validates that all `from_time` and `to_time` values in the trip_details table fall
		within the range defined by `starting_date_and_time` and `ending_date_and_time`.
		'''
		if not self.starting_date_and_time or not self.ending_date_and_time:
			return

		starting_date = frappe.utils.getdate(self.starting_date_and_time)
		ending_date = frappe.utils.getdate(self.ending_date_and_time)

		for row in self.trip_details:
			if row.get("from_time"):
				from_date = frappe.utils.getdate(row.from_time)
				if not (starting_date <= from_date <= ending_date):
					frappe.throw(
						_("Row #{0}: From Date must be between Starting Date and Ending Date.").format(row.idx),
						title=_("Message")
					)
			if row.get("to_time"):
				to_date = frappe.utils.getdate(row.to_time)
				if not (starting_date <= to_date <= ending_date):
					frappe.throw(
						_("Row #{0}: To Date must be between Starting Date and Ending Date.").format(row.idx),
						title=_("Message")
					)


	@frappe.whitelist()
	def validate_start_datetime_and_end_datetime(self):
		'''
		Validates that starting_datetime and ending_datetime are properly set and checks
		if starting_datetime is not later than ending_datetime.
		'''
		if not self.starting_date_and_time or not self.ending_date_and_time:
			return

		starting_date_and_time = getdate(self.starting_date_and_time)
		ending_date_and_time = getdate(self.ending_date_and_time)


		if starting_date_and_time > ending_date_and_time:
			frappe.throw(
				msg=_("Starting Date and Time cannot be after Ending Date and Time."),
				title=_("Validation Error")
				)

	@frappe.whitelist()
	def calculate_and_validate_fuel_data(self):
		'''
		Validate odometer readings and calculate distance traveled and fuel consumption per km.
		Automatically updates the fields on the same document.
		'''
		if self.final_odometer_reading is None or self.initial_odometer_reading is None:
			return
		if self.initial_odometer_reading > self.final_odometer_reading:
			frappe.throw(_("Initial Odometer Reading must be less than  Final Odometer Reading"))

		if self.final_odometer_reading and self.initial_odometer_reading:
			self.distance_traveledkm = self.final_odometer_reading - self.initial_odometer_reading
		else:
			self.distance_traveledkm = 0

		if self.mileage and self.mileage != 0 and self.distance_traveledkm:
			self.fuel_consumed = self.distance_traveledkm / self.mileage
		else:
			self.fuel_consumed = 0

	@frappe.whitelist()
	def validate_posting_date(self):
		if self.posting_date:
			if getdate(self.posting_date) > getdate(today()):
				frappe.throw(_("Posting Date cannot be set after today's date."))



@frappe.whitelist()
def get_last_odometer(vehicle):
	if not vehicle:
		return 0

	final_odometer = frappe.db.get_value(
		"Trip Sheet",
		{"vehicle": vehicle, "docstatus": 1},
		"final_odometer_reading",
		order_by="starting_date_and_time desc"
	)

	if final_odometer is not None:
		return final_odometer or 0
	vehicle_odometer = frappe.db.get_value("Vehicle", vehicle, "last_odometer") or 0
	return vehicle_odometer


@frappe.whitelist()
def get_selected_requests(child_table, fieldname):
	'''
	Retrieve specific field values from a child table for submitted Trip Sheet documents.

	This function collects values from the specified field in a child table where the parent
	document belongs to the "Trip Sheet" doctype and is in the submitted state (docstatus=1).
	The values are returned as a list.

	Args:
		child_table (str): The name of the child table to retrieve data from.
		fieldname (str): The field in the child table whose values need to be fetched.
	Returns:
		list: A list of values from the specified field. If no matching records are found or the field is empty, an empty list is returned..
	'''
	selected_requests = []
	eligible_parents = frappe.db.get_all("Trip Sheet", {"docstatus": 1}, pluck="name")
	result = frappe.db.get_all(
		child_table,
		filters={"parent": ["in", eligible_parents]},
		fields=[fieldname]
	)

	for doc in result:
		if doc.get(fieldname):
			selected_requests.append(doc.get(fieldname))

	return selected_requests

@frappe.whitelist()
def create_vehicle_incident_record(trip_sheet):
	'''
	Creates a new Vehicle Incident Record for the given Trip Sheet.
	'''
	if not trip_sheet:
		frappe.throw("Trip Sheet is required to create a Vehicle Incident Record.")

	trip_sheet_doc = frappe.get_doc("Trip Sheet", trip_sheet)

	vehicle_incident_data = {
		"doctype": "Vehicle Incident Record",
		"trip_sheet": trip_sheet
	}

	return vehicle_incident_data

@frappe.whitelist()
def create_batta_request(trip_sheet):
	"""
	Creates a new Batta Claim for the given Trip Sheet or returns existing one.
	"""
	if not trip_sheet:
		frappe.throw("Trip Sheet is required to create a Batta Request.")

	trip_sheet_doc = frappe.get_doc("Trip Sheet", trip_sheet)

	existing_bc = frappe.db.exists("Batta Claim", {"trip_sheet": trip_sheet_doc.name})
	if existing_bc:
		return {"status": "exists", "name": existing_bc}

	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
	if not employee:
		frappe.throw("No Employee record found for the current user.")

	trip_details = trip_sheet_doc.get("trip_details")
	if not trip_details:
		frappe.throw("No Trip Details found in the Trip Sheet.")

	first_trip = trip_details[0]
	last_trip = trip_details[-1]

	batta_claim = frappe.new_doc("Batta Claim")
	batta_claim.trip_sheet = trip_sheet_doc.name
	batta_claim.employee = employee
	batta_claim.origin = first_trip.departure
	batta_claim.destination = last_trip.destination

	work_detail = []
	for row in trip_details:
		work_detail.append({
			"origin": row.departure,
			"destination": row.destination,
			"from_date_and_time": row.from_time,
			"to_date_and_time": row.to_time,
			"distance_travelled_km": row.distance_traveled,
			"total_hours": row.hrs
		})

	batta_claim.insert(ignore_permissions=True)

	return {
		"status": "new",
		"name": batta_claim.name
	}

@frappe.whitelist()
def get_filtered_travel_requests(doctype, txt, searchfield, start, page_len, filters):
	driver = filters.get("driver") if filters else None
	if not driver:
		return []

	conditions = []
	if txt:
		conditions.append(f"etr.name LIKE %(txt)s")

	query = """
		SELECT DISTINCT etr.name, etr.requested_by
		FROM `tabEmployee Travel Request` etr
		INNER JOIN `tabVehicle Allocation` tva
			ON tva.parent = etr.name
		WHERE tva.driver = %(driver)s
		{conditions}
		ORDER BY etr.name
		LIMIT %(start)s, %(page_len)s
	""".format(conditions=" AND " + " AND ".join(conditions) if conditions else "")

	return frappe.db.sql(
		query,
		{
			"driver": driver,
			"txt": f"%{txt}%" if txt else None,
			"start": start,
			"page_len": page_len,
		},
		as_list=True,
	)
