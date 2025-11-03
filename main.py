import asyncio
import random
import logging
import json
import os
from datetime import datetime, date
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- Налаштування бота ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_PASSWORD = "WaterBoss_2025"
# Monobank Jar (встав свою):
# https://send.monobank.ua/jar/9dJNHNB4vS

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

DATA_FILE = "bot_data.json"
ADMINS_FILE = "admins.json"
PROMO_FILE = "promo_data.json"

# --- Меню (повний список, лише перегляд) ---
menu = {
    "☕ Кава": {
        "Кава класика": [
            "Еспресо — 30 мл / 35 грн", "Еспресо допіо — 60 мл / 39 грн",
            "Американо — 180 мл / 40 грн", "Фільтр кава — 200 мл / 40 грн",
            "Еспресо з молоком — 40 мл / 45 грн", "Американо з молоком — 200 мл / 45 грн",
            "Капучино маленьке — 180 мл / 45 грн", "Капучино стандартне — 240 мл / 55 грн",
            "Лате стандартне — 240 мл / 60 грн", "Лате велике — 360 мл / 70 грн",
            "Флет Уайт — 240 мл / 65 грн"
        ],
        "Кава класика по-новому": [
            "АЙС ЛАТЕ йогурт крем — 70 грн", "ОРАНЖ кава — 70 грн",
            "ЕСПРЕСО ТОНІК фіалка — 70 грн", "КРЕМ КАВА ваніль-кунжут — 75 грн",
            "ГЛЯСЕ мікс морозиво — 85 грн"
        ],
        "Кава авторська": [
            "КАВУН-ДИНЯ мікс — 75 грн", "ШОКО-МОКА згущене молоко — 70 грн",
            "ФІЛЬТР кола-ваніль — 70 грн", "ФІЛЬТР тонік-грейпфрут — 70 грн",
            "ЯГІДНИЙ айс мигдаль — 75 грн", "АЙС КАВА халва-мигдаль — 75 грн"
        ]
    },
    "❄️ Холодні напої": {
        "Холодні тренди": [
            "БАБЛ ТІ екзотичний мікс — 500 мл / 110 грн", "БАБЛ ТІ шоко-кава — 500 мл / 110 грн",
            "ХЕЛСІ лимонад цитрус пінка — 300 мл / 90 грн", "ДУБАЙСЬКИЙ ШЕЙК — 300 мл / 120 грн",
            "ФІСТАШКА карамель — 300 мл / 110 грн", "МАТЧА ТРОПІК молоко — 300 мл / 110 грн",
            "МАТЧА ТРОПІК фреш — 300 мл / 110 грн"
        ],
        "Мілкшейки": [
            "КЛАСІК молоко-морозиво — 85 грн", "ЛІСОВІ ЯГОДИ малина-смородина — 85 грн",
            "МУЛЬТІФРУКТ папая-маракуя — 85 грн", "ШОКО ШЕЙК банан-печиво орео — 85 грн",
            "КОКОС-МИГДАЛЬ крем паста — 85 грн"
        ]
    },
    "🍵 Чай": {
        "Чай авторський": [
            "КАСКАРА пряний апельсин — 70 грн", "МАЛИНОВИЙ джем з каркаде — 70 грн",
            "ОБЛІПИХОВИЙ з персиком — 70 грн", "ФРУКТОВИЙ папая-маракуя — 70 грн",
            "ЯБЛУЧНИЙ штрудель з корицею — 70 грн"
        ],
        "Чай Ronnefeldt (пакетований)": [
            "ЧОРНИЙ класичний — 500 мл / 60 грн", "ЕРЛ ГРЕЙ бергамот — 500 мл / 60 грн",
            "ЗЕЛЕНИЙ класичний — 500 мл / 60 грн", "РОМАШКА класичний — 500 мл / 60 грн",
            "УЛУН молочний — 500 мл / 60 грн", "РОЙБУШ апельсин — 500 мл / 60 грн"
        ],
        "🔥 ГАРЯЧІ НАПОЇ": [
            "КАКАО ТОФФІ карамель — 240 мл / 65 грн", "КАКАО БЕЛЬГІЙСЬКЕ з червоних бобів — 240 мл / 65 грн",
            "ПУНШ ЯГІДНИЙ з прянощами — 240 мл / 65 грн", "МАТЧА ЛАТЕ чай з молоком — 240 мл / 65 грн",
            "ДИТЯЧА КАВА кокос-халва — 240 мл / 65 грн"
        ]
    }
}

# Константа для безкоштовної кави
DRINKS_FOR_FREE_DRINK = 9


# --- Збереження/завантаження ---
def load_admins():
    if os.path.exists(ADMINS_FILE):
        try:
            with open(ADMINS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"admins": []}
    return {"admins": []}


def save_admins():
    with open(ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump(admins_data, f, ensure_ascii=False, indent=2)


def is_admin(user_id: int) -> bool:
    return user_id in admins_data["admins"]


admins_data = load_admins()


def load_promo():
    if os.path.exists(PROMO_FILE):
        try:
            with open(PROMO_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('promo_text', '🎁 Акції розробляються! Незабаром з\'явиться щось цікаве!')
        except:
            return '🎁 Акції розробляються! Незабаром з\'явиться щось цікаве!'
    return '🎁 Акції розробляються! Незабаром з\'явиться щось цікаве!'


def save_promo(text: str):
    with open(PROMO_FILE, 'w', encoding='utf-8') as f:
        json.dump({'promo_text': text}, f, ensure_ascii=False, indent=2)


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'user_drinks_count': user_drinks_count,
            'user_orders': user_orders,
            'user_birthdays': user_birthdays,
            'user_names': user_names,
            'user_reviews': user_reviews,
            'contest_winner': contest_winner,
            'contest_participants': contest_participants,
            'known_users': list(known_users),
            'pending_free_drink_requests': pending_free_drink_requests,
        }, f, ensure_ascii=False, indent=2)


