/**
 * Import function triggers from their respective submodules:
 *
 * const {onCall} = require("firebase-functions/v2/https");
 * const {onDocumentWritten} = require("firebase-functions/v2/firestore");
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

const {setGlobalOptions} = require("firebase-functions");
const {onRequest} = require("firebase-functions/v2/https");
const express = require("express");
const nodemailer = require("nodemailer");
const multer = require("multer");
const cors = require("cors");
require("dotenv").config();

const app = express();

// Middleware
app.use(cors({origin: true}));
app.use(express.json());

// Multer (memory storage)
const storage = multer.memoryStorage();
const upload = multer({
  storage,
  limits: {fileSize: 10 * 1024 * 1024},
});

// Nodemailer transporter
const transporter = nodemailer.createTransport({
  host: process.env.EMAIL_HOST,
  port: process.env.EMAIL_PORT,
  secure: process.env.EMAIL_PORT == 465,
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

// API Routes
app.post("/apply", upload.single("attachment"), async (req, res) => {
  try {
    const {name, email, position, note} = req.body;
    const file = req.file;

    if (!name || !email || !position) {
      return res.status(400).json({error: "Missing required fields"});
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
      attachments: file ?
                [{filename: file.originalname, content: file.buffer}] :
                [],
    };

    await transporter.sendMail(mailOptions);
    console.log(`✅ Email sent successfully for ${name}`);
    res.status(200).json({
      success: true,
      message: "Application submitted successfully!",
    });
  } catch (error) {
    console.error("❌ Error during email submission:", error);
    res.status(500).json({
      error: "Failed to send application",
      debug: error.message,
    });
  }
});

// Global options
setGlobalOptions({maxInstances: 10});

// Export the function
exports.api = onRequest(app);
