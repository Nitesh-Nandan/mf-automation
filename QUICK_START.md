# Quick Start Guide

## 1. Set Up Credentials (Gmail Example)

```bash
# For Gmail, get an App Password first:
# 1. Go to https://myaccount.google.com/apppasswords
# 2. Generate app password for "Mail"
# 3. Copy the 16-character password

# Set environment variables
export EMAIL_USERNAME="your-email@gmail.com"
export EMAIL_PASSWORD="your-16-char-app-password"
```

## 2. Send Your First Email

```bash
python send_email.py \
  --to recipient@example.com \
  --subject "My First Email" \
  --body "Hello from Python!"
```

## 3. Common Use Cases

### Send Email with Attachment

```bash
python send_email.py \
  --to boss@company.com \
  --subject "Monthly Report" \
  --body "Please review the attached report" \
  --attachments report.pdf
```

### Send to Multiple People

```bash
python send_email.py \
  --to alice@example.com bob@example.com \
  --cc manager@example.com \
  --subject "Team Meeting Notes" \
  --body "See meeting notes below..."
```

### Send HTML Email

```bash
python send_email.py \
  --to client@example.com \
  --subject "Welcome!" \
  --body "<h1>Welcome!</h1><p>Thanks for signing up.</p>" \
  --html
```

## 4. Use in Your Python Scripts

```python
from send_email import EmailSender

# Initialize
sender = EmailSender(provider='gmail')

# Send email
sender.send_email(
    to_email='someone@example.com',
    subject='Hello',
    body='This is automated!'
)
```

## Troubleshooting

**Error: Authentication failed**
→ For Gmail, make sure you're using an App Password, not your regular password

**Error: Connection timeout**
→ Check your internet connection or try a different network

**Error: Credentials not provided**
→ Make sure EMAIL_USERNAME and EMAIL_PASSWORD are set

## Need Help?

See full documentation in `README.md` or run:

```bash
python send_email.py --help
```

