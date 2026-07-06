import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from telegram.request import HTTPXRequest

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "693765101"))

(
    LANGUAGE,
    NAME,
    AGE,
    CITY,
    HEIGHT,
    WEIGHT,
    MEASUREMENTS,
    SHOE_SIZE,
    HAIR_COLOR,
    EYE_COLOR,
    EXPERIENCE,
    ABROAD,
    BOOK,
    PHOTO,
) = range(14)

STRINGS = {
    "ru": {
        "welcome": (
            "Привет! Добро пожаловать в кастинг-бот для моделей.\n\n"
            "Я задам тебе несколько вопросов, а затем попрошу фото.\n"
            "Для отмены в любой момент напиши /cancel.\n\n"
            "Давай начнём!\n\n"
            "Введи своё *имя и фамилию*:"
        ),
        "ask_age": "Сколько тебе *лет*?",
        "err_age": "Пожалуйста, введи корректный возраст (число от 14 до 80):",
        "ask_city": "В каком *городе* ты живёшь?",
        "ask_height": "Твой *рост* (в см, например: 175)?",
        "err_height": "Пожалуйста, введи рост в сантиметрах (число от 140 до 220):",
        "ask_weight": "Твой *вес* (в кг, например: 55)?",
        "err_weight": "Пожалуйста, введи вес в килограммах (число от 30 до 200):",
        "ask_measurements": "Введи свои *параметры* (обхват груди/талии/бёдер) в формате: *90/60/90*",
        "err_measurements": "Пожалуйста, введи параметры в формате: 90/60/90",
        "ask_shoe": "Размер *обуви*?",
        "err_shoe": "Пожалуйста, введи размер обуви (например: 38 или 38.5):",
        "ask_hair": "Цвет *волос*?",
        "ask_eyes": "Цвет *глаз*?",
        "ask_experience": (
            "*Опыт* в моделинге?\n\n"
            "Например: нет опыта / 1 год / участвовала в показах / работала с брендами и т.д."
        ),
        "ask_abroad": "*Готов/а ли ты к зарубежным контрактам 1–2 раза в год сроком от 3 месяцев?*",
        "abroad_yes": "Да",
        "abroad_no": "Нет",
        "abroad_yes_val": "Да",
        "abroad_no_val": "Нет",
        "err_abroad": "Пожалуйста, выбери один из вариантов:",
        "ask_book": (
            "Пришли ссылку на своё *портфолио / бук*.\n\n"
            "Это может быть ссылка на Instagram, сайт, Google Drive, OneDrive или любой другой ресурс.\n"
            "Если бука нет — напиши *нет*."
        ),
        "err_book": "Пожалуйста, пришли ссылку или напиши «нет»:",
        "caption_book": "*Бук / портфолио:*",
        "ask_photo": (
            "Отлично! Теперь пришли *снэпы* — фото без макияжа, при дневном освещении.\n\n"
            "Требования:\n"
            "• Без макияжа\n"
            "• При естественном дневном свете\n"
            "• Чёткое фото (лицо + фигура)\n"
            "• Без фильтров и обработки\n\n"
            "Можно прислать до 5 фото. После каждого фото нажимай *«Ещё»* или *«Готово»*."
        ),
        "err_photo": "Пожалуйста, пришли именно *фотографию* (снэп без макияжа при дневном освещении).",
        "photo_received": "Фото {} получено! Пришли ещё или нажми «Готово».",
        "photo_done_btn": "Готово",
        "photo_more_btn": "Ещё фото",
        "photo_max": "Максимум 5 фото. Нажми «Готово» для отправки.",
        "photo_none": "Сначала пришли хотя бы одно фото!",
        "photo_count": "*Снэпов в заявке:*",
        "caption_count": "*Снэпов:*",
        "success": "*Спасибо! Твоя заявка отправлена.*\n\nМы свяжемся с тобой в ближайшее время. Удачи!",
        "cancel": "Заявка отменена. Напиши /start чтобы начать заново.",
        "send_error": (
            "Заявка принята, но возникла ошибка при отправке администратору. "
            "Пожалуйста, свяжитесь с нами напрямую."
        ),
        "caption_header": "*НОВАЯ ЗАЯВКА НА КАСТИНГ*",
        "caption_lang": "*Язык:* Русский",
        "caption_name": "*Имя:*",
        "caption_age": "*Возраст:*",
        "caption_city": "*Город:*",
        "caption_height": "*Рост:*",
        "caption_height_unit": "см",
        "caption_weight": "*Вес:*",
        "caption_weight_unit": "кг",
        "caption_measurements": "*Параметры (г/т/б):*",
        "caption_shoe": "*Размер обуви:*",
        "caption_hair": "*Цвет волос:*",
        "caption_eyes": "*Цвет глаз:*",
        "caption_experience": "*Опыт:*",
        "caption_abroad": "*Зарубежные контракты:*",
        "caption_tg": "*Telegram:*",
    },
    "en": {
        "welcome": (
            "Hi! Welcome to the model casting bot.\n\n"
            "I'll ask you a few questions and then request a photo.\n"
            "To cancel at any time, type /cancel.\n\n"
            "Let's get started!\n\n"
            "Enter your *full name*:"
        ),
        "ask_age": "How old are you?",
        "err_age": "Please enter a valid age (a number between 14 and 80):",
        "ask_city": "What *city* do you live in?",
        "ask_height": "Your *height* (in cm, e.g. 175)?",
        "err_height": "Please enter your height in centimetres (a number between 140 and 220):",
        "ask_weight": "Your *weight* (in kg, e.g. 55)?",
        "err_weight": "Please enter your weight in kilograms (a number between 30 and 200):",
        "ask_measurements": "Enter your *measurements* (bust/waist/hips) in the format: *90/60/90*",
        "err_measurements": "Please enter measurements in the format: 90/60/90",
        "ask_shoe": "*Shoe size*?",
        "err_shoe": "Please enter your shoe size (e.g. 38 or 38.5):",
        "ask_hair": "*Hair colour*?",
        "ask_eyes": "*Eye colour*?",
        "ask_experience": (
            "*Modelling experience*?\n\n"
            "E.g. no experience / 1 year / runway shows / worked with brands, etc."
        ),
        "ask_abroad": "*Are you open to international contracts 1–2 times a year, each lasting 3+ months?*",
        "abroad_yes": "Yes",
        "abroad_no": "No",
        "abroad_yes_val": "Yes",
        "abroad_no_val": "No",
        "err_abroad": "Please choose one of the options:",
        "ask_book": (
            "Please send a link to your *portfolio / book*.\n\n"
            "This can be a link to Instagram, a website, Google Drive, OneDrive, or any other resource.\n"
            "If you don't have one — type *no*."
        ),
        "err_book": "Please send a link or type 'no':",
        "caption_book": "*Book / portfolio:*",
        "ask_photo": (
            "Great! Now please send your *snaps* — photos without makeup, taken in natural daylight.\n\n"
            "Requirements:\n"
            "• No makeup\n"
            "• Natural daylight only\n"
            "• Clear photo (face + full body)\n"
            "• No filters or editing\n\n"
            "You can send up to 5 photos. After each one tap *«More»* or *«Done»*."
        ),
        "err_photo": "Please send an actual *photo* (a snap without makeup in natural daylight).",
        "photo_received": "Photo {} received! Send another or tap «Done».",
        "photo_done_btn": "Done",
        "photo_more_btn": "More photos",
        "photo_max": "Maximum 5 photos reached. Tap «Done» to submit.",
        "photo_none": "Please send at least one photo first!",
        "photo_count": "*Snaps in application:*",
        "caption_count": "*Snaps:*",
        "success": "*Thank you! Your application has been submitted.*\n\nWe'll be in touch soon. Good luck!",
        "cancel": "Application cancelled. Type /start to begin again.",
        "send_error": (
            "Application received, but there was an error sending it to the admin. "
            "Please contact us directly."
        ),
        "caption_header": "*NEW CASTING APPLICATION*",
        "caption_lang": "*Language:* English",
        "caption_name": "*Name:*",
        "caption_age": "*Age:*",
        "caption_city": "*City:*",
        "caption_height": "*Height:*",
        "caption_height_unit": "cm",
        "caption_weight": "*Weight:*",
        "caption_weight_unit": "kg",
        "caption_measurements": "*Measurements (B/W/H):*",
        "caption_shoe": "*Shoe size:*",
        "caption_hair": "*Hair colour:*",
        "caption_eyes": "*Eye colour:*",
        "caption_experience": "*Experience:*",
        "caption_abroad": "*International contracts:*",
        "caption_tg": "*Telegram:*",
    },
}


