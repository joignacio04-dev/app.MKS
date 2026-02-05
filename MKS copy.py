import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Simulador Macro I - Keynes", layout="wide")

st.title("📊 Simulador del Modelo Keynesiano Simple")
st.markdown("""
Este modelo interactivo permite analizar cómo afectan las distintas variables de la **Demanda Agregada** al nivel de **Ingreso de Equilibrio ($Y_e$)** bajo un esquema de **impuestos proporcionales**.
""")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Parámetros del Modelo")

# Definimos los sliders en la barra lateral
c1 = st.sidebar.slider("Propensión Mg a Consumir (c)", 0.1, 0.99, 0.80, 0.01)
t = st.sidebar.slider("Tasa Impositiva (t)", 0.0, 0.5, 0.20, 0.01)
G = st.sidebar.number_input("Gasto Público (G)", 0, 2000, 500, 50)
I = st.sidebar.number_input("Inversión Autónoma (I)", 0, 2000, 400, 50)
TR = st.sidebar.number_input("Transferencias (TR)", 0, 1000, 100, 50)
T0 = st.sidebar.number_input("Impuestos Fijos (T0)", 0, 1000, 100, 50)
c0 = st.sidebar.number_input("Consumo Autónomo (c0)", 0, 1000, 200, 50)

# --- LÓGICA DEL MODELO (FUNCIONES) ---
def calcular_DA(Y, c0, c1, I, G, T0, t, TR):
    Yd = Y - (T0 + t * Y) + TR
    C = c0 + c1 * Yd
    return C + I + G

def calcular_equilibrio(c0, c1, I, G, T0, t, TR):
    # Componentes autónomos (Ordenada al origen)
    A = c0 + I + G + (c1 * TR) - (c1 * T0)
    # Pendiente de la curva DA
    pendiente = c1 * (1 - t)
    
    if pendiente >= 1:
        return None, None # Evitar explosión del modelo
    
    k = 1 / (1 - pendiente) # Multiplicador
    Ye = A * k
    return Ye, k

# --- CÁLCULOS ---
Y_max = 6000
Y_vals = np.linspace(0, Y_max, 100)

DA_vals = calcular_DA(Y_vals, c0, c1, I, G, T0, t, TR)
Ye, k = calcular_equilibrio(c0, c1, I, G, T0, t, TR)

# --- VISUALIZACIÓN ---

# Columnas para métricas clave
col1, col2, col3 = st.columns(3)
col1.metric("Ingreso de Equilibrio (Ye)", f"${Ye:,.2f}" if Ye else "Indefinido")
col2.metric("Multiplicador (k)", f"{k:.2f}" if k else "∞")
col3.metric("Gasto Público (G)", f"${G}")

# Gráfico
fig, ax = plt.subplots(figsize=(10, 6))

# Línea de 45 grados
ax.plot(Y_vals, Y_vals, 'k--', linewidth=1, alpha=0.5, label='Oferta Agregada (45°)')

# Curva DA
ax.plot(Y_vals, DA_vals, 'b-', linewidth=2, label='Demanda Agregada (DA)')

# Punto de equilibrio
if Ye and 0 <= Ye <= Y_max:
    ax.plot([Ye], [Ye], 'ro', zorder=10, markersize=10)
    ax.vlines(Ye, 0, Ye, colors='r', linestyles='dotted', alpha=0.5)
    ax.text(Ye + 100, 100, f'Ye', color='red', fontweight='bold')

ax.set_title('Cruz Keynesiana con Impuestos Proporcionales')
ax.set_xlabel('Renta / Producción (Y)')
ax.set_ylabel('Demanda Agregada (DA)')
ax.set_xlim(0, Y_max)
ax.set_ylim(0, Y_max)
ax.legend()
ax.grid(True, alpha=0.3)

# Mostrar gráfico en Streamlit
st.pyplot(fig)

# --- EXPLICACIÓN TEÓRICA ---
st.markdown("---")
st.subheader("📝 Fórmulas utilizadas")
st.latex(r'''
Y_e = \frac{1}{1 - c(1-t)} \cdot [C_0 - cT_0 + cTr + I + G]
''')
st.info(f"""
**Análisis actual:**
Con una propensión a consumir de **{c1}** y una tasa impositiva del **{t*100}%**, 
por cada $1 peso que aumenta el Gasto Público, la economía crece **${k:.2f}** pesos.
""")
