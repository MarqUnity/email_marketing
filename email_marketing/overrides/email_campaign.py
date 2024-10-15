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

# Monkey-patch the methods
EmailCampaign.validate = custom_validate
EmailCampaign.copy_schedule_entries = copy_schedule_entries
EmailCampaign.validate_start_date = validate_start_date
EmailCampaign.update_status = custom_update_status
