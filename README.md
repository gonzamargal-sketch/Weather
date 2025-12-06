# Dashboard Clima ☀️

Dashboard interactivo en tiempo real para consultar el clima actual y previsión de varios días utilizando la API de OpenWeatherMap. Construido con **Streamlit** y **Python**.

## 🎯 Características

- **Clima actual**: Temperatura, sensación térmica, humedad, velocidad del viento, presión y más.
- **Información localizada**: Nombres de países en español, descripciones en español.
- **Previsión de 5+ días**: Resumen diario con temperaturas mín/máx, descripción y probabilidad de precipitación.
- **Interfaz visual**: Iconos del clima, columnas de métricas, expanders organizados.
- **Búsqueda flexible**: Soporta enter para enviar búsquedas y geocodificación automática.
- **Optimización de API**: Caché local, fallback automático si la clave no soporta ciertos endpoints, debounce de envíos.
- **Nombres de países en español**: Usando la librería Babel para mapeos localizados.

## 📋 Requisitos

- Python 3.8+
- pip
- Clave API de [OpenWeatherMap](https://openweathermap.org/api) (gratuita disponible)

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/gonzamargal-sketch/dashboard_clima.git
cd dashboard_clima
```

### 2. Crear un entorno virtual (recomendado)
```bash
# Windows (PowerShell)
python -m venv clima
.\clima\Scripts\Activate.ps1

# Linux / macOS
python -m venv clima
source clima/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto:
```bash
API_KEY=tu_api_key_de_openweathermap
```

Reemplaza `tu_api_key_de_openweathermap` con tu clave API de OpenWeatherMap (puedes obtenerla gratis en https://openweathermap.org/api).

## 📖 Uso

### Ejecutar la aplicación
```bash
# Con el venv activado:
streamlit run app.py
```

Streamlit abrirá automáticamente el navegador en `http://localhost:8501`.

### Funcionalidad
1. **Buscar ciudad**: Escribe el nombre de una ciudad en el campo de entrada (ej: "Madrid", "London", "Barcelona").
2. **Ver clima actual**: Después de buscar, verás:
   - Cabecera con icono y descripción
   - 3 métricas principales: temperatura, humedad, viento
   - Panel expandible "Info completa" con datos detallados (país, coordenadas, presión, etc.)
3. **Previsión**: Abre el expander "Previsión 7 días" para ver pronósticos diarios (si tu clave API lo permite).

## 🔧 Estructura del proyecto

```
dashboard_clima/
├── README.md              # Este archivo
├── app.py                 # Código principal de la app Streamlit
├── requirements.txt       # Dependencias Python
├── .env                   # Variables de entorno (NO subir a GitHub)
├── .gitignore             # Archivos a ignorar en Git
└── clima/                 # Entorno virtual (NO subir a GitHub)
```

## 📚 Dependencias principales

- **streamlit**: Framework para crear dashboards web interactivos
- **requests**: Cliente HTTP para llamadas a la API
- **babel**: Localización de nombres de países
- **python-dotenv**: Gestión de variables de entorno

Consulta `requirements.txt` para la lista completa con versiones.

## 🌐 API de OpenWeatherMap

### Endpoints utilizados
- **Geocoding**: `/geo/1.0/direct` — Convierte nombre de ciudad a coordenadas
- **Weather actual**: `/data/2.5/weather` — Clima actual en coordenadas
- **Forecast**: `/data/2.5/forecast` — Previsión 3-horaria por 5 días (fallback)
- **One Call** (opcional): `/data/2.5/onecall` — Previsión diaria por 7 días (requiere plan superior)

### Límites

- **Plan gratuito**: 60 llamadas/minuto, 1000 llamadas/día
- **Endpoints disponibles**: Weather, Forecast (3h), Geocoding
- **Endpoints limitados**: One Call, Forecast daily (requieren suscripción)

### Limitaciones conocidas

Si tu clave no soporta el endpoint One Call (`/data/2.5/onecall`):
- La app intenta automáticamente usar `/data/2.5/forecast` (3h)
- Genera un resumen diario agregado (hasta 5 días en lugar de 7)
- Muestra un aviso en la UI: *"Mostrando resumen diario generado desde /forecast"*

## ⚙️ Optimización

### Caché local
- **Geocoding** (coordenadas): 24 horas
- **Clima actual**: 10 minutos
- **Previsión**: 30 minutos

Esto evita llamadas repetidas por la misma ciudad en corto tiempo.

### Debounce
- Envíos de búsqueda más rápidos que 1.5 segundos se ignoran
- Previene accidentes al hacer clic múltiples veces

## 🐛 Solución de problemas

### "No se encontró API_KEY"
- Verifica que el archivo `.env` exista en la raíz del proyecto
- Comprueba que contiene la línea `API_KEY=tu_clave_aqui`
- Reinicia Streamlit después de cambiar `.env`

### "Ciudad no encontrada"
- Asegúrate de escribir el nombre correcto en inglés o con tilde si aplica
- Prueba agregando el código de país: "Madrid,ES", "Copenhagen,DK"
- Algunos nombres locales (p.ej. "Copenhague") pueden requerir la forma inglesa ("Copenhagen")

### "No se pudo obtener la previsión: 401"
- Tu clave API no tiene acceso al endpoint One Call
- La app hace fallback automático a `/forecast` (previsión 3h resumida)
- Si prefieres 7 días reales, upgradea tu plan en OpenWeatherMap

### Streamlit no abre automáticamente el navegador
- Abre manualmente: http://localhost:8501

## 📝 Variables de entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `API_KEY` | Clave de API de OpenWeatherMap | `abc123def456...` |

## 🔒 Seguridad

- **Nunca** commits `.env` o archivos con credenciales
- Usa `.gitignore` para excluir archivos sensibles (ya configurado)
- Si accidentalmente subes tu API_KEY, revócala inmediatamente en OpenWeatherMap

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios grandes, abre un issue primero para discutir.

## 📄 Licencia

Este proyecto está disponible bajo la licencia MIT.

## 👤 Autor

**gonzamargal-sketch**  
- GitHub: https://github.com/gonzamargal-sketch

## 🔗 Enlaces útiles

- [Streamlit Docs](https://docs.streamlit.io/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Python Requests](https://requests.readthedocs.io/)

---

**Última actualización**: Diciembre 2025
