
# -*- coding: utf-8 -*-
import streamlit as st
import math
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
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE LA PÁGINA ---
try:
    st.set_page_config(
        page_title="Análisis de Compresor",
        page_icon="⚙️",
        layout="centered"
    )
except st.errors.StreamlitAPIException as e:
    if "st.set_page_config() can only be called once per app" not in str(e):
        raise e

# ==============================================================================
# 1. FUNCIÓN DE CÁLCULO PRINCIPAL
# ==============================================================================


@st.cache_data
def analizar_compresor(
    m_dot_in: float, q_out_in: float,
    P1_in: float, T1_in: float, V1_in: float,
    P2_in: float, T2_in: float, V2_in: float,
    unit_system: str
) -> Dict[str, Any]:
    """
    Realiza el análisis termodinámico de un compresor de aire, manejando unidades SI e Inglesas.
    """
    # --- Constantes para el Aire (en unidades SI) ---
    R_air_si = 0.287  # kJ/kg·K
    cp_air_si = 1.005  # kJ/kg·K

    # --- Factores de Conversión ---
    KGS_TO_LBMS = 2.20462
    KJ_KG_TO_BTU_LBM = 0.429923
    KPA_TO_PSI = 0.145038
    K_TO_R = 1.8
    MS_TO_FTS = 3.28084
    KW_TO_HP = 1.34102
    M3S_TO_FT3S = 35.3147
    KW_TO_BTUS = 0.947817  # kW to BTU/s

    # --- Definición de Unidades y Conversión de Entradas ---
    units = {}
    if unit_system == 'Sistema Internacional (SI)':
        units = {
            "power": "kW", "volume_flow": "m³/s", "work_mass": "kJ/kg",
            "heat_rate": "kW", "enthalpy_change": "kJ/kg", "ke_change": "kJ/kg"
        }
        m_dot_kgs = m_dot_in
        q_out_kjkg = q_out_in
        P1_kpa, T1_k, V1_ms = P1_in, T1_in, V1_in
        P2_kpa, T2_k, V2_ms = P2_in, T2_in, V2_in
    else:  # Sistema Inglés (Imperial)
        units = {
            "power": "hp", "volume_flow": "ft³/s", "work_mass": "Btu/lbm",
            "heat_rate": "Btu/s", "enthalpy_change": "Btu/lbm", "ke_change": "Btu/lbm"
        }
        m_dot_kgs = m_dot_in / KGS_TO_LBMS
        q_out_kjkg = q_out_in / KJ_KG_TO_BTU_LBM
        P1_kpa = P1_in / KPA_TO_PSI
        T1_k = T1_in / K_TO_R
        V1_ms = V1_in / MS_TO_FTS
        P2_kpa = P2_in / KPA_TO_PSI
        T2_k = T2_in / K_TO_R
        V2_ms = V2_in / MS_TO_FTS

    # --- Cálculos Internos (siempre en SI) ---
    # a) Flujo volumétrico
    V_dot_1_m3s = (m_dot_kgs * R_air_si * T1_k) / P1_kpa if P1_kpa > 0 else 0

    # b) Potencia requerida
    Q_dot_kw = -m_dot_kgs * q_out_kjkg
    delta_h_kjkg = cp_air_si * (T2_k - T1_k)
    delta_ec_kjkg = (V2_ms**2 - V1_ms**2) / 2000.0
    W_dot_kw = Q_dot_kw - m_dot_kgs * (delta_h_kjkg + delta_ec_kjkg)

    # c) Trabajo por unidad de masa
    w_kjkg = W_dot_kw / m_dot_kgs if m_dot_kgs > 0 else 0

    # --- Conversión de Resultados a Unidades Seleccionadas ---
    if unit_system == 'Sistema Inglés (Imperial)':
        potencia_final = W_dot_kw * KW_TO_HP
        V_dot_1_final = V_dot_1_m3s * M3S_TO_FT3S
        w_final = w_kjkg * KJ_KG_TO_BTU_LBM
        Q_dot_final = Q_dot_kw * KW_TO_BTUS
        delta_h_final = delta_h_kjkg * KJ_KG_TO_BTU_LBM
        delta_ec_final = delta_ec_kjkg * KJ_KG_TO_BTU_LBM
    else:
        potencia_final = W_dot_kw
        V_dot_1_final = V_dot_1_m3s
        w_final = w_kjkg
        Q_dot_final = Q_dot_kw
        delta_h_final = delta_h_kjkg
        delta_ec_final = delta_ec_kjkg

    return {
        "potencia_w": potencia_final,
        "flujo_volumetrico": V_dot_1_final,
        "trabajo_por_masa": w_final,
        "Q_dot": Q_dot_final,
        "delta_h": delta_h_final,
        "delta_ec": delta_ec_final,
        "units": units
    }


col_img, col_title = st.columns([0.2, 1])
with col_img:
    st.image("https://raw.githubusercontent.com/Jmontoyaor/thermodynamics/main/IMAGENES/Compresor%20de%20aire%20ilustre.png", width=200)