data = load_data()
user_drinks_count: dict[int, int] = {int(k): v for k, v in data.get('user_drinks_count', {}).items()}
user_orders: dict[int, int] = {int(k): v for k, v in data.get('user_orders', {}).items()}
user_birthdays: dict[int, str] = {int(k): v for k, v in data.get('user_birthdays', {}).items()}
user_names: dict[int, str] = {int(k): v for k, v in data.get('user_names', {}).items()}
user_reviews: list = data.get('user_reviews', [])
contest_winner = data.get('contest_winner', None)
contest_participants: list = data.get('contest_participants', [])
known_users: set[int] = set(map(int, data.get('known_users', [])))
pending_free_drink_requests: dict[int, dict] = {int(k): v for k, v in
                                                data.get('pending_free_drink_requests', {}).items()}


def next_review_id() -> int:
    ids = [r.get('id', 0) for r in user_reviews if isinstance(r, dict)]
    return (max(ids) + 1) if ids else 1


def get_user_display_name(user_id: int) -> str:
    """Повертає ім'я користувача або ID якщо ім'я немає"""
    return user_names.get(user_id, f"ID {user_id}")


# --- Стан машини ---
class AdminPasswordStates(StatesGroup):
    waiting_for_password = State()


class PromoEditStates(StatesGroup):
    waiting_for_promo_text = State()


class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_birthday = State()


class ReviewStates(StatesGroup):
    waiting_for_review = State()


class AdminEnterAmountStates(StatesGroup):
    waiting_for_amount = State()


class ContestStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_description = State()


class NewsletterStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_content = State()
    waiting_for_confirmation = State()


# --- Кнопки ---
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👋 Я тут"), KeyboardButton(text="💎 Мій баланс")],
            [KeyboardButton(text="🥤 Напої"), KeyboardButton(text="🎁 Безкоштовна кава")],
            [KeyboardButton(text="💸 Списати бонуси"), KeyboardButton(text="☕ Акції")],
            [KeyboardButton(text="📸 Конкурс фото"), KeyboardButton(text="🏆 Переможці")],
            [KeyboardButton(text="💬 Відгуки"), KeyboardButton(text="💸 Залишити чайові")],
            [KeyboardButton(text="☕ Про нас")]
        ],
        resize_keyboard=True,
        persistent=True
    )


def get_admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Розсилка"), KeyboardButton(text="🏆 Переможці")],
            [KeyboardButton(text="☕ Акції"), KeyboardButton(text="✏️ Редагувати акцію")],
            [KeyboardButton(text="🗑 Відгуки (адмін)"), KeyboardButton(text="🚪 Вийти з адмін-режиму")]
        ],
        resize_keyboard=True,
        persistent=True
    )


def get_tip_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Відкрити Банку", url="https://send.monobank.ua/jar/9dJNHNB4vS")]
    ])


def get_enter_amount_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Ввести кількість напоїв", callback_data=f"enter_amount_{user_id}")]
    ])


# Кнопки головного меню для виходу зі станів
BUTTON_TEXTS = {
    "👋 Я тут", "💎 Мій баланс", "🥤 Напої", "🎁 Безкоштовна кава", "💸 Списати бонуси", "☕ Акції",
    "📸 Конкурс фото", "🏆 Переможці", "💬 Відгуки", "💸 Залишити чайові", "☕ Про нас"
}

GREETINGS = [
    "Привіт! ☕ Ласкаво просимо до нашої кав'ярні!",
    "Вітаю! 🌟 Раді бачити вас у нашій кав'ярні!",
    "Привіт! ☕ Готові до смачного кавового досвіду?"
]


def newsletter_targets() -> list[int]:
    ids = set(known_users) | set(user_drinks_count.keys()) | set(user_birthdays.keys())
    return [int(x) for x in ids]


# --- /start ---
@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "Користувач"
    known_users.add(user_id)
    save_data()

    # Перевірка чи є ім'я
    if user_id not in user_names:
        await message.answer(
            f"👋 Привіт, {username}!\n\n"
            f"Для початку роботи введіть ваше ім'я:"
        )
        await state.set_state(RegistrationStates.waiting_for_name)
        return

    # Перевірка чи є день народження
    if user_id not in user_birthdays:
        user_name = user_names.get(user_id, username)
        await message.answer(
            f"🎂 Привіт, {user_name}!\n\n"
            f"Введіть свій день народження у форматі ДД.ММ.РРРР (наприклад: 15.03.1990)"
        )
        await state.set_state(RegistrationStates.waiting_for_birthday)
        return

    role = "👑 Адмін" if is_admin(user_id) else "👤 Клієнт"
    drinks_count = user_drinks_count.get(user_id, 0)
    order_count = user_orders.get(user_id, 0)
    drinks_until_free = DRINKS_FOR_FREE_DRINK - (drinks_count % DRINKS_FOR_FREE_DRINK)
    has_free_drink = drinks_count % DRINKS_FOR_FREE_DRINK == 0 and drinks_count > 0
    greeting = random.choice(GREETINGS)
    user_name = user_names.get(user_id, username)

    status_text = "🎁 У вас є безкоштовна кава!" if has_free_drink else f"☕ До безкоштовної кави: {drinks_until_free} напоїв"

    await message.answer(
        f"{greeting}\n\n"
        f"👤 Роль: {role}\n"
        f"👤 Ім'я: {user_name}\n"
        f"🥤 Випито напоїв: {drinks_count}\n"
        f"📦 Замовлень: {order_count}\n"
        f"{status_text}\n\n"
        f"Обирайте дії з меню 👇",
        reply_markup=get_admin_menu() if is_admin(user_id) else get_main_menu()
    )


