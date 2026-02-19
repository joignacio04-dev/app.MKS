import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Simulador Macro I - Keynes", layout="wide")

# --- ESTADO DE LA SESIÓN (Para la estática comparativa) ---
# Inicializamos variables en memoria para "recordar" el estado inicial
if 'base_A' not in st.session_state:
    st.session_state.base_A = None
    st.session_state.base_Y = None
    st.session_state.base_k = None
    st.session_state.base_DA_vals = None

st.title("📊 Simulador del Modelo Keynesiano Simple")
st.markdown("""
Este modelo interactivo permite analizar cómo afectan las distintas variables de la **Demanda Agregada** al nivel de **Ingreso de Equilibrio ($Y$)** bajo un esquema de impuestos proporcionales.
""")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Parámetros del Modelo")

c1 = st.sidebar.slider("Propensión Mg a Consumir (c)", 0.1, 0.99, 0.80, 0.01)
t = st.sidebar.slider("Tasa Impositiva (t)", 0.0, 0.5, 0.20, 0.01)
G = st.sidebar.number_input("Gasto Público (G)", 0, 2000, 500, 50)
I = st.sidebar.number_input("Inversión Autónoma (I)", 0, 2000, 400, 50)
TR = st.sidebar.number_input("Transferencias (TR)", 0, 1000, 100, 50)
T0 = st.sidebar.number_input("Impuestos Fijos (T0)", 0, 1000, 100, 50)
c0 = st.sidebar.number_input("Consumo Autónomo (c0)", 0, 1000, 200, 50)

# --- LÓGICA DEL MODELO (FUNCIONES) ---
def calcular_A(c0, c1, I, G, T0, TR):
    # Calcula el Gasto Autónomo total (Ordenada al origen)
    return c0 + I + G + (c1 * TR) - (c1 * T0)

def calcular_DA(Y, c0, c1, I, G, T0, t, TR):
    Yd = Y - (T0 + t * Y) + TR
    C = c0 + c1 * Yd
    return C + I + G

def calcular_equilibrio(A, c1, t):
    pendiente = c1 * (1 - t)
    if pendiente >= 1:
        return None, None 
    
    k = 1 / (1 - pendiente) # Multiplicador
    Y_eq = A * k
    return Y_eq, k

# --- CÁLCULOS ACTUALES ---
Y_max = 6000
Y_vals = np.linspace(0, Y_max, 100)

A_actual = calcular_A(c0, c1, I, G, T0, TR)
DA_vals_actual = calcular_DA(Y_vals, c0, c1, I, G, T0, t, TR)
Y_actual, k_actual = calcular_equilibrio(A_actual, c1, t)

# --- BOTÓN PARA GUARDAR ESCENARIO BASE ---
st.sidebar.markdown("---")
st.sidebar.markdown("Para ver el efecto de un cambio, primero guarda el escenario actual y luego mueve un parámetro.")
if st.sidebar.button("📌 Fijar Escenario Base"):
    st.session_state.base_A = A_actual
    st.session_state.base_Y = Y_actual
    st.session_state.base_k = k_actual
    st.session_state.base_DA_vals = DA_vals_actual

# --- VISUALIZACIÓN ---

# Cálculos de variaciones (Deltas) si hay un escenario base
delta_Y = Y_actual - st.session_state.base_Y if st.session_state.base_Y else None
delta_A = A_actual - st.session_state.base_A if st.session_state.base_A else None

col1, col2, col3 = st.columns(3)
# Cambio 2: Reemplazar G por A en las métricas y agregar las variaciones
col1.metric("Ingreso de Equilibrio (Y)", f"${Y_actual:,.2f}" if Y_actual else "Indefinido", delta=f"{delta_Y:,.2f}" if delta_Y else None)
col2.metric("Multiplicador (k)", f"{k_actual:.2f}" if k_actual else "∞")
col3.metric("Gasto Autónomo (A)", f"${A_actual:,.2f}", delta=f"{delta_A:,.2f}" if delta_A else None)

# Gráfico
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(Y_vals, Y_vals, 'k--', linewidth=1, alpha=0.5, label='Oferta Agregada (45°)')

# Curva Base y Desequilibrio (Sugerencia 2 de la profe)
if st.session_state.base_A is not None:
    # Dibujar DA original
    ax.plot(Y_vals, st.session_state.base_DA_vals, color='gray', linestyle='dashed', linewidth=2, label='DA Inicial')
    
    # Marcar el desequilibrio en el Y base
    Y_base = st.session_state.base_Y
    DA_en_Y_base = calcular_DA(Y_base, c0, c1, I, G, T0, t, TR)
    
    if Y_base != Y_actual: # Solo graficar si hubo un desplazamiento real
        # Línea vertical mostrando la variación de existencias no planeadas
        ax.vlines(Y_base, Y_base, DA_en_Y_base, colors='red', linestyles='solid', linewidth=2.5, label='Var. Existencias No Planeadas')

# Curva DA Actual
ax.plot(Y_vals, DA_vals_actual, 'b-', linewidth=2, label='Demanda Agregada (DA)')

# Sugerencia 1: Marcar la ordenada al origen (A)
ax.plot(0, A_actual, 'go', zorder=10)
ax.text(100, A_actual + 100, f'A = {A_actual:.0f}', color='green', fontweight='bold')

# Punto de equilibrio
if Y_actual and 0 <= Y_actual <= Y_max:
    ax.plot([Y_actual], [Y_actual], 'ro', zorder=10, markersize=8)
    ax.vlines(Y_actual, 0, Y_actual, colors='r', linestyles='dotted', alpha=0.5)
    # Sugerencia 1: Cambiar 'Ye' por 'Y'
    ax.text(Y_actual + 100, 100, 'Y', color='red', fontweight='bold')

ax.set_title('Cruz Keynesiana con Impuestos Proporcionales')
ax.set_xlabel('Renta / Producción (Y)')
ax.set_ylabel('Demanda Agregada (DA)')
ax.set_xlim(0, Y_max)
ax.set_ylim(0, Y_max)
ax.legend()
ax.grid(True, alpha=0.3)

st.pyplot(fig)

# --- EXPLICACIÓN TEÓRICA ---
st.markdown("---")
st.subheader("📝 Fórmulas utilizadas")
# Cambio 1: Ecuación exacta de equilibrio
st.latex(r'''
Y = k \cdot A
''')
# Cambio 1: Modificar la conclusión para hablar de A y no de G
st.info(f"""
**Análisis actual:**
El Gasto Autónomo total ($A$) es de **${A_actual:.2f} y el multiplicador ($k$) es {k_actual:.2f}. 
Por cada $1 de variación del Gasto Autónomo ($A$), el Ingreso ($Y$) varía en **${k_actual:.2f}**.

(Es decir, $\Delta Y = k \cdot \Delta A$)
""")


