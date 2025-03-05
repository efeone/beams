from frappe import _

def get_data(data=None):
    """
    Method to add transaction data to the provided data dictionary.

    """

    data["non_standard_fieldnames"].update({"Asset":"custodian"})

    # Adding transactions to the data dictionary
    data["transactions"] = [
        {'label': _('Attendance'), 'items': ['Attendance', 'Attendance Request', 'Employee Checkin']},
        {'label': _('Leave'), 'items': ['Leave Application', 'Leave Allocation', 'Leave Policy Assignment']},
        {'label': _('Lifecycle'), 'items': ['Employee Onboarding', 'Employee Transfer', 'Employee Promotion', 'Employee Grievance']},
        {'label': _('Exit'), 'items': ['Employee Separation', 'Exit Interview', 'Full and Final Statement', 'Salary Withholding']},
        {'label': _('Shift'), 'items': ['Shift Request', 'Shift Assignment']},
        {'label': _('Expense'), 'items': ['Expense Claim', 'Travel Request', 'Employee Advance']},
        {'label': _('Benefit'), 'items': ['Employee Benefit Application', 'Employee Benefit Claim']},
        {'label': _('Payroll'), 'items': ['Salary Structure Assignment', 'Salary Slip', 'Additional Salary', 'Timesheet', 'Employee Incentive', 'Retention Bonus', 'Bank Account']},
        {'label': _('Training'), 'items': ['Training Request', 'Training Event', 'Training Result', 'Training Feedback', 'Employee Skill Map']},
        {'label': _('Evaluation'), 'items': ['Appraisal']},
        {'label': _('Assets'), 'items': ['Asset']}

    ]

    # Return the updated data
    return data
