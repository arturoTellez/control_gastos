import streamlit as st
import pandas as pd
from datetime import datetime

# --- Configuración de la Página ---
st.set_page_config(page_title="Gestión de Gastos", layout="wide")

st.title("💸 Gestión Detallada de Gastos")
st.markdown("Añade, edita y lleva un registro de todos tus gastos, tanto estimados como reales.")

# --- Inicialización del estado de sesión para guardar la lista de gastos ---
if 'gastos_detallados' not in st.session_state:
    st.session_state.gastos_detallados = []

# --- Formulario para añadir un nuevo gasto ---
with st.form(key="gasto_form", clear_on_submit=True):
    st.subheader("Añadir un Nuevo Gasto")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        nombre = st.text_input("Nombre del Gasto", placeholder="Ej. Renta, Netflix, Supermercado")
        categoria = st.text_input("Categoría", placeholder="Ej. Vivienda, Entretenimiento, Comida")
        subcategoria = st.text_input("Subcategoría", placeholder="Ej. Hipoteca, Streaming, Frutas y Verduras")
    
    with c2:
        estimado = st.number_input("Monto Estimado (MXN)", min_value=0.0, step=50.0)
        periodicidad = st.selectbox("Periodicidad", 
                                    ["Único", "Diario", "Semanal", "Quincenal", "Mensual", "Anual"],
                                    help="¿Con qué frecuencia ocurre este gasto?")
        fecha_inicio = st.date_input("Fecha de Inicio o Próximo Pago")

    with c3:
        num_pagos = st.number_input("Número de Pagos", 
                                    min_value=0, step=1, 
                                    help="Para gastos con fin (ej. 12 meses sin intereses). Pon 0 si es un gasto indefinido (ej. la renta).")
        # El campo para el gasto real estará en la tabla para ser editado después
    
    submit_button = st.form_submit_button(label='Añadir Gasto a la Lista')

# --- Lógica para procesar el formulario ---
if submit_button and nombre:
    nuevo_gasto = {
        "Nombre": nombre,
        "Categoría": categoria,
        "Subcategoría": subcategoria,
        "Monto Estimado": estimado,
        "Monto Real": 0.0, # Se inicia en 0, se edita después
        "Periodicidad": periodicidad,
        "Fecha de Inicio": fecha_inicio,
        "Pagos Totales": num_pagos if num_pagos > 0 else "Indefinido",
    }
    st.session_state.gastos_detallados.append(nuevo_gasto)
    st.success(f"¡Gasto '{nombre}' añadido!")

# --- Visualización y edición de la tabla de gastos ---
st.markdown("---")
st.header("Mis Gastos Registrados")

if not st.session_state.gastos_detallados:
    st.info("Aún no has añadido ningún gasto. Usa el formulario de arriba para empezar.")
else:
    # Convertir la lista de diccionarios a un DataFrame de Pandas
    df = pd.DataFrame(st.session_state.gastos_detallados)
    
    # Calcular la diferencia
    df['Diferencia'] = df['Monto Real'] - df['Monto Estimado']
    
    # Reordenar columnas para una mejor visualización
    column_order = [
        "Nombre", "Categoría", "Subcategoría", "Monto Estimado", "Monto Real", "Diferencia",
        "Periodicidad", "Fecha de Inicio", "Pagos Totales"
    ]
    df_display = df[column_order]

    st.markdown("Puedes editar los valores directamente en la tabla. Para registrar un pago, **cambia el 'Monto Real' de 0 al valor que pagaste**.")
    
    # Usar st.data_editor para una tabla interactiva
    edited_df = st.data_editor(
        df_display,
        num_rows="dynamic", # Permite añadir y borrar filas desde la UI
        key="gastos_editor",
        # Configurar columnas para edición
        column_config={
            "Monto Estimado": st.column_config.NumberColumn(format="$%.2f"),
            "Monto Real": st.column_config.NumberColumn(format="$%.2f"),
            "Diferencia": st.column_config.NumberColumn(format="$%.2f"),
            "Fecha de Inicio": st.column_config.DateColumn(format="DD/MM/YYYY")
        }
    )
    
    # Guardar los cambios de la tabla en el estado de la sesión
    # Esto es crucial para que las ediciones persistan durante la sesión
    st.session_state.gastos_detallados = edited_df.drop(columns=['Diferencia']).to_dict('records')