def t(key: str, lang: str) -> str:
    return STRINGS.get(lang, STRINGS["ru"]).get(key, key)


def lang_of(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "ru")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    keyboard = [["Русский", "English"]]
    await update.message.reply_text(
        "Выбери язык / Choose your language:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return LANGUAGE


async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if "English" in text or "english" in text.lower():
        context.user_data["lang"] = "en"
    else:
        context.user_data["lang"] = "ru"
    lang = lang_of(context)
    await update.message.reply_text(
        t("welcome", lang),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text(t("ask_age", lang), parse_mode="Markdown")
    return AGE


async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    text = update.message.text.strip()
    if not text.isdigit() or not (14 <= int(text) <= 80):
        await update.message.reply_text(t("err_age", lang))
        return AGE
    context.user_data["age"] = text
    await update.message.reply_text(t("ask_city", lang), parse_mode="Markdown")
    return CITY


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    context.user_data["city"] = update.message.text.strip()
    await update.message.reply_text(t("ask_height", lang), parse_mode="Markdown")
    return HEIGHT


async def height(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    text = update.message.text.strip()
    if not text.isdigit() or not (140 <= int(text) <= 220):
        await update.message.reply_text(t("err_height", lang))
        return HEIGHT
    context.user_data["height"] = text
    await update.message.reply_text(t("ask_weight", lang), parse_mode="Markdown")
    return WEIGHT


async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    text = update.message.text.strip().replace(",", ".")
    try:
        val = float(text)
        if not (30 <= val <= 200):
            raise ValueError
    except ValueError:
        await update.message.reply_text(t("err_weight", lang))
        return WEIGHT
    context.user_data["weight"] = text
    await update.message.reply_text(t("ask_measurements", lang), parse_mode="Markdown")
    return MEASUREMENTS


async def measurements(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    text = update.message.text.strip()
    parts = text.replace(" ", "").split("/")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        await update.message.reply_text(t("err_measurements", lang))
        return MEASUREMENTS
    context.user_data["measurements"] = text
    await update.message.reply_text(t("ask_shoe", lang), parse_mode="Markdown")
    return SHOE_SIZE


async def shoe_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    text = update.message.text.strip()
    if not text.replace(".", "").isdigit():
        await update.message.reply_text(t("err_shoe", lang))
        return SHOE_SIZE
    context.user_data["shoe_size"] = text
    await update.message.reply_text(t("ask_hair", lang), parse_mode="Markdown")
    return HAIR_COLOR


async def hair_color(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    context.user_data["hair_color"] = update.message.text.strip()
    await update.message.reply_text(t("ask_eyes", lang), parse_mode="Markdown")
    return EYE_COLOR


async def eye_color(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    context.user_data["eye_color"] = update.message.text.strip()
    await update.message.reply_text(t("ask_experience", lang), parse_mode="Markdown")
    return EXPERIENCE


async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    context.user_data["experience"] = update.message.text.strip()
    keyboard = [[t("abroad_yes", lang), t("abroad_no", lang)]]
    await update.message.reply_text(
        t("ask_abroad", lang),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return ABROAD


async def abroad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    text = update.message.text.strip()
    yes_vals = (t("abroad_yes", lang), t("abroad_yes_val", lang), "yes", "да", "Yes", "Да")
    no_vals = (t("abroad_no", lang), t("abroad_no_val", lang), "no", "нет", "No", "Нет")
    if text not in yes_vals and text not in no_vals:
        keyboard = [[t("abroad_yes", lang), t("abroad_no", lang)]]
        await update.message.reply_text(
            t("err_abroad", lang),
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return ABROAD
    context.user_data["abroad"] = t("abroad_yes_val", lang) if text in yes_vals else t("abroad_no_val", lang)
    await update.message.reply_text(
        t("ask_book", lang),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return BOOK


async def book(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text(t("err_book", lang))
        return BOOK
    context.user_data["book"] = text
    await update.message.reply_text(
        t("ask_photo", lang),
        parse_mode="Markdown",
    )
    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    user = update.effective_user
    data = context.user_data

    done_btn = t("photo_done_btn", lang)
    more_btn = t("photo_more_btn", lang)
    photos: list = data.setdefault("photos", [])

    # User tapped "Done" or sent done text
    if update.message.text:
        text = update.message.text.strip()
        done_vals = (done_btn, "Done", "Готово", "done", "готово")
        if text in done_vals:
            if not photos:
                await update.message.reply_text(t("photo_none", lang), parse_mode="Markdown")
                return PHOTO
            return await _submit_application(update, context, lang, user, data, photos)
        # Any other text while in photo state
        await update.message.reply_text(t("err_photo", lang), parse_mode="Markdown")
        return PHOTO

    # Received a photo
    if not update.message.photo:
        await update.message.reply_text(t("err_photo", lang), parse_mode="Markdown")
        return PHOTO

    if len(photos) >= 5:
        await update.message.reply_text(
            t("photo_max", lang),
            reply_markup=ReplyKeyboardMarkup([[done_btn]], one_time_keyboard=True, resize_keyboard=True),
        )
        return PHOTO

    photos.append(update.message.photo[-1].file_id)
    count = len(photos)

    if count < 5:
        keyboard = [[more_btn, done_btn]]
        await update.message.reply_text(
            t("photo_received", lang).format(count),
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return PHOTO
    else:
        # Auto-submit at 5 photos
        return await _submit_application(update, context, lang, user, data, photos)


async def _submit_application(update, context, lang, user, data, photos):
    caption = (
        f"{t('caption_header', lang)}\n\n"
        f"{t('caption_lang', lang)}\n"
        f"{t('caption_name', lang)} {data.get('name', '—')}\n"
        f"{t('caption_age', lang)} {data.get('age', '—')}\n"
        f"{t('caption_city', lang)} {data.get('city', '—')}\n"
        f"{t('caption_height', lang)} {data.get('height', '—')} {t('caption_height_unit', lang)}\n"
        f"{t('caption_weight', lang)} {data.get('weight', '—')} {t('caption_weight_unit', lang)}\n"
        f"{t('caption_measurements', lang)} {data.get('measurements', '—')}\n"
        f"{t('caption_shoe', lang)} {data.get('shoe_size', '—')}\n"
        f"{t('caption_hair', lang)} {data.get('hair_color', '—')}\n"
        f"{t('caption_eyes', lang)} {data.get('eye_color', '—')}\n"
        f"{t('caption_experience', lang)} {data.get('experience', '—')}\n"
        f"{t('caption_abroad', lang)} {data.get('abroad', '—')}\n"
        f"{t('caption_book', lang)} {data.get('book', '—')}\n"
        f"{t('caption_count', lang)} {len(photos)}\n\n"
        f"{t('caption_tg', lang)} @{user.username or '—'} (ID: {user.id})"
    )

    try:
        if len(photos) == 1:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=photos[0],
                caption=caption,
                parse_mode="Markdown",
            )
        else:
            media = [InputMediaPhoto(media=photos[0], caption=caption, parse_mode="Markdown")]
            media += [InputMediaPhoto(media=fid) for fid in photos[1:]]
            await context.bot.send_media_group(chat_id=ADMIN_CHAT_ID, media=media)
        logger.info(f"Application sent to admin {ADMIN_CHAT_ID} from user {user.id} (@{user.username}), {len(photos)} photo(s)")
    except Exception as e:
        logger.error(f"FAILED to send application to admin {ADMIN_CHAT_ID}: {e}")
        await update.message.reply_text(t("send_error", lang))
        context.user_data.clear()
        return ConversationHandler.END

    await update.message.reply_text(
        t("success", lang),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    await update.message.reply_text(
        t("cancel", lang),
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"Test successful! Bot is delivering messages to this chat.\nADMIN_CHAT_ID = {ADMIN_CHAT_ID}",
        )
        await update.message.reply_text("Test sent — check this chat.")
    except Exception as e:
        logger.error(f"test_admin failed: {e}")
        await update.message.reply_text(f"Error: {e}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)


def main() -> None:
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=15.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=15.0,
    )
    app = Application.builder().token(BOT_TOKEN).request(request).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, height)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weight)],
            MEASUREMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, measurements)],
            SHOE_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, shoe_size)],
            HAIR_COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, hair_color)],
            EYE_COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, eye_color)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience)],
            ABROAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, abroad)],
            BOOK: [MessageHandler(filters.TEXT & ~filters.COMMAND, book)],
            PHOTO: [MessageHandler(filters.PHOTO, photo), MessageHandler(filters.TEXT & ~filters.COMMAND, photo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("test_admin", test_admin))
    app.add_error_handler(error_handler)

    logger.info("Bot starting (polling)...")
    app.run_polling(drop_pending_updates=True, timeout=30)


if __name__ == "__main__":
    main()




 




   





   


   

  



   









       

       

       





   

        

   

           

    

  

