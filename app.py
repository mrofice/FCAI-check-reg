from flask import Flask, jsonify
import os
import requests
import json

app = Flask(__name__)

# The "closed" state to compare against
CLOSED_STATE = {
    "responseCode": -1,
    "allowConflict": False,  # updated here
    "failedCourses": [],
    "prerequistesSatistfiedCourses": [],
    "registeredCourses": [],
    "successfulCourses": [],
    "maxElectiveHours": None,
    "maxMandatoryHours": None,
    "maxRegisteredHoursPerTerm": None,
    "minRegisteredHoursPerTerm": None,
    "maxElectiveCoursesOutsideDepartment": None,
    "costPerChange": None,
    "maxHoursForRepeatedCourses": None,
    "maxNumForRepeatedCourses": None,
    "costForRepeatedCourse": None,
    "pendingCourses": None,
    "excludeIncompleteFromMaxRegHours": None,
    "majorGroup": None
}

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
            headers={"Content-Type": "application/json"},
            timeout=10
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
        return jsonify({"status": "error", "message": msg}), 200

    # 2. Fetch registration courses
    try:
        response = requests.get(
            courses_url,
            headers={"Authorization": f"Bearer {jwt}"},
            timeout=10
        ).json()
    except requests.exceptions.RequestException as e:
        msg = f"⚠️ Server is down or not responding.\nError: {str(e)}"
        requests.post(
            f"https://api.telegram.org/bot{tg_bot_token}/sendMessage",
            data={"chat_id": tg_chat_id, "text": msg}
        )
        return jsonify({"status": "error", "message": "Server is down"}), 200

    # 3. Build message
    if response != CLOSED_STATE:
        msg = f"📢 Registration state CHANGED!\n👉 @ofice0_0 @MuhammaddFouadd @mohamedatefx12 \n{json.dumps(response, indent=2)}"
    else:
        msg = f"ℹ️ Registration still closed.\n{json.dumps(response, indent=2)}"

    # Always send Telegram message
    requests.post(
        f"https://api.telegram.org/bot{tg_bot_token}/sendMessage",
        data={"chat_id": tg_chat_id, "text": msg}
    )

    # Always return the API response
    return jsonify(response)
