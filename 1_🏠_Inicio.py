import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Diagnóstico Financiero",
    page_icon="💡",
    layout="wide"
)

# --- INICIALIZACIÓN DEL ESTADO DE SESIÓN ---
if 'lifestyle_calculated' not in st.session_state:
    st.session_state.lifestyle_calculated = False
if 'credit_calculated' not in st.session_state:
    st.session_state.credit_calculated = False

# --- Título ---
st.title('💡 Diagnóstico Financiero Personal')
st.markdown("""
Esta herramienta te guía en dos partes:

**Paso 1: Conoce tu Salud Financiera Actual**
- Descubre si tu estilo de vida actual es sostenible con tus ingresos y gastos.

**Paso 2: Simula un Crédito**
- Una vez que conozcas tu situación, podrás analizar si te conviene tomar un préstamo.
""")
st.markdown("---")
# --- ====================================================================== ---
# --- =============== ETAPA 1: SALUD FINANCIERA ACTUAL ===================== ---
# --- ====================================================================== ---
with st.container(border=True):
    st.header("Paso 1: Conoce tu Salud Financiera Actual")
    st.markdown("Ingresa cuánto ganas y gastas al mes para saber si tu estilo de vida es sostenible.")
    
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("💰 ¿Cuál es tu ingreso?")
        st.markdown("Tu sueldo mensual (libre de impuestos).")
        ingreso_mensual = st.number_input('Ingreso Mensual Neto (MXN)', min_value=0.0, step=500.0, label_visibility="collapsed")

    with col2:
        st.subheader("🏠 ¿Cuánto gastas?")
        st.markdown("Suma de gastos fijos y variables.")
        gastos_fijos = st.number_input('Gastos Fijos (MXN)', min_value=0.0, step=100.0)
        gastos_variables = st.number_input('Gastos Variables (MXN)', min_value=0.0, step=100.0)

    if st.button('Analizar mi Salud Financiera', use_container_width=True):
        st.session_state.lifestyle_calculated = True
        st.session_state.credit_calculated = False # Resetea el análisis de crédito

    # --- RESULTADO DEL DIAGNÓSTICO 1 ---
    if st.session_state.lifestyle_calculated:
        total_gastos = gastos_fijos + gastos_variables
        flujo_libre = ingreso_mensual - total_gastos
        
        st.subheader("Diagnóstico de tus Hábitos:")
        diag_col1, diag_col2 = st.columns([2, 1])
        with diag_col1:
            if flujo_libre >= 0:
                st.success(f"**¡Vas bien! Te sobran ${flujo_libre:,.2f} al mes.** ✅")
            else:
                st.error(f"**¡Cuidado! Gastas más de lo que ganas. Te faltan ${abs(flujo_libre):,.2f} al mes.** ❌")
        with diag_col2:
            if total_gastos > 0:
                labels = ['Fijos', 'Variables']
                values = [gastos_fijos, gastos_variables]
                pie_fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, textinfo='percent', marker_colors=['#FF6347', '#FFD700'])])
                pie_fig.update_layout(title_text='Tus Gastos', showlegend=True, margin=dict(t=40, b=0, l=0, r=0))
                st.plotly_chart(pie_fig, use_container_width=True)

