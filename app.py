import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
from streamlit_folium import folium_static
import folium
import matplotlib.pyplot as plt


class VisualizadorDatos:
    def __init__(self, archivo):
        self.data = pd.read_csv(archivo, delimiter=";")
        self.data_ubigeos = pd.read_csv('TB_UBIGEOS.csv')
        self.columnas_departamento = ['DEPARTAMENTO1']
        self.columnas_provincia = ['DEPARTAMENTO1', 'PROVINCIA1']
        self.columnas_distrito = ['DEPARTAMENTO1', 'PROVINCIA1', 'DISTRITO1']
        self.columnas_anp_cate = ['ANP_CATE']

    def filtrar_y_eliminar_nulos(self, data_frame):
        return data_frame.dropna()

    def convertir_a_str(self, data_frame):
        return data_frame.applymap(str)

    def concatenar_columnas(self, data_frame, columnas):
        data_frame['Location'] = data_frame.apply(lambda row: ', '.join(row), axis=1)
        return data_frame

    def contar_ocurrencias(self, data_frame):
        conteo = data_frame['Location'].value_counts().reset_index()
        conteo.columns = ['Ubicacion', 'Count']
        return conteo

    def generar_grafica(self, conteo, titulo):
        figura = px.bar(conteo, x='Ubicacion', y='Count', title=titulo, labels={'Ubicacion': 'Ubicación', 'Count': 'Cantidad'})
        figura.update_traces(marker_color='cyan', marker_line_color='darkblue', marker_line_width=2, opacity=0.8)
        figura.update_layout(title_text=titulo, title_x=0.5, xaxis_title='Ubicación', yaxis_title='Cantidad', template='plotly_dark')
        return figura

    def mostrar_grafica(self, figura):
        st.plotly_chart(figura)

    def generar_mapa_ubigeos(self, gdf):
        m = folium.Map(location=[-9.1900, -75.0152], zoom_start=5, control_scale=True)

        for idx, row in gdf.iterrows():
            folium.Marker(
                location=[row['latitud'], row['longitud']],
                popup=row['distrito'],
                icon=folium.Icon(color='blue')
            ).add_to(m)

        return m


