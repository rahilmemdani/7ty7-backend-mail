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
    body { font-family: 'Inter', 'Segoe UI', Arial, sans-serif; line-height: 1.5; color: #1a1a1a; margin: 0; padding: 0; background-color: #f8f9fa; }
    .container { max-width: 540px; margin: 40px auto; padding: 0; border: 1px solid #e0e0e0; border-radius: 12px; background-color: #ffffff; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .header { text-align: center; padding: 32px 20px; background-color: #ffffff; border-bottom: 1px solid #f0f0f0; }
    .logo { width: 130px; height: auto; display: block; margin: 0 auto; }
    .content { padding: 32px 40px; }
    .title { font-size: 22px; font-weight: 700; color: #111; margin-bottom: 8px; margin-top: 0; }
    .subtitle { font-size: 15px; color: #666; margin-bottom: 24px; }
    .footer { font-size: 13px; color: #999; padding: 24px; text-align: center; background-color: #fafafa; border-top: 1px solid #f0f0f0; }
    .highlight { color: #f43f5e; font-weight: 600; }
    .details-card { background-color: #fcfcfc; border: 1px solid #f0f0f0; border-radius: 8px; margin-top: 16px; width: 100%; border-collapse: separate; }
    .details-card td { padding: 12px 16px; font-size: 15px; border-bottom: 1px solid #f5f5f5; }
    .details-card tr:last-child td { border-bottom: none; }
    .label { color: #888; width: 30%; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }
    .value { color: #222; font-weight: 500; }
    p { margin: 0 0 16px 0; font-size: 16px; color: #444; }
    .btn { display: inline-block; padding: 12px 24px; background-color: #111; color: #fff; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px; margin-top: 8px; }
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
                        <h2 class="title">Application Received</h2>
                        <p class="subtitle">A new talent has joined the pipeline via the portal.</p>
                        <table class="details-card">
                            <tr><td class="label">Name</td><td class="value">{name}</td></tr>
                            <tr><td class="label">Email</td><td class="value">{email}</td></tr>
                            <tr><td class="label">Role</td><td class="value highlight">{position}</td></tr>
                        </table>
                    </div>
                    <div class="footer">
                        <p>Automated Recruitment System &bull; 7ty7</p>
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
        app_msg["Subject"] = f"Application Received: {position} | 7ty7"

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
                        <p>Thanks for reaching out! We’ve successfully received your application for the <span style="font-weight: 600;">{position}</span> position.</p>
                        <p>Our talent team is currently reviewing your profile and CV. We'll be in touch soon if there's a match!</p>
                        <p style="margin-top: 32px; margin-bottom: 0;">Stay tuned,<br/><span style="font-weight: 700; color: #111;">Team 7ty7</span></p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 7ty7 Entertainment. All rights reserved.</p>
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

@app.get("/")
def read_root():
    return {"status": "7ty7 FastAPI is online"}