@dp.message(RegistrationStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or len(name) > 50:
        await message.answer("❌ Ім'я має бути від 2 до 50 символів. Спробуйте ще раз:")
        return
    user_names[message.from_user.id] = name
    save_data()

    await message.answer(
        f"✅ Ім'я збережено: {name}\n\n"
        f"🎂 Тепер введіть свій день народження у форматі ДД.ММ.РРРР (наприклад: 15.03.1990)"
    )
    await state.set_state(RegistrationStates.waiting_for_birthday)


@dp.message(RegistrationStates.waiting_for_birthday)
async def process_birthday(message: types.Message, state: FSMContext):
    try:
        birthday = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
        user_birthdays[message.from_user.id] = birthday.isoformat()
        save_data()
        user_name = user_names.get(message.from_user.id, "Користувач")
        await message.answer(f"✅ Дата збережена, {user_name}! Можете користуватися ботом.")
        await state.clear()
        await start_command(message, state)
    except ValueError:
        await message.answer("❌ Невірний формат. Приклад: 15.03.1990")


# --- Адмінка ---
@dp.message(Command("admin"))
async def admin_panel(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("✅ Ви вже адміністратор", reply_markup=get_admin_menu())
        return
    await message.answer("🔐 Введіть пароль для доступу до адмін панелі:")
    await state.set_state(AdminPasswordStates.waiting_for_password)


@dp.message(AdminPasswordStates.waiting_for_password)
async def process_admin_password(message: types.Message, state: FSMContext):
    if message.text.strip() == ADMIN_PASSWORD:
        if message.from_user.id not in admins_data["admins"]:
            admins_data["admins"].append(message.from_user.id)
            save_admins()
        await message.answer("✅ Успішний вхід в адмін панель.", reply_markup=get_admin_menu())
    else:
        await message.answer("❌ Неправильний пароль")
    await state.clear()


@dp.message(F.text == "🚪 Вийти з адмін-режиму")
async def exit_admin_mode(message: types.Message):
    uid = message.from_user.id
    if not is_admin(uid):
        await message.answer("❌ Ви не є адміністратором")
        return
    admins_data["admins"] = [a for a in admins_data["admins"] if a != uid]
    save_admins()
    await message.answer("👤 Ви вийшли з адмін-режиму", reply_markup=get_main_menu())


# --- Я ТУТ ---
@dp.message(F.text == "👋 Я тут")
async def i_am_here(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Невідомий"
    user_name = get_user_display_name(user_id)
    known_users.add(user_id)
    save_data()

    text_for_admin = (
        "🟢 Клієнт на місці!\n\n"
        f"👤 Ім'я: {user_name}\n"
        f"🥤 Поточна кількість напоїв: {user_drinks_count.get(user_id, 0)}\n\n"
        "Натисніть кнопку нижче, щоб додати напій."
    )
    keyboard = get_enter_amount_keyboard(user_id)
    for admin_id in admins_data["admins"]:
        try:
            await bot.send_message(admin_id, text_for_admin, reply_markup=keyboard)
        except Exception as e:
            logging.error(f"Error send to admin {admin_id}: {e}")
    await message.answer("✅ Повідомили адміністратора. Очікуйте оновлення лічильника напоїв.")


@dp.callback_query(F.data.startswith("enter_amount_"))
async def enter_amount_callback(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Лише для адміністраторів")
        return
    try:
        target_user_id = int(callback.data.split("_")[2])
    except:
        await callback.answer("❌ Неправильні дані")
        return
    target_name = get_user_display_name(target_user_id)
    await callback.message.edit_text(f"✍️ Введіть кількість напоїв для користувача {target_name}\nЧисло від 1 до 10:")
    await state.update_data(target_user_id=target_user_id)
    await state.set_state(AdminEnterAmountStates.waiting_for_amount)
    await callback.answer()


@dp.message(AdminEnterAmountStates.waiting_for_amount)
async def admin_enter_amount(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ заборонено")
        await state.clear()
        return
    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    if not target_user_id:
        await message.answer("❌ Не знайдено користувача. Спробуйте знову.")
        await state.clear()
        return
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("❌ Введіть коректну кількість (лише число!)")
        return
    drinks = int(text)
    if drinks < 1 or drinks > 10:
        await message.answer("❌ Кількість має бути від 1 до 10")
        return

    old_count = user_drinks_count.get(target_user_id, 0)
    user_drinks_count[target_user_id] = old_count + drinks
    user_orders[target_user_id] = user_orders.get(target_user_id, 0) + 1
    save_data()

    new_count = user_drinks_count[target_user_id]
    drinks_until_free = DRINKS_FOR_FREE_DRINK - (new_count % DRINKS_FOR_FREE_DRINK)
    has_free_drink = new_count % DRINKS_FOR_FREE_DRINK == 0

    status_text = "🎉 Вітаємо! У вас накопичилася безкоштовна кава!" if has_free_drink else f"☕ До безкоштовної кави залишилось: {drinks_until_free} напоїв"

    target_name = get_user_display_name(target_user_id)
    try:
        await bot.send_message(
            target_user_id,
            f"✅ Дякуємо за покупку!\n"
            f"🥤 Додано напоїв: {drinks}\n"
            f"📊 Загальна кількість: {new_count}\n\n"
            f"{status_text}"
        )
    except Exception as e:
        logging.error(f"Error notify user {target_user_id}: {e}")

    await message.answer(f"✅ Додано {drinks} напоїв користувачу {target_name}.\n📊 Нова кількість: {new_count} напоїв.")
    await state.clear()


# --- Напої (перегляд) ---
@dp.message(F.text == "🥤 Напої")
async def show_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for category in menu.keys():
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=category, callback_data=f"category_{category}")])
    await message.answer("📱 <b>Наше меню</b>\n\nОберіть категорію:", reply_markup=keyboard)


@dp.callback_query(F.data.startswith("category_"))
async def show_category(callback: types.CallbackQuery):
    category_name = callback.data.replace("category_", "")
    if category_name not in menu:
        await callback.answer("❌ Категорія не знайдена")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for subcategory in menu[category_name].keys():
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text=subcategory, callback_data=f"subcategory_{subcategory}")])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад до меню", callback_data="back_to_menu")])
    await callback.message.edit_text(f"📱 <b>{category_name}</b>\n\nОберіть підкатегорію:", reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data.startswith("subcategory_"))
