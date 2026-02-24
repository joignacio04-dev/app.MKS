import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Simulador Macro I", layout="wide")

# --- ESTADOS DE LA SESIÓN
# Tab 1
if 'base_A' not in st.session_state:
    st.session_state.base_A = None
    st.session_state.base_Y = None
    st.session_state.base_k = None
    st.session_state.base_Z_vals = None
# Tab 2
if 'base_Ms' not in st.session_state:
    st.session_state.base_Ms = None
    st.session_state.base_i = None
    st.session_state.base_Md_vals = None
# Tab 3
if 'base_Y_islm' not in st.session_state:
    st.session_state.base_Y_islm = None
    st.session_state.base_i_islm = None
    st.session_state.base_IS_vals = None
    st.session_state.base_LM_vals = None

# --- TÍTULO PRINCIPAL ---
st.title("📊 Simuladores Macroeconómicos")
st.markdown("Modelo completo interactivo: Mercado de Bienes, Mercado Monetario y Equilibrio General (IS-LM).")

# ==========================================
# BARRA LATERAL UNIFICADA (PANEL DE CONTROL)
st.sidebar.header("⚙️ Panel de Control Global")

# -- SECCIÓN 1: Mercado de Bienes
st.sidebar.markdown("---")
st.sidebar.subheader("📦 Mercado de Bienes")
st.sidebar.caption("Afecta: Cruz Keynesiana (Tab 1) y Curva IS (Tab 3)")

c1 = st.sidebar.slider("Propensión Mg a Consumir (c)", 0.1, 0.99, 0.80, 0.01)
t = st.sidebar.slider("Tasa Impositiva (t)", 0.0, 0.5, 0.20, 0.01)
c0 = st.sidebar.number_input("Consumo Autónomo (c0)", 0, 1000, 200, 50)
I_aut = st.sidebar.number_input("Inversión Autónoma (I_0)", 0, 2000, 400, 50)
G = st.sidebar.number_input("Gasto Público (G)", 0, 2000, 500, 50)
TR = st.sidebar.number_input("Transferencias (TR)", 0, 1000, 100, 50)
T0 = st.sidebar.number_input("Impuestos Fijos (T0)", 0, 1000, 100, 50)

# Sector Externo
st.sidebar.markdown("**Sector Externo**")
X = st.sidebar.number_input("Exportaciones (X)", 0, 2000, 200, 50)
M = st.sidebar.number_input("Importaciones (M)", 0, 2000, 100, 50)

# -- SECCIÓN 2: Interacción IS-LM
st.sidebar.markdown("---")
st.sidebar.subheader(" Vinculación Bienes-Dinero")
st.sidebar.caption("Afecta: Solo Curva IS (Tab 3)")
b = st.sidebar.slider("Sensibilidad de Inversión a tasa (b)", 10, 500, 100, 10)

# -- SECCIÓN 3: Mercado de Dinero
st.sidebar.markdown("---")
st.sidebar.subheader("Mercado Monetario💵")
st.sidebar.caption("Afecta: Mercado de Dinero (Tab 2) y Curva LM (Tab 3)")

Ms = st.sidebar.slider("Oferta Monetaria Real (M/P)", 100, 2000, 800, 50)
k_y = st.sidebar.slider("Sensibilidad L al Ingreso (k_Y)", 0.1, 1.0, 0.5, 0.05)
h = st.sidebar.slider("Sensibilidad L a la Tasa (h)", 10, 200, 50, 10)

# Ingreso Exógeno 
st.sidebar.markdown("**Variable Exógena (Solo Tab 2)**")
Y_din = st.sidebar.slider("Nivel de Ingreso Exógeno (Y)", 1000, 5000, 2000, 100)


# CREACIÓN DE PESTAÑAS (TABS)
# ==========================================
tab1, tab2, tab3 = st.tabs(["Mercado de Bienes (Keynes)", "Mercado de Dinero (Liquidez)", "Modelo IS-LM (Eq. General)"])


