
# -*- coding: utf-8 -*-
import streamlit as st
from iapws import IAPWS97
from typing import Dict, Any

# --- Estilos CSS Personalizados ---
custom_css = """
<style>
    .stApp {
        background-color: #0e1a40;
        color: #E0E0E0;
        font-family: 'Courier New', monospace;
    }
    h1, h2, h3 {
        color: #00BFFF;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #1B1D2B;
        border-radius: 10px;
    }
    section[data-testid="stSidebar"] {
        background-color: #222f5b;
        border-radius: 10px;
    }
    section[data-testid="stSidebar"] * {
        color: #c6e2ff !important;
    }
    .resultado-final {
        color: #FFD700;
        background-color: #2c3e50;
        border: 1px solid #FFD700;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        font-size: 1.1rem;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 10px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Configuración de la Página ---
try:
    st.set_page_config(
        page_title="Análisis de Turbina",
        layout="centered",
        initial_sidebar_state="expanded"
    )
except st.errors.StreamlitAPIException as e:
    if "st.set_page_config() can only be called once per app" not in str(e):
        raise e

# ==============================================================================
# 1. FUNCIÓN DE CÁLCULO PRINCIPAL
# ==============================================================================


@st.cache_data
def analizar_turbina(
    m_dot_in: float, P1_in: float, T1_in: float, V1_in: float,
    P2_in: float, x2_in: float, V2_in: float,
    q_loss_I_in: float, q_loss_II_in: float,
    unit_system: str
) -> Dict[str, Any]:
    """
    Realiza el análisis termodinámico de la turbina, manejando unidades SI e Inglesas.
    """
    # --- Factores de Conversión ---
    KGS_TO_LBMS = 2.20462
    MPA_TO_PSI = 145.038
    KPA_TO_PSI = 0.145038
    MS_TO_FTS = 3.28084
    M2_TO_FT2 = 10.7639
    M3KG_TO_FT3LBM = 16.0185
    KJ_KG_TO_BTU_LBM = 0.429923
    KW_TO_HP = 1.34102

    # --- Definición de Unidades y Conversión de Entradas ---
    units = {}
    if unit_system == 'Sistema Internacional (SI)':
        units = {
            "mass_flow": "kg/s", "pressure_mpa": "MPa", "pressure_kpa": "kPa",
            "temperature": "°C", "velocity": "m/s", "quality": "",
            "heat_loss": "kJ/kg", "area": "m²", "enthalpy": "kJ/kg",
            "spec_vol": "m³/kg", "spec_energy": "kJ/kg", "power": "kW"
        }
        m_dot_kgs = m_dot_in
        P1_mpa = P1_in
        T1_c = T1_in
        V1_ms = V1_in
        P2_kpa = P2_in
        x2 = x2_in
        V2_ms = V2_in
        q_loss_I_kjkg = q_loss_I_in
        q_loss_II_kjkg = q_loss_II_in
    else:  # Sistema Inglés (Imperial)
        units = {
            "mass_flow": "lbm/s", "pressure_mpa": "psi", "pressure_kpa": "psi",
            "temperature": "°F", "velocity": "ft/s", "quality": "",
            "heat_loss": "Btu/lbm", "area": "ft²", "enthalpy": "Btu/lbm",
            "spec_vol": "ft³/lbm", "spec_energy": "Btu/lbm", "power": "hp"
        }
        m_dot_kgs = m_dot_in / KGS_TO_LBMS
        P1_mpa = P1_in / MPA_TO_PSI
        T1_c = (T1_in - 32) * 5/9
        V1_ms = V1_in / MS_TO_FTS
        P2_kpa = P2_in / KPA_TO_PSI
        x2 = x2_in
        V2_ms = V2_in / MS_TO_FTS
        q_loss_I_kjkg = q_loss_I_in / KJ_KG_TO_BTU_LBM
        q_loss_II_kjkg = q_loss_II_in / KJ_KG_TO_BTU_LBM

    try:
        # --- Cálculos Internos (siempre en SI) ---
        P2_mpa = P2_kpa / 1000.0
        T1_k = T1_c + 273.15

        delta_ec_kjkg = (V2_ms**2 - V1_ms**2) / 2000.0

        state1 = IAPWS97(P=P1_mpa, T=T1_k)
        h1_kjkg = state1.h
        v1_m3kg = state1.v
        A1_m2 = m_dot_kgs * v1_m3kg / V1_ms

        state2 = IAPWS97(P=P2_mpa, x=x2)
        h2_kjkg = state2.h
        v2_m3kg = state2.v
        A2_m2 = m_dot_kgs * v2_m3kg / V2_ms

        delta_h_kjkg = h1_kjkg - h2_kjkg

        Q_dot_I_kw = -q_loss_I_kjkg * m_dot_kgs
        Wt_I_kw = m_dot_kgs * (delta_h_kjkg - delta_ec_kjkg) + Q_dot_I_kw

        Q_dot_II_kw = -q_loss_II_kjkg * m_dot_kgs
        Wt_II_kw = m_dot_kgs * delta_h_kjkg + Q_dot_II_kw

        Wt_III_kw = m_dot_kgs * (delta_h_kjkg - delta_ec_kjkg)
        Wt_IV_kw = m_dot_kgs * delta_h_kjkg

        # --- Conversión de Resultados a Unidades Seleccionadas ---
        if unit_system == 'Sistema Inglés (Imperial)':
            delta_ec_final = delta_ec_kjkg * KJ_KG_TO_BTU_LBM
            h1_final, h2_final = h1_kjkg * KJ_KG_TO_BTU_LBM, h2_kjkg * KJ_KG_TO_BTU_LBM
            v1_final, v2_final = v1_m3kg * M3KG_TO_FT3LBM, v2_m3kg * M3KG_TO_FT3LBM
            A1_final, A2_final = A1_m2 * M2_TO_FT2, A2_m2 * M2_TO_FT2
            delta_h_final = delta_h_kjkg * KJ_KG_TO_BTU_LBM
            Wt_I, Wt_II, Wt_III, Wt_IV = Wt_I_kw * KW_TO_HP, Wt_II_kw * \
                KW_TO_HP, Wt_III_kw * KW_TO_HP, Wt_IV_kw * KW_TO_HP
        else:
            delta_ec_final = delta_ec_kjkg
            h1_final, h2_final = h1_kjkg, h2_kjkg
            v1_final, v2_final = v1_m3kg, v2_m3kg
            A1_final, A2_final = A1_m2, A2_m2
            delta_h_final = delta_h_kjkg
            Wt_I, Wt_II, Wt_III, Wt_IV = Wt_I_kw, Wt_II_kw, Wt_III_kw, Wt_IV_kw

        return {
            "delta_ec": delta_ec_final, "h1": h1_final, "v1": v1_final, "A1": A1_final,
            "h2": h2_final, "v2": v2_final, "A2": A2_final, "delta_h": delta_h_final,
            "Wt_I": Wt_I, "Wt_II": Wt_II, "Wt_III": Wt_III, "Wt_IV": Wt_IV,
            "units": units, "error": None
        }
    except Exception as e:
        return {"error": str(e)}

# ==============================================================================
# 2. INTERFAZ GRÁFICA CON STREAMLIT
# ==============================================================================


# --- Configuración de la página ---
col_img, col_title = st.columns([0.2, 1])
with col_img:
    st.image("https://raw.githubusercontent.com/Jmontoyaor/thermodynamics/main/IMAGENES/Turbina%20y%20flecha%20en%20contraste.png", width=200)
with col_title:
    st.title("Turbina: Análisis Interactivo de Expansión de Vapor")
st.markdown(
    "#### Analiza cómo se transforma la energía del fluido en trabajo útil a través de una turbina.")
st.write("---")


# =========================
# 📘 Teoría
# =========================
with st.expander("📘 Fundamentos Termodinámicos de Turbinas (Çengel, 7ª ed.)"):
    st.markdown(r"""
