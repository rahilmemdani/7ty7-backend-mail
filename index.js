const functions = require("firebase-functions");
const express = require("express");
const nodemailer = require("nodemailer");
const multer = require("multer");
const cors = require("cors");

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

// Route
app.post("/api/apply", upload.single("attachment"), async (req, res) => {
    try {
        const { name, email, position, note } = req.body;
        const file = req.file;

        if (!name || !email || !position) {
            return res.status(400).json({ error: "Missing required fields" });
        }

        const mailOptions = {
            from: `"7ty7 Talent Portal" <${process.env.EMAIL_USER}>`,
            to: process.env.DESTINATION_EMAIL || "rahil@7ty7.ent",
            subject: `New Talent Application | ${position} | ${name}`,
            html: `
        <h3>New Application Received</h3>
        <p><strong>Name:</strong> ${name}</p>
        <p><strong>Email:</strong> ${email}</p>
        <p><strong>Position:</strong> ${position}</p>
        <p><strong>Note:</strong> ${note || "N/A"}</p>
      `,
            attachments: file
                ? [{ filename: file.originalname, content: file.buffer }]
                : []
        };

        await transporter.sendMail(mailOptions);

        res.status(200).json({
            success: true,
            message: "Application submitted successfully!"
        });

    } catch (error) {
        console.error(error);
        res.status(500).json({
            error: "Failed to send application",
            debug: error.message
        });
    }
});

// EXPORT EXPRESS APP TO FIREBASE
exports.api = functions.https.onRequest(app);
