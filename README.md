# 🛡️ GuardBot — Professional Telegram Moderation Bot

GuardBot automatically moderates Telegram groups using multi-layer AI analysis:
spam detection, sentiment analysis, topic relevance, flood detection, and
a progressive violation/ban policy.

---

## Features

| Feature | Description |
|---|---|
| Spam Detection | Keywords + suspicious links + CAPS + repetition |
| Sentiment Analysis | VADER-based toxicity scoring |
| Topic Filter | Blocks off-topic messages after threshold |
| Flood Detection | Sliding-window burst detection |
| Link Quota | Warn after >3 links/day |
| Violation Tracking | Per-user, per-chat daily counters |
| Auto Ban | Ban after violations on 3 separate days |
| Admin Alerts | DM admins when user is close to ban |
| Reputation Score | 0–100 score per user |
| Audit Log | Full DB log of every action |

---

## Project Structure

```
guardbot/
├── main.py                  ← Entry point
├── requirements.txt
├── .env.example
│
├── config/
│   └── settings.py          ← All tunable thresholds & keywords
│
├── bot/
│   ├── bot.py               ← Application bootstrap
│   ├── handlers.py          ← Telegram update handlers
│   └── moderation.py        ← Moderation engine (orchestrator)
│
├── ai/
│   ├── spam_detector.py     ← 3-layer spam detection
│   ├── sentiment_analyzer.py← VADER toxicity analysis
│   ├── topic_detector.py    ← Relevance scoring
│   └── anomaly_detector.py  ← Flood / raid detection
│
├── database/
│   ├── db.py                ← Engine, session manager
│   ├── models.py            ← SQLAlchemy ORM models
│   └── crud.py              ← All DB operations
│
├── services/
│   ├── activity_tracker.py  ← Message pattern tracker
│   └── reputation_engine.py ← User reputation scoring
│
├── utils/
│   ├── logger.py            ← Rotating file + console logger
│   └── helpers.py           ← Utility functions
│
└── logs/
    └── guardbot.log
```

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/yourname/guardbot.git
cd guardbot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env — add your BOT_TOKEN
```

### 3. Run

```bash
python main.py
```

---

## Bot Commands

| Command | Description |
|---|---|
| `/start` | Confirm bot is active |
| `/rules` | Show group rules |
| `/status` | Show your violation count |

---

## Configuration (config/settings.py)

| Setting | Default | Description |
|---|---|---|
| `SPAM_SCORE_THRESHOLD` | 0.65 | Score above which message is spam |
| `TOXICITY_SCORE_THRESHOLD` | 0.60 | Score above which message is toxic |
| `TOPIC_WARN_THRESHOLD` | 5 | Off-topic messages/day before warn |
| `LINK_WARN_THRESHOLD` | 3 | Links/day before warn |
| `VIOLATION_BAN_DAYS` | 3 | Violation days before auto-ban |
| `MESSAGE_FLOOD_LIMIT` | 10 | Messages per 60s before flood |

---

## Moderation Flow

```
Message received
      │
      ├─ Flood? → Delete
      ├─ Spam?  → Delete + Warn + Record
      ├─ Toxic? → Delete + Warn + Record
      ├─ Too many links? → Warn + Record
      ├─ Off-topic quota exceeded? → Delete + Warn + Record
      │
      └─ Violation days ≥ 3? → BAN + Alert admins
```

---

## Requirements

- Python 3.10+
- `python-telegram-bot` 21.x
- `SQLAlchemy` 2.x
- `vaderSentiment`
- `python-dotenv`

---

## License

MIT
