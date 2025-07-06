import json
import csv
import base64
import os
from email.mime.text import MIMEText
from collections import deque
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Memory and contacts
memory = deque(maxlen=3)
with open("contacts.csv", newline='', encoding='utf-8') as f:
    contacts = list(csv.DictReader(f))

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    print("📂 Current working directory:", os.getcwd())
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def create_message(to, subject, message_text):
    message = MIMEText(message_text)
    message["to"] = to
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}

def send_email(to, subject, message_text):
    service = get_gmail_service()
    message = create_message(to, subject, message_text)
    result = service.users().messages().send(userId="me", body=message).execute()
    print(f"✅ Email sent to {to} | Message ID: {result['id']}")

def handle_email_intent(user_msg):
    memory.append(user_msg)

    # Format contacts as a table
    contact_table = "\n".join([f"{i+1}. {c['name']} ({c['relationship']}) - {c['email id']}" for i, c in enumerate(contacts)])

    # Prompt to GPT
    prompt = f"""
    You are Orijeet. Given the user message and the contact list, write an email directly from Orijeet to the appropriate person based on their name and relationship.

    Your job:
    - Choose the correct recipient from the contact list.
    - Write a friendly and personal subject line.
    - Write the email as if Orijeet is directly speaking to the recipient (not as an assistant).
    - Do not include "Best," or "Regards" from an assistant—write it like a natural human message.

    User Message: "{user_msg}"

    Contacts:
    {contact_table}

    Respond ONLY in this JSON format:
    {{
      "email": "<recipient_email>",
      "subject": "<subject_line>",
      "body": "<email_body_written_as_orijeet>"
    }}
    """.strip()

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        content = response.choices[0].message.content.strip()
        parsed = json.loads(content)

        recipient_email = parsed["email"]
        subject = parsed["subject"]
        body = parsed["body"]

        send_email(recipient_email, subject, body)

        return {
            "status": "success",
            "message": f"📧 Email sent to {recipient_email}",
            "memory": list(memory)
        }

    except Exception as e:
        print("❌ Email Error:", e)
        return {"status": "error", "message": f"❌ Failed to send email: {str(e)}"}