# PESTAÑA 1: MERCADO DE BIENES
# ==========================================
with tab1:
    st.header("Cruz Keynesiana con Sector Externo Exógeno")
    
    # Lógica Matemática Tab 1
    def calcular_A_tab1(c0, c1, I, G, T0, TR, X, M):
        return c0 + I + G + X - M + (c1 * TR) - (c1 * T0)

    def calcular_Z_tab1(Y, c0, c1, I, G, T0, t, TR, X, M): 
        Yd = Y - (T0 + t * Y) + TR
        C = c0 + c1 * Yd
        return C + I + G + X - M

    def calcular_equilibrio_tab1(A, c1, t):
        pendiente = c1 * (1 - t)
        if pendiente >= 1: return None, None 
        k = 1 / (1 - pendiente)
        Y_eq = A * k
        return Y_eq, k

    Y_max = 6000
    Y_vals = np.linspace(0, Y_max, 100)
    A_actual = calcular_A_tab1(c0, c1, I_aut, G, T0, TR, X, M)
    Z_vals_actual = np.maximum(0, calcular_Z_tab1(Y_vals, c0, c1, I_aut, G, T0, t, TR, X, M))
    Y_actual, k_actual = calcular_equilibrio_tab1(A_actual, c1, t)

    # Botón Base
    if st.button("📌 Fijar Escenario Base (Bienes)", key="btn_bienes"):
        st.session_state.base_A = A_actual
        st.session_state.base_Y = Y_actual
        st.session_state.base_k = k_actual
        st.session_state.base_Z_vals = Z_vals_actual

    # Métricas
    delta_Y = Y_actual - st.session_state.base_Y if st.session_state.base_Y else None
    delta_A = A_actual - st.session_state.base_A if st.session_state.base_A else None
    col1_1, col1_2, col1_3 = st.columns(3)
    col1_1.metric("Ingreso de Equilibrio (Y)", f"${Y_actual:,.2f}" if Y_actual else "Indefinido", delta=f"{delta_Y:,.2f}" if delta_Y else None)
    col1_2.metric("Multiplicador (k)", f"{k_actual:.2f}" if k_actual else "∞")
    col1_3.metric("Gasto Autónomo (A)", f"${A_actual:,.2f}", delta=f"{delta_A:,.2f}" if delta_A else None)

    # Gráfico Tab 1
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(Y_vals, Y_vals, 'k--', linewidth=1, alpha=0.5, label='Oferta Agregada (45°)')

    if st.session_state.base_A is not None:
        ax1.plot(Y_vals, st.session_state.base_Z_vals, color='gray', linestyle='dashed', linewidth=2, label='Z Inicial')
        Y_base = st.session_state.base_Y
        Z_en_Y_base = calcular_Z_tab1(Y_base, c0, c1, I_aut, G, T0, t, TR, X, M)
        if Y_base != Y_actual: 
            ax1.vlines(Y_base, Y_base, Z_en_Y_base, colors='red', linestyles='solid', linewidth=2.5, label='Var. Existencias No Planeadas')

    ax1.plot(Y_vals, Z_vals_actual, 'b-', linewidth=2, label='Demanda Agregada (Z)')
    ax1.plot(0, A_actual, 'go', zorder=10)
    ax1.text(100, A_actual + 100, f'A = {A_actual:.0f}', color='green', fontweight='bold')

    if Y_actual and 0 <= Y_actual <= Y_max:
        ax1.plot([Y_actual], [Y_actual], 'ro', zorder=10, markersize=8)
        ax1.vlines(Y_actual, 0, Y_actual, colors='r', linestyles='dotted', alpha=0.5)
        ax1.text(Y_actual + 100, 100, 'Y', color='red', fontweight='bold')

    ax1.set_title('Cruz Keynesiana con Impuestos y Sector Externo')
    ax1.set_xlabel('Renta / Producción (Y)')
    ax1.set_ylabel('Demanda Agregada (Z)')
    ax1.set_xlim(left=0, right=Y_max)
    ax1.set_ylim(bottom=0, top=Y_max)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

    st.markdown("---")
    st.latex(r''' Y = \overbrace{\frac{1}{1 - c(1-t)}}^{k} \cdot \overbrace{[c_0 + I_0 + G + X - M + c \cdot TR - c \cdot T_0]}^{A} ''')


# PESTAÑA 2: MERCADO DE DINERO
# ==========================================
with tab2:
    st.header("Equilibrio en el Mercado Monetario")
    
    #Matemática Tab 2
    def calcular_i_eq_tab2(Ms, Y, k_y, h):
        i = (k_y * Y - Ms) / h
        return i if i > 0 else 0 

    M_vals = np.linspace(0, 2500, 100)
    #np.maximum evita que la curva de demanda de dinero baje de 0
    Md_vals_actual = np.maximum(0, (k_y * Y_din - M_vals) / h)
    i_actual = calcular_i_eq_tab2(Ms, Y_din, k_y, h)

    #Botón Base
    if st.button("Fijar Escenario Base (Monetario📌 )", key="btn_dinero"):
        st.session_state.base_Ms = Ms
        st.session_state.base_i = i_actual
        st.session_state.base_Md_vals = Md_vals_actual

    #Métricas
    delta_i = i_actual - st.session_state.base_i if st.session_state.base_i is not None else None
    st.metric("Tasa de Interés de Equilibrio (i*)", f"{i_actual:.2f}%", delta=f"{delta_i:.2f}%" if delta_i is not None else None)

    #Gráfico Tab 2
    fig2, ax2 = plt.subplots(figsize=(10, 6))

    if st.session_state.base_Ms is not None:
        ax2.plot(M_vals, st.session_state.base_Md_vals, color='gray', linestyle='dashed', linewidth=2, label='Demanda (L) Inicial')
        ax2.vlines(st.session_state.base_Ms, 0, 30, colors='gray', linestyles='dashed', linewidth=2, label='Oferta (M/P) Inicial')
        if st.session_state.base_i != i_actual and st.session_state.base_i > 0:
            ax2.hlines(st.session_state.base_i, min(Ms, st.session_state.base_Ms), max(Ms, st.session_state.base_Ms), colors='red', linewidth=2.5)

    ax2.plot(M_vals, Md_vals_actual, 'b-', linewidth=2, label='Demanda de Dinero (L)')
    ax2.vlines(Ms, 0, 30, colors='green', linewidth=2.5, label='Oferta Monetaria (M/P)')

    if i_actual > 0:
        ax2.plot([Ms], [i_actual], 'ro', zorder=10, markersize=8)
        ax2.hlines(i_actual, 0, Ms, colors='r', linestyles='dotted', alpha=0.5)

    ax2.set_title('Mercado de Dinero (Preferencia por la Liquidez)')
    ax2.set_xlabel('Cantidad de Dinero Real (M/P)')
    ax2.set_ylabel('Tasa de Interés (i %)')
    ax2.set_xlim(left=0, right=2500)
    ax2.set_ylim(bottom=0, top=max(Md_vals_actual.max() + 5, 20))
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

    st.markdown("---")
    st.latex(r''' i^* = \frac{k_Y \cdot Y}{h} - \frac{M^s/P}{h} ''')