async def show_items(callback: types.CallbackQuery):
    subcategory_name = callback.data.replace("subcategory_", "")
    parent_category, items = None, None
    for cat, subcats in menu.items():
        if subcategory_name in subcats:
            parent_category = cat
            items = subcats[subcategory_name]
            break
    if not items:
        await callback.answer("❌ Підкатегорія не знайдена")
        return
    text = f"📋 <b>{subcategory_name}</b>\n\n" + "\n".join(f"• {i}" for i in items)
    await callback.message.edit_text(
        text + "\n\n🔙 Назад",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"category_{parent_category}")]
        ])
    )
    await callback.answer()


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for category in menu.keys():
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=category, callback_data=f"category_{category}")])
    await callback.message.edit_text("📱 <b>Наше меню</b>\n\nОберіть категорію:", reply_markup=keyboard)
    await callback.answer()


# --- Баланс / Безкоштовна кава / Списати бонуси ---
@dp.message(F.text == "💎 Мій баланс")
async def balance(message: types.Message):
    uid = message.from_user.id
    known_users.add(uid)
    save_data()
    drinks_count = user_drinks_count.get(uid, 0)
    orders = user_orders.get(uid, 0)
    drinks_until_free = DRINKS_FOR_FREE_DRINK - (drinks_count % DRINKS_FOR_FREE_DRINK)
    has_free_drink = drinks_count % DRINKS_FOR_FREE_DRINK == 0 and drinks_count > 0

    if has_free_drink:
        status_text = "🎁 У вас є безкоштовна кава! Використайте її через кнопку 'Списати бонуси'."
    else:
        status_text = f"☕ До безкоштовної кави залишилось: {drinks_until_free} напоїв"

    await message.answer(
        f"💎 <b>Ваш баланс</b>\n\n"
        f"🥤 Випито напоїв: {drinks_count}\n"
        f"📦 Кількість замовлень: {orders}\n"
        f"🎯 Система: кожна {DRINKS_FOR_FREE_DRINK}-та кава безкоштовна\n\n"
        f"{status_text}"
    )


@dp.message(F.text == "🎁 Безкоштовна кава")
async def free_drink_info(message: types.Message):
    uid = message.from_user.id
    known_users.add(uid)
    save_data()
    drinks_count = user_drinks_count.get(uid, 0)
    drinks_until_free = DRINKS_FOR_FREE_DRINK - (drinks_count % DRINKS_FOR_FREE_DRINK)
    has_free_drink = drinks_count % DRINKS_FOR_FREE_DRINK == 0 and drinks_count > 0

    if has_free_drink:
        await message.answer(
            f"🎁 <b>Безкоштовна кава</b>\n\n"
            f"🎉 Вітаємо! У вас накопичилася безкоштовна кава!\n\n"
            f"🥤 Випито напоїв: {drinks_count}\n"
            f"📊 Кожна {DRINKS_FOR_FREE_DRINK}-та кава безкоштовна\n\n"
            f"Натисніть кнопку '💸 Списати бонуси', щоб використати безкоштовну каву ☕"
        )
    else:
        await message.answer(
            f"🎁 <b>Безкоштовна кава</b>\n\n"
            f"🥤 Випито напоїв: {drinks_count}\n"
            f"☕ До безкоштовної кави залишилось: {drinks_until_free} напоїв\n\n"
            f"🎯 Система: кожна {DRINKS_FOR_FREE_DRINK}-та кава безкоштовна\n"
            f"Продовжуйте замовляти, і незабаром ви отримаєте безкоштовну каву!"
        )


@dp.message(F.text == "💸 Списати бонуси")
async def request_free_drink(message: types.Message):
    uid = message.from_user.id
    known_users.add(uid)
    save_data()
    drinks_count = user_drinks_count.get(uid, 0)
    user_name = get_user_display_name(uid)

    # Перевірка чи є безкоштовна кава
    if drinks_count % DRINKS_FOR_FREE_DRINK != 0 or drinks_count == 0:
        drinks_until_free = DRINKS_FOR_FREE_DRINK - (drinks_count % DRINKS_FOR_FREE_DRINK)
        await message.answer(
            f"❌ На жаль, у вас немає безкоштовної кави.\n\n"
            f"🥤 Поточна кількість напоїв: {drinks_count}\n"
            f"☕ Потрібно ще {drinks_until_free} напоїв до безкоштовної кави."
        )
        return

    # Створюємо запит
    pending_free_drink_requests[uid] = {
        "user_id": uid,
        "user_name": user_name,
        "username": message.from_user.username or "Користувач",
        "drinks_count": drinks_count,
        "date": datetime.now().isoformat()
    }
    save_data()

    # Відправляємо адмінам
    text_admin = (
        f"💸 <b>Запит на списання бонусів (безкоштовна кава)</b>\n\n"
        f"👤 Ім'я: {user_name}\n"
        f"🥤 Кількість напоїв: {drinks_count}\n\n"
        f"Підтвердити списання?"
    )
    kb_admin = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Підтвердити", callback_data=f"fd_confirm_{uid}"),
            InlineKeyboardButton(text="❌ Відхилити", callback_data=f"fd_reject_{uid}")
        ]
    ])

    sent_to_admins = False
    for admin_id in admins_data["admins"]:
        try:
            await bot.send_message(admin_id, text_admin, reply_markup=kb_admin)
            sent_to_admins = True
        except Exception as e:
            logging.error(f"Send free drink request to admin {admin_id}: {e}")

    if sent_to_admins:
        await message.answer(
            f"✅ Заявку відправлено адміністратору.\n"
            f"Очікуйте підтвердження для використання безкоштовної кави ☕"
        )
    else:
        await message.answer("❌ Не вдалося відправити заявку. Спробуйте пізніше.")


