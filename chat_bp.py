# chat_bp.py
import os
import re
import unicodedata
import resend
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, make_response
from extensions import db
import jwt
import threading
import smtplib
import ssl
from email.message import EmailMessage
import hashlib
import logging

chat_bp = Blueprint('chat_bp', __name__)

# Import models inside functions to avoid circular imports
def get_user_model():
    from models import User
    return User

def get_chatlog_model():
    from models import ChatLog
    return ChatLog

# ============================== Configuration ==============================
# Email alert configuration
DEFAULT_ALERTS = [
    "najairieais@gmail.com",
    "where.is.tiejh@gmail.com",
]
ALERT_EMAILS = [e.strip() for e in os.getenv("ALERT_EMAILS", ",".join(DEFAULT_ALERTS)).split(",") if e.strip()]
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "0") or 0)
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
ALERT_FROM = os.getenv("ALERT_FROM", os.getenv("SMTP_USER", "no-reply@example.com"))
REDACT_MESSAGES = os.getenv("REDACT_MESSAGES", "true").lower() in ("1", "true", "yes")

# Resend config
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_FROM = os.getenv("RESEND_FROM", "Support <alerts@yourdomain.com>")
RESEND_ALERT_EMAILS = [
    e.strip() for e in os.getenv("ALERT_EMAILS", "").split(",") if e.strip()
]

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Logging
logger = logging.getLogger("mindlink")

# ============================== Helper Functions ==============================
def send_alert_email_async(subject: str, body: str, to_addrs: list[str]):
    """Send an email in a background thread. Non-fatal on error."""
    def _send():
        if not (to_addrs and SMTP_HOST and SMTP_PORT):
            logger.warning(
                "Alert email not sent: SMTP or recipients not configured (SMTP_HOST=%s SMTP_PORT=%s ALERT_EMAILS=%s)",
                SMTP_HOST, SMTP_PORT, to_addrs
            )
            return
        try:
            logger.info(
                "Sending alert email to %s via %s:%s (from=%s)",
                to_addrs, SMTP_HOST, SMTP_PORT, ALERT_FROM
            )
            msg = EmailMessage()
            msg.set_content(body)
            msg["Subject"] = subject
            msg["From"] = ALERT_FROM
            msg["To"] = ", ".join(to_addrs)

            if SMTP_PORT == 465:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
                    if SMTP_USER and SMTP_PASS:
                        server.login(SMTP_USER, SMTP_PASS)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                    server.ehlo()
                    try:
                        server.starttls(context=ssl.create_default_context())
                        server.ehlo()
                    except Exception:
                        pass
                    if SMTP_USER and SMTP_PASS:
                        server.login(SMTP_USER, SMTP_PASS)
                    server.send_message(msg)
            logger.info(f"Alert email sent to: {to_addrs}")
        except Exception:
            logger.exception("Failed to send alert email")

    threading.Thread(target=_send, daemon=True).start()

def send_high_risk_alert_via_resend(subject: str, html: str) -> None:
    """Send alert via Resend (HTML). No-op if not fully configured."""
    if not (RESEND_API_KEY and RESEND_FROM and RESEND_ALERT_EMAILS):
        logger.warning("Resend not configured; skipping Resend send.")
        return
    try:
        resend.Emails.send({
            "from": RESEND_FROM,
            "to": RESEND_ALERT_EMAILS,
            "subject": subject,
            "html": html,
        })
        logger.info("Resend alert sent to %s", RESEND_ALERT_EMAILS)
    except Exception:
        logger.exception("Resend send failed")



SAFETY_NOTE_JM = (
    "Remember, if you're in immediate danger, call 119 (Police) or 110 (Ambulance/Fire) now.\n\n"
    "For mental health or emotional support:\n"
    "• SafeSpot JA (children & teens): 876-439-5199 or 888-723-3776\n"
    "• U-Matter (youth chatline): Message 'SUPPORT' to 876-838-4897 via WhatsApp or SMS\n"
    "• Mental Health & Suicide Prevention Helpline: 888-639-5433 (888-NEW-LIFE)"
)

MONITORING_NOTICE_JM = (
    "Safety notice: This conversation is automatically screened for crisis language so we can help keep you safe. "
    "If high-risk phrases are detected, we may notify a designated helpline and share the minimum necessary information "
    "to assist you. If you're in immediate danger, call 119 (Police) or 110 (Ambulance/Fire)."
)

