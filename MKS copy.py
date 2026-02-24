import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador Macro I", layout="wide")
st.title("📊 Simuladores Macroeconómicos")

# Creamos las pestañas
tab1, tab2 = st.tabs(["Mercado de Bienes (Cruz Keynesiana)", "Mercado de Dinero (Liquidez)"])

# ==========================================
# PESTAÑA 1: MERCADO DE BIENES (Tu código actual)
# ==========================================
with tab1:
    st.header("Cruz Keynesiana con Sector Externo")
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Simulador Macro I - Keynes", layout="wide")

# --- ESTADO DE LA SESIÓN (Para la estática comparativa) ---
if 'base_A' not in st.session_state:
    st.session_state.base_A = None
    st.session_state.base_Y = None
    st.session_state.base_k = None
    st.session_state.base_Z_vals = None

st.title("📊 Simulador del Modelo Keynesiano Simple (Economía Abierta)")
st.markdown("""
Este modelo interactivo permite analizar cómo afectan las distintas variables de la **Demanda Agregada (Z)** al nivel de **Ingreso de Equilibrio ($Y$)** bajo un esquema de impuestos proporcionales y **sector externo exógeno**.
""")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Parámetros del Modelo")

st.sidebar.subheader("Sector Privado y Público")
c1 = st.sidebar.slider("Propensión Mg a Consumir (c)", 0.1, 0.99, 0.80, 0.01)
t = st.sidebar.slider("Tasa Impositiva (t)", 0.0, 0.5, 0.20, 0.01)
G = st.sidebar.number_input("Gasto Público (G)", 0, 2000, 500, 50)
I = st.sidebar.number_input("Inversión Autónoma (I)", 0, 2000, 400, 50)
TR = st.sidebar.number_input("Transferencias (TR)", 0, 1000, 100, 50)
T0 = st.sidebar.number_input("Impuestos Fijos (T0)", 0, 1000, 100, 50)
c0 = st.sidebar.number_input("Consumo Autónomo (c0)", 0, 1000, 200, 50)

st.sidebar.subheader("Sector Externo")
X = st.sidebar.number_input("Exportaciones (X)", 0, 2000, 200, 50)
# Cambiamos la propensión 'm' por un valor fijo 'M'
M = st.sidebar.number_input("Importaciones Autónomas (M)", 0, 2000, 100, 50)

# --- LÓGICA DEL MODELO (FUNCIONES) ---
def calcular_A(c0, c1, I, G, T0, TR, X, M):
    # El Gasto Autónomo ahora suma X y resta M directamente
    return c0 + I + G + X - M + (c1 * TR) - (c1 * T0)

def calcular_Z(Y, c0, c1, I, G, T0, t, TR, X, M): 
    Yd = Y - (T0 + t * Y) + TR
    C = c0 + c1 * Yd
    # Las importaciones ya no dependen de Y, simplemente se restan al final
    return C + I + G + X - M

def calcular_equilibrio(A, c1, t):
    # La pendiente vuelve a ser la original (sin 'm')
    pendiente = c1 * (1 - t)
    
    if pendiente >= 1:
        return None, None 
    
    k = 1 / (1 - pendiente) # Multiplicador original
    Y_eq = A * k
    return Y_eq, k

# --- CÁLCULOS ACTUALES ---
Y_max = 6000
Y_vals = np.linspace(0, Y_max, 100)

A_actual = calcular_A(c0, c1, I, G, T0, TR, X, M)
Z_vals_actual = calcular_Z(Y_vals, c0, c1, I, G, T0, t, TR, X, M) 
Y_actual, k_actual = calcular_equilibrio(A_actual, c1, t)

# --- BOTÓN PARA GUARDAR ESCENARIO BASE ---
st.sidebar.markdown("---")
st.sidebar.markdown("Para ver el efecto de un desplazamiento, guarda el escenario actual y luego mueve un parámetro.")
if st.sidebar.button("📌 Fijar Escenario Base"):
    st.session_state.base_A = A_actual
    st.session_state.base_Y = Y_actual
    st.session_state.base_k = k_actual
    st.session_state.base_Z_vals = Z_vals_actual

