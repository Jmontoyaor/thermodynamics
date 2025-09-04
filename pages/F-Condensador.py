
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
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 10px;
    }
    .nota-info {
        color: #98FB98;
        background-color: rgba(152, 251, 152, 0.1);
        border-left: 5px solid #98FB98;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE LA PÁGINA ---
try:
    st.set_page_config(
        page_title="Análisis de Condensador",
        page_icon="💨",
        layout="centered"
    )
except st.errors.StreamlitAPIException as e:
    if "st.set_page_config() can only be called once per app" not in str(e):
        raise e

# ==============================================================================
# 1. FUNCIÓN DE CÁLCULO PRINCIPAL
# ==============================================================================


@st.cache_data
def analizar_condensador(
    m_dot_v_in: float, P_in: float, calidad_in: float, delta_T_in: float,
    unit_system: str
) -> Dict[str, Any]:
    """
    Calcula el flujo de enfriamiento en un condensador, manejando unidades SI e Inglesas.
    """
    # --- Constantes y Factores de Conversión ---
    CP_AGUA_SI = 4.186  # kJ/kg·°C
    KG_MIN_TO_KGS = 1/60
    KGS_TO_LBMS = 2.20462
    KPA_TO_PSI = 0.145038
    C_TO_F_FACTOR = 9/5
    KJ_KG_TO_BTU_LBM = 0.429923
    KW_TO_BTUS = 0.947817

    # --- Definición de Unidades y Conversión de Entradas ---
    units = {}
    if unit_system == 'Sistema Internacional (SI)':
        units = {"mass_flow_in": "kg/min", "mass_flow": "kg/s", "pressure": "kPa",
                 "delta_t": "°C", "heat_rate": "kW", "enthalpy": "kJ/kg"}
        m_dot_v_kgs = m_dot_v_in * KG_MIN_TO_KGS
        P_kpa = P_in
        calidad_vapor = calidad_in
        delta_T_agua_C = delta_T_in
    else:  # Sistema Inglés (Imperial)
        units = {"mass_flow_in": "lbm/min", "mass_flow": "lbm/s", "pressure": "psi",
                 "delta_t": "°F", "heat_rate": "Btu/s", "enthalpy": "Btu/lbm"}
        m_dot_v_kgs = (m_dot_v_in / KGS_TO_LBMS) * \
            KG_MIN_TO_KGS  # lbm/min -> kg/s
        P_kpa = P_in / KPA_TO_PSI
        calidad_vapor = calidad_in
        delta_T_agua_C = delta_T_in / C_TO_F_FACTOR

    try:
        # --- Cálculos Internos (siempre en SI) ---
        P_MPa = P_kpa / 1000.0
        liq_saturado = IAPWS97(P=P_MPa, x=0)
        vap_saturado = IAPWS97(P=P_MPa, x=1)

        h_f_kjkg = liq_saturado.h
        h_g_kjkg = vap_saturado.h
        h_fg_kjkg = h_g_kjkg - h_f_kjkg

        h_entrada_kjkg = h_f_kjkg + calidad_vapor * h_fg_kjkg
        h_salida_kjkg = h_f_kjkg

        delta_h_v_kjkg = h_entrada_kjkg - h_salida_kjkg
        Q_punto_kw = m_dot_v_kgs * delta_h_v_kjkg

        if delta_T_agua_C == 0:
            return {"error": "El incremento de temperatura no puede ser cero."}
        m_dot_a_kgs = Q_punto_kw / (CP_AGUA_SI * delta_T_agua_C)

        # --- Conversión de Resultados a Unidades Seleccionadas ---
        if unit_system == 'Sistema Inglés (Imperial)':
            m_dot_a_final = m_dot_a_kgs * KGS_TO_LBMS
            Q_punto_final = Q_punto_kw * KW_TO_BTUS
            h_f_final = h_f_kjkg * KJ_KG_TO_BTU_LBM
            h_g_final = h_g_kjkg * KJ_KG_TO_BTU_LBM
            h_fg_final = h_fg_kjkg * KJ_KG_TO_BTU_LBM
            h_entrada_final = h_entrada_kjkg * KJ_KG_TO_BTU_LBM
            h_salida_final = h_salida_kjkg * KJ_KG_TO_BTU_LBM
        else:
            m_dot_a_final = m_dot_a_kgs
            Q_punto_final = Q_punto_kw
            h_f_final = h_f_kjkg
            h_g_final = h_g_kjkg
            h_fg_final = h_fg_kjkg
            h_entrada_final = h_entrada_kjkg
            h_salida_final = h_salida_kjkg

        return {
            "m_dot_agua_enfriamiento": m_dot_a_final,
            "Q_punto": Q_punto_final,
            "h_f": h_f_final,
            "h_g": h_g_final,
            "h_fg": h_fg_final,
            "h_entrada": h_entrada_final,
            "h_salida": h_salida_final,
            "m_dot_v_kgs": m_dot_v_kgs,
            "units": units,
            "error": None
        }
    except Exception as e:
        return {"error": f"Error en cálculo de propiedades: {e}"}


# ==============================================================================
# 2. VISTA (Interfaz Gráfica con Streamlit)
# ==============================================================================
# --- Contenido Principal ---
col_img, col_title = st.columns([0.2, 1])
with col_img:
    st.image("https://raw.githubusercontent.com/Jmontoyaor/thermodynamics/main/IMAGENES/Intercambiador%20de%20calor%20moderno.png", width=200)
with col_title:
    st.title(
        "Intercambiador de calor: Análisis interactivo de Intercambiador de calor")
st.markdown("""
**Este módulo interactivo** te permite analizar las condiciones de operación de un intercambiador de calor de forma sencilla.
Podrás observar cómo cambian variables clave como **presión**, **temperatura** y **velocidad** del fluido, y calcular parámetros importantes como el **flujo másico de enfriamiento necesario**.
""")

st.write("---")


with st.expander("📘 Fundamentos Termodinámicos de Compresores (Çengel, 7ª ed.)"):
    st.markdown(r"""
        Los **compresores** son dispositivos mecánicos que elevan la presión de un gas al reducir su volumen. Son ampliamente utilizados en sistemas de refrigeración, aire acondicionado, turbomáquinas, y plantas industriales.

        A diferencia de las bombas (que trabajan con líquidos), los compresores manipulan **gases** y generalmente requieren **trabajo de entrada** para operar, debido a la compresibilidad del fluido.

        **Principios Clave:**
        - **Primera Ley para sistemas abiertos:** Se analiza aplicando un balance de energía en régimen estacionario.
        - **Trabajo de compresión:** El trabajo requerido por unidad de masa está dado por:
          $$
          w = h_2 - h_1
          $$
          donde \( h_1 \) y \( h_2 \) son las entalpías del gas a la entrada y salida del compresor.
        - **Eficiencia isentrópica:** Compara el trabajo real del compresor con el trabajo ideal (reversible y adiabático).
        - **Aumento de temperatura y presión:** Durante la compresión, ambos parámetros aumentan, dependiendo del tipo de proceso (isentrópico, politrópico o real).

        📚 **Fuente**: Çengel, Y. A., & Boles, M. A. (2011). *Termodinámica* (7ª ed.). McGraw-Hill.
    """)

col1, col2 = st.columns(2)
with col1:
    with st.expander("🧪 Ejercicio Propuesto – Compresor"):
        st.markdown("""
Al **Condensador** de una Termoeléctrica entran **420 kg/min de Vapor** con una
**Presión de 30 kPa** y una **Calidad del 90%**; se requiere que el vapor
salga como **líquido saturado**.

Para enfriar el vapor, se utiliza **agua de un río**, haciéndola pasar por el interior del condensador.
Para prevenir la contaminación térmica, el **agua del río** no debe superar un incremento
de temperatura igual a **10 °C**.

---

**Calcular:**

El **flujo másico de agua de enfriamiento** necesario para satisfacer el cambio demandado por el vapor.

---

📚 **Fuente**: *Ejercicio tomado y adaptado de **LaMejorAsesoríaEducativa – YouTube***.
        """)


with col2:
    st.image(
        "https://raw.githubusercontent.com/Jmontoyaor/thermodynamics/main/IMAGENES/Imagen%202.png",
        caption="Figura 5-35, Un intercambiador de calor puede ser tan simple como dos tuberías concéntricas. Fuente: Çengel – Termodinámica, 7ª Edición.",
        use_container_width=True
    )

    st.markdown("### Desarrollo visual")
    st.video("https://youtu.be/XeOi0Rcqxio?si=Lv0RB7-jzc3riA-6")

st.markdown("---")

# --- Barra Lateral con Controles de Entrada ---
st.sidebar.header("Parámetros de Entrada")
unit_system = st.sidebar.radio("Seleccione el Sistema de Unidades",
                               ('Sistema Internacional (SI)', 'Sistema Inglés (Imperial)'))

if unit_system == 'Sistema Internacional (SI)':
    m_dot_v = st.sidebar.slider(
        "Flujo másico de vapor [kg/min]", 1.0, 1000.0, 420.0, 1.0)
    P = st.sidebar.slider("Presión del vapor [kPa]", 5.0, 600.0, 30.0, 0.5)
    calidad = st.sidebar.slider("Calidad del vapor (x)", 0.0, 1.0, 0.90, 0.01)
    delta_T = st.sidebar.slider(
        "Incremento de temp. del agua [°C]", 1.0, 30.0, 10.0, 0.5)
else:  # Sistema Inglés
    m_dot_v = st.sidebar.slider(
        "Flujo másico de vapor [lbm/min]", 2.0, 2200.0, 926.0, 10.0)
    P = st.sidebar.slider("Presión del vapor [psi]", 0.7, 30.0, 4.35, 0.05)
    calidad = st.sidebar.slider("Calidad del vapor (x)", 0.0, 1.0, 0.90, 0.01)
    delta_T = st.sidebar.slider(
        "Incremento de temp. del agua [°F]", 2.0, 55.0, 18.0, 1.0)

# --- Ejecución y Presentación de Resultados ---
resultados = analizar_condensador(m_dot_v, P, calidad, delta_T, unit_system)

st.header("📊 Resultados del Análisis")

if resultados.get("error"):
    st.error(f"**Error en el cálculo:** {resultados['error']}")
else:
    units = resultados['units']
    st.markdown(f"""
    <div class='resultado-final' style='background-color: #004d40; border-color: #00BFFF;'>
        <strong style='color: #E0E0E0;'>Flujo de Agua de Enfriamiento Requerido (ṁ_agua):</strong>
        <span style='font-size: 1.5rem; color: #FFFFFF; margin-top: 10px;'>
            {resultados['m_dot_agua_enfriamiento']:.2f} {units['mass_flow']}
        </span>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Ver desglose de los cálculos"):
        st.subheader("Datos de Entrada Utilizados")
        st.write(
            f"- **Flujo másico de vapor (ṁ_v):** {m_dot_v:.1f} {units['mass_flow_in']} ({resultados['m_dot_v_kgs']:.3f} kg/s)")
        st.write(f"- **Presión del vapor (P):** {P:.2f} {units['pressure']}")
        st.write(f"- **Calidad del vapor (x):** {calidad:.2f}")
        st.write(
            f"- **Incremento de temp. del agua (ΔT):** {delta_T:.1f} {units['delta_t']}")

        st.subheader(f"Propiedades del Vapor (a {P:.2f} {units['pressure']})")
        st.write(
            f"- **Entalpía del líquido saturado ($h_f$):** {resultados['h_f']:.2f} {units['enthalpy']}")
        st.write(
            f"- **Entalpía del vapor saturado ($h_g$):** {resultados['h_g']:.2f} {units['enthalpy']}")
        st.write(
            f"- **Entalpía de vaporización ($h_{{fg}}$):** {resultados['h_fg']:.2f} {units['enthalpy']}")

        st.subheader("Balance de Energía para el Vapor")
        st.write(
            f"- **Entalpía de entrada ($h_{{entrada}}$):** {resultados['h_entrada']:.2f} {units['enthalpy']}")
        st.write(
            f"- **Entalpía de salida ($h_{{salida}}$):** {resultados['h_salida']:.2f} {units['enthalpy']}")
        st.write(
            f"**- Tasa de calor liberado por el vapor ($\\dot{{Q}}$):** {resultados['Q_punto']:.2f} {units['heat_rate']}")

st.markdown("---")
st.markdown("""
<div class='nota-info'>
<b>Nota sobre la precisión:</b> Este script utiliza el estándar internacional IAPWS-IF97 para obtener las propiedades termodinámicas del agua y el vapor, lo que garantiza una alta precisión en los cálculos.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Developed by Juan Fernando Montoya Ortiz -Electrical Engineering Student -Universidad Nacional de Colombia")