@dp.callback_query(F.data.startswith("fd_confirm_"))
async def free_drink_confirm(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌")
        return
    try:
        uid = int(callback.data.replace("fd_confirm_", ""))
    except:
        await callback.answer("Помилка")
        return

    req = pending_free_drink_requests.get(uid)
    if not req:
        await callback.message.edit_text("❌ Заявку не знайдено (можливо вже оброблена).")
        await callback.answer()
        return

    drinks_count = user_drinks_count.get(uid, 0)

    # Перевірка чи ще є безкоштовна кава
    if drinks_count % DRINKS_FOR_FREE_DRINK != 0 or drinks_count == 0:
        await callback.message.edit_text(
            f"❌ У користувача вже немає безкоштовної кави.\n"
            f"🥤 Поточна кількість напоїв: {drinks_count}"
        )
        if uid in pending_free_drink_requests:
            del pending_free_drink_requests[uid]
            save_data()
        await callback.answer("Недостатньо напоїв")
        return

    # Скидаємо лічильник
    user_drinks_count[uid] = (drinks_count // DRINKS_FOR_FREE_DRINK - 1) * DRINKS_FOR_FREE_DRINK
    user_name = get_user_display_name(uid)
    save_data()

    try:
        await bot.send_message(
            uid,
            f"🎉 Безкоштовна кава підтверджена!\n"
            f"☕ Насолоджуйтесь вашою безкоштовною кавою!\n\n"
            f"🥤 Залишилось напоїв: {user_drinks_count[uid]}\n"
            f"📊 До наступної безкоштовної кави: {DRINKS_FOR_FREE_DRINK} напоїв"
        )
    except Exception as e:
        logging.error(f"Error notify user {uid}: {e}")

    del pending_free_drink_requests[uid]
    save_data()
    await callback.message.edit_text(f"✅ Підтверджено. Безкоштовна кава використана користувачем {user_name}.")
    await callback.answer("Готово")


@dp.callback_query(F.data.startswith("fd_reject_"))
async def free_drink_reject(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌")
        return
    try:
        uid = int(callback.data.replace("fd_reject_", ""))
    except:
        await callback.answer("Помилка")
        return

    if uid in pending_free_drink_requests:
        user_name = get_user_display_name(uid)
        del pending_free_drink_requests[uid]
        save_data()
        try:
            await bot.send_message(uid, "❌ Ваш запит на використання безкоштовної кави відхилено.")
        except Exception as e:
            logging.error(e)
        await callback.message.edit_text(f"❌ Відхилено запит на списання бонусів для {user_name}.")
        await callback.answer("Відхилено")
    else:
        await callback.message.edit_text("❌ Заявку не знайдено.")
        await callback.answer()


# --- Акції / Про нас ---
@dp.message(F.text == "☕ Акції")
async def show_promo(message: types.Message):
    await message.answer(f"🎉 <b>Поточні акції</b>\n\n{load_promo()}")


@dp.message(F.text == "✏️ Редагувати акцію")
async def edit_promo_start(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ заборонено")
        return
    await message.answer(
        f"✏️ <b>Редагування акції</b>\n\nПоточний текст:\n{load_promo()}\n\nНадішліть новий текст:"
    )
    await state.set_state(PromoEditStates.waiting_for_promo_text)


@dp.message(PromoEditStates.waiting_for_promo_text)
async def save_promo_text(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ заборонено")
        await state.clear()
        return
    save_promo(message.text)
    await message.answer("✅ Акцію оновлено!", reply_markup=get_admin_menu())
    await state.clear()


@dp.message(F.text == "☕ Про нас")
async def about_us(message: types.Message):
    await message.answer(
        "☕ <b>Про нас</b>\n\n"
        "Свіжа кава, професійні бариста, затишна атмосфера.\n"
        "🎂 Безкоштовний напій у день народження.\n"
        "🎁 Регулярні акції та конкурс фото.\n"
        f"☕ Кожна {DRINKS_FOR_FREE_DRINK}-та кава безкоштовна!"
    )


@dp.message(F.text == "💸 Залишити чайові")
async def leave_tip(message: types.Message):
    await message.answer("Дякуємо за підтримку! 💖 Натисніть нижче, щоб залишити чайові 👇",
                         reply_markup=get_tip_keyboard())


# --- Відгуки ---
@dp.message(F.text == "💬 Відгуки")
async def reviews_entry(message: types.Message):
    kb_rows = [
        [InlineKeyboardButton(text="📝 Залишити відгук", callback_data="rv_leave")],
        [InlineKeyboardButton(text="📖 Переглянути відгуки", callback_data="rv_view")]
    ]
    if is_admin(message.from_user.id):
        kb_rows.append([InlineKeyboardButton(text="🗑 Всі відгуки (адмін)", callback_data="rv_admin_view")])
    await message.answer("💬 Виберіть дію:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))


@dp.message(F.text == "🗑 Відгуки (адмін)")
async def admin_reviews_manage(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ заборонено")
        return

    # Показуємо меню керування відгуками
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Переглянути всі відгуки", callback_data="rv_admin_view")],
        [InlineKeyboardButton(text="🗑 Видалити всі старі відгуки", callback_data="rv_delete_all_old")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="rv_back")]
    ])
    await message.answer(
        "🗑 <b>Керування відгуками</b>\n\n"
        "Оберіть дію:",
        reply_markup=kb
    )


@dp.callback_query(F.data == "rv_delete_all_old")
async def rv_delete_all_old(callback: types.CallbackQuery):
    """Видаляє всі старі відгуки (ті що були до нової версії)"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ заборонено")
        return

    original_count = len(user_reviews)

    # Видаляємо відгуки які відповідають старим паттернам
    filtered_reviews = []
    for r in user_reviews:
        if not isinstance(r, dict):
            continue

        username = r.get("username", "").lower()
        comment = r.get("comment", "")

        # Перевіряємо чи цей відгук потрібно видалити
        should_delete = False

        # ВИДАЛЯЄМО ВСІ ВІДГУКИ ВІД ЦИХ КОРИСТУВАЧІВ
        old_usernames = ["igoor2_2", "ania_shvalikovska", "невідомий", "користувач"]

        # Перевірка по username
        for old_username in old_usernames:
            if old_username in username or old_username.replace("@", "") in username:
                should_delete = True
                break

        # Також видаляємо за коментарями
        if not should_delete:
            old_comments = [
                "спина кава", "найвищому рівні", "супер", "чудова кава", "🎁 акції"
            ]
            comment_lower = comment.lower()
            for old_comment in old_comments:
                if old_comment in comment_lower:
                    should_delete = True
                    break

        # Видаляємо відгуки які складаються тільки з рейтингу (⭐ 5/5, ⭐ 4/5 тощо)
        if not should_delete and comment:
            comment_clean = comment.strip()
            # Перевіряємо чи це тільки рейтинг
            if len(comment_clean) <= 10:
                if "⭐" in comment_clean and "/5" in comment_clean:
                    should_delete = True

        if not should_delete:
            filtered_reviews.append(r)

    user_reviews[:] = filtered_reviews
    deleted = original_count - len(user_reviews)
    save_data()

    await callback.message.edit_text(
        f"✅ Видалено старих відгуків: {deleted}\n"
        f"📖 Залишилось відгуків: {len(user_reviews)}"
    )
    await callback.answer("Готово")


@dp.callback_query(F.data == "rv_admin_view")
async def rv_admin_view_callback(callback: types.CallbackQuery):
    """Окремий callback для адміна щоб бачити всі відгуки з кнопками"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ заборонено")
        return
    await rv_view_admin(callback)


async def rv_view_admin(message_or_callback):
    """Показує всі відгуки з кнопками видалення для адміна"""
    if not user_reviews:
        text = "📖 Поки що немає відгуків."
        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(text, reply_markup=get_admin_menu())
        else:
            await message_or_callback.message.edit_text(text)
            await message_or_callback.answer()
        return

    # Формуємо список відгуків з кнопками видалення
    lines = []
    keyboard_rows = []

    # Фільтруємо валідні відгуки
    valid_reviews = [r for r in user_reviews if isinstance(r, dict) and r.get("id", 0) > 0]

    if not valid_reviews:
        text = "📖 Поки що немає валідних відгуків."
        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(text, reply_markup=get_admin_menu())
        else:
            await message_or_callback.message.edit_text(text)
            await message_or_callback.answer()
        return

    # Показуємо всі відгуки
    for i, r in enumerate(valid_reviews, 1):
        rid = r.get("id", 0)
        uname = r.get("username", "user")
        comment = r.get("comment", "")
        rating = r.get("rating", 0)

        # Формуємо текст відгуку
        review_text = f"{i}. @{uname}: {comment}"
        if rating > 0:
            review_text += f" ⭐{rating}/5"
        lines.append(review_text)

        # Додаємо кнопку видалення для кожного відгуку
        short_comment = (comment[:30] + "…") if len(comment) > 30 else comment
        if not short_comment:
            short_comment = "(порожній)"
        keyboard_rows.append([
            InlineKeyboardButton(
                text=f"❌ Видалити #{i}: {short_comment}",
                callback_data=f"rv_del_{rid}"
            )
        ])

    # Додаємо кнопки управління
    keyboard_rows.append([
        InlineKeyboardButton(text="🗑 Видалити всі старі", callback_data="rv_delete_all_old"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="rv_back")
    ])

    text = "📖 <b>Всі відгуки (для адміна)</b>\n\n" + "\n\n".join(lines)

    if isinstance(message_or_callback, types.Message):
        await message_or_callback.answer(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
        )
    else:
        await message_or_callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
        )
        await message_or_callback.answer()


@dp.callback_query(F.data == "rv_view")
async def rv_view(callback: types.CallbackQuery):
    # Перевіряємо чи адмін
    user_id = callback.from_user.id
    if is_admin(user_id):
        # Адмін - показуємо всі відгуки з кнопками
        await rv_view_admin(callback)
        return

    # Для звичайних користувачів - просто перегляд останніх 10
    if not user_reviews:
        await callback.message.edit_text("📖 Поки що немає відгуків.")
        await callback.answer()
        return

    valid_reviews = [r for r in user_reviews if isinstance(r, dict)]
    lines = []
    for i, r in enumerate(valid_reviews[-10:], 1):
        comment = r.get("comment", "")
        rating = r.get("rating", 0)
        uname = r.get("username", "user")
        review_text = f"{i}. @{uname}: {comment}"
        if rating > 0:
            review_text += f" ⭐{rating}/5"
        lines.append(review_text)

    await callback.message.edit_text("📖 <b>Останні відгуки</b>\n\n" + "\n\n".join(lines))
    await callback.answer()


@dp.callback_query(F.data == "rv_back")
async def rv_back(callback: types.CallbackQuery):
    await callback.message.edit_text("💬 Виберіть дію:")
    kb_rows = [
        [InlineKeyboardButton(text="📝 Залишити відгук", callback_data="rv_leave")],
        [InlineKeyboardButton(text="📖 Переглянути відгуки", callback_data="rv_view")]
    ]
    if is_admin(callback.from_user.id):
        kb_rows.append([InlineKeyboardButton(text="🗑 Всі відгуки (адмін)", callback_data="rv_admin_view")])
    await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await callback.answer()


@dp.callback_query(F.data == "rv_leave")
async def rv_leave(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝 Напишіть ваш відгук одним повідомленням:")
    await state.set_state(ReviewStates.waiting_for_review)
    await callback.answer()


@dp.message(ReviewStates.waiting_for_review)
async def rv_save(message: types.Message, state: FSMContext):
    review = {
        "id": next_review_id(),
        "user_id": message.from_user.id,
        "username": message.from_user.username or "Користувач",
        "comment": message.text,
        "rating": 0,
        "date": datetime.now().isoformat()
    }
    user_reviews.append(review)
    save_data()
    await message.answer("✅ Дякуємо за відгук!")
    await state.clear()


@dp.callback_query(F.data == "rv_manage")
async def rv_manage(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌")
        return
    await rv_view_admin(callback)


@dp.callback_query(F.data.startswith("rv_del_"))
async def rv_delete(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ заборонено")
        return

    try:
        rid_str = callback.data.replace("rv_del_", "")
        rid = int(rid_str)
    except ValueError:
        await callback.answer("❌ Помилка")
        return

    # Знаходимо і видаляємо відгук
    found = False
    for i, r in enumerate(user_reviews):
        if isinstance(r, dict) and r.get("id") == rid:
            user_reviews.pop(i)
            found = True
            break

    if found:
        save_data()
        await callback.answer("✅ Відгук видалено")
        # Оновлюємо список відгуків
        await rv_view_admin(callback)
    else:
        await callback.answer("❌ Відгук не знайдено")


# --- Конкурс фото ---
@dp.message(F.text == "📸 Конкурс фото")
async def contest_start(message: types.Message, state: FSMContext):
    await message.answer("📸 Надішліть фото для участі у конкурсі:")
    await state.set_state(ContestStates.waiting_for_photo)


@dp.message(ContestStates.waiting_for_photo, F.photo)
async def contest_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo_id=message.photo[-1].file_id)
    await message.answer("📝 Додайте короткий опис (1 повідомлення):")
    await state.set_state(ContestStates.waiting_for_description)


@dp.message(ContestStates.waiting_for_description)
async def contest_descr(message: types.Message, state: FSMContext):
    data = await state.get_data()
    entry = {
        "user_id": message.from_user.id,
        "username": message.from_user.username or "Користувач",
        "photo_id": data.get("photo_id"),
        "description": message.text,
        "date": datetime.now().isoformat()
    }
    contest_participants.append(entry)
    known_users.add(message.from_user.id)
    save_data()
    await message.answer("✅ Заявку прийнято! Результати в кінці місяця.")
    await state.clear()


@dp.message(F.text == "🏆 Переможці")
async def winners_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        if contest_winner:
            winner_name = get_user_display_name(contest_winner)
            await message.answer(
                f"🏆 <b>Переможці конкурсу</b>\n\nОстанній переможець: {winner_name}\n🎁 20% знижка на місяць")
        else:
            await message.answer("🏆 Поки що немає переможців. Беріть участь!")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Учасники", callback_data="ct_participants")],
        [InlineKeyboardButton(text="🎉 Обрати переможця (випадково)", callback_data="ct_pick_random")]
    ])
    await message.answer("🏆 Переможці — панель адміністратора", reply_markup=kb)


@dp.callback_query(F.data == "ct_participants")
async def ct_participants_view(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌")
        return
    if not contest_participants:
        # Перевіряємо тип повідомлення
        try:
            if callback.message.photo:
                await callback.message.edit_caption("👥 Учасників поки немає.")
            else:
                await callback.message.edit_text("👥 Учасників поки немає.")
        except:
            await callback.message.answer("👥 Учасників поки немає.")
        await callback.answer()
        return

    rows = []
    for p in contest_participants[-10:]:
        u = p.get("username", "user")
        uid = p["user_id"]
        p_name = get_user_display_name(uid)
        rows.append([InlineKeyboardButton(text=f"👤 {p_name} — Переглянути", callback_data=f"ct_view_{uid}")])

    kb = InlineKeyboardMarkup(inline_keyboard=rows + [[InlineKeyboardButton(text="🔙 Назад", callback_data="ct_back")]])

    # Перевіряємо тип повідомлення перед редагуванням
    try:
        if callback.message.photo:
            # Якщо це фото - видаляємо і відправляємо нове текстове повідомлення
            await callback.message.delete()
            await bot.send_message(
                callback.from_user.id,
                "👥 Останні учасники:",
                reply_markup=kb
            )
        else:
            # Якщо це текст - редагуємо
            await callback.message.edit_text("👥 Останні учасники:", reply_markup=kb)
    except Exception as e:
        logging.error(f"Error in ct_participants_view: {e}")
        # У разі помилки відправляємо нове повідомлення
        try:
            if callback.message.photo:
                await callback.message.delete()
        except:
            pass
        await bot.send_message(
            callback.from_user.id,
            "👥 Останні учасники:",
            reply_markup=kb
        )

    await callback.answer()


@dp.callback_query(F.data.startswith("ct_view_"))
async def ct_view_photo(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌")
        return
    try:
        uid = int(callback.data.replace("ct_view_", ""))
    except:
        await callback.answer("Помилка")
        return

    # Знаходимо учасника
    participant = None
    for p in contest_participants:
        if p.get("user_id") == uid:
            participant = p
            break

    if not participant:
        await callback.answer("Учасника не знайдено")
        return

    photo_id = participant.get("photo_id")
    description = participant.get("description", "Без опису")
    p_name = get_user_display_name(uid)
    username = participant.get("username", "user")

    if photo_id:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎉 Обрати переможцем", callback_data=f"ct_choose_{uid}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="ct_participants")]
        ])
        await callback.message.delete()
        await bot.send_photo(
            callback.from_user.id,
            photo_id,
            caption=f"👤 <b>Учасник:</b> {p_name} (@{username})\n\n📝 <b>Опис:</b> {description}",
            reply_markup=kb
        )
    else:
        await callback.message.edit_text(f"❌ Фото не знайдено для учасника {p_name}")
        await callback.answer("Фото не знайдено")

    await callback.answer()


