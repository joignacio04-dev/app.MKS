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
