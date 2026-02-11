from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logo path
BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"

# Shared HTML Styles
EMAIL_STYLES = """
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #eee; border-radius: 10px; background-color: #ffffff; }
    .header { text-align: center; margin-bottom: 30px; background-color: #ffffff; padding: 20px; border-radius: 8px 8px 0 0; }
    .logo { width: 140px; height: auto; display: block; margin: 0 auto; }
    .content { margin-bottom: 30px; padding: 0 10px; }
    .footer { font-size: 14px; color: #777; border-top: 1px solid #eee; padding-top: 20px; text-align: center; }
    .highlight { color: #f43f5e; font-weight: bold; }
    .details-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    .details-table td { padding: 12px; border-bottom: 1px solid #f9f9f9; }
    .label { font-weight: bold; color: #555; width: 30%; }
</style>
"""

@app.post("/api/apply")
async def apply(
    name: str = Form(...),
    email: str = Form(...),
    position: str = Form(...),
    attachment: UploadFile = File(None)
):
    try:
        # Validate required fields
        if not name or not email or not position:
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Email credentials
        email_user = os.getenv("EMAIL_USER")
        email_pass = os.getenv("EMAIL_PASS")
        email_host = os.getenv("EMAIL_HOST")
        email_port = int(os.getenv("EMAIL_PORT", 587))
        destination_email = os.getenv("DESTINATION_EMAIL") or "rahil@7ty7.ent"

        # --- 1. HR EMAIL (Notification) ---
        hr_msg = MIMEMultipart()
        hr_msg["From"] = f'"7ty7 Talent Portal" <{email_user}>'
        hr_msg["To"] = destination_email
        hr_msg["Subject"] = f"TAADAA! New Application Received | {position}"

        hr_html = f"""
        <html>
            <head>{EMAIL_STYLES}</head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="cid:7ty7logo" class="logo" alt="7ty7 Logo" />
                    </div>
                    <div class="content">
                        <h2 style="color: #111;">New Application Received</h2>
                        <p>TAADAA! A new talent has applied through the portal.</p>
                        <table class="details-table">
                            <tr><td class="label">Name:</td><td>{name}</td></tr>
                            <tr><td class="label">Email:</td><td>{email}</td></tr>
                            <tr><td class="label">Position:</td><td class="highlight">{position}</td></tr>
                        </table>
                    </div>
                    <div class="footer">
                        <p>&copy; 2026 7ty7 Entertainment. All rights reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        hr_msg.attach(MIMEText(hr_html, "html"))

        # --- 2. APPLICANT EMAIL (Confirmation) ---
        app_msg = MIMEMultipart()
        app_msg["From"] = f'"Team 7ty7" <{email_user}>'
        app_msg["To"] = email
        app_msg["Subject"] = f"Thanks for reaching out, {name.split(' ')[0]}!"

        app_html = f"""
        <html>
            <head>{EMAIL_STYLES}</head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="cid:7ty7logo" class="logo" alt="7ty7 Logo" />
                    </div>
                    <div class="content">
                        <p>Hey <span class="highlight">{name.split(' ')[0]}</span> 👋</p>
                        <p>Thanks for reaching out. We’ve received your application for <strong>{position}</strong>.</p>
                        <p>Our talent team will review your CV. Stay tuned!</p>
                        <br/>
                        <p>Best,<br/>Team 7ty7</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2026 7ty7 Entertainment. All rights reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        app_msg.attach(MIMEText(app_html, "html"))

        # Attach logo to both
        with open(LOGO_PATH, "rb") as f:
            logo_data = f.read()
            
        for msg in [hr_msg, app_msg]:
            logo_part = MIMEApplication(logo_data, Name="logo.png")
            logo_part.add_header("Content-ID", "<7ty7logo>")
            logo_part.add_header("Content-Disposition", "inline", filename="logo.png")
            logo_part.add_header("Content-Type", "image/png")
            msg.attach(logo_part)

        # Attach CV to HR email
        if attachment:
            file_content = await attachment.read()
            cv_part = MIMEApplication(file_content, Name=attachment.filename)
            cv_part.add_header("Content-Disposition", f'attachment; filename="{attachment.filename}"')
            hr_msg.attach(cv_part)

        # Send emails
        with smtplib.SMTP(email_host, email_port) as server:
            if email_port == 587:
                server.starttls()
            server.login(email_user, email_pass)
            server.send_message(hr_msg)
            server.send_message(app_msg)

        return {"success": True, "message": "Application submitted successfully!"}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to send application", "debug": str(e)}
        )

