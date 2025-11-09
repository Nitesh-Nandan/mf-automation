# MF Automation - Email Sender

A Python script for sending emails via SMTP with support for attachments, HTML content, and multiple recipients.

## Features

- ✉️ Send plain text or HTML emails
- 📎 Attach multiple files
- 👥 Support for multiple recipients (To, CC, BCC)
- 🔧 Pre-configured for Gmail, Outlook, and Yahoo
- 🎨 Custom SMTP server support
- 🔐 Secure credential handling via environment variables
- 💻 Command-line interface and Python API

## Installation

This project uses Python 3.12+. All required modules are part of Python's standard library, so no additional dependencies are needed.

```bash
# Clone or navigate to the project directory
cd mf-automation
```

## Configuration

### Option 1: Environment Variables (Recommended)

Set your email credentials as environment variables:

```bash
export EMAIL_USERNAME="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
```

### Option 2: Create a .env file

Create a `.env` file in the project root:

```env
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### Gmail Setup

For Gmail, you'll need to use an **App Password** instead of your regular password:

1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate a new app password for "Mail"
4. Use this 16-character password as your `EMAIL_PASSWORD`

### Outlook/Yahoo Setup

For Outlook and Yahoo, you can typically use your regular account password, or generate an app-specific password from your account security settings.

## Usage

### Command Line

#### Basic Email

```bash
python send_email.py \
  --to recipient@example.com \
  --subject "Hello" \
  --body "This is a test message"
```

#### HTML Email

```bash
python send_email.py \
  --to recipient@example.com \
  --subject "Report" \
  --body "<h1>Monthly Report</h1><p>See attachment</p>" \
  --html
```

#### Email with Attachments

```bash
python send_email.py \
  --to recipient@example.com \
  --subject "Documents" \
  --body "Please find attached files" \
  --attachments report.pdf data.csv image.png
```

#### Multiple Recipients with CC

```bash
python send_email.py \
  --to user1@example.com user2@example.com \
  --cc manager@example.com \
  --subject "Team Update" \
  --body "Important announcement"
```

#### Using Different Email Providers

```bash
# Gmail (default)
python send_email.py --provider gmail --to user@example.com ...

# Outlook
python send_email.py --provider outlook --to user@example.com ...

# Yahoo
python send_email.py --provider yahoo --to user@example.com ...
```

#### Custom SMTP Server

```bash
python send_email.py \
  --smtp-host smtp.example.com \
  --smtp-port 587 \
  --username your-email@example.com \
  --password your-password \
  --to recipient@example.com \
  --subject "Test" \
  --body "Message"
```

### Python API

Use the `EmailSender` class in your Python scripts:

```python
from send_email import EmailSender

# Initialize sender
sender = EmailSender(provider='gmail')

# Send basic email
sender.send_email(
    to_email='recipient@example.com',
    subject='Hello',
    body='This is a test email'
)

# Send HTML email with attachments
sender.send_email(
    to_email=['user1@example.com', 'user2@example.com'],
    cc='manager@example.com',
    subject='Report',
    body='<h1>Report</h1><p>See attachments</p>',
    html=True,
    attachments=['report.pdf', 'data.csv'],
    from_name='John Doe'
)
```

See `email_example.py` for more examples.

## Command-Line Options

```
--to              Recipient email address(es) [required]
--subject         Email subject [required]
--body            Email body content [required]
--cc              CC email address(es)
--bcc             BCC email address(es)
--attachments     File paths to attach
--html            Send as HTML email
--from-name       Display name for sender

--provider        Email provider (gmail, outlook, yahoo)
--smtp-host       Custom SMTP host
--smtp-port       Custom SMTP port
--username        Email username (overrides EMAIL_USERNAME)
--password        Email password (overrides EMAIL_PASSWORD)
```

## Examples

Check out `email_example.py` for various usage examples:

```bash
python email_example.py
```

## Troubleshooting

### Authentication Failed

- **Gmail**: Make sure you're using an App Password, not your regular password
- **Outlook/Yahoo**: Check that you've enabled "Allow less secure apps" or use an app password
- Verify your username and password are correct

### Connection Timeout

- Check your internet connection
- Some networks block SMTP ports (587, 465)
- Try using port 587 with STARTTLS

### SSL/TLS Errors

- Ensure you're using the correct port (587 for STARTTLS)
- Update your Python installation to the latest version

### Attachment Not Found

- Verify the file path is correct
- Use absolute paths if relative paths don't work

## Security Notes

- Never commit your `.env` file or credentials to version control
- Use App Passwords instead of regular passwords when possible
- Store credentials in environment variables or secure credential managers
- Be cautious with BCC to avoid exposing recipient addresses

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Feel free to submit issues and enhancement requests!

