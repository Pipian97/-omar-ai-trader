# OMAR AI TRADER — Web Edition

## Objetivo
Abrir OMAR AI TRADER desde iPhone, iPad o computadora usando una URL de Streamlit.

## Archivos importantes
- `streamlit_app.py` — punto de entrada para la nube
- `app.py` — dashboard principal
- `broker.py` — conexión PAPER a Alpaca
- `requirements.txt` — dependencias
- `.streamlit/config.toml` — configuración visual
- `.gitignore` — evita publicar secretos

## Despliegue
1. Crea una cuenta en GitHub.
2. Crea un repositorio nuevo.
3. Sube todos los archivos de esta carpeta al repositorio.
4. Entra a Streamlit Community Cloud y conecta GitHub.
5. Crea una nueva app.
6. Elige tu repositorio y usa `streamlit_app.py` como entrypoint.
7. En App settings > Secrets agrega:

```toml
ALPACA_API_KEY = "TU_PAPER_API_KEY"
ALPACA_SECRET_KEY = "TU_PAPER_SECRET_KEY"
ALPACA_PAPER = "true"
```

8. Guarda/reinicia la app.
9. Streamlit te dará una URL `*.streamlit.app` que puedes abrir desde Safari.

## Seguridad
- Nunca subas `.env` o `secrets.toml` a GitHub.
- Nunca uses claves de trading real en esta versión.
- La aplicación rechaza ALPACA_PAPER=false.

## Importante
El sistema es experimental y los backtests no garantizan resultados futuros.