@app.post("/api/sayhello")
async def sayhello(
    fullName: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    message: str = Form(...)
):
    try:
        # Email credentials
        email_user = os.getenv("EMAIL_USER")
        email_pass = os.getenv("EMAIL_PASS")
        email_host = os.getenv("EMAIL_HOST")
        email_port = int(os.getenv("EMAIL_PORT", 587))
        destination_email = os.getenv("DESTINATION_EMAIL") or "rahil@7ty7.ent"

        # --- 1. COMPANY EMAIL (Notification) ---
        company_msg = MIMEMultipart()
        company_msg["From"] = f'"7ty7 Contact Form" <{email_user}>'
        company_msg["To"] = destination_email
        company_msg["Subject"] = f"New Inquiry from {fullName}"

        company_html = f"""
        <html>
            <head>{EMAIL_STYLES}</head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="cid:7ty7logo" class="logo" alt="7ty7 Logo" />
                    </div>
                    <div class="content">
                        <h2 style="color: #111;">New Message Received</h2>
                        <p>You have a new inquiry from the contact form.</p>
                        <table class="details-table">
                            <tr><td class="label">Name:</td><td>{fullName}</td></tr>
                            <tr><td class="label">Email:</td><td>{email}</td></tr>
                            <tr><td class="label">Phone:</td><td>{phone}</td></tr>
                            <tr><td class="label">Message:</td><td>{message}</td></tr>
                        </table>
                    </div>
                    <div class="footer">
                        <p>&copy; 2026 7ty7 Entertainment. All rights reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        company_msg.attach(MIMEText(company_html, "html"))

        # --- 2. SENDER EMAIL (Acknowledgment) ---
        sender_msg = MIMEMultipart()
        sender_msg["From"] = f'"Team 7ty7" <{email_user}>'
        sender_msg["To"] = email
        sender_msg["Subject"] = f"Thanks for reaching out, {fullName.split(' ')[0]}!"

        sender_html = f"""
        <html>
            <head>{EMAIL_STYLES}</head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="cid:7ty7logo" class="logo" alt="7ty7 Logo" />
                    </div>
                    <div class="content">
                        <p>Hey <span class="highlight">{fullName.split(' ')[0]}</span> 👋</p>
                        <p>Thank you for contacting <strong>7ty7</strong>! We have received your inquiry and our team is already reviewing it.</p>
                        <p>We will contact you shortly to answer all the questions you have for us.</p>
                        <br/>
                        <p>Best,<br/>Team 7ty7</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2026 7ty7 Entertainment. All rights reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        sender_msg.attach(MIMEText(sender_html, "html"))

        # Attach logo to both
        with open(LOGO_PATH, "rb") as f:
            logo_data = f.read()
            
        for msg in [company_msg, sender_msg]:
            logo_part = MIMEApplication(logo_data, Name="logo.png")
            logo_part.add_header("Content-ID", "<7ty7logo>")
            logo_part.add_header("Content-Disposition", "inline", filename="logo.png")
            logo_part.add_header("Content-Type", "image/png")
            msg.attach(logo_part)

        # Send emails
        with smtplib.SMTP(email_host, email_port) as server:
            if email_port == 587:
                server.starttls()
            server.login(email_user, email_pass)
            server.send_message(company_msg)
            server.send_message(sender_msg)

        return {"success": True, "message": "Message sent successfully!"}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to send message", "debug": str(e)}
        )

@app.get("/")
def read_root():
    return {"status": "7ty7 FastAPI is online"}