# --- ====================================================================== ---
# --- =============== ETAPA 2: SIMULACIÓN DE CRÉDITO ======================= ---
# --- ====================================================================== ---
if st.session_state.lifestyle_calculated:
    st.markdown("---")
    with st.container(border=True):
        st.header("Paso 2: Simula un Crédito (Opcional)")
        st.markdown("Si estás pensando en pedir un préstamo, ingresa los datos para ver si es viable.")
        
        credit_cols = st.columns(3)
        with credit_cols[0]:
            monto_prestamo = st.number_input('Monto del préstamo', min_value=0.0, step=1000.0)
        with credit_cols[1]:
            plazo_meses = st.number_input('Plazo (meses)', min_value=1, step=1)
        with credit_cols[2]:
            tasa_anual = st.slider('Tasa Anual (%)', min_value=0.0, max_value=120.0, value=35.0, step=0.5)

        if monto_prestamo > 0:
            if st.button('Analizar Viabilidad del Crédito', use_container_width=True, type="primary"):
                st.session_state.credit_calculated = True

        # --- RESULTADO DEL DIAGNÓSTICO 2 ---
        if st.session_state.credit_calculated:
            # Re-calculamos flujo_libre para asegurar que esté disponible en este scope
            flujo_libre = ingreso_mensual - (gastos_fijos + gastos_variables)
            pago_mensual_credito = 0.0
            tasa_mensual = (tasa_anual / 100) / 12
            if plazo_meses > 0:
                if tasa_anual > 0:
                    numerador = tasa_mensual * ((1 + tasa_mensual) ** plazo_meses)
                    denominador = ((1 + tasa_mensual) ** plazo_meses) - 1
                    if denominador > 0: pago_mensual_credito = monto_prestamo * (numerador / denominador)
                    else: pago_mensual_credito = monto_prestamo / plazo_meses
                else: pago_mensual_credito = monto_prestamo / plazo_meses

            flujo_final_con_credito = flujo_libre - pago_mensual_credito

            st.subheader("Diagnóstico del Crédito:")

            if flujo_libre < 0:
                st.warning("**OJO:** Estás analizando un crédito cuando ya gastas más de lo que ganas. Es muy riesgoso.")

            st.metric('La mensualidad sería de:', f"${pago_mensual_credito:,.2f}")

            if flujo_final_con_credito >= 0:
                st.success(f"**Crédito VIABLE.** 👍 Podrías pagarlo y te sobrarían **${flujo_final_con_credito:,.2f}** al mes.")
            else:
                deficit_total_mensual = abs(flujo_final_con_credito)
                st.error(f"**Crédito NO VIABLE.** 👎 Te faltarían **${deficit_total_mensual:,.2f}** al mes para cubrirlo.")
                st.info(f"Para pagarlo, necesitas ganar **${deficit_total_mensual:,.2f}** más al mes o recortar esa misma cantidad de tus gastos.")
                
                st.subheader("⚠️ Así crecería tu deuda...")
                años_proj = [1, 2, 3, 5, 10, 20]
                deuda_proyectada = []
                deuda_actual = 0
                deficit_estructural = abs(min(0, flujo_libre))
                for mes_actual in range(1, max(años_proj) * 12 + 1):
                    if mes_actual <= plazo_meses:
                        deficit_a_sumar = deficit_total_mensual
                    else:
                        deficit_a_sumar = deficit_estructural
                    deuda_actual += deficit_a_sumar
                    deuda_actual *= (1 + tasa_mensual)
                    if mes_actual % 12 == 0:
                        año = mes_actual // 12
                        if año in años_proj:
                            deuda_proyectada.append((f"{año} año(s)", f"${deuda_actual:,.2f}"))
                df_proyeccion = pd.DataFrame(deuda_proyectada, columns=['Tiempo', 'Deuda Total'])
                st.table(df_proyeccion)
                st.caption("Nota: No incluye multas o recargos.")

                st.subheader("Gráfica: Ahorro vs Deuda")
                meses_grafica = list(range(int(plazo_meses) + 1))
                saldo_acumulado = [flujo_final_con_credito * mes for mes in meses_grafica]
                fig = go.Figure()
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                fig.add_trace(go.Scatter(x=meses_grafica, y=[min(0, s) for s in saldo_acumulado], fill='tozeroy', mode='lines', line_color='rgba(255,0,0,0.7)', fillcolor='rgba(255,0,0,0.2)', name='Deuda'))
                fig.add_trace(go.Scatter(x=meses_grafica, y=[max(0, s) for s in saldo_acumulado], fill='tozeroy', mode='lines', line_color='rgba(0,128,0,0.7)', fillcolor='rgba(0,128,0,0.2)', name='Ahorro'))
                fig.update_layout(title_text='Tu Balance mes a mes', xaxis_title='Mes', yaxis_title='Balance (MXN)')
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("El problema de la **Inflación**"):
                    st.markdown("Con la inflación, todo sube de precio. El dinero que te falta hoy, será más difícil de conseguir mañana porque tus gastos básicos serán más caros.")
                
                with st.expander("⚖️ **¿Qué pasa si no pago en México?**"):
                    st.markdown("""
                    - **Buró de Crédito:** Te califican mal y te niegan futuros créditos, tarjetas o planes de celular.
                    - **Cobranza:** Te llamarán insistentemente a ti y a tus referencias.
                    - **Embargo:** Un juez puede ordenar quitarte bienes (coche, TV, parte de tu sueldo) para pagar.
                    - **¿Cárcel? NO.** Es una deuda civil, no un delito. No te pueden meter a la cárcel por no pagar.
                    """)