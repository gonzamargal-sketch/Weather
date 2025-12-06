import os
from dotenv import load_dotenv
import requests
import streamlit as st
from datetime import datetime
from babel import Locale

load_dotenv()
API_KEY = os.getenv("API_KEY")

_locale_es = Locale.parse('es')

def get_country_name(code: str) -> str:
    if not code:
        return '—'
    try:
        return _locale_es.territories.get(code.upper(), code)
    except Exception:
        return code

def obtener_coordenadas(nombre):
    url = f'http://api.openweathermap.org/geo/1.0/direct'
    params = {
        'q': nombre,
        'limit': 1,
        'appid': API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    if not data:
        raise ValueError("Ciudad no encontrada")
    
    else:
        lat = data[0]['lat']
        lon = data[0]['lon']
        return lat, lon


def obtener_nombre_localizada(nombre, lang='es'):
    """Devuelve el nombre localizado en `lang` si está disponible en la respuesta de geocoding."""
    try:
        url = 'http://api.openweathermap.org/geo/1.0/direct'
        params = {'q': nombre, 'limit': 1, 'appid': API_KEY}
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        items = resp.json()
        if not items:
            return nombre
        item = items[0]
        local_names = item.get('local_names', {}) or {}
        # intentar clave 'es' y fallback al nombre provisto por la API
        return local_names.get(lang) or item.get('name') or nombre
    except Exception:
        return nombre

def obtener_clima_hoy(lat:float, lon:float):
    url = f'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'es'
    }
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:    
        return response.json()
    else:
        try:
            error_message = response.json()
        except ValueError:
            error_message = {'mensaje':response.text}
        return {'error': True, 'mensaje': error_message}


def obtener_prevision_7dias(lat: float, lon: float):
    """Devuelve la respuesta JSON de la API One Call (previsión diaria).
    Usa 'exclude' para omitir datos innecesarios y 'lang=es' para descripciones en español.
    """
    url = 'https://api.openweathermap.org/data/2.5/onecall'
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'es',
        'exclude': 'minutely,hourly,alerts'
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
    except Exception as e:
        return {'error': True, 'mensaje': str(e)}

    if resp.status_code == 200:
        return resp.json()
    else:
        try:
            return {'error': True, 'mensaje': resp.json()}
        except Exception:
            return {'error': True, 'mensaje': resp.text}


def _format_basic(data):
    """Return a small dict with the most useful fields for display."""
    try:
        return {
            'ciudad': data.get('name'),
            'temperatura_C': data['main']['temp'],
            'temp_sentida_C': data['main']['feels_like'],
            'descripcion': data['weather'][0]['description'],
            'humedad_%': data['main']['humidity'],
            'viento_m_s': data['wind']['speed']
        }
    except Exception:
        return {'error': 'Formato inesperado de respuesta'}


def main():
    st.set_page_config(page_title='Dashboard Clima', layout='centered')
    st.title('Dashboard Clima')
    st.write('Busca el clima por ciudad usando OpenWeatherMap')

    # Input + submit dentro de un formulario: Enter actúa como enviar
    with st.form(key='search_form'):
        ciudad = st.text_input('Ciudad', value='Madrid', key='ciudad')
        buscar = st.form_submit_button('Buscar')

    if buscar:
        if not API_KEY:
            st.error('No se encontró `API_KEY`. Coloca `API_KEY=tu_api_key` en un archivo `.env` en la raíz.')
            st.info('Mostrando ejemplo estático para que veas la UI')
            ejemplo = {
                'name': 'Ejemplo City',
                'main': {'temp': 21.3, 'feels_like': 20.0, 'humidity': 60},
                'weather': [{'description': 'cielo claro', 'icon': '01d'}],
                'wind': {'speed': 3.4}
            }
            mostrar_clima(ejemplo, ejemplo_mode=True)
        else:
            try:
                lat, lon = obtener_coordenadas(ciudad)
                # obtener nombre localizado en español (si disponible)
                ciudad_local = obtener_nombre_localizada(ciudad, lang='es')
                clima = obtener_clima_hoy(lat, lon)
                if isinstance(clima, dict) and clima.get('error'):
                    st.error(f"Error: {clima.get('mensaje')}")
                else:
                    mostrar_clima(clima, ciudad_display=ciudad_local)
            except Exception as e:
                st.error(str(e))

    st.markdown('---')

