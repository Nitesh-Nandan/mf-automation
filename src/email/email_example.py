#!/usr/bin/env python3
"""
Example usage of the EmailSender class (Gmail only).
"""

from email_sender import EmailSender

def example_basic_email():
    """Send a basic plain text email."""
    sender = EmailSender()
    
    sender.send_email(
        to_email='talk2nandan5686@gmail.com',
        subject='Test Email',
        body='This is a test email sent from Python!',
        from_name='Nitesh Nandan'
    )
    


def example_html_email():
    """Send an HTML formatted email."""
    sender = EmailSender()
    
    html_body = """
    <html>
        <body>
            <h1 style="color: #333;">Hello!</h1>
            <p>This is an <strong>HTML email</strong> with formatting.</p>
            <ul>
                <li>Bullet point 1</li>
                <li>Bullet point 2</li>
            </ul>
        </body>
    </html>
    """
    
    sender.send_email(
        to_email='talk2nandan5686@gmail.com',
        subject='HTML Email Test',
        body=html_body,
        html=True
    )


def example_email_with_attachments():
    """Send an email with attachments."""
    sender = EmailSender()
    
    sender.send_email(
        to_email='talk2nandan5686@gmail.com',
        subject='Email with Attachments',
        body='Please find the attached files.',
        attachments=['report.pdf', 'data.csv']
    )


def example_multiple_recipients():
    """Send email to multiple recipients with CC and BCC."""
    sender = EmailSender()
    
    sender.send_email(
        to_email=['user1@example.com', 'user2@example.com'],
        cc='manager@example.com',
        bcc='archive@example.com',
        subject='Team Update',
        body='Important team announcement here.',
        from_name='John Doe'
    )


def example_with_custom_sender_name():
    """Send email with custom sender name."""
    sender = EmailSender()
    
    sender.send_email(
        to_email='talk2nandan5686@gmail.com',
        subject='Custom Sender Name',
        body='Notice the sender name is different from the email address.',
        from_name='Nitesh Nandan'
    )


if __name__ == '__main__':
    print("Email Sender Examples")
    print("=" * 50)
    print("\nUncomment the example you want to run:\n")
    
    # Uncomment one of these to test:
    example_basic_email()
    # example_html_email()
    # example_email_with_attachments()
    # example_multiple_recipients()
    # example_with_custom_sender_name()
    
    print("Please set EMAIL_USERNAME and EMAIL_PASSWORD environment variables first!")
    print("See .env.example for configuration details.")

