import psutil
import yaml
from telegram import Bot
import time
import asyncio

# Definizione degli emoji con Unicode
SIREN_EMOJI = "\U0001F6A8"  # Emoji for general alert 🚨
FIRE_EMOJI = "\U0001F525"  # Emoji for high CPU fire 🔥
WARNING_EMOJI = "\U000026A0"  # Emoji for high RAM warning ⚠️
DISK_EMOJI = "\U0001F4BE"  # Emoji for disk usage floppy disk 💾
ANGER_EMOJI = "\U0001F92C"  # Unicode for face with symbols over mouth 🤬


# Funzione per caricare il file YAML
def load_config(file_path="config.yaml"):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


# Decoratore per aggiungere emoji all'inizio e alla fine del messaggio
def add_emoji(emj):
    def decorator(func):
        async def wrapper(bot, chat_id, message, *args, **kwargs):
            decorated_message = f"{emj}{emj} {message} {emj}{emj}"
            return await func(bot, chat_id, decorated_message, *args, **kwargs)

        return wrapper

    return decorator


# Funzione per inviare notifiche su Telegram con decoratore parametrizzato
@add_emoji(FIRE_EMOJI)
async def send_cpu_notification(bot, chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)


@add_emoji(WARNING_EMOJI)
async def send_ram_notification(bot, chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)


@add_emoji(DISK_EMOJI)
async def send_disk_notification(bot, chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)


@add_emoji(DISK_EMOJI)
async def send_disk_2_notification(bot, chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)


# Funzione per inviare il messaggio speciale
async def send_special_message(bot, chat_id):
    special_message = f"{ANGER_EMOJI}{ANGER_EMOJI} Il responsabile agisca, prima che gli tagli le mani {ANGER_EMOJI}{ANGER_EMOJI}"
    await bot.send_message(chat_id=chat_id, text=special_message)


# Funzione per monitorare le risorse
async def monitor_system(config, bot, message_counts):
    thresholds = config["thresholds"]
    chat_id = config["telegram"]["chat_id"]
    repeat_threshold = config.get(
        "repeat_threshold", 5
    )  # Soglia di messaggi consecutivi

    # Uso CPU
    cpu_usage = psutil.cpu_percent(interval=0.5)
    if cpu_usage > thresholds["cpu"]:
        message_counts["cpu"] += 1
        if message_counts["cpu"] > repeat_threshold:
            await send_special_message(bot, chat_id)
            message_counts["cpu"] = 0  # Reset contatore
        else:
            await send_cpu_notification(
                bot, chat_id, f"Attenzione! Uso CPU: {cpu_usage}%"
            )

    # Uso RAM
    ram_usage = psutil.virtual_memory().percent
    if ram_usage > thresholds["ram"]:
        message_counts["ram"] += 1
        if message_counts["ram"] > repeat_threshold:
            await send_special_message(bot, chat_id)
            message_counts["ram"] = 0  # Reset contatore
        else:
            await send_ram_notification(
                bot, chat_id, f"Attenzione! Uso RAM: {ram_usage}%"
            )

    # Uso disco principale
    disk_usage = psutil.disk_usage("/home").percent
    if disk_usage > thresholds["disk"]:
        message_counts["disk"] += 1
        if message_counts["disk"] > repeat_threshold:
            await send_special_message(bot, chat_id)
            message_counts["disk"] = 0  # Reset contatore
        else:
            await send_disk_notification(
                bot, chat_id, f"Attenzione! Uso Disco /home: {disk_usage}%"
            )

    # Uso secondo disco
    second_disk_usage = psutil.disk_usage("/data").percent
    if second_disk_usage > thresholds["disk_2"]:
        message_counts["disk_2"] += 1
        if message_counts["disk_2"] > repeat_threshold:
            await send_special_message(bot, chat_id)
            message_counts["disk_2"] = 0  # Reset contatore
        else:
            await send_disk_2_notification(
                bot, chat_id, f"Attenzione! Uso Disco /data: {second_disk_usage}%"
            )


# Funzione principale
async def main():
    config = load_config("config.yaml")
    bot = Bot(token=config["telegram"]["token"])

    message_counts = {
        "cpu": 0,
        "ram": 0,
        "disk": 0,
        "disk_2": 0,
    }  # Contatori per CPU, RAM, dischi

    # Monitoraggio continuo
    interval = config.get("interval", 60)  # Tempo di sleep (default: 60 secondi)
    while True:
        await monitor_system(config, bot, message_counts)
        await asyncio.sleep(interval)


if __name__ == "__main__":
    asyncio.run(main())
