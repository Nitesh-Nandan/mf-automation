#!/usr/bin/env python3
"""
Email sending script for Gmail with support for plain text, HTML, and attachments.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional, List, Union
from dotenv import load_dotenv

load_dotenv()   


class EmailSender:
    """A class to handle email sending via Gmail SMTP."""
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize EmailSender for Gmail.
        
        Args:
            username: Gmail address (from EMAIL_USERNAME env var if not provided)
            password: Gmail app password (from EMAIL_PASSWORD env var if not provided)
        """
        self.username = username or os.getenv('EMAIL_USERNAME')
        self.password = password or os.getenv('EMAIL_PASSWORD')
        self.smtp_host = 'smtp.gmail.com'
        self.smtp_port = 587
    
    def send_email(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        body: str,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        attachments: Optional[List[str]] = None,
        html: bool = False,
        from_name: Optional[str] = None
    ) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address(es)
            subject: Email subject
            body: Email body content
            cc: CC email address(es)
            bcc: BCC email address(es)
            attachments: List of file paths to attach
            html: Whether the body is HTML
            from_name: Display name for sender
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{from_name} <{self.username}>" if from_name else self.username
            msg['Subject'] = subject
            
            # Handle multiple recipients
            if isinstance(to_email, list):
                msg['To'] = ', '.join(to_email)
            else:
                msg['To'] = to_email
                to_email = [to_email]
            
            # Handle CC
            if cc:
                if isinstance(cc, list):
                    msg['Cc'] = ', '.join(cc)
                    to_email.extend(cc)
                else:
                    msg['Cc'] = cc
                    to_email.append(cc)
            
            # Handle BCC
            if bcc:
                if isinstance(bcc, list):
                    to_email.extend(bcc)
                else:
                    to_email.append(bcc)
            
            # Attach body
            body_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, body_type))
            
            # Attach files
            if attachments:
                for file_path in attachments:
                    self._attach_file(msg, file_path)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg, to_addrs=to_email)
            
            print(f"✓ Email sent successfully to {', '.join(to_email)}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send email: {str(e)}")
            return False
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str) -> None:
        """Attach a file to the email message."""
        path = Path(file_path)
        
        if not path.exists():
            print(f"Warning: Attachment not found: {file_path}")
            return
        
        with open(path, 'rb') as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {path.name}'
        )
        msg.attach(part)
        print(f"✓ Attached: {path.name}")

