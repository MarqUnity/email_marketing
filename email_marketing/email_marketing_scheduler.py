# email_marketing/email_marketing_scheduler.py

import frappe
from frappe.utils import now_datetime, get_datetime, add_days
from erpnext.crm.doctype.email_campaign.email_campaign import send_mail

def send_campaign_emails(campaign):
    for schedule_entry in campaign.get("custom_campaign_schedules"):
        #frappe.log(schedule_entry)
        # Calculate the scheduled datetime
        email_to_send_found=False
        send_after_days = schedule_entry.send_after_days or 0
        custom_send_time = schedule_entry.custom_send_time or '00:00:00'
       # frappe.log(custom_send_time)
        scheduled_date = add_days(campaign.start_date, send_after_days)
        scheduled_datetime = get_datetime(f"{scheduled_date} {custom_send_time}")
        frappe.log(f"Scheduled Datetime1:{scheduled_datetime}")
        # Check if the email is due to be sent and not already sent
        if now_datetime() >= scheduled_datetime and not schedule_entry.get('custom_email_sent'):
            email_to_send_found=True
            try:
                # Send the email
                send_mail(schedule_entry, campaign)

                # Mark the schedule entry as sent
                schedule_entry.db_set('custom_email_sent', True)

                # Log the successful email send
                frappe.logger().info(f"Email sent successfully for campaign '{campaign.name}' to schedule entry ID {schedule_entry.name} at {now_datetime()}")

            except Exception as e:
                # Log any errors that occur during sending
                frappe.logger().error(f"Failed to send email for campaign '{campaign.name}' - Schedule Entry ID {schedule_entry.name}: {str(e)}")
        if email_to_send_found:
            # Update status and save
            campaign.update_status()
            campaign.save()



def send_scheduled_email_campaigns():
    # Get all Email Campaigns that are not completed or unsubscribed
    campaigns = frappe.get_all('Email Campaign', filters={
        'status': ['not in', ['Completed', 'Unsubscribed']]
    })

    for campaign_data in campaigns:
        try:
            campaign = frappe.get_doc('Email Campaign', campaign_data.name)

            # Log the start of sending emails for the campaign
            frappe.logger().info(f"Starting email sending process for campaign '{campaign.name}' at {now_datetime()}")

            # Send emails for this campaign
            send_campaign_emails(campaign)

            # Log the completion of the campaign email process
            frappe.logger().info(f"Completed email sending for campaign '{campaign.name}' at {now_datetime()}")

        except Exception as e:
            # Log any errors related to processing the entire campaign
            frappe.logger().error(f"Error processing campaign '{campaign_data.name}': {str(e)}")
    frappe.db.commit() # required when testing from console debugger


@frappe.whitelist()
def send_now(campaign_name):
    campaign = frappe.get_doc('Email Campaign', campaign_name)
    if campaign.status != 'Draft':
        frappe.throw('Only drafts can be sent immediately.')

    # Update status to 'In Progress'
    campaign.status = 'In Progress'
    campaign.save()

    try:
        send_campaign_emails(campaign)
    except Exception as e:
        frappe.logger().error(f"Error sending mail for campaign {campaign.name}: {str(e)}")

    # Update status
    campaign.update_status()
    campaign.save()
    frappe.msgprint('First email sent successfully.')