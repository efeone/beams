import frappe

def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user
    
    user_roles = frappe.get_roles(user)
    
    
    if "Administrator" in user_roles:
        return ""

    
    if "Interviewer" in user_roles:
        return f"""
        `tabJob Applicant`.name IN (
            SELECT reference_name 
            FROM `tabToDo`
            WHERE reference_type = 'Job Applicant'
            AND allocated_to = '{user}'
        )
        """
    return None



