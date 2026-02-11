from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv

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

@app.post("/api/apply")
async def apply(
    name: str = Form(...),
    email: str = Form(...),
    position: str = Form(...),
    note: str = Form(None),
    attachment: UploadFile = File(None)
):
    try:
        # Validate required fields
        if not name or not email or not position:
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Email details
        email_user = os.getenv("EMAIL_USER")
        email_pass = os.getenv("EMAIL_PASS")
        email_host = os.getenv("EMAIL_HOST")
        email_port = int(os.getenv("EMAIL_PORT", 587))
        destination_email = os.getenv("DESTINATION_EMAIL") or "rahil@7ty7.ent"

        # Create email
        msg = MIMEMultipart()
        msg["From"] = f'"7ty7 Talent Portal" <{email_user}>'
        msg["To"] = destination_email
        msg["Subject"] = f"New Talent Application | {position} | {name}"

        # HTML Body
        html = f"""
        <h3>New Application Received</h3>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Position:</strong> {position}</p>
        <p><strong>Note:</strong> {note or "N/A"}</p>
        """
        msg.attach(MIMEText(html, "html"))

        # Attachment
        if attachment:
            file_content = await attachment.read()
            part = MIMEApplication(file_content, Name=attachment.filename)
            part['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
            msg.attach(part)

        # Send email
        server = smtplib.SMTP(email_host, email_port)
        if email_port == 587:
            server.starttls()
        server.login(email_user, email_pass)
        server.send_message(msg)
        server.quit()

        return {"success": True, "message": "Application submitted successfully!"}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to send application", "debug": str(e)}
        )

@app.get("/")
def read_root():
    return {"status": "FastAPI is running"}
