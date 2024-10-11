import psutil
import yaml
from telegram import Bot
import time
import asyncio
import emoji

# Definizione degli emoji
SIREN_EMOJI = emoji.emojize(':rotating_light:')  # Emoji per allerta generale
FIRE_EMOJI = emoji.emojize(':fire:')  # Emoji per allerta alta CPU
WARNING_EMOJI = emoji.emojize(':warning:')  # Emoji per alta RAM
DISK_EMOJI = emoji.emojize(':floppy_disk:')  # Emoji per uso disco
ANGER_EMOJI = emoji.emojize(':face_with_symbols_over_mouth:')  # Emoji per messaggio speciale 🤬

# Funzione per caricare il file YAML
def load_config(file_path="config.yaml"):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Decoratore per aggiungere emoji all'inizio e alla fine del messaggio
def add_emoji(emj):
    def decorator(func):
        async def wrapper(bot, chat_id, message, *args, **kwargs):
            decorated_message = f"{emj}{emj} {message} {emj}{emj}"
            return await func(bot, chat_id, decorated_message, *args, **kwargs)
        return wrapper
    return decorator

# Funzione per inviare una notifica su Telegram con decoratore parametrizzato
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

# Messaggio speciale per 5 messaggi consecutivi
SPECIAL_MESSAGE = f"{ANGER_EMOJI}{ANGER_EMOJI} Il responsabile agisca, prima che gli tagli le mani {ANGER_EMOJI}{ANGER_EMOJI}"

# Funzione per monitorare le risorse
async def monitor_system(config, bot, message_counts, last_message_times):
    thresholds = config['thresholds']
    chat_id = config['telegram']['chat_id']
    repeat_threshold = config.get('repeat_threshold', 5)  # Soglia di messaggi consecutivi
    time_threshold = config.get('time_threshold', 600)  # Soglia di tempo per il reset dei contatori

    current_time = time.time()  # Otteniamo il tempo corrente

    # Reset dei contatori se sono passati più di time_threshold secondi dall'ultimo messaggio
    for key in message_counts.keys():
        if current_time - last_message_times[key] > time_threshold:
            message_counts[key] = 0

    # Uso CPU
    cpu_usage = psutil.cpu_percent(interval=0.5)  # Aumentato il numero di campioni
    if cpu_usage > thresholds['cpu']:
        message_counts['cpu'] += 1
        if message_counts['cpu'] > repeat_threshold:
            await send_cpu_notification(bot, chat_id, SPECIAL_MESSAGE)
            message_counts['cpu'] = 0  # Reset contatore
            last_message_times['cpu'] = current_time  # Aggiorna l'ora dell'ultimo messaggio
        else:
            await send_cpu_notification(bot, chat_id, f"Attenzione! Uso CPU: {cpu_usage}%")
            last_message_times['cpu'] = current_time

    # Uso RAM
    ram_usage = psutil.virtual_memory().percent
    if ram_usage > thresholds['ram']:
        message_counts['ram'] += 1
        if message_counts['ram'] > repeat_threshold:
            await send_ram_notification(bot, chat_id, SPECIAL_MESSAGE)
            message_counts['ram'] = 0  # Reset contatore
            last_message_times['ram'] = current_time
        else:
            await send_ram_notification(bot, chat_id, f"Attenzione! Uso RAM: {ram_usage}%")
            last_message_times['ram'] = current_time

    # Uso disco principale
    disk_usage = psutil.disk_usage('/home').percent
    if disk_usage > thresholds['disk']:
        message_counts['disk'] += 1
        if message_counts['disk'] > repeat_threshold:
            await send_disk_notification(bot, chat_id, SPECIAL_MESSAGE)
            message_counts['disk'] = 0  # Reset contatore
            last_message_times['disk'] = current_time
        else:
            await send_disk_notification(bot, chat_id, f"Attenzione! Uso Disco /home: {disk_usage}%")
            last_message_times['disk'] = current_time

    # Uso secondo disco
    second_disk_usage = psutil.disk_usage('/data').percent
    if second_disk_usage > thresholds['disk_2']:
        message_counts['disk_2'] += 1
        if message_counts['disk_2'] > repeat_threshold:
            await send_disk_2_notification(bot, chat_id, SPECIAL_MESSAGE)
            message_counts['disk_2'] = 0  # Reset contatore
            last_message_times['disk_2'] = current_time
        else:
            await send_disk_2_notification(bot, chat_id, f"Attenzione! Uso Disco /data: {second_disk_usage}%")
            last_message_times['disk_2'] = current_time

# Funzione principale
async def main():
    config = load_config('config.yaml')
    bot = Bot(token=config['telegram']['token'])

    message_counts = {'cpu': 0, 'ram': 0, 'disk': 0, 'disk_2': 0}  # Contatori per CPU, RAM, disco principale e secondo disco
    last_message_times = {'cpu': -1, 'ram': -1, 'disk': -1, 'disk_2': -1}  # Inizializzato a -1 per evitare il reset immediato

    # Monitoraggio continuo
    interval = config.get('interval', 60)  # Tempo di sleep (default: 60 secondi)
    while True:
        await monitor_system(config, bot, message_counts, last_message_times)
        await asyncio.sleep(interval)

if __name__ == "__main__":
    asyncio.run(main())
