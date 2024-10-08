# email_marketing/email_campaign.py

import frappe
from frappe.utils import now_datetime, get_datetime, add_days
from erpnext.crm.doctype.email_campaign.email_campaign import send_mail

# email_marketing/email_campaign.py

import frappe
from frappe.utils import now_datetime, get_datetime, add_days
from erpnext.crm.doctype.email_campaign.email_campaign import send_mail

def send_campaign_emails(campaign):
    campaign_doc = frappe.get_doc('Campaign', campaign.campaign_name)

    for schedule_entry in campaign_doc.get("campaign_schedules"):
        # Calculate the scheduled datetime
        send_after_days = schedule_entry.send_after_days or 0
        custom_send_time = schedule_entry.custom_send_time or '00:00:00'

        scheduled_date = add_days(campaign.start_date, send_after_days)
        scheduled_datetime = get_datetime(f"{scheduled_date} {custom_send_time}")

        # Check if the email is due to be sent and not already sent
        if now_datetime() >= scheduled_datetime and not schedule_entry.get('custom_email_sent'):
            # Send the email
            send_mail(schedule_entry, campaign)

            # Mark the schedule entry as sent
            schedule_entry.db_set('custom_email_sent', True)

def send_scheduled_email_campaigns():
    # Get all Email Campaigns that are not completed or unsubscribed
    campaigns = frappe.get_all('Email Campaign', filters={
        'status': ['not in', ['Completed', 'Unsubscribed']]
    })

    for campaign_data in campaigns:
        campaign = frappe.get_doc('Email Campaign', campaign_data.name)

        # Send emails for this campaign
        send_campaign_emails(campaign)

        # Update status
        campaign.update_status()
        campaign.save()


def send_now(campaign_name):
    campaign = frappe.get_doc('Email Campaign', campaign_name)
    if campaign.status != 'Draft':
        frappe.throw('Only drafts can be sent immediately.')

    # Update status to 'In Progress'
    campaign.status = 'In Progress'
    campaign.save()

    # Send emails for this campaign
    send_campaign_emails(campaign)

    # Update status to 'Sent'
    campaign.update_status()
    campaign.save()
    frappe.msgprint('First email sent successfully.')