# PESTAÑA 3: MODELO IS-LM
# ==========================================
with tab3:
    st.header("Modelo IS-LM: Equilibrio Simultáneo")
    
    # Lógica Matemática Tab 3
    A_base = c0 + I_aut + G + X - M + (c1 * TR) - (c1 * T0)
    pendiente_bienes = c1 * (1 - t)
    k = 1 / (1 - pendiente_bienes) if pendiente_bienes < 1 else 1

    Y_vals_islm = np.linspace(0, Y_max, 100)
    
    # np.maximum recorta las partes donde las curvas cruzan al cuadrante negativo
    IS_vals = np.maximum(0, (A_base / b) - (Y_vals_islm / (k * b)))
    LM_vals = np.maximum(0, (k_y / h) * Y_vals_islm - (Ms / h))

    denominador = (k_y / h) + (1 / (k * b))
    Y_eq_islm = ((A_base / b) + (Ms / h)) / denominador
    i_eq_islm = (A_base / b) - (Y_eq_islm / (k * b))

    # Botón Base
    if st.button("📌 Fijar Escenario Base (IS-LM)", key="btn_islm"):
        st.session_state.base_Y_islm = Y_eq_islm
        st.session_state.base_i_islm = i_eq_islm
        st.session_state.base_IS_vals = IS_vals.copy()
        st.session_state.base_LM_vals = LM_vals.copy()

    # Métricas
    delta_Y_islm = Y_eq_islm - st.session_state.base_Y_islm if st.session_state.base_Y_islm else None
    delta_i_islm = i_eq_islm - st.session_state.base_i_islm if st.session_state.base_i_islm else None
    col3_1, col3_2 = st.columns(2)
    col3_1.metric("Ingreso de Eq. General (Y*)", f"${Y_eq_islm:,.2f}", delta=f"{delta_Y_islm:,.2f}" if delta_Y_islm else None)
    col3_2.metric("Tasa de Interés de Eq. (i*)", f"{i_eq_islm:.2f}%", delta=f"{delta_i_islm:.2f}%" if delta_i_islm else None)

    # Gráfico Tab 3
    fig3, ax3 = plt.subplots(figsize=(10, 6))

    if st.session_state.base_Y_islm is not None:
        ax3.plot(Y_vals_islm, st.session_state.base_IS_vals, color='lightcoral', linestyle='dashed', linewidth=2, label='IS Inicial')
        ax3.plot(Y_vals_islm, st.session_state.base_LM_vals, color='lightblue', linestyle='dashed', linewidth=2, label='LM Inicial')
        ax3.plot([st.session_state.base_Y_islm], [st.session_state.base_i_islm], 'ko', alpha=0.3, markersize=8)

    ax3.plot(Y_vals_islm, IS_vals, 'r-', linewidth=2.5, label='Curva IS')
    ax3.plot(Y_vals_islm, LM_vals, 'b-', linewidth=2.5, label='Curva LM')

    if Y_eq_islm > 0 and i_eq_islm > 0:
        ax3.plot([Y_eq_islm], [i_eq_islm], 'ko', zorder=10, markersize=10)
        ax3.vlines(Y_eq_islm, 0, i_eq_islm, colors='k', linestyles='dotted', alpha=0.5)
        ax3.hlines(i_eq_islm, 0, Y_eq_islm, colors='k', linestyles='dotted', alpha=0.5)
        ax3.text(Y_eq_islm + 50, i_eq_islm + 0.5, 'Eq', fontweight='bold')

    ax3.set_title('Modelo IS-LM')
    ax3.set_xlabel('Ingreso / Producción (Y)')
    ax3.set_ylabel('Tasa de Interés (i %)')
    ax3.set_xlim(left=0, right=Y_max)
    ylim_max = max(i_eq_islm * 2, 20) if i_eq_islm > 0 else 20
    ax3.set_ylim(bottom=0, top=ylim_max)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    st.pyplot(fig3)

    st.markdown("---")
    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.markdown("**Curva IS**")
        st.latex(r''' i = \frac{A}{b} - \frac{Y}{k \cdot b} ''')
    with col_eq2:
        st.markdown("**Curva LM**")
        st.latex(r''' i = \frac{k_Y}{h} \cdot Y - \frac{M^s/P}{h} ''')

