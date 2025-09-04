from typing import Dict, Any
import math
from iapws import IAPWS97
import streamlit as st

# -*- coding: utf-8 -*-

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
        height: 110px; /* Altura fija para alinear cajas */
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

# --- Configuración de la Página ---
try:
    st.set_page_config(
        page_title="Análisis de Caldera",
        layout="centered",
        initial_sidebar_state="expanded"
    )
except st.errors.StreamlitAPIException as e:
    if "st.set_page_config() can only be called once per app" not in str(e):
        raise e

# --- MODELO (Lógica de cálculo) ---


@st.cache_data
def calcular_propiedades_caldera(
    P_proceso: float,
    T_in: float,
    T_out: float,
    V_out: float,
    D_val: float,
    unit_system: str
) -> Dict[str, Any]:
    """
    Calcula las propiedades termodinámicas en una caldera, manejando unidades SI e Inglesas.
    """
    # --- Factores de Conversión ---
    PSI_TO_MPA = 0.00689476
    MM_TO_M = 0.001
    IN_TO_M = 0.0254
    MS_TO_FTS = 3.28084
    M2_TO_FT2 = 10.7639
    KGS_TO_LBMS = 2.20462
    M3S_TO_FT3S = 35.3147
    M3KG_TO_FT3LBM = 16.0185

    # --- Definición de Unidades para UI ---
    units = {}
    if unit_system == 'Sistema Internacional (SI)':
        units = {
            "pressure": "MPa", "temperature": "°C", "velocity": "m/s",
            "diameter": "mm", "area": "m²", "mass_flow": "kg/s",
            "volume_flow": "m³/s", "spec_vol": "m³/kg"
        }
        # Conversión de entradas a SI (base para cálculos)
        P_in_MPa = P_out_MPa = P_proceso
        T_in_C = T_in
        T_out_C = T_out
        V_out_ms = V_out
        D_m = D_val * MM_TO_M
    else:  # Sistema Inglés (Imperial)
        units = {
            "pressure": "psi", "temperature": "°F", "velocity": "ft/s",
            "diameter": "in", "area": "ft²", "mass_flow": "lbm/s",
            "volume_flow": "ft³/s", "spec_vol": "ft³/lbm"
        }
        # Conversión de entradas a SI (base para cálculos)
        P_in_MPa = P_out_MPa = P_proceso * PSI_TO_MPA
        T_in_C = (T_in - 32) * 5/9
        T_out_C = (T_out - 32) * 5/9
        V_out_ms = V_out / MS_TO_FTS
        D_m = D_val * IN_TO_M

    try:
        # --- Cálculos Internos (siempre en SI) ---
        A_m2 = (math.pi * D_m**2) / 4
        T_in_K = T_in_C + 273.15
        T_out_K = T_out_C + 273.15

        # Estado de salida para obtener volumen específico
        estado_salida = IAPWS97(P=P_out_MPa, T=T_out_K)
        v_out_m3kg = estado_salida.v

        # Flujo másico
        m_dot_kgs = (A_m2 * V_out_ms) / v_out_m3kg

        # Estado de entrada
        estado_entrada = IAPWS97(P=P_in_MPa, T=T_in_K)
        v_in_m3kg = estado_entrada.v

        # Flujo volumétrico y velocidad de entrada
        V_dot_in_m3s = m_dot_kgs * v_in_m3kg
        V_in_ms = V_dot_in_m3s / A_m2

        # --- Conversión de Resultados a Unidades Seleccionadas ---
        if unit_system == 'Sistema Inglés (Imperial)':
            area_final = A_m2 * M2_TO_FT2
            v_in_final = v_in_m3kg * M3KG_TO_FT3LBM
            v_out_final = v_out_m3kg * M3KG_TO_FT3LBM
            m_dot_final = m_dot_kgs * KGS_TO_LBMS
            V_dot_in_final = V_dot_in_m3s * M3S_TO_FT3S
            V_in_final = V_in_ms * MS_TO_FTS
        else:
            area_final = A_m2
            v_in_final = v_in_m3kg
            v_out_final = v_out_m3kg
            m_dot_final = m_dot_kgs
            V_dot_in_final = V_dot_in_m3s
            V_in_final = V_in_ms

        return {
            "area": area_final,
            "v_especifico_entrada": v_in_final,
            "v_especifico_salida": v_out_final,
            "flujo_masico": m_dot_final,
            "flujo_volumetrico_entrada": V_dot_in_final,
            "velocidad_entrada": V_in_final,
            "units": units,
            "error": None
        }
    except Exception as e:
        return {"error": f"No se pudieron calcular las propiedades. Verifique los valores. Error: {e}"}


