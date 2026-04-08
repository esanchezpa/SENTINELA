import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR / ".env"

def load_config():
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
    else:
        create_default_env()

    return {
        "telegram_token": os.getenv("TELEGRAM_TOKEN", ""),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
        "whatsapp_webhook_url": os.getenv("WHATSAPP_WEBHOOK_URL", ""),
        "twilio_api_key": os.getenv("TWILIO_API_KEY", ""),
        "twilio_sid": os.getenv("TWILIO_SID", ""),
        "twilio_account_sid": os.getenv("TWILIO_ACCOUNT_SID", ""),
        "twilio_auth_token": os.getenv("TWILIO_AUTH_TOKEN", ""),
        "twilio_from": os.getenv("TWILIO_FROM", ""),
        "twilio_to": os.getenv("TWILIO_TO", ""),
        "twilio_test_sid": os.getenv("TWILIO_TEST_SID", ""),
        "twilio_test_auth_token": os.getenv("TWILIO_TEST_AUTH_TOKEN", ""),
        "twilio_burst_calls": int(os.getenv("TWILIO_BURST_CALLS", "3")),
        "twilio_time_callout": int(os.getenv("TWILIO_TIME_CALLOUT", "20")),
        "twilio_time_to_make_call": int(os.getenv("TWILIO_TIME_TO_MAKE_CALL", "10")),
        "check_interval_min": float(os.getenv("CHECK_INTERVAL_MIN", "45")),
        "check_interval_max": float(os.getenv("CHECK_INTERVAL_MAX", "90")),
        "consecutive_failures": int(os.getenv("CONSECUTIVE_FAILURES", "3")),
        "calibration_x": int(os.getenv("CALIBRATION_X", "0")),
        "calibration_y": int(os.getenv("CALIBRATION_Y", "0")),
        "calibration_w": int(os.getenv("CALIBRATION_W", "200")),
        "calibration_h": int(os.getenv("CALIBRATION_H", "100")),
        "red_color_hex": os.getenv("RED_COLOR_HEX", "#FF0000"),
        "red_template_path": str(BASE_DIR / os.getenv("RED_TEMPLATE_PATH", "templates/budget_red.png")),
        "grey_color_hex": os.getenv("GREY_COLOR_HEX", "#6B7280"),
        "grey_template_path": str(BASE_DIR / os.getenv("GREY_TEMPLATE_PATH", "templates/budget_grey.png")),
        "detection_mode": os.getenv("DETECTION_MODE", "NORMAL").upper(),
        "verificacion_hubstaff": os.getenv("VERIFICACION_HUBSTAFF", "ENABLED").upper(),
        "template_confidence": float(os.getenv("TEMPLATE_CONFIDENCE", "0.9")),
        "color_ratio_threshold": float(os.getenv("COLOR_RATIO_THRESHOLD", "0.15")),
    }

def create_default_env():
    default_content = """TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
WHATSAPP_WEBHOOK_URL=
TWILIO_API_KEY=
TWILIO_SID=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM=
TWILIO_TO=
TWILIO_TEST_SID=
TWILIO_TEST_AUTH_TOKEN=
TWILIO_BURST_CALLS=3
TWILIO_TIME_CALLOUT=20
TWILIO_TIME_TO_MAKE_CALL=10
CHECK_INTERVAL_MIN=45
CHECK_INTERVAL_MAX=90
CONSECUTIVE_FAILURES=3
CALIBRATION_X=0
CALIBRATION_Y=0
CALIBRATION_W=200
CALIBRATION_H=100
DETECTION_MODE=NORMAL
VERIFICACION_HUBSTAFF=ENABLED
TEMPLATE_CONFIDENCE=0.9
COLOR_RATIO_THRESHOLD=0.15
RED_COLOR_HEX=#FF0000
RED_TEMPLATE_PATH=templates/budget_red.png
GREY_COLOR_HEX=#6B7280
GREY_TEMPLATE_PATH=templates/budget_grey.png
"""
    with open(ENV_FILE, "w") as f:
        f.write(default_content)
    Path(BASE_DIR / "templates").mkdir(exist_ok=True)

CONFIG = load_config()
