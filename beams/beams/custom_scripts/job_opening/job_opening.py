import frappe
import requests
import os
from frappe.utils import get_files_path, get_url
from io import BytesIO

@frappe.whitelist()
def generate_qr_for_job(doc, method=None):
	"""
		Generate a QR code for the Job Opening that links to its public portal page
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("Job Opening", doc)

	base_url = get_url()
	job_url = f"{base_url}/job_portal/job?job_opening={doc.name}"
	doc.job_url = job_url

	qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={job_url}"
	response = requests.get(qr_api_url)

	if response.status_code != 200:
		frappe.log_error(f"Failed to generate QR code for Job Opening {doc.name}. URL: {qr_api_url}",
						 f"QR API returned status code {response.status_code}")
		return {"success": False, "error": f"QR API returned status code {response.status_code}"}

	buffer = BytesIO(response.content)

	file_name = f"qr_{doc.name}.png"
	file_path = os.path.join(get_files_path(), file_name)
	with open(file_path, "wb") as f:
		f.write(buffer.read())

	file_doc = frappe.get_doc({
		"doctype": "File",
		"file_url": f"/files/{file_name}",
		"attached_to_doctype": "Job Opening",
		"attached_to_name": doc.name,
		"is_private": 0
	})
	file_doc.insert(ignore_permissions=True)

	doc.qr_scan_to_apply = file_doc.file_url
	doc.save()
	return {"success": True, "file_url": file_doc.file_url}