# ---------------- JWT Utilities ----------------
def create_jwt_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ---------------- Risk Level Assessment ----------------
def determine_risk_level(message):
    lower_msg = message.lower()

    low_words = [
        "happy","good","fine","okay","ok","great","alright","all right","cool","blessed",
        "i'm good","im good","i am good","i'm fine","im fine","i am fine","i'm okay","im okay","i am okay",
        "can't complain","cant complain","mi good","mi deh yah","deh yah","mi irie","irie","mi alright",
        "mi alrite","mi alr","😊","🙂","👍","👌","bless up","no problem","np"
    ]
    medium_words = [
        "sad","down","low","blue","anxious","anxiety","worried","worry","stressed","stress",
        "tired","exhausted","burnt out","burned out","overwhelmed","overwhelm","lonely","alone",
        "angry","frustrated","mixed feelings","not great","not okay","not ok","meh",
        "struggling","having a hard time","not feeling like myself","drained","can't focus","cant focus",
        "can't sleep","cant sleep","insomnia",
        "mi tired","mi stress","mi stress out","mi mash up","mi nuh too good","mi nah manage",
        "head a hurt mi","mi spirit low","mi nah feel like miself","mi feel away",
        "😕","🙁","😟","😞","🥺","💤","😴"
    ]
    high_words = [
        "suicidal","suicide","i want to die","i wanna die","i want die","wish i were dead","wish i was dead",
        "i'm done with life","im done with life","done with life","life not worth it","life isn't worth it",
        "nothing is worth it anymore","nothing matters anymore","i can't go on","cant go on",
        "i'm going to kill myself","im going to kill myself","kill myself","end my life","end it all",
        "self harm","self-harm","cut myself","hurt myself","overdose","od","take my life",
        "hopeless","worthless","no reason to live","i see no way out","i give up",
        "mi cyah badda","mi cyaan badda","mi cyaa badda","mi cyan badda","mi cah badda","mi cyaa manage",
        "mi tired a life","mi tyad a life","mi done wid life","mi feel fi dead",
        "mi nuh waan live","mi noh waan live","mi no waan live","mi waan done","mi feel fi end it",
        "mi cyaan tek dis","mi cyan tek dis","mi can't take this","cant take this anymore","mi cyah badda",
        "goodbye everyone","this is my last message","you won't hear from me again","i won't be here tomorrow",
        "i don't want to live anymore","i dont want to live anymore","don't want to live anymore","dont want to live anymore",
        "i don't want to live","i dont want to live","don't want to live","dont want to live",
        "i'm tired of living","im tired of living","tired of living","tired of life",
        "i should end my life","should end my life",
        "there's no point in living","theres no point in living","no point in living","no point to live",
        "🪦","🔪","💊","🩸"
    ]

    if any(word in lower_msg for word in low_words):
        return 'low'
    elif any(word in lower_msg for word in medium_words):
        return 'medium'
    elif any(word in lower_msg for word in high_words):
        return 'high'
    return 'low'

