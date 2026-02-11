const express = require("express");
const nodemailer = require("nodemailer");
const multer = require("multer");
const cors = require("cors");
const path = require("path");
const fs = require("fs");
require("dotenv").config();
// Analytics removed as it is for Next.js and causes syntax errors in CommonJS

const app = express();

// Middleware
app.use(cors({ origin: true }));
app.use(express.json());

// Multer (memory storage)
const storage = multer.memoryStorage();
const upload = multer({
    storage,
    limits: { fileSize: 10 * 1024 * 1024 }
});

// Nodemailer transporter
const transporter = nodemailer.createTransport({
    host: process.env.EMAIL_HOST,
    port: process.env.EMAIL_PORT,
    secure: process.env.EMAIL_PORT == 465,
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
    }
});

// Logo path for embedding
const logoPath = path.join(__dirname, "assets", "logo.svg");

// Route
app.post("/api/apply", upload.single("attachment"), async (req, res) => {
    try {
        const { name, email, position, note } = req.body;
        const file = req.file;

        if (!name || !email || !position) {
            return res.status(400).json({ error: "Missing required fields" });
        }

        // Shared Email Styles
        const emailStyles = `
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #eee; border-radius: 10px; background-color: #ffffff; }
                .header { text-align: center; margin-bottom: 30px; background-color: #ffffff; padding: 10px; border-radius: 8px 8px 0 0; }
                .logo { width: 120px; height: auto; }
                .content { margin-bottom: 30px; }
                .footer { font-size: 14px; color: #777; border-top: 1px solid #eee; padding-top: 20px; text-align: center; }
                .highlight { color: #f43f5e; font-weight: bold; }
                .details-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                .details-table td { padding: 10px; border-bottom: 1px solid #f9f9f9; }
                .label { font-weight: bold; color: #555; width: 30%; }
            </style>
        `;

        // 1. Send Email to HR
        const hrMailOptions = {
            from: `"7ty7 Talent Portal" <${process.env.EMAIL_USER}>`,
            to: process.env.DESTINATION_EMAIL || "rahil@7ty7.ent",
            subject: `TAADAA! New Application Received | ${position}`,
            html: `
                <html>
                    <head>${emailStyles}</head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <img src="cid:7ty7logo" class="logo" alt="7ty7 Logo" />
                            </div>
                            <div class="content">
                                <h2 style="color: #111;">New Application Received</h2>
                                <p>TAADAA! A new talent has applied through the portal.</p>
                                <table class="details-table">
                                    <tr><td class="label">Name:</td><td>${name}</td></tr>
                                    <tr><td class="label">Email:</td><td>${email}</td></tr>
                                    <tr><td class="label">Position:</td><td class="highlight">${position}</td></tr>
                                </table>
                            </div>
                            <div class="footer">
                                <p>Automated by 7ty7 Systems</p>
                            </div>
                        </div>
                    </body>
                </html>
            `,
            attachments: [
                {
                    filename: 'logo.svg',
                    path: logoPath,
                    cid: '7ty7logo'
                },
                ...(file ? [{ filename: file.originalname, content: file.buffer }] : [])
            ]
        };

        // 2. Send Email to Applicant
        const applicantMailOptions = {
            from: `"Team 7ty7" <${process.env.EMAIL_USER}>`,
            to: email,
            subject: `Thanks for reaching out, ${name.split(' ')[0]}!`,
            html: `
                <html>
                    <head>${emailStyles}</head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <img src="cid:7ty7logo" class="logo" alt="7ty7 Logo" />
                            </div>
                            <div class="content">
                                <p>Hey <span class="highlight">${name.split(' ')[0]}</span> 👋</p>
                                <p>Thanks for reaching out. We’ve received your application for <strong>${position}</strong>.</p>
                                <p>Our talent team will review your CV. Stay tuned!</p>
                                <br/>
                                <p>Best,<br/>Team 7ty7</p>
                            </div>
                            <div class="footer">
                                <p>&copy; 2024 7ty7 Entertainment. All rights reserved.</p>
                            </div>
                        </div>
                    </body>
                </html>
            `,
            attachments: [
                {
                    filename: 'logo.svg',
                    path: logoPath,
                    cid: '7ty7logo'
                }
            ]
        };

        // Execute both sends
        await Promise.all([
            transporter.sendMail(hrMailOptions),
            transporter.sendMail(applicantMailOptions)
        ]);

        console.log(`✅ Dual Emails sent successfully for ${name}`);

        res.status(200).json({
            success: true,
            message: "Application submitted successfully! Emails sent to both HR and Applicant."
        });

    } catch (error) {
        console.error("❌ Email Error:", error);
        res.status(500).json({
            error: "Failed to send application emails",
            debug: error.message
        });
    }
});

app.get("/", (req, res) => {
    res.json({ status: "7ty7 Mailing API is active" });
});

// Correct export for Vercel
module.exports = app;

// Local development
if (process.env.NODE_ENV !== "production") {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`Server is running on http://localhost:${PORT}`);
    });
}