@dp.callback_query(F.data == "ct_back")
async def ct_back(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Учасники", callback_data="ct_participants")],
        [InlineKeyboardButton(text="🎉 Обрати переможця (випадково)", callback_data="ct_pick_random")]
    ])
    # Перевіряємо тип повідомлення
    try:
        # Якщо це фото - видаляємо і відправляємо нове текстове
        if callback.message.photo:
            await callback.message.delete()
            await bot.send_message(
                callback.from_user.id,
                "🏆 Переможці — панель адміністратора",
                reply_markup=kb
            )
        else:
            # Якщо це текст - редагуємо
            await callback.message.edit_text(
                "🏆 Переможці — панель адміністратора",
                reply_markup=kb
            )
    except Exception as e:
        logging.error(f"Error in ct_back: {e}")
        # Якщо помилка - просто відправляємо нове повідомлення
        try:
            if callback.message.photo:
                await callback.message.delete()
        except:
            pass
        await bot.send_message(
            callback.from_user.id,
            "🏆 Переможці — панель адміністратора",
            reply_markup=kb
        )
    await callback.answer()


@dp.callback_query(F.data.startswith("ct_choose_"))
async def ct_choose(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌")
        return
    uid = int(callback.data.replace("ct_choose_", ""))
    global contest_winner
    contest_winner = uid
    save_data()
    winner_name = get_user_display_name(uid)
    try:
        await bot.send_message(uid, "🎉 Вітаємо! Ви — переможець конкурсу! 🎁 Знижка 20% на місяць.")
    except Exception as e:
        logging.error(e)
    try:
        await callback.message.edit_caption(f"✅ Переможця встановлено: {winner_name}")
    except:
        await callback.message.edit_text(f"✅ Переможця встановлено: {winner_name}")
    await callback.answer("Готово")


@dp.callback_query(F.data == "ct_pick_random")
async def ct_pick_random(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌")
        return
    if not contest_participants:
        await callback.answer("Немає учасників")
        return
    winner = random.choice(contest_participants)
    uid = winner["user_id"]
    global contest_winner
    contest_winner = uid
    save_data()
    winner_name = get_user_display_name(uid)
    try:
        await bot.send_message(uid, "🎉 Вітаємо! Ви — переможець конкурсу! 🎁 Знижка 20% на місяць.")
    except Exception as e:
        logging.error(e)
    await callback.message.edit_text(f"✅ Випадковий переможець: {winner_name} (@{winner.get('username', 'user')})")
    await callback.answer()


# --- Розсилка ---
@dp.message(F.text == "📢 Розсилка")
async def newsletter_start(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ заборонено")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Текст", callback_data="nl_type_text")],
        [InlineKeyboardButton(text="📸 Фото + текст", callback_data="nl_type_photo")],
        [InlineKeyboardButton(text="🎥 Відео + текст", callback_data="nl_type_video")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="nl_cancel")],
    ])
    await message.answer("📢 <b>Розсилка</b>\nОберіть тип:", reply_markup=kb)
    await state.set_state(NewsletterStates.waiting_for_type)


