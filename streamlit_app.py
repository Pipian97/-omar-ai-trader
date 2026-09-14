import streamlit as st

st.set_page_config(
    page_title="OMAR AI TRADER",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

from broker import credentials_configured

st.title("📈 OMAR AI TRADER")
st.caption("Paper-trading research terminal · Web Edition")

if not credentials_configured():
    st.warning("Falta conectar la cuenta PAPER de Alpaca.")
    st.markdown("""
### Configuración inicial
En **Streamlit Community Cloud → App settings → Secrets**, pega:

```toml
ALPACA_API_KEY = "TU_PAPER_API_KEY"
ALPACA_SECRET_KEY = "TU_PAPER_SECRET_KEY"
ALPACA_PAPER = "true"
```

No pongas estas claves dentro de GitHub ni las compartas públicamente.

Esta aplicación está bloqueada a **paper trading**.
""")
    st.stop()

# Run the full dashboard only after keys are configured.
exec(open("app.py", encoding="utf-8").read())
