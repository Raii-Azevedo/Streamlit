import streamlit as st
import pandas as pd
import altair as alt
from streamlit_echarts import st_echarts  

# Carregar o dataset
try:
    df = pd.read_csv("DataCirclePodcast.csv", sep=',')
except FileNotFoundError:
    st.error("The file 'DataCirclePodcast.csv' was not found. Please upload the correct file.")
    st.stop()

# Título do app
st.title("AE MeetUp - Building an App with Streamlit")

# Mensagem inicial
st.markdown(
    """
    Hello, MAE! Let's start this adventure?
    """
)

# Mostrar o DataFrame
st.header("Reading the Dataset")
st.dataframe(df)

# Verificar se as colunas necessárias existem no DataFrame
if "Título do episódio" in df.columns and "Reproduções" in df.columns:
    # Adicionar filtro de lista suspensa para selecionar episódio
    st.subheader("Filter by Episode Title")
    selected_episode = st.selectbox(
        "Select an episode to filter:",
        options=["All"] + df["Título do episódio"].drop_duplicates().tolist()
    )

    # Filtro para outras métricas, como "Estúdio" e "Classificação"
    selected_studio = st.selectbox(
        "Filter by Studio",
        options=["All"] + df["Estúdio"].drop_duplicates().tolist()
    )
    
    selected_classification = st.selectbox(
        "Filter by Classification",
        options=["All"] + df["Classificação"].drop_duplicates().tolist()
    )

    # Filtrar o DataFrame com base nas seleções
    filtered_df = df
    if selected_episode != "All":
        filtered_df = filtered_df[filtered_df["Título do episódio"] == selected_episode]
    if selected_studio != "All":
        filtered_df = filtered_df[filtered_df["Estúdio"] == selected_studio]
    if selected_classification != "All":
        filtered_df = filtered_df[filtered_df["Classificação"] == selected_classification]

    # Exibir o DataFrame filtrado
    st.write(f"Data for selected filters:")
    st.dataframe(filtered_df)

    # Criar o gráfico de barras com Altair (Gráfico de Reproduções)
    if not filtered_df.empty:
        chart = (
            alt.Chart(filtered_df)
            .mark_bar()
            .encode(
                x=alt.X("Título do episódio", sort='-y', title="Episode Title"),
                y=alt.Y("Reproduções", title="Reproductions"),
                tooltip=["Título do episódio", "Reproduções"]
            )
            .properties(
                width=800,  # Largura do gráfico
                height=400,  # Altura do gráfico
                title="Reproductions per Episode"
            )
        )

        # Exibir o gráfico
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No data to display for the selected filters.")
else:
    st.error("The dataset must have columns named 'Título do episódio' and 'Reproduções'.")

# Final Message
st.title("Now it's your time!")

# Final Message2
st.markdown(
    """
    Use your creativity, the streamlit library, and your BFF, Chat GPT, to help you develop an amazing app!
    """
)

# Tratar valores NaN nas colunas de reproduções e curtidas
df['Reproduções'] = df['Reproduções'].fillna(0)  # Substituir NaN por 0 em 'Reproduções'
df['Curtidas'] = df['Curtidas'].fillna(0)  # Substituir NaN por 0 em 'Curtidas'

# Filtrar dados para usar no gráfico (Assumindo que temos as colunas 'Título do episódio', 'Reproduções', e 'Curtidas')
episodios = df['Título do episódio'].tolist()  # Lista com os títulos dos episódios
reproducoes = df['Reproduções'].tolist()      # Lista com o número de reproduções dos episódios
curtidas = df['Curtidas'].tolist()             # Lista com o número de curtidas dos episódios
# Criar o gráfico de linha com as suas colunas
option = {
    "tooltip": {
        "trigger": "axis",  # Quando o usuário passar o mouse sobre a linha, o tooltip será ativado
        "formatter": """
            function(params) {
                var tooltipContent = params[0].name + '<br>';
                for (var i = 0; i < params.length; i++) {
                    if (params[i].seriesName == 'Reproduções por episódio') {
                        tooltipContent += 'Reproduções: ' + params[i].data + '<br>';
                    } else if (params[i].seriesName == 'Curtidas por episódio') {
                        tooltipContent += 'Curtidas: ' + params[i].data + '<br>';
                    }
                }
                return tooltipContent;
            }
        """
    },
    "xAxis": {
        "type": "category",
        "data": episodios,  # Usar os títulos dos episódios como dados do eixo X
    },
    "yAxis": [
        {
            "type": "value",
            "name": "Reproduções",  # Nome do eixo Y para as reproduções
        },
        {
            "type": "value",
            "name": "Curtidas",  # Nome do eixo Y para as curtidas
            "position": "right"  # Colocar o eixo Y da soma das curtidas no lado direito
        }
    ],
    "series": [
        {
            "data": reproducoes,  # Usar as reproduções como dados da série de linha
            "type": "line",
            "smooth": True,  # Tornar a linha mais suave
            "name": "Reproduções por episódio",  # Nome da série para o gráfico
        },
        {
            "data": curtidas,  # Usar as curtidas como dados da série de linha
            "type": "line",     # Tipo de gráfico para a linha de curtidas
            "name": "Curtidas por episódio",  # Nome da série de curtidas
            "yAxisIndex": 1,    # Usar o eixo Y secundário para o gráfico de curtidas
            "itemStyle": {
                "color": "orange"  # Cor da linha de curtidas
            },
            "smooth": True,  # Tornar a linha de curtidas suave também
        },
    ]
}

# Exibir o gráfico no Streamlit
st_echarts(options=option, height="400px")