@dp.callback_query(NewsletterStates.waiting_for_type, F.data.startswith("nl_type_"))
async def nl_pick_type(callback: types.CallbackQuery, state: FSMContext):
    nl_type = callback.data.replace("nl_type_", "")
    await state.update_data(nl_type=nl_type)
    if nl_type == "text":
        await callback.message.edit_text("📝 Надішліть текст розсилки одним повідомленням.")
    elif nl_type == "photo":
        await callback.message.edit_text("📸 Надішліть фото з підписом (caption).")
    else:
        await callback.message.edit_text("🎥 Надішліть відео з підписом (caption).")
    await state.set_state(NewsletterStates.waiting_for_content)
    await callback.answer()


@dp.message(NewsletterStates.waiting_for_content)
async def nl_receive(message: types.Message, state: FSMContext):
    data = await state.get_data()
    nl_type = data.get("nl_type")
    payload = {}
    if nl_type == "text":
        if not message.text:
            await message.answer("❌ Надішліть текст.")
            return
        payload = {"type": "text", "text": message.text}
        preview = f"📝 <b>Попередній перегляд</b>\n\n{message.text}"
    elif nl_type == "photo":
        if not message.photo:
            await message.answer("❌ Надішліть фото з підписом.")
            return
        payload = {"type": "photo", "file_id": message.photo[-1].file_id, "caption": message.caption or ""}
        preview = "📸 <b>Попередній перегляд</b> (фото + текст)"
    else:
        if not message.video:
            await message.answer("❌ Надішліть відео з підписом.")
            return
        payload = {"type": "video", "file_id": message.video.file_id, "caption": message.caption or ""}
        preview = "🎥 <b>Попередній перегляд</b> (відео + текст)"
    await state.update_data(payload=payload)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Відправити", callback_data="nl_send")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="nl_cancel")],
    ])
    await message.answer(preview, reply_markup=kb)
    await state.set_state(NewsletterStates.waiting_for_confirmation)


