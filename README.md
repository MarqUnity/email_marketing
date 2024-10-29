## Work In Progress
Requires custom fields to be created. App Will be merged into CRM Frappe hopefully in future. 

Current Development:
- Automatic Leads reference import with "Import Subscribers" action
- Separate email sending for email groups
- Group members reference linked as doc for email template (e.g. {{doc.first_name}} if subscriber import was from FCRM Lead)
- Time-based email scheduling
- Email campaigns can be customised after creation
- Proper unsubscribe handling for email group campaigns

Still pending:
- SMS support
- Filtering email group members

### Email Marketing

Additions to Email Marketing Functionality

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app email_marketing
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/email_marketing
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit
