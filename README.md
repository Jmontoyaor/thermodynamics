# ♨️ Simulador Interactivo de Dispositivos Termodinámicos

> _"Entendiendo la termodinámica, un dispositivo a la vez."_
> _Este repositorio contiene una suite de aplicaciones web interactivas para analizar los principios de la Primera Ley de la Termodinámica en sistemas abiertos._

---

## 🧠 Sobre este Proyecto

Este proyecto es una colección de simuladores interactivos desarrollados en Python con Streamlit, diseñados para servir como una herramienta de aprendizaje visual para estudiantes de ingeniería de la **Universidad Nacional de Colombia**.

Cada aplicación se centra en un dispositivo termodinámico específico, permitiendo a los usuarios modificar parámetros clave y observar los resultados en tiempo real, conectando la teoría de los libros de texto con la aplicación práctica.

---

## 🚀 Aplicaciones Incluidas

Este repositorio contiene un único notebook de Jupyter (`Aplicaciones_Termodinamicas3.ipynb`) que despliega una aplicación Streamlit con múltiples páginas. Cada página es un simulador para un dispositivo diferente:

1.  **💧 Bomba:** Analiza el trabajo requerido para incrementar la presión de un líquido.
2.  **🔥 Caldera:** Explora la transferencia de calor para generar vapor a partir de agua.
3.  **⚙️ Turbina:** Calcula la potencia generada por la expansión de vapor.
4.  **💨 Compresor:** Determina la potencia necesaria para comprimir aire (tratado como gas ideal).
5.  **✈️ Tobera:** Analiza la conversión de entalpía en energía cinética para acelerar un fluido.
6.  **❄️ Condensador:** Calcula el flujo de un refrigerante necesario para condensar vapor.

---

## ✨ Características Principales

-   **Interfaz Interactiva:** Utiliza deslizadores y controles para modificar las condiciones de entrada y ver cómo afectan los resultados al instante.
-   **Sistema Dual de Unidades:** Todos los cálculos se pueden realizar tanto en el **Sistema Internacional (SI)** como en el **Sistema Inglés (Imperial)**, con conversiones automáticas.
-   **Fundamento Teórico Integrado:** Cada módulo incluye extractos teóricos relevantes (basados en el libro de texto de Çengel) para contextualizar los cálculos.
-   **Ejercicios y Videos Guía:** Cada aplicación presenta un ejercicio propuesto y un video explicativo que muestra la resolución paso a paso.
-   **Cálculos Precisos:** Utiliza la librería **IAPWS-IF97** para obtener propiedades termodinámicas del agua y vapor con alta precisión.

---

## 🛠️ Stack Tecnológico

-   **Lenguaje:** Python
-   **Framework Web:** Streamlit
-   **Librerías Científicas:** `iapws` (propiedades del agua/vapor), `numpy`.
-   **Entorno de Desarrollo:** Jupyter Notebook / Google Colab

---

## 📂 Estructura del Proyecto

El proyecto está consolidado en un único archivo principal que contiene el código para todas las aplicaciones:

```bash
📁 thermodynamics/
└── 🚀 Aplicaciones_Termodinamicas3.ipynb  # Notebook con el código de la app Streamlit
```

---

## ▶️ ¿Cómo ejecutarlo?

1.  **Clona el repositorio:**
    ```bash
    git clone [https://github.com/Jmontoyaor/thermodynamics.git](https://github.com/Jmontoyaor/thermodynamics.git)
    cd thermodynamics
    ```

2.  **Instala las dependencias:**
    ```bash
    pip install streamlit iapws numpy
    ```

3.  **Ejecuta la aplicación Streamlit:**
    (Nota: Primero necesitarás convertir el notebook `.ipynb` a un script `.py` o copiar el código a un archivo `app.py`)
    ```bash
    streamlit run app.py
    