def main():
    st.set_page_config(
        page_title="Proyecto PA",
        page_icon="🌐",
        layout="wide"
    )
    st.markdown("<h1 style='text-align: center; color: #38b6ff;'>Áreas Naturales Protegidas (ANP) de Administración Nacional Definitiva </h1>", unsafe_allow_html=True)

    # Título de la aplicación Streamlit


    # Crear una instancia de la clase VisualizadorDatos y cargar el archivo CSV
    visualizador = VisualizadorDatos("archivo.csv")

    # Filtrar y eliminar valores nulos para cada nivel geográfico (departamento, provincia, distrito)
    data_anp_cate = visualizador.filtrar_y_eliminar_nulos(visualizador.data[visualizador.columnas_anp_cate])
    data_departamento = visualizador.filtrar_y_eliminar_nulos(visualizador.data[visualizador.columnas_departamento])
    data_provincia = visualizador.filtrar_y_eliminar_nulos(visualizador.data[visualizador.columnas_provincia])
    data_distrito = visualizador.filtrar_y_eliminar_nulos(visualizador.data[visualizador.columnas_distrito])

    # Convertir las columnas a tipo str si no lo son
    data_anp_cate = visualizador.convertir_a_str(data_anp_cate)
    data_departamento = visualizador.convertir_a_str(data_departamento)
    data_provincia = visualizador.convertir_a_str(data_provincia)
    data_distrito = visualizador.convertir_a_str(data_distrito)

    # Concatenar las columnas para formar la columna 'Location' para cada nivel geográfico
    data_anp_cate = visualizador.concatenar_columnas(data_anp_cate, visualizador.columnas_anp_cate)
    data_departamento = visualizador.concatenar_columnas(data_departamento, visualizador.columnas_departamento)
    data_provincia = visualizador.concatenar_columnas(data_provincia, visualizador.columnas_provincia)
    data_distrito = visualizador.concatenar_columnas(data_distrito, visualizador.columnas_distrito)

    # Contar las ocurrencias de cada ubicación para cada nivel geográfico
    conteo_anp_cate = visualizador.contar_ocurrencias(data_anp_cate)
    conteo_departamento = visualizador.contar_ocurrencias(data_departamento)
    conteo_provincia = visualizador.contar_ocurrencias(data_provincia)
    conteo_distrito = visualizador.contar_ocurrencias(data_distrito)

    # Generar gráficas de barras para cada nivel geográfico
    fig_anp_cate = visualizador.generar_grafica(conteo_anp_cate, "Conteo por ANP CATE")
    fig_departamento = visualizador.generar_grafica(conteo_departamento, "Conteo por Departamento")
    fig_provincia = visualizador.generar_grafica(conteo_provincia, "Conteo por Provincia")
    fig_distrito = visualizador.generar_grafica(conteo_distrito, "Conteo por Distrito")

    # Personalizar los estilos de las gráficas
    fig_anp_cate.update_traces(marker_color='#2ecc71', marker_line_color='rgb(8,48,107)', marker_line_width=1.5)
    fig_departamento.update_traces(marker_color='#3498db', marker_line_color='rgb(8,48,107)', marker_line_width=1.5)
    fig_provincia.update_traces(marker_color='#9b59b6', marker_line_color='rgb(8,48,107)', marker_line_width=1.5)
    fig_distrito.update_traces(marker_color='#e74c3c', marker_line_color='rgb(8,48,107)', marker_line_width=1.5)

    # Unir los datos de coordenadas con los datos de Ubigeos utilizando el código UBIGEO1
    merged_data = pd.merge(visualizador.data, visualizador.data_ubigeos, how="left", left_on="UBIGEO1",
                           right_on="ubigeo_inei")

    # Filtrar solo las filas que tienen datos de Ubigeo y coordenadas
    filtered_data = merged_data.dropna(subset=['latitud', 'longitud'])

    # Crear un GeoDataFrame con la información de Ubigeos
    geometry = gpd.points_from_xy(filtered_data['longitud'], filtered_data['latitud'])
    gdf = gpd.GeoDataFrame(filtered_data, geometry=geometry)

    # Generar el mapa de Ubigeos
    mapa_ubigeos = visualizador.generar_mapa_ubigeos(gdf)


    # Mostrar el mapa de Ubigeos en la aplicación Streamlit
    st.markdown("## Mapa de Ubigeos")
    folium_static(mapa_ubigeos)
    st.markdown("## Gráficas")

    st.plotly_chart(fig_anp_cate)
    st.code("python\nst.plotly_chart(fig_anp_cate)\n")

    st.plotly_chart(fig_departamento)
    st.code("python\nst.plotly_chart(fig_departamento)\n")

    st.plotly_chart(fig_provincia)
    st.code("python\nst.plotly_chart(fig_provincia)\n")

    st.plotly_chart(fig_distrito)
    st.code("python\nst.plotly_chart(fig_distrito)\n")

        
     # Gráfica de barras adicional
    st.markdown("## *Superficies de las Áreas*")
    data_barras = {
        'Área Natural Protegida': ['Chancaybaños', 'Santiago Comaina', 'Cordillera Huayhuash', 'Sierra del Divisor', 'Río Nieva', 'Bosque de Zárate', 'Reserva Paisajística Cerro Khapia', 'Ancón'],
        'Superficie (ha)': [2628, 398449.44, 67589.76, 62234.62, 36348.3, 545.75, 18313.79, 2193.01]
    }

    df_barras = pd.DataFrame(data_barras)

    fig_barras, ax_barras = plt.subplots(figsize=(10,6))
    ax_barras.barh(df_barras['Área Natural Protegida'], df_barras['Superficie (ha)'])
    ax_barras.set_xlabel('Superficie (ha)')
    ax_barras.set_title('Superficies de las Áreas')
    
    # Mostrar la gráfica de barras adicional
    st.pyplot(fig_barras)


if __name__ == "__main__":
    main()