@dp.callback_query(NewsletterStates.waiting_for_confirmation, F.data == "nl_send")
async def nl_send(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌")
        return
    data = await state.get_data()
    payload = data.get("payload", {})
    users = newsletter_targets()
    sent = 0
    for uid in users:
        try:
            if payload["type"] == "text":
                await bot.send_message(uid, payload["text"])
            elif payload["type"] == "photo":
                await bot.send_photo(uid, payload["file_id"], caption=payload["caption"])
            else:
                await bot.send_video(uid, payload["file_id"], caption=payload["caption"])
            sent += 1
        except Exception as e:
            logging.error(f"Newsletter to {uid}: {e}")
    await callback.message.edit_text(f"✅ Розсилка відправлена {sent}/{len(users)}")
    await state.clear()
    await callback.answer("Готово")


@dp.callback_query(F.data == "nl_cancel")
async def nl_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Розсилку скасовано")
    await callback.answer()


# --- День народження ---
async def check_birthdays():
    today = date.today()
    for uid, birthday_str in user_birthdays.items():
        try:
            birthday = datetime.fromisoformat(birthday_str).date()
            if birthday.month == today.month and birthday.day == today.day:
                try:
                    user_name = get_user_display_name(uid)
                    await bot.send_message(uid,
                                           f"🎂 <b>З Днем народження, {user_name}!</b>\nСьогодні для вас безкоштовний напій ☕")
                except Exception as e:
                    logging.error(f"Birthday message error {uid}: {e}")
        except Exception as e:
            logging.error(f"Birthday parse error {uid}: {e}")


async def birthday_checker():
    while True:
        await check_birthdays()
        await asyncio.sleep(3600)


# --- Запуск ---
async def main():
    try:
        asyncio.create_task(birthday_checker())
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())