with col_title:
    st.title("Compresor: Análisis Interactivo del Trabajo de Compresión")
st.markdown("#### Explora cómo varían la presión, la temperatura y la entalpía del gas durante el proceso de compresión.")


# =========================
# 📘 Teoría
# =========================
with st.expander("📘 Fundamentos Termodinámicos de Compresores (Çengel, 7ª ed.)"):
    st.markdown(r"""
Los **compresores** son dispositivos utilizados para **aumentar la presión de un gas** mediante el suministro de **trabajo mecánico** desde una fuente externa. Son fundamentales en sistemas de refrigeración, aire acondicionado, motores de combustión y procesos industriales.

En un compresor, el fluido (generalmente un gas) recibe energía en forma de **trabajo de eje**. A diferencia de las turbinas, los compresores **no generan trabajo**, sino que lo **consumen**:

$$
\dot{W}_{\text{entrada}} > 0
$$

Los compresores se analizan generalmente bajo estas suposiciones ideales:
- **Sin transferencia de calor significativa** ($\dot{Q} \approx 0$) → proceso adiabático
- **Sin cambios importantes en energía potencial** ($\Delta ep \approx 0$)
- **Cambios en energía cinética despreciables**, salvo que el gas se acelere notablemente ($\Delta ec \approx 0$)

Aplicando la **Primera Ley de la Termodinámica** para flujo estacionario:

$$
\dot{W}_{\text{compresor}} = \dot{m} \left( h_2 - h_1 + \frac{V_2^2 - V_1^2}{2} + g(z_2 - z_1) \right)
$$

Y si se considera un compresor **adiabático y sin variaciones de energía cinética ni potencial**, se simplifica a:

$$
\dot{W}_{\text{compresor}} = \dot{m}(h_2 - h_1)
$$

donde:
- $h$ es la entalpía específica
- $\dot{m}$ es el flujo másico
- $\dot{W}_{\text{compresor}}$ es el trabajo requerido por unidad de tiempo

Este modelo permite calcular el **trabajo de compresión** requerido para lograr un aumento de presión y temperatura en el gas.

📚 **Fuente**: Çengel, Yunus A., *Termodinámica*, 7ª Edición, McGraw-Hill, Sección 5.5 "Compresores", pp. 279–280.
""")

col1, col2 = st.columns(2)
with col1:
    with st.expander("🧪 Ejercicio Propuesto – Compresor"):
        st.markdown("""
**Primera ley de la termodinámica – Sistemas Abiertos**

**COMPRESOR**

Un compresor recibe **aire** a:
- **Presión:** 100 kPa
- **Temperatura:** 300 K
- **Velocidad:** 5 m/s

Y lo entrega a:
- **Presión:** 800 kPa
- **Temperatura:** 500 K
- **Velocidad:** 7 m/s

El **flujo másico** de aire es de **0.3 kg/s**.
El **calor disipado** hacia el ambiente es **15 kJ/kg**.

Asuma que el aire se comporta como un **gas ideal**.

Determinar:
- a) El **flujo volumétrico** a la entrada del compresor.
- b) La **potencia requerida** para operar el compresor.
- c) El **trabajo por unidad de masa**.
---
""")

with col2:
    st.image("https://raw.githubusercontent.com/Jmontoyaor/thermodynamics/main/IMAGENES/Compresor.png",
             caption="**FIGURA 5-27 - Esquema de compresor\\n\\nFuente: Çengel – Termodinámica, 7ª Edición.")
    st.markdown("### Ejercicio adicional")
    st.video("https://www.youtube.com/watch?v=atcJEUzwVRk")
st.markdown("---")

# --- Barra Lateral con Controles de Entrada ---
st.sidebar.header("Parámetros de Entrada")
unit_system = st.sidebar.radio("Seleccione el Sistema de Unidades",
                               ('Sistema Internacional (SI)', 'Sistema Inglés (Imperial)'))

if unit_system == 'Sistema Internacional (SI)':
    m_dot = st.sidebar.slider("Flujo másico (ṁ) [kg/s]", 0.01, 2.0, 0.3, 0.01)
    q_out = st.sidebar.slider(
        "Calor disipado (q) [kJ/kg]", 0.0, 100.0, 15.0, 0.5)
    st.sidebar.subheader("Entrada (1)")
    P1 = st.sidebar.slider("Presión (P₁) [kPa]", 50.0, 500.0, 100.0, 1.0)
    T1 = st.sidebar.slider("Temperatura (T₁) [K]", 250.0, 600.0, 300.0, 1.0)
    V1 = st.sidebar.slider("Velocidad (V₁) [m/s]", 0.0, 100.0, 5.0, 0.5)
    st.sidebar.subheader("Salida (2)")
    P2 = st.sidebar.slider("Presión (P₂) [kPa]", 100.0, 1500.0, 800.0, 5.0)
    T2 = st.sidebar.slider("Temperatura (T₂) [K]", 300.0, 1000.0, 500.0, 1.0)
    V2 = st.sidebar.slider("Velocidad (V₂) [m/s]", 0.0, 100.0, 7.0, 0.5)
