import streamlit as st
import pandas as pd

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Cotizador de Retos",
    page_icon="🎯",
    layout="wide"
)

st.title('🎯 Cotizador de Presupuesto para Retos')

# --- Cargar y Preparar los Datos ---
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    currency_columns = ['RentabilidadPromedioVale', 'ComprasPromedio6meses']
    
    for col in currency_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r'[$,]', '', regex=True),
                errors='coerce'
            )
    
    df.dropna(subset=currency_columns, inplace=True)
    return df

try:
    df = load_data('RFM Salevale general V4.1 - Hoja 1.csv')
except FileNotFoundError:
    st.error("Error: No se encontró el archivo 'RFM Salevale general V4.1 - Hoja 1.csv'.")
    st.stop()

# --- Barra Lateral de Filtros ---
st.sidebar.header('Configura tu Simulación')

challenge_type = st.sidebar.selectbox("1. Selecciona el Tipo de Reto:", ["Recencia", "Frecuencia"])
available_segments = df['Accion requerida'].unique()
available_levels = df['Nivel'].unique()
return_factors = [2, 3, 4, 5, 6, 7, 8, 9, 10]

if challenge_type == "Recencia":
    st.sidebar.subheader("Configuración de Recencia")
    selected_segments = st.sidebar.multiselect('2. Selecciona los Segmentos:', available_segments)
    selected_levels = st.sidebar.multiselect('3. Selecciona los Niveles:', available_levels)
    selected_return_factor = st.sidebar.selectbox('4. Selecciona el Factor de Retorno:', return_factors)
    min_points = st.sidebar.number_input('5. Puntos Mínimos a Otorgar:', min_value=0, value=5, step=5)
    max_points = st.sidebar.number_input('6. Puntos Máximos a Otorgar:', min_value=0, value=500, step=5)

elif challenge_type == "Frecuencia":
    st.sidebar.subheader("Configuración de Frecuencia")
    selected_segments = st.sidebar.multiselect('2. Selecciona los Segmentos:', available_segments)
    selected_levels = st.sidebar.multiselect('3. Selecciona los Niveles:', available_levels)
    target_increase_pct = st.sidebar.number_input('4. Porcentaje de Incremento Objetivo (%):', min_value=1.0, value=10.0, step=1.0)
    selected_return_factor = st.sidebar.selectbox('5. Selecciona el Factor de Retorno:', return_factors)
    min_points = st.sidebar.number_input('6. Puntos Mínimos a Otorgar:', min_value=0, value=10, step=5)
    max_points = st.sidebar.number_input('7. Puntos Máximos a Otorgar:', min_value=0, value=1000, step=5)

# --- Lógica de Cálculo y Visualización ---
st.info("👈 ¡Bienvenido! Usa los filtros en la barra lateral y haz clic en 'Calcular' para ver los resultados.")

if st.sidebar.button('Calcular Presupuesto', type="primary"):
    if not selected_segments or not selected_levels:
        st.warning("Por favor, selecciona al menos un segmento y un nivel.")
    else:
        st.info("Paso 1: Botón presionado. Iniciando el filtrado...") # MENSAJE DE DIAGNÓSTICO 1
        
        filtered_df = df[
            df['Accion requerida'].isin(selected_segments) &
            df['Nivel'].isin(selected_levels)
        ].copy()

        st.info(f"Paso 2: Filtrado completado. Se encontraron {len(filtered_df)} expertas que coinciden.") # MENSAJE DE DIAGNÓSTICO 2

        if filtered_df.empty:
            st.warning("No se encontraron datos para la combinación de filtros seleccionada. Prueba con otros filtros.")
        else:
            st.info("Paso 3: Calculando puntos...") # MENSAJE DE DIAGNÓSTICO 3
            if challenge_type == "Recencia":
                filtered_df['Puntos'] = filtered_df['RentabilidadPromedioVale'] / selected_return_factor
            elif challenge_type == "Frecuencia":
                increase_decimal = target_increase_pct / 100
                vales_extra = filtered_df['ComprasPromedio6meses'] * increase_decimal
                rentabilidad_extra = vales_extra * filtered_df['RentabilidadPromedioVale']
                filtered_df['Puntos'] = rentabilidad_extra / selected_return_factor

            filtered_df['Puntos'] = (filtered_df['Puntos'] // 5) * 5
            filtered_df['Puntos'] = filtered_df['Puntos'].clip(lower=min_points, upper=max_points)
            total_cost = filtered_df['Puntos'].sum()

            st.info("Paso 4: ¡Cálculos finalizados! Mostrando resultados.") # MENSAJE DE DIAGNÓSTICO 4

            # --- Mostrar Resultados ---
            st.subheader(f'Resultados del Reto de {challenge_type}')
            col1, col2 = st.columns(2)
            col1.metric("Puntos Totales Proyectados", f"{total_cost:,.0f}")
            col2.metric("Expertas Incluidas", f"{len(filtered_df):,.0f}")
            
            st.write("---")
            
            st.subheader('Detalle de Expertas y Puntos Asignados')
            st.dataframe(filtered_df[['id_distributor', 'Accion requerida', 'Nivel', 'RentabilidadPromedioVale', 'Puntos']])