Las **turbinas** son dispositivos que convierten la energía contenida en un fluido en **trabajo mecánico útil**. Se utilizan ampliamente en **centrales térmicas y hidroeléctricas**, donde impulsan generadores eléctricos.

En una turbina, el fluido realiza trabajo al expandirse y empujar los **álabes** conectados a un eje giratorio, provocando su rotación. El dispositivo entonces produce trabajo al entorno ($\dot{W}_{\text{salida}} > 0$).

Desde el punto de vista energético, el análisis ideal de una turbina considera que:
- No hay **transferencia significativa de calor** ($\dot{Q} \approx 0$), debido al buen aislamiento térmico.
- No hay cambio apreciable de **energía potencial** ni de **energía cinética** ($\Delta ep \approx 0$, $\Delta ec \approx 0$).

Por lo tanto, la **Primera Ley de la Termodinámica** (para flujo estable) se simplifica como:

$$
\dot{W}_{\text{turbina}} = \dot{m}(h_1 - h_2)
$$

donde:
- $\dot{W}_{\text{turbina}}$ es el **trabajo generado por unidad de tiempo**
- $\dot{m}$ es el **flujo másico**
- $h_1$ y $h_2$ son las **entalpías específicas** de entrada y salida

Este modelo permite estimar el trabajo que se puede obtener a partir de la caída de entalpía del fluido durante su paso por la turbina.

