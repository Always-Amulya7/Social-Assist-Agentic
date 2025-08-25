from __future__ import print_function
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import markdown

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def get_service(client_secret_file: str, token_file: str):
    creds = None
    try:
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    except Exception:
        creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as token:
            token.write(creds.to_json())
    service = build("gmail", "v1", credentials=creds)
    return service

def send_email(client_secret_file: str, token_file: str, sender: str, to: List[str], subject: str, body_markdown: str, is_html: bool = True):
    service = get_service(client_secret_file, token_file)
    message = MIMEMultipart("alternative")
    message["to"] = ", ".join(to)
    message["from"] = sender
    message["subject"] = subject

    if is_html:
        html_content = markdown.markdown(body_markdown)
        part = MIMEText(html_content, "html", "utf-8")
    else:
        part = MIMEText(body_markdown, "plain", "utf-8")

    message.attach(part)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return sent.get("id")