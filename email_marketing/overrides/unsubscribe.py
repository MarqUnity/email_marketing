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
    elif doctype == "Email Campaign":
        # Get the email group from the campaign
        campaign = frappe.get_doc("Email Campaign", name)
        if campaign.email_campaign_for == "Email Group":
            return [{"email_group": campaign.recipient}]
    return []

# Monkey-patch
unsubscribe_module.get_current_groups = custom_get_current_groups