else:  # Sistema Inglés
    m_dot = st.sidebar.slider(
        "Flujo másico (ṁ) [lbm/s]", 0.02, 4.0, 0.66, 0.02)
    q_out = st.sidebar.slider(
        "Calor disipado (q) [Btu/lbm]", 0.0, 50.0, 6.4, 0.2)
    st.sidebar.subheader("Entrada (1)")
    P1 = st.sidebar.slider("Presión (P₁) [psi]", 7.0, 75.0, 14.7, 0.5)
    T1 = st.sidebar.slider("Temperatura (T₁) [°R]", 450.0, 1100.0, 540.0, 5.0)
    V1 = st.sidebar.slider("Velocidad (V₁) [ft/s]", 0.0, 330.0, 16.4, 1.0)
    st.sidebar.subheader("Salida (2)")
    P2 = st.sidebar.slider("Presión (P₂) [psi]", 15.0, 220.0, 116.0, 1.0)
    T2 = st.sidebar.slider("Temperatura (T₂) [°R]", 540.0, 1800.0, 900.0, 5.0)
    V2 = st.sidebar.slider("Velocidad (V₂) [ft/s]", 0.0, 330.0, 23.0, 1.0)

# --- Ejecución y Presentación de Resultados ---
resultados = analizar_compresor(
    m_dot, q_out, P1, T1, V1, P2, T2, V2, unit_system)
units = resultados['units']

st.header("📊 Resultados del Análisis")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"<div class='resultado-final'><strong>Potencia de Entrada (Ẇ):</strong><br>{resultados['potencia_w']:.3f} {units['power']}</div>", unsafe_allow_html=True)
with col2:
    st.markdown(
        f"<div class='resultado-final'><strong>Flujo Volumétrico Entrada:</strong><br>{resultados['flujo_volumetrico']:.4f} {units['volume_flow']}</div>", unsafe_allow_html=True)
with col3:
    st.markdown(
        f"<div class='resultado-final'><strong>Trabajo por Masa (w):</strong><br>{resultados['trabajo_por_masa']:.3f} {units['work_mass']}</div>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; font-style: italic;'>Nota: El signo negativo indica que el trabajo es una entrada de energía al sistema (consumo).</p>", unsafe_allow_html=True)


with st.expander("Ver desglose de los cálculos", expanded=False):
    st.subheader("Desglose del Cálculo de Potencia")

    st.markdown(f"""
    <div class='resultado-final'>
        <strong>Tasa de calor disipado (Q̇):</strong><br>
        {resultados['Q_dot']:.3f} {units['heat_rate']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='resultado-final'>
        <strong>Cambio de entalpía específica (Δh):</strong><br>
        {resultados['delta_h']:.3f} {units['enthalpy_change']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='resultado-final'>
        <strong>Cambio de energía cinética específica (Δec):</strong><br>
        {resultados['delta_ec']:.4f} {units['ke_change']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='resultado-final'>
        <strong>Potencia de entrada al compresor (Ẇ):</strong><br>
        {resultados['potencia_w']:.3f} {units['power']}
    </div>

    """, unsafe_allow_html=True)

st.header("Fundamento Teórico")
with st.expander("Ver Fórmulas Utilizadas", expanded=False):
    st.subheader("a) Flujo Volumétrico (Ecuación del Gas Ideal)")
    st.latex(
        r'''P_1 \dot{V}_1 = \dot{m} R T_1 \quad \implies \quad \dot{V}_1 = \frac{\dot{m} R T_1}{P_1}''')

    st.subheader("b) Potencia (Primera Ley de la Termodinámica)")
    st.write(
        "Para un sistema abierto en estado estacionario, el balance de energía es:")
    st.latex(
        r'''\dot{Q} - \dot{W} = \dot{m} \left[ (h_2 - h_1) + \frac{V_2^2 - V_1^2}{2} + g(z_2 - z_1) \right]''')
    st.write(
        "Asumiendo que el cambio de energía potencial es despreciable y despejando la potencia $\dot{W}$:")
    st.latex(
        r'''\dot{W} = \dot{Q} - \dot{m} \left[ \Delta h + \Delta e_c \right]''')
    st.write("Donde:")
    st.latex(r'''\dot{Q} = -\dot{m} \cdot q_{out}''')
    st.latex(r'''\Delta h = c_p (T_2 - T_1)''')
    st.latex(
        r'''\Delta e_c = \frac{V_2^2 - V_1^2}{2000} \quad (\text{en kJ/kg})''')

    st.subheader("c) Trabajo por Unidad de Masa")
    st.latex(r'''w = \frac{\dot{W}}{\dot{m}}''')


st.markdown("---")
st.caption("Desarrollado por Juan Fernando Montoya Ortiz - Estudiante de Ingeniería Eléctrica - Universidad Nacional de Colombia")
