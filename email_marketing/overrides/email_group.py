# email_marketing/overrides/email_group.py

import frappe
from frappe.email.doctype.email_group.email_group import EmailGroup
import contextlib
from frappe.utils import parse_addr
from frappe import _

def custom_import_from(self, doctype):
    """Extract Email Addresses from given doctype and add them to the current list"""
    meta = frappe.get_meta(doctype)
    email_field = next(
        d.fieldname
        for d in meta.fields
        if d.fieldtype in ("Data", "Small Text", "Text", "Code") and d.options == "Email"
    )
    unsubscribed_field = "unsubscribed" if meta.get_field("unsubscribed") else None
    added = 0
    
    for user in frappe.get_all(doctype, [email_field, unsubscribed_field or "name"]):
        with contextlib.suppress(frappe.UniqueValidationError, frappe.InvalidEmailAddressError):
            email = parse_addr(user.get(email_field))[1] if user.get(email_field) else None
            if email:
                frappe.get_doc(
                    {
                        "doctype": "Email Group Member",
                        "email_group": self.name,
                        "email": email,
                        "unsubscribed": user.get(unsubscribed_field) if unsubscribed_field else 0,
                        "custom_reference_type": doctype,  # Add custom reference type
                        "custom_reference": user.get('name')  # Add custom reference
                    }
                ).insert(ignore_permissions=True)
                added += 1
                
    frappe.msgprint(_("{0} subscribers added").format(added))
    return self.update_total_subscribers()

# Monkey-patch the import_from method
EmailGroup.import_from = custom_import_from