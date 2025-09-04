# pages/Bomba.py
# -*- coding: utf-8 -*-

import streamlit as st
from iapws import IAPWS97

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
        height: 100px; /* Altura fija para alinear cajas */
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .nota-info {
        color: #98FB98;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT
# -----------------------------------------------------------------------------
# Esta configuración debe ser el primer comando de Streamlit
try:
    st.set_page_config(
        page_title="Cálculo de Bomba",
        layout="centered",
        initial_sidebar_state="expanded"
    )
except st.errors.StreamlitAPIException as e:
    if "st.set_page_config() can only be called once per app" not in str(e):
        raise e

# -----------------------------------------------------------------------------
# FUNCIÓN DE CÁLCULO MODIFICADA
# -----------------------------------------------------------------------------


def calcular_bomba(
    caudal_volumetrico: float,
    presion_entrada: float,
    presion_salida: float,
    unit_system: str
) -> dict:
    """
    Calcula el trabajo, la potencia y la entalpía de salida para una bomba.
    Maneja tanto el Sistema Internacional como el Sistema Inglés.
    """
    # --- Factores de Conversión ---
    PSI_TO_KPA = 6.89476
    MPA_TO_PSI = 145.038
    M3S_TO_FT3S = 35.3147
    KW_TO_HP = 1.34102
    KJ_KG_TO_BTU_LBM = 0.429923

    # --- Unidades para los resultados ---
    units = {}
    if unit_system == 'Sistema Internacional (SI)':
        units = {
            "power": "kW",
            "specific_work": "kJ/kg",
            "enthalpy": "kJ/kg",
            "volume_flow": "m³/s",
            "pressure_in": "kPa",
            "pressure_out": "MPa"
        }
        # Convertir entradas a SI (ya están en SI, solo se asignan)
        caudal_volumetrico_m3_s = caudal_volumetrico
        presion_entrada_kpa = presion_entrada
        presion_salida_mpa = presion_salida
    else:  # Sistema Inglés (Imperial)
        units = {
            "power": "hp",
            "specific_work": "Btu/lbm",
            "enthalpy": "Btu/lbm",
            "volume_flow": "ft³/s",
            "pressure_in": "psi",
            "pressure_out": "psi"
        }
        # Convertir entradas de Inglés a SI para el cálculo
        caudal_volumetrico_m3_s = caudal_volumetrico / M3S_TO_FT3S
        presion_entrada_kpa = presion_entrada * PSI_TO_KPA
        # La presión de salida en inglés también se da en psi, convertir a MPa
        presion_salida_mpa = (presion_salida * PSI_TO_KPA) / 1000

    # Conversión de Unidades para el cálculo interno (siempre en SI)
    presion_entrada_mpa = presion_entrada_kpa / 1000
    presion_salida_kpa = presion_salida_mpa * 1000

    # PASO 1: Propiedades a la entrada (Líquido saturado) usando IAPWS97
    try:
        # IAPWS97 requiere Presión en MPa y Calidad (x=0 para líquido saturado)
        estado_entrada = IAPWS97(P=presion_entrada_mpa, x=0)
        v_especifico = estado_entrada.v  # m³/kg
        h1_entalpia = estado_entrada.h    # kJ/kg
    except Exception as e:
        st.error(f"Error al obtener propiedades del agua: {e}")
        st.stop()

    # PASO 2: Flujo másico (siempre en kg/s)
    flujo_masico_kgs = caudal_volumetrico_m3_s / v_especifico

    # PASO 3: Trabajo específico (siempre en kJ/kg)
    delta_presion_kpa = presion_salida_kpa - presion_entrada_kpa
    trabajo_especifico_kj_kg = v_especifico * delta_presion_kpa

    # PASO 4: Potencia de la bomba (siempre en kW)
    potencia_kw = flujo_masico_kgs * trabajo_especifico_kj_kg

    # PASO 5: Entalpía de salida (siempre en kJ/kg)
    h2_entalpia_kj_kg = h1_entalpia + trabajo_especifico_kj_kg

    # --- Empaquetar resultados y convertir si es necesario ---
    if unit_system == 'Sistema Inglés (Imperial)':
        potencia_final = potencia_kw * KW_TO_HP
        trabajo_especifico_final = trabajo_especifico_kj_kg * KJ_KG_TO_BTU_LBM
        h2_entalpia_final = h2_entalpia_kj_kg * KJ_KG_TO_BTU_LBM
        h1_entalpia_final = h1_entalpia * KJ_KG_TO_BTU_LBM
    else:
        potencia_final = potencia_kw
        trabajo_especifico_final = trabajo_especifico_kj_kg
        h2_entalpia_final = h2_entalpia_kj_kg
        h1_entalpia_final = h1_entalpia

    return {
        "entradas": {
            f"Caudal Volumétrico [{units['volume_flow']}]": caudal_volumetrico,
            f"Presión de Entrada [{units['pressure_in']}]": presion_entrada,
            f"Presión de Salida [{units['pressure_out']}]": presion_salida
        },
        "propiedades_entrada": {
            "volumen_especifico_m3_kg": v_especifico,
            "entalpia_h1_kj_kg": h1_entalpia_final,
            "entalpia_h1_units": units['enthalpy']
        },
        "calculos_intermedios": {
            "flujo_masico_kgs": flujo_masico_kgs,
        },
        "resultados_finales": {
            "trabajo_especifico": trabajo_especifico_final,
            "potencia_requerida": potencia_final,
            "entalpia_h2": h2_entalpia_final
        },
        "units": units
    }


# -----------------------------------------------------------------------------
# INTERFAZ DE USUARIO CON STREAMLIT
# -
# --- Título de la Aplicación ---
# =========================
# 🚀 Interfaz Streamlit
# =========================
col_img, col_title = st.columns([0.2, 1])
with col_img:
    st.image("https://raw.githubusercontent.com/Jmontoyaor/thermodynamics/main/IMAGENES/Bomba.png", width=200)
with col_title:
    st.title("Bomba: Análisis interactivo de Bomba")
st.markdown("#### Esta herramienta calcula la potencia y entalpía para una bomba que maneja agua como líquido incompresible.")
st.write("---")


# =========================
# 📘 Teoría
# =========================
with st.expander("📘 Fundamentos Termodinámicos de Bombas Centrífugas"):
    st.markdown(r"""
Las **bombas** son dispositivos mecánicos diseñados para **incrementar la presión de un líquido**, transportándolo de una región de menor presión a otra de mayor presión. Son ampliamente usadas en sistemas de suministro de agua, plantas termoeléctricas, procesos industriales y sistemas de calefacción y refrigeración.

A diferencia de toberas y difusores, **las bombas sí realizan trabajo mecánico** sobre el fluido. En términos de la **Primera Ley de la Termodinámica para sistemas abiertos (volumen de control)**, la potencia de bombeo se calcula como:

$$
\dot{W}_{bomba} = \dot{m} (h_2 - h_1)
$$

donde:
- $\dot{m}$ es el flujo másico de líquido
- $h_1$ y $h_2$ son las entalpías específica a la entrada y salida de la bomba, respectivamente

En líquidos **incompresibles**, la variación de entalpía puede expresarse como una diferencia de presión:

$$
h_2 - h_1 = v (P_2 - P_1)
$$

donde:
- $v$ es el **volumen específico**, prácticamente constante
- $P_1$ y $P_2$ son las presiones a la entrada y salida

De esta forma, la potencia requerida por la bomba es:

$$
\dot{W}_{bomba} = \dot{m} v (P_2 - P_1)
$$

En la práctica, se debe considerar la **eficiencia de la bomba**, que relaciona la potencia hidráulica útil con la potencia suministrada por el motor.
""")


# =========================
# 🧪 Ejercicio y Figura
# =========================
col1, col2 = st.columns(2)
with col1:
    with st.expander("📚 Ejercicio Propuesto – Análisis de Bomba"):
        st.markdown("""
**Primera Ley de la Termodinámica – Sistemas Abiertos**

**BOMBAS**

Entra un flujo volumétrico de **agua** igual a **0.015645 m³/s** con una **presión de 100 kPa** a una bomba, y sale con una **presión de 2.5 MPa**.
Calcular:

- a) La potencia de la bomba por unidad de masa \([kJ/kg]\)
- b) La potencia de la bomba en kW
- c) La entalpía del agua a la salida de la bomba

---

**Fuente:** *Ejercicio tomado y adaptado de **LaMejorAsesoríaEducativa – YouTube***.
""")

with col2:
    st.image("https://raw.githubusercontent.com/Jmontoyaor/thermodynamics/main/IMAGENES/partes-de-una-bomba-centrifuga.jpg",
             caption="**Partes de una bomba centrífuga .\\n\\nFuente: Seguas – Diagrama de bomba centrífuga (segua​s.com).")
    st.markdown("### Desarrollo visual")
    st.video("https://youtu.be/yqasAH1LFOw?si=_TbbgdZrU_uff-JP")
st.markdown("---")


# --- Barra Lateral con Controles de Entrada ---
st.sidebar.header("Parámetros de Entrada")

# Selector de Sistema de Unidades
unit_system = st.sidebar.radio(
    "Seleccione el Sistema de Unidades",
    ('Sistema Internacional (SI)', 'Sistema Inglés (Imperial)')
)

# Entradas dinámicas basadas en el sistema de unidades
if unit_system == 'Sistema Internacional (SI)':
    v_dot = st.sidebar.slider(
        'Caudal Volumétrico (V̇) [m³/s]', min_value=0.001, max_value=0.1, value=0.0156, step=0.0001, format="%.4f")
    p1 = st.sidebar.slider(
        'Presión de Entrada (P₁) [kPa]', min_value=10.0, max_value=1000.0, value=100.0, step=1.0, format="%.1f")
    p2 = st.sidebar.slider(
        'Presión de Salida (P₂) [MPa]', min_value=0.5, max_value=15.0, value=2.5, step=0.1, format="%.2f")
else:  # Sistema Inglés (Imperial)
    v_dot = st.sidebar.slider(
        'Caudal Volumétrico (V̇) [ft³/s]', min_value=0.01, max_value=5.0, value=0.55, step=0.01, format="%.2f")
    p1 = st.sidebar.slider(
        'Presión de Entrada (P₁) [psi]', min_value=1.0, max_value=150.0, value=14.7, step=0.1, format="%.1f")
    p2 = st.sidebar.slider(
        'Presión de Salida (P₂) [psi]', min_value=50.0, max_value=2200.0, value=362.6, step=1.0, format="%.1f")


# --- Realizar el cálculo con los valores de la UI ---
calculo = calcular_bomba(
    caudal_volumetrico=v_dot,
    presion_entrada=p1,
    presion_salida=p2,
    unit_system=unit_system
)

# --- Extracción de resultados para mostrarlos ---
entradas = calculo["entradas"]
props = calculo["propiedades_entrada"]
finales = calculo["resultados_finales"]
units = calculo["units"]

# -----------------------------------------------------------------------------
# PRESENTACIÓN DE RESULTADOS EN EL ÁREA PRINCIPAL
# -----------------------------------------------------------------------------

st.header("Resultados del Cálculo")
st.markdown("---")

# --- Resumen Final en la parte superior ---
st.subheader("Resumen Final")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class='resultado-final'>
        <strong>Potencia Requerida:</strong><br>
        {finales['potencia_requerida']:.2f} {units['power']}
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='resultado-final'>
        <strong>Trabajo Específico:</strong><br>
        {finales['trabajo_especifico']:.4f} {units['specific_work']}
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='resultado-final'>
        <strong>Entalpía de Salida (h₂):</strong><br>
        {finales['entalpia_h2']:.2f} {units['enthalpy']}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Pestañas con el detalle del cálculo ---
with st.expander("Ver Detalles del Proceso de Cálculo"):
    st.subheader("Condiciones y Propiedades")
    st.markdown("**Datos de Entrada Seleccionados:**")
    st.json(entradas)

    st.markdown(f"**Propiedades del Agua a la Entrada (Líquido Saturado):**")
    st.json({
        f"Entalpía h₁ [{props['entalpia_h1_units']}]": f"{props['entalpia_h1_kj_kg']:.2f}",
        "Volumen Específico v [m³/kg]": f"{props['volumen_especifico_m3_kg']:.6f} (usado para cálculos internos en SI)"
    })


st.markdown("""
<div class='nota-info'>
<b>Nota sobre la precisión:</b> Este script utiliza el estándar internacional IAPWS-IF97 para obtener las propiedades termodinámicas del agua y el vapor, lo que garantiza una alta precisión en los cálculos.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Developed by Juan Fernando Montoya Ortiz -Electrical Engineering Student -Universidad Nacional de Colombia")
