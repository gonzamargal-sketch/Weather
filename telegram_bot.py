import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')


def obtener_coordenadas_simple(nombre):
    url = 'http://api.openweathermap.org/geo/1.0/direct'
    params = {'q': nombre, 'limit': 1, 'appid': API_KEY}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        return None
    items = r.json()
    if not items:
        return None
    return items[0]['lat'], items[0]['lon']


def obtener_clima_hoy_simple(lat, lon):
    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {'lat': lat, 'lon': lon, 'appid': API_KEY, 'units': 'metric', 'lang': 'es'}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        return None
    return r.json()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hola! Mándame el nombre de una ciudad y te digo el clima actual. Ej: "Madrid" o "clima Barcelona"')


def deg_to_arrow(deg):
    """Convierte grados en una flecha y etiqueta cardinal breve (8 puntos).
    Retorna (arrow, label, deg_value) — deg_value es '—' si no disponible.
    """
    try:
        if deg is None:
            return ('', '—', '—')
        d = float(deg) % 360
    except Exception:
        return ('', '—', '—')

    arrows = ['⬆️', '↗️', '➡️', '↘️', '⬇️', '↙️', '⬅️', '↖️']
    labels = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']
    idx = int(((d + 22.5) % 360) // 45)
    return (arrows[idx], labels[idx], round(d, 0))


def parse_ciudad(text: str) -> str:
    """Extrae nombre de ciudad del texto del usuario de forma simple."""
    if not text:
        return ''
    t = text.lower().strip()
    for prefix in ('clima en ', 'clima ', 'tiempo en ', 'tiempo ', 'weather in ', 'weather '):
        if t.startswith(prefix):
            return text[len(prefix):].strip()
    return text.strip()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text if update.message and update.message.text else None
    if not text:
        await update.message.reply_text('Sólo puedo procesar texto con el nombre de la ciudad.')
        return

    ciudad = parse_ciudad(text)
    if not ciudad:
        await update.message.reply_text('Dime la ciudad, por ejemplo: Madrid')
        return

    await update.message.reply_text(f'Buscando clima para "{ciudad}"...')

    coords = obtener_coordenadas_simple(ciudad)
    if not coords:
        await update.message.reply_text('No encontré la ciudad. Prueba con otra o escribe más específica, p.ej. "Madrid, ES"')
        return

    lat, lon = coords
    clima = obtener_clima_hoy_simple(lat, lon)
    if not clima:
        await update.message.reply_text('Error al obtener datos del clima.')
        return

    desc = clima.get('weather', [{}])[0].get('description', '—').capitalize()
    temp = clima.get('main', {}).get('temp', '—')
    feels = clima.get('main', {}).get('feels_like', '—')
    hum = clima.get('main', {}).get('humidity', '—')
    wind = clima.get('wind', {})
    wind_s = wind.get('speed', '—')
    wind_deg = wind.get('deg', '—')

    # Formatear viento con flecha/etiqueta si hay grado disponible
    arrow, label, deg_val = deg_to_arrow(wind_deg)
    if deg_val == '—':
        viento_text = f"{wind_s} m/s"
    else:
        viento_text = f"{wind_s} m/s {arrow} {int(deg_val)}° ({label})"

    resp = (
        f'Clima en {ciudad}: {desc}\n'
        f'Temperatura: {temp}°C (sensación térmica {feels}°C)\n'
        f'Humedad: {hum}%\n'
        f'Vento: {viento_text}'
    )

    await update.message.reply_text(resp)


def main():
    if not BOT_TOKEN:
        print('Pone `BOT_TOKEN` en el archivo .env antes de ejecutar este script.')
        return
    if not API_KEY:
        print('Pone `API_KEY` (OpenWeatherMap) en el archivo .env antes de ejecutar este script.')
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print('Bot arrancando (polling). Ctrl-C para parar.')
    app.run_polling()


if __name__ == '__main__':
    main()