# =========================
# 🚀 Interfaz Streamlit
# =========================
col_img, col_title = st.columns([0.2, 1])
with col_img:
    st.image("https://raw.githubusercontent.com/Jmontoyaor/thermodynamics/main/IMAGENES/%C3%8Dcono%20de%20calderas%20minimalista%20y%20funcional.png", width=200)
with col_title:
    st.title("Caldera: Análisis Interactivo del Comportamiento Térmico")
st.markdown("#### Explora cómo varían la temperatura, la presión y la entalpía del fluido en una caldera de vapor.")
st.write("---")


# =========================
# 📘 Teoría
# =========================
with st.expander("Fundamentos Termodinámicos de Calderas (1ª Ley – Sistemas Abiertos)"):
    st.markdown(r"""
Las **calderas** son dispositivos termodinámicos diseñados para **transferir calor a un fluido**, generalmente agua, con el fin de **generar vapor** que se utilizará en procesos industriales o generación de energía.

Desde el punto de vista termodinámico, una caldera es un **sistema abierto en régimen estacionario**, ya que existe flujo de masa (agua/vapor) a través del volumen de control.

---

### Aplicación de la Primera Ley de la Termodinámica

Para un sistema abierto en estado estacionario, la **Primera Ley** se expresa como:

$$
\dot{Q} - \dot{W}_s = \dot{m} \left( h_{\text{salida}} - h_{\text{entrada}} + \frac{V_2^2 - V_1^2}{2} + g(z_2 - z_1) \right)
$$

Donde:
- $\dot{Q}$: Calor transferido al fluido [kW]
- $\dot{W}_s$: Trabajo de eje (en calderas típicamente $\dot{W}_s = 0$)
- $\dot{m}$: Flujo másico del fluido [kg/s]
- $h$: Entalpía específica [kJ/kg]
- $V$: Velocidad [m/s]
- $z$: Altura [m]
- $g$: Gravedad [9.81 m/s²]

---

### Simplificación para Calderas

En las calderas comunes:
- No hay trabajo de eje: $\dot{W}_s = 0$
- Cambios de energía cinética y potencial son despreciables:
  $\frac{V_2^2 - V_1^2}{2} \approx 0$, $g(z_2 - z_1) \approx 0$

Entonces, la ecuación se reduce a:

$$
\dot{Q} = \dot{m} (h_{\text{vapor}} - h_{\text{agua}})
$$

Esto implica que la **tasa de transferencia de calor** está directamente relacionada con el **salto entálpico** entre el estado inicial (agua líquida) y el estado final (vapor).

---

### Eficiencia térmica de la caldera

Aunque las calderas no producen trabajo mecánico directo, se puede definir una eficiencia basada en el uso del combustible:

$$
\eta = \frac{\dot{m} (h_{\text{vapor}} - h_{\text{agua}})}{\dot{m}_{\text{comb}} \cdot \text{PCI}}
$$

Donde:
- $\dot{m}_{\text{comb}}$: Flujo másico del combustible
- $\text{PCI}$: Poder calorífico inferior del combustible

---

### Conclusión

Las calderas son un claro ejemplo de aplicación de la **Primera Ley de la Termodinámica** en sistemas abiertos. Su análisis permite determinar el **calor requerido** para generar vapor a partir de agua líquida, esencial para el diseño y evaluación energética de ciclos térmicos como el de Rankine.

📚 **Fuente**: Adaptado de [termodinamica-1aa131.blogspot.com](https://termodinamica-1aa131.blogspot.com/2013/06/caldera.html)
""")

# =========================
# 🧪 Ejercicio y Figura
# =========================
col1, col2 = st.columns(2)
with col1:
    with st.expander("🧪 Ejercicio Propuesto – Caldera"):
        st.markdown("""
**Primera ley de la termodinámica – Sistemas Abiertos**

**CALDERA**

Entra **Agua** a los tubos de una Caldera de **120 mm de diámetro constante**, con una **Presión de 5 MPa** y una **Temperatura de 60°C**, y **Sale** a una **Temperatura de 450°C** y una **velocidad de 80 m/s**.

Determinar:

- a) El **flujo volumétrico** de entrada.
- b) La **velocidad del Agua** a la entrada de este dispositivo.
---

**Fuente:** *Ejercicio tomado y adaptado de **LaMejorAsesoríaEducativa – YouTube***.
""")
with col2:
    st.image("https://raw.githubusercontent.com/Jmontoyaor/thermodynamics/main/IMAGENES/Caldera.png",
             caption="**Comparación esquemática del funcionamiento interno de una caldera tipo locomotora.\\n\\nFuente: Adaptado de https://termodinamica-1aa131.blogspot.com/2013/06/caldera.html.")
    st.markdown("### Desarrollo visual")
    st.video("https://youtu.be/CuOPVWsVw5Q?si=VHYeOAiwX5XSV2kJ")
