import frappe
from erpnext.crm.doctype.email_campaign.email_campaign import EmailCampaign
import erpnext.crm.doctype.email_campaign.email_campaign as email_campaign_module
from frappe.core.doctype.communication.email import make
from frappe.utils import get_url
from frappe.utils.verified_command import get_signed_params

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
        frappe.throw(("Start Date cannot be before the current date"))

def custom_update_status(self):
    all_sent = True
    for schedule_entry in self.get("custom_campaign_schedules"):
        if not schedule_entry.get('custom_email_sent'):
            all_sent = False
            break
    if all_sent:
        self.status = "Completed"
    elif self.status !=  "In Progress":
        self.status = "In Progress"

def custom_send_mail(entry, email_campaign):
    members = []
    if email_campaign.email_campaign_for == "Email Group":
        # Add unsubscribed=0 to the filters to exclude unsubscribed members
        members = frappe.get_all(
            "Email Group Member",
            filters={
                "email_group": email_campaign.get("recipient"),
                "unsubscribed": 0  # Only get members who haven't unsubscribed
            },
            fields=["*"]
        )
    else:
        recipient_email = frappe.db.get_value(
            email_campaign.email_campaign_for, 
            email_campaign.get("recipient"), 
            "email_id"
        )
        members.append({
            "name": None,
            "email": recipient_email,
            "custom_reference": None
        })
    
    # Skip if no active members
    if not members:
        frappe.logger().info(f"No active members found for campaign '{email_campaign.name}'")
        return
    
    email_template = frappe.get_doc("Email Template", entry.get("email_template"))
    sender = frappe.db.get_value("User", email_campaign.get("sender"), "email")
    
    for member in members:
        recipient = member["email"]
        
        # Prepare the context for template rendering
        if member.get("custom_reference"):
            try:
                doc = frappe.get_doc(member["custom_reference_type"], member["custom_reference"])
            except frappe.DoesNotExistError:
                frappe.log_error(f"Reference '{member['custom_reference']}' not found for member '{member['name']}'")
                doc = frappe._dict({'email': recipient})
        else:
            if member["name"]:
                doc = frappe.get_doc("Email Group Member", member["name"])
            else:
                doc = frappe._dict({'email': recipient})
        
        context = {"doc": doc}
        
        # For email group recipients, create newsletter-style unsubscribe link
        # There may be a better way to do this, but I didn't want to use the frappe.email_send directly as I don't think it uses the email queue

        if email_campaign.email_campaign_for == "Email Group":
            params = {
                "email": recipient,
                "doctype": "Newsletter",  
                "name": member.name,
                "email_group": email_campaign.get("recipient")
            }
            signed_params = get_signed_params(params)
            unsubscribe_url = get_url(f"/unsubscribe?{signed_params}")
            
            # Add unsubscribe link to the content
            unsubscribe_html = f"""
            <div class="email-unsubscribe">
                <p style="margin: 15px 0;">
                    <a href="{unsubscribe_url}" style="color: #8899a6; text-decoration: underline;">
                        Click here to manage your email subscriptions
                    </a>
                </p>
            </div>
            """
            
            # Render the original content
            content = frappe.render_template(email_template.response_, context)
            
            # Add unsubscribe link if not already present
            if 'email-unsubscribe' not in content:
                content = content + unsubscribe_html
        else:
            content = frappe.render_template(email_template.response_, context)

        # Use make to create the communication record and send email
        comm = make(
            doctype="Email Campaign",
            name=email_campaign.name,
            subject=frappe.render_template(email_template.subject, context),
            content=content,
            sender=sender,
            recipients=[recipient],
            communication_medium="Email",
            sent_or_received="Sent",
            send_email=True,
            email_template=email_template.name
        )
        
    return comm



# Monkey-patch the methods
EmailCampaign.validate = custom_validate
EmailCampaign.copy_schedule_entries = copy_schedule_entries
EmailCampaign.validate_start_date = validate_start_date
EmailCampaign.update_status = custom_update_status
email_campaign_module.send_mail = custom_send_mail