# --- VISUALIZACIÓN ---

delta_Y = Y_actual - st.session_state.base_Y if st.session_state.base_Y else None
delta_A = A_actual - st.session_state.base_A if st.session_state.base_A else None

col1, col2, col3 = st.columns(3)
col1.metric("Ingreso de Equilibrio (Y)", f"${Y_actual:,.2f}" if Y_actual else "Indefinido", delta=f"{delta_Y:,.2f}" if delta_Y else None)
col2.metric("Multiplicador (k)", f"{k_actual:.2f}" if k_actual else "∞")
col3.metric("Gasto Autónomo (A)", f"${A_actual:,.2f}", delta=f"{delta_A:,.2f}" if delta_A else None)

# Gráfico
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(Y_vals, Y_vals, 'k--', linewidth=1, alpha=0.5, label='Oferta Agregada (45°)')

# Curva Base y Desequilibrio
if st.session_state.base_A is not None:
    ax.plot(Y_vals, st.session_state.base_Z_vals, color='gray', linestyle='dashed', linewidth=2, label='Z Inicial')
    
    Y_base = st.session_state.base_Y
    Z_en_Y_base = calcular_Z(Y_base, c0, c1, I, G, T0, t, TR, X, M)
    
    if Y_base != Y_actual: 
        ax.vlines(Y_base, Y_base, Z_en_Y_base, colors='red', linestyles='solid', linewidth=2.5, label='Var. Existencias No Planeadas')

# Curva Z Actual
ax.plot(Y_vals, Z_vals_actual, 'b-', linewidth=2, label='Demanda Agregada (Z)')

ax.plot(0, A_actual, 'go', zorder=10)
ax.text(100, A_actual + 100, f'A = {A_actual:.0f}', color='green', fontweight='bold')

if Y_actual and 0 <= Y_actual <= Y_max:
    ax.plot([Y_actual], [Y_actual], 'ro', zorder=10, markersize=8)
    ax.vlines(Y_actual, 0, Y_actual, colors='r', linestyles='dotted', alpha=0.5)
    ax.text(Y_actual + 100, 100, 'Y', color='red', fontweight='bold')

ax.set_title('Cruz Keynesiana con Impuestos y Sector Externo (M exógeno)')
ax.set_xlabel('Renta / Producción (Y)')
ax.set_ylabel('Demanda Agregada (Z)')
ax.set_xlim(0, Y_max)
ax.set_ylim(0, Y_max)
ax.legend()
ax.grid(True, alpha=0.3)

st.pyplot(fig)

# --- EXPLICACIÓN TEÓRICA ---
st.markdown("---")
st.subheader("📝 Fórmulas utilizadas")

# Fórmula completa actualizada con M exógeno
st.latex(r'''
Y = \overbrace{\frac{1}{1 - c(1-t)}}^{k} \cdot \overbrace{[c_0 + I + G + X - M + c \cdot TR - c \cdot T_0]}^{A}
''')

st.info(f"""
**Análisis actual:**
El Gasto Autónomo total ($A$) es de **${A_actual:.2f}** y el multiplicador ($k$) es **{k_actual:.2f}**. 
Por cada **$1** de variación del Gasto Autónomo ($A$), el Ingreso ($Y$) varía en **${k_actual:.2f}**.

(Es decir, $\Delta Y = \\frac{{1}}{{1 - c(1-t)}} \cdot \Delta [c_0 + I + G + X - M + c \cdot TR - c \cdot T_0]$)
""")


