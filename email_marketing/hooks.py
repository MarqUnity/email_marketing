app_name = "email_marketing"
app_title = "Email Marketing"
app_publisher = "MarqUnity Inc."
app_description = "Additions to Email Marketing Functionality"
app_email = "admin@marqunity.org"
app_license = "mit"

# include js, css files in header of desk.html
app_include_css = "/assets/email_marketing/css/email_marketing.css"
app_include_js = ["/assets/email_marketing/js/email_campaign_list.js"]

# include js in doctype views
doctype_list_js = {
    "Email Campaign": "public/js/email_campaign_list.js"
}

fixtures = [
    {"dt": "Custom Field"}
]

scheduler_events = {
    "cron": {
        "*/5 * * * *": [
            "email_marketing.email_marketing_scheduler.send_scheduled_email_campaigns"
        ]
    }
}