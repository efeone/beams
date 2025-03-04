# Copyright (c) 2024, efeone and contributors
# For license information, please see license.txt
import frappe
import datetime
from frappe.model.document import Document
from frappe import _
from frappe.email.doctype.email_account.email_account import EmailAccount

class BeamsHRSettings(Document):
    pass

@frappe.whitelist()
def send_shift_publication_notifications():
    '''
    Send notifications to users with the 'Shift Publisher' role
    based on the configured Shift Publication Day and Reminder Lead Time.
    '''

    settings = frappe.get_doc('Beams HR Settings')
    enable_shift_notification = settings.enable_shift_notification  # New checkbox field
    shift_publication_day = settings.shift_publication_day
    shift_publisher_role = settings.shift_publisher_role
    send_shift_creation_reminder = settings.send_shift_creation_reminder
    shift_creation_reminder_template = settings.shift_creation_reminder_template

    if not enable_shift_notification:
        return

    today = datetime.datetime.today()
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    publication_index = days_of_week.index(shift_publication_day)
    reminder_index = (publication_index - int(send_shift_creation_reminder)) % 7
    reminder_day = days_of_week[reminder_index]

    if today.strftime('%A') != reminder_day:
        return

    shift_publishers = frappe.utils.user.get_users_with_role(shift_publisher_role)
    if not shift_publishers:
        return

    # Send notifications to each user with the Shift Publisher role
    for user_email in shift_publishers:
        user = frappe.get_doc('User', user_email)
        send_email_notification(user, shift_creation_reminder_template)
        send_inapp_notification(user)

@frappe.whitelist()
def send_email_notification(user, shift_creation_reminder_template):
    '''
    Send email notification to the user using the email template.
    '''
    email_template = frappe.get_doc("Email Template", shift_creation_reminder_template)

    if not email_template:
        return

    subject = email_template.subject
    email_content = email_template.response

    if not subject or not email_content:
        return

    email_content = email_content.format(user_full_name=user.full_name)

    # Send the email with the subject and formatted content
    frappe.sendmail(
        recipients=user.email,
        subject=subject,
        content=email_content,
        reference_doctype='User',
        reference_name=user.name,
        now=True
    )


@frappe.whitelist()
def send_inapp_notification(user):
    '''
    Send in-app notification to the user similar to the send_system_notification function.
    '''
    settings = frappe.get_doc("Beams HR Settings")
    shift_creation_reminder_template = settings.shift_creation_reminder_template
    notification_template = frappe.get_doc("Email Template", shift_creation_reminder_template)

    if not notification_template:
        return

    subject = notification_template.subject
    notification_message = notification_template.response

    if not subject or not notification_message:
        return

    notification_message = notification_message.format(user_full_name=user.full_name)

    # Create the Notification Log for the user
    notification = frappe.get_doc({
        'doctype': 'Notification Log',
        'subject': subject,
        'for_user': user.name,
        'type': 'Alert',
        'email_content': notification_message,
        'content': notification_message,
        'is_seen': 0
    })
    notification.insert(ignore_permissions=True)
import frappe
from frappe import _
from frappe.utils import get_url, now_datetime
import datetime

def send_appraisal_reminders():
    '''
    Send notifications to HR Managers based on the configured Appraisal Creation Period
    and Enable Appraisal Reminder flag in Beams HR Settings.
    '''
    settings = frappe.get_doc('Beams HR Settings')
    enable_appraisal_reminder = settings.enable_appraisal_reminder
    appraisal_creation_period = settings.appraisal_creation_period  # Integer field representing the number of days
    appraisal_reminder_template = settings.appraisal_reminder_template

    if not enable_appraisal_reminder:
        return

    today = datetime.datetime.today().date()
    hr_managers = frappe.get_list('User', filters={'role': 'HR Manager'})

    if not hr_managers:
        return

    employees = frappe.get_all('Employee', fields=['name', 'employee_name', 'date_of_joining'])

    # Set to track HR Managers that have already been notified today
    notified_hr_managers = set()

    for employee in employees:
        joining_date = employee.date_of_joining
        if not joining_date:
            continue

        # Calculate the appraisal due date by adding the appraisal creation period (in days)
        appraisal_due_date = joining_date + datetime.timedelta(days=appraisal_creation_period)

        # If the appraisal due date matches today's date, send reminder
        if appraisal_due_date == today:
            for hr_manager in hr_managers:
                if hr_manager.name not in notified_hr_managers:
                    user = frappe.get_doc('User', hr_manager.name)

                    # Send reminder email and in-app notification
                    send_appraisal_email_notification(user, appraisal_reminder_template, today, appraisal_creation_period, employee.employee_name)
                    send_appraisal_inapp_notification(user, appraisal_reminder_template, today, appraisal_creation_period, employee.employee_name)

                    notified_hr_managers.add(hr_manager.name)
    return

def send_appraisal_email_notification(user, appraisal_reminder_template, today, appraisal_creation_period, employee):
    '''
    Send email notification to the HR Manager about the appraisal reminder.
    '''
    email_template = frappe.get_doc("Email Template", appraisal_reminder_template)

    if not email_template:
        return

    subject = email_template.subject
    email_content = email_template.response

    if not subject or not email_content:
        return

    # Render the email content using frappe.render_template
    try:
        email_content = frappe.render_template(email_content, {
            'user_full_name': user.full_name,
            'today': today,
            'appraisal_creation_period': appraisal_creation_period,
            'employee': employee
        })
    except Exception as e:
        frappe.log_error(f"Error rendering email template: {e}", "Appraisal Email Notification")
        return

    # Send the email
    frappe.sendmail(
        recipients=user.email,
        subject=subject,
        content=email_content,
        reference_doctype='User',
        reference_name=user.name,
        now=True
    )

def send_appraisal_inapp_notification(user, appraisal_reminder_template, today, appraisal_creation_period, employee):
    '''
    Send in-app notification to the HR Manager about the appraisal reminder.
    '''
    # Fetch the notification template
    notification_template = frappe.get_doc("Email Template", appraisal_reminder_template)

    if not notification_template:
        return

    subject = notification_template.subject
    notification_message = notification_template.response

    if not subject or not notification_message:
        return

    # Render the in-app notification message using frappe.render_template
    try:
        notification_message = frappe.render_template(notification_message, {
            'user_full_name': user.full_name,
            'today': today,
            'appraisal_creation_period': appraisal_creation_period,
            'employee': employee
        })
    except Exception as e:
        frappe.log_error(f"Error rendering in-app notification template: {e}", "Appraisal In-App Notification")
        return

    # Create the Notification Log for the user
    notification = frappe.get_doc({
        'doctype': 'Notification Log',
        'subject': subject,
        'for_user': user.name,
        'type': 'Alert',
        'email_content': notification_message,
        'content': notification_message,
        'is_seen': 0
    })
    notification.insert(ignore_permissions=True)
