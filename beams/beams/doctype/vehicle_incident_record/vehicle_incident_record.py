# Copyright (c) 2025, efeone and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today
from frappe.utils.user import get_users_with_role
from frappe.desk.form.assign_to import add as add_assign

class VehicleIncidentRecord(Document):
	def on_update(self):
		if self.workflow_state == "Approved":
			self.create_journal_entry_for_payable_items()

	def validate(self):
		self.validate_offense_date_and_time()

	@frappe.whitelist()
	def validate_posting_date(self):
		if self.posting_date:
			if self.posting_date > today():
				frappe.throw(_("Posting Date cannot be set after today's date."))

	@frappe.whitelist()
	def validate_offense_date_and_time(self):
		'''
		Validates that the offense date is not in the future and falls within the trip start and end dates.
		'''
		if self.offense_date_and_time:
			offense_date = frappe.utils.getdate(self.offense_date_and_time)
			current_date = frappe.utils.getdate()

			if offense_date > current_date:
				frappe.throw(_("Offense Date cannot be in the future."))

			offense_date = frappe.utils.getdate(self.offense_date_and_time)

			if self.trip_start_date and self.trip_end_date:
				start_date = frappe.utils.getdate(self.trip_start_date)
				end_date = frappe.utils.getdate(self.trip_end_date)

				if not (start_date <= offense_date <= end_date):
					frappe.throw(_("Offense Date must be between Start Date and End Date of the trip."))

	def create_journal_entry_for_payable_items(self):
		'''
		Automatically creates and submits a Journal Entry for each payable vehicle incident
		where the 'is_employee_payable' field is checked
		'''
		settings = frappe.get_single("BEAMS Admin Settings")
		debit_account = settings.default_employee_payable_account

		if not debit_account:
			frappe.throw("Default Employee Payable Account is not set in BEAMS Admin Settings.")

		employee_id = frappe.db.get_value("Driver", self.driver, "employee")
		if not employee_id:
			frappe.throw(f"Employee not linked to Driver {self.driver}")

		for row in self.vehicle_incident_details:
			if not row.get("journal_entry"):
				# Fetch the default_account from the Expense Claim Type's accounts child table
				credit_account = None
				if row.expense_type:
					expense_type_doc = frappe.get_doc("Expense Claim Type", row.expense_type)
					for account_row in expense_type_doc.get("accounts", []):
						if account_row.default_account:
							credit_account = account_row.default_account
							break

				if not credit_account:
					frappe.throw(f"No default account found for Expense Claim Type {row.expense_type}")

				journal_entry = frappe.new_doc("Journal Entry")
				journal_entry.voucher_type = "Journal Entry"
				journal_entry.posting_date = self.posting_date or nowdate()
				journal_entry.company = frappe.defaults.get_user_default("Company")
				journal_entry.remark = f"Payable offense recorded in Vehicle Incident Record {self.name}"
				journal_entry.vehicle_incident_record = self.name

				if row.is_employee_payable:
					journal_entry.append("accounts", {
						"account": debit_account,
						"party_type": "Employee",
						"party": employee_id,
						"debit_in_account_currency": row.amount
					})
					journal_entry.append("accounts", {
						"account": credit_account,
						"credit_in_account_currency": row.amount
					})
				else:
					journal_entry.append("accounts", {
						"account": credit_account,
						"debit_in_account_currency": row.amount
					})
					journal_entry.append("accounts", {
						"account": debit_account,
						"party_type": "Employee",
						"party": employee_id,
						"credit_in_account_currency": row.amount
					})

				journal_entry.insert(ignore_permissions=True)
				row.journal_entry = journal_entry.name
				self.assign_todo_for_accounts(journal_entry.name)
				frappe.msgprint(f"Journal Entry {journal_entry.name} has been created successfully.", alert=True, indicator="green")

		self.save(ignore_permissions=True)

	def assign_todo_for_accounts(self, journal_entry_name):
		'''
		Create a ToDo for Accounts User(s) when a Journal Entry
		is created and linked to the Vehicle Incident Record.
		'''
		# Prevent duplicate ToDos
		exists = frappe.db.exists("ToDo", {
			"reference_type": "Journal Entry",
			"reference_name": journal_entry_name
		})
		if exists:
			return

		# Get all Accounts Users
		users = get_users_with_role("Accounts User")

		if users:
			description = (
				f"Journal Entry <b>{journal_entry_name}</b> has been created "
				f"for Vehicle Incident Record <b>{self.name}</b>.<br>"
				"Please review and take necessary action."
			)
			add_assign({
				"assign_to": users,
				"doctype": "Journal Entry",
				"name": journal_entry_name,
				"description": description
			})