# ---------------- POST /chat/message ----------------
@chat_bp.route('/message', methods=['POST'])
def send_message():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
        
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = decode_jwt_token(token)

    if not user_id:
        return jsonify({'error': 'Invalid or missing token'}), 401

    message = data.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Import models here to avoid circular imports
    User = get_user_model()
    ChatLog = get_chatlog_model()

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Ensure telephone is mandatory
    if not user.telephone:
        return jsonify({'error': 'User telephone number is missing'}), 400

    risk_level = determine_risk_level(message)

    # Simple response without OpenAI
    ai_reply = "I'm here and listening. Tell me more about how you're feeling. 💭"

    # Save the chat
    chat = ChatLog()
    chat.user_id = user_id
    chat.message = message
    chat.risk_level = risk_level

    try:
        db.session.add(chat)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to save message', 'details': str(e)}), 500

    # Prepare response
    response = {
        'message': 'Message saved', 
        'risk_level': risk_level,
        'ai_reply': ai_reply
    }

    # High-risk alert handling
    if risk_level == 'high':
        safety_note = SAFETY_NOTE_JM
        monitoring_note = MONITORING_NOTICE_JM
        
        logger.info("High risk detected for user_id=%s message='%s'", user_id, message)
        try:
            subject = f"High-risk chat detected (user_id={user_id})"
            # minimal PII: include user info and short excerpt or fingerprint
            if REDACT_MESSAGES and message:
                digest = hashlib.sha256(message.encode("utf-8")).hexdigest()[:8]
                message_display = f"[REDACTED] (fingerprint: {digest})"
            else:
                message_display = (message[:200] + "...") if len(message) > 200 else message

            username = user.username or "unknown"
            email = user.email or "unknown"
            telephone = user.telephone or "unknown"

            body = (
                "User at risk!\n\n"
                f"User: {username} ({email}, {telephone})\n"
                f"User ID: {user_id}\n"
                f"Time (UTC): {datetime.utcnow().isoformat()}\n"
                f"Message: {message_display}\n\n"
                "This message may indicate immediate risk. Please follow your org's escalation policy."
            )

            # HTML body for Resend
            html_body = f"""
            <div style="font-family: Arial, sans-serif;">
              <p><strong>User at risk!</strong></p>
              <p><b>User:</b> {username} ({email}, {telephone})<br/>
                 <b>User ID:</b> {user_id}<br/>
                 <b>Time (UTC):</b> {datetime.utcnow().isoformat()}<br/>
                 <b>Message:</b> {message_display}</p>
              <p>This message may indicate immediate risk. Please follow your org's escalation policy.</p>
            </div>
            """
            send_high_risk_alert_via_resend(subject, html_body)

            # SMTP fallback
            if ALERT_EMAILS:
                logger.info("Triggering SMTP alert email for user_id=%s to %s", user_id, ALERT_EMAILS)
                send_alert_email_async(subject, body, ALERT_EMAILS)
            else:
                logger.warning("High-risk detected but ALERT_EMAILS not configured; no SMTP email sent")

            # Add safety info to response
            response['safety_note'] = safety_note
            response['monitoring_note'] = monitoring_note
            response['alert'] = f"High-risk detected! Notify authorities for user {username} immediately."
            response['helplines'] = "\n".join([
                "SafeSpot JA - 876-439-5199 or 888-723-3776",
                "U‑Matter - Message 'SUPPORT' to 876-838-4897", 
                "Mental Health Helpline - 888-639-5433",
                "Emergency number - 119"
            ])
            
        except Exception:
            logger.exception("Error triggering alert email")

    return jsonify(response), 201

# ---------------- GET /chat/history ----------------
@chat_bp.route('/history', methods=['GET'])
def get_history():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = decode_jwt_token(token)

    if not user_id:
        return jsonify({'error': 'Invalid or missing token'}), 401

    # Import model here to avoid circular imports
    ChatLog = get_chatlog_model()

    chats = ChatLog.query.filter_by(user_id=user_id).order_by(ChatLog.created_at.asc()).all()
    chat_list = [{
        'id': chat.id,
        'message': chat.message,
        'risk_level': chat.risk_level,
        'created_at': chat.created_at.isoformat()
    } for chat in chats]

    return jsonify({'chats': chat_list}), 200

# ---------------- Additional chat route ----------------
@chat_bp.route('/chat', methods=['POST'])
def chat():
    """Simple chat endpoint without OpenAI integration"""
    data = request.get_json(silent=True) or {}
    user_msg = (data.get("message") or "").strip()

    if not user_msg:
        return jsonify({"reply": "Please type a message.", "risk": "low"})

    # Get user from token (optional for anonymous chat)
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = decode_jwt_token(token) if token else None

    risk = determine_risk_level(user_msg)

    # Simple response without OpenAI
    reply = "Thank you for sharing. I'm here to listen. How are you feeling today? 💭"

    # Save to database if user is authenticated
    if user_id:
        User = get_user_model()
        ChatLog = get_chatlog_model()
        user = User.query.get(user_id)
        if user:
            chat = ChatLog()
            chat.user_id = user_id
            chat.message = user_msg
            chat.risk_level = risk
            try:
                db.session.add(chat)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to save chat: {e}")

    # Prepare response
    response = {
        "reply": reply,
        "risk": risk,
    }

    # Add safety notes for high risk
    if risk == "high":
        response["safety_note"] = SAFETY_NOTE_JM
        response["monitoring_note"] = MONITORING_NOTICE_JM

    return jsonify(response), 200