📚 **Fuente**: Çengel, Yunus A., *Termodinámica*, 7ª Edición, McGraw-Hill, Sección 5.5 "Turbinas", pp. 279–280.
""")


# =========================
# 🧪 Ejercicio y Figura
# =========================
col1, col2 = st.columns(2)
with col1:
    with st.expander("🧪 Ejercicio Propuesto – Turbinas"):
        st.markdown(r"""
**Primera ley de la termodinámica – Sistemas Abiertos**

**TURBINA**

Por una **turbina** pasa un flujo másico estable de **agua** igual a **15 kg/s**.

- En la **entrada**:
  - Temperatura: **350 °C**
  - Presión: **5 MPa**
  - Velocidad: **70 m/s**

- En la **salida**:
  - Presión: **75 kPa**
  - Calidad: **90%**
  - Velocidad: **40 m/s**

Se pide calcular:

- a) El **cambio de energía cinética**: $\Delta e_C$
- b) El **área** en la entrada y salida de la turbina
- c) La **potencia generada por la turbina** bajo los siguientes casos:

  - c.1) La turbina pierde **10 kJ/kg** y se considera $\Delta e_C$
  - c.2) La turbina pierde **80 kJ/s** y no se considera $\Delta e_C$
  - c.3) La turbina es **adiabática** y se considera $\Delta e_C$
  - c.4) La turbina es **adiabática** y **no** se considera $\Delta e_C$

---