def mostrar_clima(data: dict, ejemplo_mode: bool = False, ciudad_display: str = None):
    basic = _format_basic(data)
    lat, lon = obtener_coordenadas(ciudad_display or basic.get('ciudad') or data.get('name'))
    ciudad_nombre = ciudad_display or basic.get('ciudad') or data.get('name') or '—'
    descripcion = basic.get('descripcion', '—')
    # Emoji selection inlined to keep helpers together and minimal edits
    d = (descripcion or '').lower()
    mapping = [
        ('clear', '☀️'),
        ('cloud', '☁️'),
        ('rain', '🌧️'),
        ('moderate rain', '🌧️'),
        ('drizzle', '🌦️'),
        ('thunder', '⛈️'),
        ('snow', '❄️'),
        ('mist', '🌫️'),
    ]
    emoji = '📌'  # default
    for key, em in mapping:
        if key in d:
            emoji = em
            break

    # Top row: title + icon
    col1, col2 = st.columns([3,1])
    with col1:
        st.subheader(f" {emoji} Clima en {ciudad_nombre}")
        st.write(f'Coordenadas: {lat:.4f}, {lon:.4f}')
        st.markdown(f"**{descripcion.capitalize()}** — actualizado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    with col2:
        icon_code = None
        try:
            icon_code = data['weather'][0].get('icon')
        except Exception:
            icon_code = None
        if icon_code:
            icon_url = f'http://openweathermap.org/img/wn/{icon_code}@2x.png'
            st.image(icon_url, width=96)

    # Metrics row
    t = basic.get('temperatura_C', '—')
    feels = basic.get('temp_sentida_C', '—')
    hum = basic.get('humedad_%', '—')
    wind = basic.get('viento_m_s', '—')


    m1, m2, m3 = st.columns(3)
    m1.metric(label='Temperatura (°C)', value=f"{t} °C", delta=f"Sensación térmica de {feels}°C", delta_color='off', delta_arrow='off')
    m2.metric(label='Humedad (%)', value=f"{hum}")
    m3.metric(label='Viento (m/s)', value=f"{wind}")

    # Info completa en formato legible (3 columnas)
    with st.expander('ℹ️ Info completa'):
        col1, col2, col3 = st.columns(3)
        
        # Columna 1: Datos del país
        with col1:
            st.subheader('🌍 País & Ubicación')
            st.write(f"**Ciudad:** {data.get('name', '—')}")
            country_code = data.get('sys', {}).get('country')
            st.write(f"**País:** {get_country_name(country_code)}")
            st.write(f"**Latitud:** {data.get('coord', {}).get('lat', '—')}°")
            st.write(f"**Longitud:** {data.get('coord', {}).get('lon', '—')}°")
            tz_offset = data.get('timezone', 0) / 3600  #Te devuelve en segundos
            tz_sign = '+' if tz_offset >= 0 else ''
            st.write(f"**Zona horaria:** UTC {tz_sign}{tz_offset:.0f}h")
        
        # Columna 2: Temperaturas y datos 'main'
        with col2:
            st.subheader('🌡️ Temperaturas')
            main_data = data.get('main', {})
            st.write(f"**Temperatura:** {main_data.get('temp', '—')}°C")
            st.write(f"**Sensación térmica:** {main_data.get('feels_like', '—')}°C")
            st.write(f"**Temp. mínima:** {main_data.get('temp_min', '—')}°C")
            st.write(f"**Temp. máxima:** {main_data.get('temp_max', '—')}°C")
            st.write(f"**Humedad:** {main_data.get('humidity', '—')}%")
            st.write(f"**Presión:** {main_data.get('pressure', '—')} hPa")
        
        # Columna 3: Resto de datos
        with col3:
            st.subheader('📊 Otros datos')
            st.write(f"**Visibilidad:** {data.get('visibility', '—')} m")
            st.write(f"**Nubosidad:** {data.get('clouds', {}).get('all', '—')}%")
            st.write(f"**Velocidad viento:** {data.get('wind', {}).get('speed', '—')} m/s")
            st.write(f"**Dirección viento:** {data.get('wind', {}).get('deg', '—')}°")
            if data.get('rain'):
                st.write(f"**Lluvia (1h):** {data.get('rain', {}).get('1h', '—')} mm")
            if data.get('snow'):
                st.write(f"**Nieve (1h):** {data.get('snow', {}).get('1h', '—')} mm")
            # Mostrar la descripción localizada (campo 'description') solicitada con 'lang=es'
            desc_loc = data.get('weather', [{}])[0].get('description', '—')
            st.write(f"**Descripción:** {desc_loc.capitalize()}")
'''
    # Previsión 7 días (extra)
    with st.expander('📅 Previsión 7 días'):
        coord = data.get('coord') or {}
        lat = coord.get('lat')
        lon = coord.get('lon')
        if not (lat and lon):
            st.info('No hay coordenadas disponibles para esta ciudad.')
        else:
            prevision = obtener_prevision_7dias(lat, lon)
            if isinstance(prevision, dict) and prevision.get('error'):
                st.error(f"No se pudo obtener la previsión: {prevision.get('mensaje')}")
            else:
                daily = prevision.get('daily', [])[:7]
                tz_offset = prevision.get('timezone_offset', 0)
                if not daily:
                    st.info('No hay datos de previsión disponibles.')
                else:
                    cols = st.columns(len(daily))
                    for i, day in enumerate(daily):
                        with cols[i]:
                            dt = datetime.utcfromtimestamp(day.get('dt', 0) + tz_offset)
                            fecha = dt.strftime('%a %d %b')
                            w = day.get('weather', [{}])[0]
                            icon = w.get('icon')
                            desc = w.get('description', '—').capitalize()
                            temp = day.get('temp', {})
                            t_day = temp.get('day', '—')
                            t_min = temp.get('min', '—')
                            t_max = temp.get('max', '—')
                            pop = int(day.get('pop', 0) * 100)
                            st.markdown(f"**{fecha}**")
                            if icon:
                                icon_url = f'http://openweathermap.org/img/wn/{icon}@2x.png'
                                st.image(icon_url, width=72)
                            st.write(f"{desc}")
                            st.write(f"{t_day}°C (min {t_min} / max {t_max})")
                            st.write(f"Prob. precipitación: {pop}%")
'''
if __name__ == '__main__':
    main()