st.markdown("---")


# --- Barra Lateral con Controles de Entrada ---
st.sidebar.header("Parámetros de Entrada")
unit_system = st.sidebar.radio(
    "Seleccione el Sistema de Unidades",
    ('Sistema Internacional (SI)', 'Sistema Inglés (Imperial)')
)

# Entradas dinámicas
if unit_system == 'Sistema Internacional (SI)':
    p_in = st.sidebar.slider("Presión del Proceso [MPa]", 0.1, 25.0, 5.0, 0.1)
    t_in = st.sidebar.slider("Temp. Entrada [°C]", 10.0, 1300.0, 60.0, 1.0)
    t_out = st.sidebar.slider("Temp. Salida [°C]", 100.0, 1300.0, 450.0, 1.0)
    v_out = st.sidebar.slider("Velocidad Salida [m/s]", 1.0, 150.0, 80.0, 1.0)
    d_val = st.sidebar.slider("Diámetro Tubo [mm]", 10.0, 500.0, 120.0, 1.0)
else:  # Sistema Inglés
    p_in = st.sidebar.slider(
        "Presión del Proceso [psi]", 15.0, 3600.0, 725.0, 5.0)
    t_in = st.sidebar.slider("Temp. Entrada [°F]", 50.0, 660.0, 140.0, 5.0)
    t_out = st.sidebar.slider("Temp. Salida [°F]", 212.0, 1800.0, 842.0, 10.0)
    v_out = st.sidebar.slider(
        "Velocidad Salida [ft/s]", 3.0, 500.0, 262.0, 5.0)
    d_val = st.sidebar.slider("Diámetro Tubo [in]", 0.5, 20.0, 4.7, 0.1)

# --- Lógica Principal ---
p_out = p_in  # Se asume presión constante
resultados = calcular_propiedades_caldera(
    p_in, t_in, t_out, v_out, d_val, unit_system)

# --- Presentación de Resultados ---
if resultados.get("error"):
    st.error(f"**Error de Cálculo:** {resultados['error']}")
    st.warning(
        "Algunas combinaciones de presión y temperatura no son físicamente posibles. Intenta ajustar los valores.")
else:
    units = resultados['units']
    st.header("📊 Resultados del Análisis")
    st.markdown("---")

    st.subheader("🎯 Objetivos Principales")
    col_res1, col_res2, col_res3 = st.columns(3)

    with col_res1:
        st.markdown(f"""
        <div class='resultado-final'>
            <strong>Flujo Másico (ṁ):</strong><br>
            {resultados['flujo_masico']:.2f} {units['mass_flow']}
        </div>
        """, unsafe_allow_html=True)
    with col_res2:
        st.markdown(f"""
        <div class='resultado-final'>
            <strong>Velocidad de Entrada (V₁):</strong><br>
            {resultados['velocidad_entrada']:.2f} {units['velocity']}
        </div>
        """, unsafe_allow_html=True)
    with col_res3:
        st.markdown(f"""
        <div class='resultado-final'>
            <strong>Flujo Volumétrico Entrada (V̇):</strong><br>
            {resultados['flujo_volumetrico_entrada']:.4f} {units['volume_flow']}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📘 Propiedades Calculadas")
    info_col1, info_col2, info_col3 = st.columns(3)

    with info_col1:
        st.markdown(f"""
        <div class='resultado-final'>
            <strong>Área del Tubo (A):</strong><br>
            {resultados['area']:.5f} {units['area']}
        </div>
        """, unsafe_allow_html=True)
    with info_col2:
        st.markdown(f"""
        <div class='resultado-final'>
            <strong>Vol. Específico Entrada (v₁):</strong><br>
            {resultados['v_especifico_entrada']:.6f} {units['spec_vol']}
        </div>
        """, unsafe_allow_html=True)
    with info_col3:
        st.markdown(f"""
        <div class='resultado-final'>
            <strong>Vol. Específico Salida (v₂):</strong><br>
            {resultados['v_especifico_salida']:.5f} {units['spec_vol']}
        </div>
        """, unsafe_allow_html=True)


st.markdown("""
<div class='nota-info'>
<b>Nota sobre la precisión:</b> Este script utiliza el estándar internacional IAPWS-IF97 para obtener las propiedades termodinámicas del agua y el vapor, lo que garantiza una alta precisión en los cálculos.
</div>
""", unsafe_allow_html=True)


st.markdown("---")
st.caption("Developed by Juan Fernando Montoya Ortiz -Electrical Engineering Student -Universidad Nacional de Colombia")
