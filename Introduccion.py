# streamlit_app.py
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title=" Aplicaciones Termodinámicas",
    page_icon="📊",
    layout="wide"
)

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
    }

    .nota-info {
        color: #98FB98;
    }


    /* Estilo para el texto de la nota */
    .nota-info {
        color: #98FB98; /* Color Verde Pálido para las letras */
    }


</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.title("Simulaciones Interactivas de Termodinámica: Un Laboratorio Virtual")

st.markdown("""
¡Hola! Te doy la bienvenida a este conjunto de herramientas educativas diseñadas para ayudarte a comprender los principios de la termodinámica de una manera práctica y visual.

Cada aplicación te permite analizar un dispositivo termodinámico clave, no solo resolviendo los cálculos, sino también entendiendo el *porqué* de cada resultado.
""")

st.write("---")

# --- Features Section ---
st.header("¿Qué encontrarás en cada simulador?")

st.markdown("""
-  **Interactividad Total:** Modifica los parámetros de entrada como presión, temperatura o flujo y observa cómo los resultados cambian en tiempo real.

-  **Análisis Bilingüe de Unidades:** Realiza todos los cálculos tanto en el **Sistema Internacional (SI)** como en el **Sistema Inglés (Imperial)** con solo un clic.

-  **Soporte Teórico Completo:** Cada módulo incluye una sección con los **fundamentos teóricos** extraídos de la bibliografía de referencia para que puedas conectar la práctica con la teoría.

-  **Recursos Visuales y Ejercicios Guiados:** Aprende con un **ejercicio propuesto** y un **video explicativo** que muestra el desarrollo paso a paso.
""")

st.write("---")


# --- Call to Action ---
st.header("¿Cómo empezar?")
st.markdown(
    "** ¡Es muy fácil! Simplemente selecciona una de las aplicaciones del menú lateral** para comenzar a explorar un dispositivo."
)


st.markdown("---")
st.header(" Fundamento Visual: Primera Ley en Sistemas Abiertos")
st.markdown("""
Este video de **LaMejorAsesoríaEducativa** te ayudará a entender de forma clara y visual
los conceptos clave de la **Primera Ley de la Termodinámica aplicada a sistemas abiertos**, incluyendo energía interna, flujo de trabajo y calor.

🔗 Fuente: [LaMejorAsesoríaEducativa - YouTube](https://www.youtube.com/@LaMejorAsesoriaEducativa)
""")

st.video("https://www.youtube.com/watch?v=zEuVc5RKu9Y")


st.markdown("---")
st.caption("Developed by Juan Fernando Montoya Ortiz -Electrical Engineering Student -Universidad Nacional de Colombia")
