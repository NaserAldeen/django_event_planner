from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail 


def send_email(email, subject, html_content):
    message = Mail(
        from_email='naseraldeen@coded.com',
        to_emails=email,
        subject=subject,
        html_content=html_content)
    
    sg = SendGridAPIClient('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')
    response = sg.send(message)