# ==========================================
# PESTAÑA 2: MERCADO DE DINERO (Nuevo)
# ==========================================
with tab2:
    st.header("Equilibrio en el Mercado Monetario")
    st.markdown("Analiza cómo se determina la tasa de interés de equilibrio ($i$) mediante la interacción entre la Oferta Monetaria del Banco Central y la Preferencia por la Liquidez.")
    
    # Estado de la sesión para Mercado de Dinero
    if 'base_Ms' not in st.session_state:
        st.session_state.base_Ms = None
        st.session_state.base_i = None
        st.session_state.base_Md_vals = None

    # Controles laterales específicos para esta pestaña
    col_ctrl_1, col_ctrl_2 = st.columns(2)
    with col_ctrl_1:
        st.subheader("Política Monetaria")
        Ms = st.slider("Oferta Monetaria Real (M/P)", 100, 2000, 800, 50)
    with col_ctrl_2:
        st.subheader("Demanda de Dinero")
        Y_din = st.slider("Nivel de Ingreso (Y)", 1000, 5000, 2000, 100)
        k_y = st.slider("Sensibilidad al Ingreso (k_Y)", 0.1, 1.0, 0.5, 0.05)
        h = st.slider("Sensibilidad a la Tasa (h)", 10, 200, 50, 10)

    # Cálculos
    def calcular_i_eq(Ms, Y, k_y, h):
        i = (k_y * Y - Ms) / h
        return i if i > 0 else 0 # La tasa no puede ser negativa en este modelo básico

    M_vals = np.linspace(50, 2500, 100)
    # Demanda de dinero inversa para graficar: i = (k_y*Y - M) / h
    Md_vals_actual = (k_y * Y_din - M_vals) / h
    i_actual = calcular_i_eq(Ms, Y_din, k_y, h)

    # Botón de escenario base
    if st.button("📌 Fijar Escenario Base (Mercado Monetario)"):
        st.session_state.base_Ms = Ms
        st.session_state.base_i = i_actual
        st.session_state.base_Md_vals = Md_vals_actual

    # Métricas
    delta_i = i_actual - st.session_state.base_i if st.session_state.base_i is not None else None
    
    st.metric("Tasa de Interés de Equilibrio (i*)", f"{i_actual:.2f}%", delta=f"{delta_i:.2f}%" if delta_i is not None else None)

    # Gráfico
    fig2, ax2 = plt.subplots(figsize=(10, 6))

    # Curva Base
    if st.session_state.base_Ms is not None:
        ax2.plot(M_vals, st.session_state.base_Md_vals, color='gray', linestyle='dashed', linewidth=2, label='Demanda (L) Inicial')
        ax2.vlines(st.session_state.base_Ms, 0, max(Md_vals_actual.max(), 20), colors='gray', linestyles='dashed', linewidth=2, label='Oferta (M/P) Inicial')
        
        # Desequilibrio (Exceso de oferta o demanda de dinero)
        if st.session_state.base_i != i_actual:
            ax2.hlines(st.session_state.base_i, min(Ms, st.session_state.base_Ms), max(Ms, st.session_state.base_Ms), colors='red', linewidth=2.5, label='Desequilibrio Monetario')

    # Curvas Actuales
    ax2.plot(M_vals, Md_vals_actual, 'b-', linewidth=2, label='Demanda de Dinero (L)')
    ax2.vlines(Ms, 0, max(Md_vals_actual.max(), 20), colors='green', linewidth=2.5, label='Oferta Monetaria (M/P)')

    # Punto de Equilibrio
    ax2.plot([Ms], [i_actual], 'ro', zorder=10, markersize=8)
    ax2.hlines(i_actual, 0, Ms, colors='r', linestyles='dotted', alpha=0.5)

    ax2.set_title('Mercado de Dinero (Preferencia por la Liquidez)')
    ax2.set_xlabel('Cantidad de Dinero Real (M/P)')
    ax2.set_ylabel('Tasa de Interés (i %)')
    ax2.set_xlim(0, 2500)
    ax2.set_ylim(0, max(Md_vals_actual.max() + 5, 20))
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    st.pyplot(fig2)

    # Explicación Teórica
    st.markdown("---")
    st.subheader("📝 Fórmulas utilizadas")
    st.latex(r'''
    i^* = \frac{k_Y \cdot Y}{h} - \frac{M^s/P}{h}
    ''')