**Fuente:** *Ejercicio tomado y adaptado de **LaMejorAsesoríaEducativa – YouTube***.
""")
with col2:
    st.image("https://raw.githubusercontent.com/Jmontoyaor/thermodynamics/main/IMAGENES/TurbinaBook.png",
             caption="**FIGURA 5-25** – FIGURA 5-28** – Esquema de turbina.\\n\\nFuente: Çengel – Termodinámica, 7ª Edición.")
    st.markdown("### Desarrollo visual")
    st.video("https://youtu.be/_n2ozXyNBSc?si=5XJVptZt_PPEl59Y")

st.markdown("---")

# --- Barra lateral para los controles de entrada ---
st.sidebar.header("Parámetros de Entrada")
unit_system = st.sidebar.radio("Seleccione el Sistema de Unidades",
                               ('Sistema Internacional (SI)', 'Sistema Inglés (Imperial)'))

if unit_system == 'Sistema Internacional (SI)':
    m_dot = st.sidebar.number_input(
        "Flujo Másico (ṁ) [kg/s]", 1.0, 100.0, 15.0, 1.0)
    st.sidebar.subheader("Estado 1 (Entrada)")
    P1 = st.sidebar.slider("Presión (P₁) [MPa]", 1.0, 15.0, 5.0, 0.5)
    T1 = st.sidebar.slider("Temperatura (T₁) [°C]", 200.0, 600.0, 350.0, 5.0)
    V1 = st.sidebar.slider("Velocidad (V₁) [m/s]", 10, 200, 70, 5)
    st.sidebar.subheader("Estado 2 (Salida)")
    P2 = st.sidebar.slider("Presión (P₂) [kPa]", 10.0, 200.0, 75.0, 5.0)
    x2 = st.sidebar.slider("Calidad de Vapor (x₂)", 0.0, 1.0, 0.9, 0.01)
    V2 = st.sidebar.slider("Velocidad (V₂) [m/s]", 10, 200, 40, 5)
    st.sidebar.subheader("Pérdidas de Calor Específicas")
    q_loss_I = st.sidebar.number_input(
        "Pérdida Caso I (q) [kJ/kg]", 0.0, 100.0, 10.0, 5.0)
    q_loss_II = st.sidebar.number_input(
        "Pérdida Caso II (q) [kJ/kg]", 0.0, 200.0, 80.0, 5.0)
else:  # Sistema Inglés
    m_dot = st.sidebar.number_input(
        "Flujo Másico (ṁ) [lbm/s]", 2.0, 220.0, 33.0, 1.0)
    st.sidebar.subheader("Estado 1 (Entrada)")
    P1 = st.sidebar.slider("Presión (P₁) [psi]", 150.0, 2200.0, 725.0, 10.0)
    T1 = st.sidebar.slider("Temperatura (T₁) [°F]", 400.0, 1100.0, 662.0, 10.0)
    V1 = st.sidebar.slider("Velocidad (V₁) [ft/s]", 30, 650, 230, 10)
    st.sidebar.subheader("Estado 2 (Salida)")
    P2 = st.sidebar.slider("Presión (P₂) [psi]", 1.5, 30.0, 10.9, 0.5)
    x2 = st.sidebar.slider("Calidad de Vapor (x₂)", 0.0, 1.0, 0.9, 0.01)
    V2 = st.sidebar.slider("Velocidad (V₂) [ft/s]", 30, 650, 131, 10)
    st.sidebar.subheader("Pérdidas de Calor Específicas")
    q_loss_I = st.sidebar.number_input(
        "Pérdida Caso I (q) [Btu/lbm]", 0.0, 50.0, 4.3, 1.0)
    q_loss_II = st.sidebar.number_input(
        "Pérdida Caso II (q) [Btu/lbm]", 0.0, 100.0, 34.4, 1.0)

# --- Ejecución y Presentación de Resultados ---
resultados = analizar_turbina(
    m_dot, P1, T1, V1, P2, x2, V2, q_loss_I, q_loss_II, unit_system)

st.divider()

if resultados.get("error"):
    st.error(f"**Error en el cálculo:** {resultados['error']}")
else:
    units = resultados['units']
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Propiedades en la Entrada (1)")
        st.markdown(
            f"<div class='resultado-final'><strong>Entalpía (h₁):</strong><br>{resultados['h1']:.2f} {units['enthalpy']}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='resultado-final'><strong>Área (A₁):</strong><br>{resultados['A1']:.4f} {units['area']}</div>", unsafe_allow_html=True)
    with col2:
        st.subheader("Propiedades en la Salida (2)")
        st.markdown(
            f"<div class='resultado-final'><strong>Entalpía (h₂):</strong><br>{resultados['h2']:.2f} {units['enthalpy']}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='resultado-final'><strong>Área (A₂):</strong><br>{resultados['A2']:.4f} {units['area']}</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("Cambios de Energía Específica")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"<div class='resultado-final'><strong>Δh (h₁ - h₂):</strong><br>{resultados['delta_h']:.2f} {units['enthalpy']}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(
            f"<div class='resultado-final'><strong>Δec:</strong><br>{resultados['delta_ec']:.2f} {units['spec_energy']}</div>", unsafe_allow_html=True)

    st.divider()
    st.header(f"⚡ Potencia Generada por la Turbina (Ẇt)")
    r1, r2 = st.columns(2)
    with r1:
        st.markdown(
            f"<div class='resultado-final'><strong>I. Con Pérdida de Calor y ΔEc</strong><br>Potencia: {resultados['Wt_I']:.2f} {units['power']}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='resultado-final'><strong>III. Adiabática y con ΔEc</strong><br>Potencia: {resultados['Wt_III']:.2f} {units['power']}</div>", unsafe_allow_html=True)
    with r2:
        st.markdown(
            f"<div class='resultado-final'><strong>II. Con Pérdida de Calor y sin ΔEc</strong><br>Potencia: {resultados['Wt_II']:.2f} {units['power']}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='resultado-final'><strong>IV. Adiabática y sin ΔEc</strong><br>Potencia: {resultados['Wt_IV']:.2f} {units['power']}</div>", unsafe_allow_html=True)

st.markdown("""
<div class='nota-info'>
<b>Nota sobre la precisión:</b> Este script utiliza el estándar internacional IAPWS-IF97 para obtener las propiedades termodinámicas del agua y el vapor, lo que garantiza una alta precisión en los cálculos.
</div>
""", unsafe_allow_html=True)


st.markdown("---")
st.caption("Developed by Juan Fernando Montoya Ortiz -Electrical Engineering Student -Universidad Nacional de Colombia")
