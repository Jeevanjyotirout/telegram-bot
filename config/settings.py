"""
GuardBot Configuration
Central configuration file for all modules
"""

import os
from dotenv import load_dotenv

# ------------------------------------------------
# Load environment variables
# ------------------------------------------------

load_dotenv()

# ------------------------------------------------
# Telegram configuration
# ------------------------------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing. Add it to your .env file")

# ------------------------------------------------
# Database configuration
# ------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///guardbot.db"
)

# ------------------------------------------------
# Moderation limits
# ------------------------------------------------

MAX_MESSAGES_PER_DAY = 5
MAX_LINKS_PER_DAY = 3

VIOLATION_BAN_DAYS = 3

# ------------------------------------------------
# Spam detection
# ------------------------------------------------

SPAM_SCORE_THRESHOLD = 0.65

SPAM_KEYWORDS = [
    "free money",
    "crypto profit",
    "forex signal",
    "click here",
    "casino",
    "adult content",
    "loan approval",
    "guaranteed return",
    "investment scheme",
    "earn from home",
    "binary options",
    "pump and dump",
    "get rich quick",
    "mlm scheme",
    "referral bonus",
    "airdrop",
    "nft giveaway",
    "onlyfans",
    "xxx",
    "18+",
    "promo code",
    "discount offer",
    "join now",
    "limited time",
    "act fast",
    "sign up now",
    "100% profit",
]

# ------------------------------------------------
# Suspicious link patterns
# ------------------------------------------------

SUSPICIOUS_LINK_PATTERNS = [
    r"http[s]?://",
    r"t\.me/",
    r"bit\.ly",
    r"tinyurl",
    r"goo\.gl",
]

LINK_WARN_THRESHOLD = 3

# ------------------------------------------------
# Topic detection
# ------------------------------------------------

TOPIC_WARN_THRESHOLD = 5

ALLOWED_TOPIC_KEYWORDS = [
    "upsc",
    "study",
    "exam",
    "education",
    "learning",
    "books",
    "notes",
    "preparation",
    "student",
    "career",
    "government job",
    "discussion",
    "question",
]

# ------------------------------------------------
# Toxicity detection
# ------------------------------------------------

TOXICITY_SCORE_THRESHOLD = 0.60

# ------------------------------------------------
# Flood / anomaly detection
# ------------------------------------------------

MESSAGE_FLOOD_LIMIT = 5
MESSAGE_FLOOD_WINDOW = 10

# ------------------------------------------------
# Messages
# ------------------------------------------------

WARNING_MESSAGE = """
⚠️ {mention}

You are violating the group rules.

Warnings: {count}

Please keep messages relevant to the group topic.
Repeated violations may result in a ban.
"""

BAN_MESSAGE = """
🚫 {mention} has been banned.

Reason: repeated rule violations.
"""

ADMIN_ALERT_MESSAGE = """
🚨 GuardBot Alert

User: {mention}
User ID: {user_id}

Violation days: {days}

Action: {action}

Time: {time}
"""