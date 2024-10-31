# email_marketing/overrides/unsubscribe.py

import frappe
import frappe.www.unsubscribe as unsubscribe_module

def custom_get_current_groups(name):
    # Return current group by which the mail has been sent.
    doctype = frappe.form_dict.get("doctype")
    email_group = frappe.form_dict.get("email_group")
    
    if doctype == "Newsletter":
        # Original newsletter behavior
        return frappe.get_all(
            "Newsletter Email Group",
            fields=["email_group"],
            filters={"parent": name, "parenttype": "Newsletter"},
        )
    else:
        # Email Campaign or direct email group behavior
        return [{"email_group": email_group}] if email_group else []

def override_unsubscribe():
    """Apply the override to unsubscribe's get_current_groups"""
    unsubscribe_module.get_current_groups = custom_get_current_groups
