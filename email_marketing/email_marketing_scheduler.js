// email_marketing/public/js/email_marketing.js

frappe.ui.form.on('Email Campaign', {
    send_now: function(frm) {
        frappe.confirm(
            'Are you sure you want to send the first email now?',
            function() {
                frappe.call({
                    method: 'email_marketing.email_marketing_scheduler.send_now',
                    args: {
                        campaign_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frm.reload_doc();
                        }
                    }
                });
            }
        );
    }
});
