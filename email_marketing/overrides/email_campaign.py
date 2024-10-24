import frappe
from erpnext.crm.doctype.email_campaign.email_campaign import EmailCampaign

def custom_validate(self):
    # Your custom validate logic
    self.copy_schedule_entries()
    self.validate_start_date()

def copy_schedule_entries(self):
    if not self.get('custom_campaign_schedules'):
        campaign_doc = frappe.get_doc('Campaign', self.campaign_name)
        for schedule_entry in campaign_doc.get("campaign_schedules"):
            self.append('custom_campaign_schedules', {
                'email_template': schedule_entry.email_template,
                'send_after_days': schedule_entry.send_after_days,
                'custom_send_time': schedule_entry.custom_send_time,
                'custom_email_sent': 0  # Initialize email_sent to 0
            })

def validate_start_date(self):
    from frappe.utils import getdate, nowdate
    if not self.start_date:
        frappe.throw(_("Start Date is required"))
    campaign_start_date = getdate(self.start_date)
    current_date = getdate(nowdate())
    if campaign_start_date < current_date:
        frappe.throw(_("Start Date cannot be before the current date"))

def custom_update_status(self):
    all_sent = True
    for schedule_entry in self.get("custom_campaign_schedules"):
        if not schedule_entry.get('custom_email_sent'):
            all_sent = False
            break
    if all_sent:
        self.status = "Completed"
    else:
        self.status = "In Progress"

def custom_send_mail(entry, email_campaign):
    # Initialize members list
    members = []
    
    if email_campaign.email_campaign_for == "Email Group":
        # Get all email group members
        members = frappe.get_all(
            "Email Group Member",
            filters={"email_group": email_campaign.get("recipient")},
            fields=["name", "email"]
        )
    else:
        # For a single recipient, create a member-like dictionary
        recipient_email = frappe.db.get_value(
            email_campaign.email_campaign_for, email_campaign.get("recipient"), "email_id"
        )
        members.append({
            "name": None,
            "email": recipient_email
        })
    
    email_template = frappe.get_doc("Email Template", entry.get("email_template"))
    sender = frappe.db.get_value("User", email_campaign.get("sender"), "email")
    
    # Loop through all members (even if only one)
    for member in members:
        recipient = member["email"]
        
        # Use the Email Group Member as 'doc' in the context
        if member["name"]:
            # Fetch the Email Group Member document
            doc = frappe.get_doc("Email Group Member", member["name"])
        else:
            # For single recipients without an Email Group Member, create a minimal 'doc'
            doc = frappe._dict({'email': recipient})
        
        context = {"doc": doc}
        
        # Send the email to the individual recipient
        comm = make(
            doctype="Email Campaign",
            name=email_campaign.name,
            subject=frappe.render_template(email_template.subject, context),
            content=frappe.render_template(email_template.response_, context),
            sender=sender,
            recipients=[recipient],  # Send to one recipient
            communication_medium="Email",
            sent_or_received="Sent",
            send_email=True,
            email_template=email_template.name,
        )
    return comm


# Monkey-patch the methods
EmailCampaign.validate = custom_validate
EmailCampaign.copy_schedule_entries = copy_schedule_entries
EmailCampaign.validate_start_date = validate_start_date
EmailCampaign.update_status = custom_update_status
EmailCampaign.send_mail = custom_send_mail