from django.core.validators import EmailValidator


def validate_emails_str(emails: str):
    validate = EmailValidator()
    for email in emails.split(","):
        if not email:
            continue
        validate(email)
