import logging
import os
from html import escape

import httpx
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
)

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = os.getenv("TOKEN", "")
API_BASE_URL = os.getenv("API_BASE_URL", "")


# Главная клавиатура
def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [["Маршруты", "Коллекции"], ["Точки интереса"]], resize_keyboard=True
    )


# Команда /start
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    if update.message:
        await update.message.reply_text(
            f"Привет, {user.first_name}! Чем могу помочь? Выберите одну из опций.",
            reply_markup=main_keyboard(),
        )


# Отображение маршрутов
async def show_routes(update: Update, context: CallbackContext):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/routers/")
            response.raise_for_status()
            routers = response.json()

            if not routers:
                await update.message.reply_text(
                    "🚧 Пока маршруты не добавлены. Создайте свой первый маршрут!"
                )
                return

            for router in routers:
                name = escape(router.get("name", "Без названия"))
                description = escape(router.get("description", "Нет описания"))
                start_date = escape(router.get("start_date", "Не указана"))
                end_date = escape(router.get("end_date", "Не указана"))
                author = escape(
                    router.get("author", {}).get("username", "Неизвестный автор")
                )
                photo = router.get("photo")

                points = router.get("points", [])
                if isinstance(points, list):
                    points_text = (
                        "\n".join(
                            f"📍 {escape(p.get('name', 'Без названия'))} ({p.get('latitude')}, {p.get('longitude')})"
                            for p in points
                        )
                        or "Нет точек интереса."
                    )
                else:
                    points_text = "Нет точек интереса."

                msg = (
                    f"🗺 <b>{name}</b>\n"
                    f"👤 Автор: {author}\n"
                    f"📅 Начало: {start_date}\n"
                    f"⏳ Конец: {end_date}\n"
                    f"📝 {description}\n\n"
                    f"{points_text}"
                )

                # if photo:
                #     # await update.message.reply_photo(photo, caption=msg, parse_mode="HTML")
                #     pass
                # else:
                await update.message.reply_text(msg, parse_mode="HTML")

        except httpx.RequestError as exc:
            logger.error(f"Ошибка запроса: {exc}")
            await update.message.reply_text("Произошла ошибка при получении маршрутов.")


# Отображение коллекций
async def show_collections(update: Update, context: CallbackContext):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/collections/")
            response.raise_for_status()
            collections = response.json()

            if not collections:
                await update.message.reply_text(
                    "📭 Коллекции пока не добавлены. Создайте свою коллекцию маршрутов!"
                )
                return

            for collection in collections:
                name = escape(collection.get("name", "Без названия"))
                description = escape(collection.get("description", "Нет описания"))
                is_public = "Да" if collection.get("is_public") else "Нет"
                routers = collection.get("routers", [])

                router_text = (
                    "\n".join(
                        f"🗺 <b>{escape(r.get('name', 'Без названия'))}</b>\n📝 {escape(r.get('description', 'Нет описания'))}"
                        for r in routers
                    )
                    or "Маршруты не добавлены."
                )

                msg = (
                    f"📚 <b>{name}</b>\n"
                    f"🖋 <i>Описание:</i> {description}\n"
                    f"🌍 Доступность: {is_public}\n\n"
                    f"{router_text}"
                )

                await update.message.reply_text(msg, parse_mode="HTML")

        except httpx.RequestError as exc:
            logger.error(f"Ошибка запроса: {exc}")
            await update.message.reply_text("Произошла ошибка при получении коллекций.")


# Отображение точек интереса (заглушка)
# Показ точек интереса
async def show_points(update: Update, context: CallbackContext):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/points/")
            response.raise_for_status()
            points = response.json()

            if not points:
                await update.message.reply_text("Нет точек интереса.")
                return

            for point in points:
                name = escape(point.get("name", "Без названия"))
                description = escape(point.get("description", ""))
                latitude = point.get("latitude", "не указано")
                longitude = point.get("longitude", "не указано")
                category = escape(point.get("category", "не указана"))
                photo = point.get("photo")

                msg = (
                    f"📍 <b>{name}</b>\n"
                    f"📝 {description}\n"
                    f"📌 Координаты: {latitude}, {longitude}\n"
                    f"🏷 Категория: {category}"
                )

                # if photo:
                #     # await update.message.reply_photo(photo, caption=msg, parse_mode="HTML")
                #     pass
                # else:
                await update.message.reply_text(msg, parse_mode="HTML")

        except httpx.RequestError as exc:
            logger.error(f"Ошибка запроса: {exc}")
            await update.message.reply_text(
                "Произошла ошибка при получении точек интереса."
            )


# Обработка нажатий на кнопки
async def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text.lower()

    if text == "маршруты":
        await show_routes(update, context)
    elif text == "коллекции":
        await show_collections(update, context)
    elif text == "точки интереса":
        await show_points(update, context)
    else:
        await update.message.reply_text(
            "Не понял. Пожалуйста, выберите одну из доступных опций."
        )


# Запуск бота
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("routes", show_routes))
    application.add_handler(CommandHandler("collections", show_collections))
    application.add_handler(CommandHandler("points", show_points))

    # Старт опроса
    application.run_polling()


if __name__ == "__main__":
    main()
