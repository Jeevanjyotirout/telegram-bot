"""
GuardBot Telegram Handlers
All update handlers wired to ModerationEngine.
"""

import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
from telegram.error import TelegramError

from bot.moderation import ModerationEngine
from config.settings import (
    WARNING_MESSAGE,
    BAN_MESSAGE,
    ADMIN_ALERT_MESSAGE,
    VIOLATION_BAN_DAYS,
)

from database.db import get_db
from database.crud import get_or_create_user, get_all_violations

logger = logging.getLogger(__name__)

# Shared moderation engine
engine = ModerationEngine()


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def mention(user) -> str:
    """Return mention string."""
    return f"@{user.username}" if user.username else user.first_name


async def get_admin_ids(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    admins = await context.bot.get_chat_administrators(chat_id)
    return [a.user.id for a in admins]


# ------------------------------------------------------------
# Message Handler
# ------------------------------------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    user = update.effective_user
    chat = update.effective_chat

    if not message or not user or not chat:
        return

    if user.is_bot:
        return

    text = message.text or message.caption or ""

    # Run moderation engine
    decision = engine.evaluate(
        user_id=user.id,
        chat_id=chat.id,
        username=user.username,
        full_name=user.full_name,
        text=text,
    )

    # ---------------- DELETE MESSAGE ----------------

    if decision.delete_message:
        try:
            await message.delete()
            logger.info(f"Deleted message from {user.id}")
        except TelegramError as e:
            logger.warning(f"Delete failed: {e}")

    # ---------------- BAN USER ----------------

    if decision.ban_user:
        try:
            await context.bot.ban_chat_member(chat.id, user.id)

            await context.bot.send_message(
                chat.id,
                BAN_MESSAGE.format(
                    mention=mention(user),
                    days=decision.violation_days,
                ),
                parse_mode=ParseMode.MARKDOWN,
            )

            logger.info(f"User banned {user.id}")

        except TelegramError as e:
            logger.error(f"Ban failed: {e}")

        return

    # ---------------- WARN USER ----------------

    if decision.warn_user:

        try:
            with get_db() as db:
                db_user = get_or_create_user(
                    db,
                    user.id,
                    user.username,
                    user.full_name,
                )

                violations = get_all_violations(db, user.id, chat.id)

            warn_text = WARNING_MESSAGE.format(
                mention=mention(user),
                count=len(violations),
            )

            sent = await context.bot.send_message(
                chat.id,
                warn_text,
                parse_mode=ParseMode.MARKDOWN,
            )

            # delete warning later
            context.job_queue.run_once(
                delete_message_job,
                30,
                data={
                    "chat_id": chat.id,
                    "message_id": sent.message_id,
                },
            )

        except TelegramError as e:
            logger.error(f"Warning failed: {e}")

    # ---------------- ALERT ADMINS ----------------

    if decision.alert_admins and not decision.ban_user:

        try:
            admin_ids = await get_admin_ids(chat.id, context)

            alert_text = ADMIN_ALERT_MESSAGE.format(
                mention=mention(user),
                user_id=user.id,
                days=decision.violation_days,
                ban_days=VIOLATION_BAN_DAYS,
                action=", ".join(decision.reasons[:2]) or "rule violation",
                time=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            )

            for admin_id in admin_ids:

                try:
                    await context.bot.send_message(
                        admin_id,
                        alert_text,
                        parse_mode=ParseMode.MARKDOWN,
                    )

                except TelegramError:
                    pass

        except TelegramError as e:
            logger.warning(f"Admin alert failed: {e}")


# ------------------------------------------------------------
# Job Queue Helper
# ------------------------------------------------------------

async def delete_message_job(context: ContextTypes.DEFAULT_TYPE):

    data = context.job.data

    try:
        await context.bot.delete_message(
            data["chat_id"],
            data["message_id"],
        )
    except TelegramError:
        pass


# ------------------------------------------------------------
# /start
# ------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🛡️ *GuardBot is active!*\n\n"
        "I monitor this group to prevent spam and rule violations.",
        parse_mode=ParseMode.MARKDOWN,
    )


# ------------------------------------------------------------
# /status
# ------------------------------------------------------------

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    chat = update.effective_chat

    with get_db() as db:
        violations = get_all_violations(db, user.id, chat.id)

    await update.message.reply_text(
        f"📊 *Moderation Status*\n\n"
        f"User: {mention(user)}\n"
        f"Violations: {len(violations)}",
        parse_mode=ParseMode.MARKDOWN,
    )


# ------------------------------------------------------------
# /rules
# ------------------------------------------------------------

async def cmd_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📋 *Group Rules*\n\n"
        "1. Stay on topic\n"
        "2. No spam or advertising\n"
        "3. No toxic language\n"
        "4. Max 3 links per day\n"
        "5. 3 violation days → ban\n",
        parse_mode=ParseMode.MARKDOWN,
    )


# ------------------------------------------------------------
# ERROR HANDLER
# ------------------------------------------------------------

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):

    logger.error(
        "Unhandled error",
        exc_info=context.error,
    )


# ------------------------------------------------------------
# REGISTER HANDLERS
# ------------------------------------------------------------

def register_handlers(application):

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("rules", cmd_rules))

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    application.add_error_handler(error_handler)