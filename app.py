from flask import Flask, jsonify
import os
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Flask app running on Railway!"

@app.route("/check", methods=["GET"])
def check_registration():
    login_url = os.getenv("LOGIN_URL")
    courses_url = os.getenv("COURSES_URL")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    tg_bot_token = os.getenv("TG_BOT_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")

    # 1. Login to get JWT
    try:
        login_res = requests.post(
            login_url,
            json={"username": username, "password": password, "rememberMe": True},
            headers={"Content-Type": "application/json"}
        ).json()
        jwt = login_res.get("id_token")
    except Exception:
        jwt = None

    if not jwt:
        msg = "❌ Failed to log in. Check credentials."
        requests.post(
            f"https://api.telegram.org/bot{tg_bot_token}/sendMessage",
            data={"chat_id": tg_chat_id, "text": msg}
        )
        return jsonify({"status": "error", "message": msg}), 500

    # 2. Fetch registration courses
    response = requests.get(
        courses_url,
        headers={"Authorization": f"Bearer {jwt}"}
    ).text

    # 3. Send Telegram message
    msg = f"📢 Registration check result:\n{response}"
    requests.post(
        f"https://api.telegram.org/bot{tg_bot_token}/sendMessage",
        data={"chat_id": tg_chat_id, "text": msg}
    )

    return jsonify({"status": "ok", "response": response})
