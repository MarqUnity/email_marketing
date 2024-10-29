// email_marketing/public/js/email_campaign_list.js

frappe.listview_settings['Email Campaign'] = {
    refresh: function(listview) {
        // Clear existing buttons to prevent duplicates
        listview.page.clear_inner_toolbar();
        
        // Add the button directly to the primary actions
        listview.page.add_button(__('Process Scheduled Campaigns'), function() {
            frappe.call({
                method: 'email_marketing.email_marketing_scheduler.send_scheduled_email_campaigns',
                callback: function(r) {
                    frappe.show_alert({
                        message: __('Processing scheduled campaigns'),
                        indicator: 'green'
                    });
                    listview.refresh();
                }
            });
        }, 'primary');
    }
};
