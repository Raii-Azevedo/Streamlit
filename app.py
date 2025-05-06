import streamlit as st
import pandas as pd
from prophet import Prophet
import plotly.graph_objects as go
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import numpy as np

# Título do App
st.title("P&L ARTEFACT")

# Subtítulo do App
st.subheader("Análise preditiva de P&L utilizando modelo de previsão Prophet")


# Upload do arquivo via Drag-and-Drop
uploaded_file = st.file_uploader("Arraste e solte a base de dados aqui", type=["csv", "xlsx", "xls"])

if uploaded_file:
    # Verifica o tipo de arquivo e lê os dados
    try:
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            data = pd.read_excel(uploaded_file)
        else:
            st.error("Formato de arquivo não suportado. Use CSV, XLS ou XLSX.")
            st.stop()

        # Mostra os dados carregados
        st.subheader("Dados Carregados (Apenas 10 Primeiras Linhas):")
        st.dataframe(data.head(10))

        # Seleção de colunas
        st.subheader("Configuração do Forecast")
        try:
            date_column = st.selectbox("Selecione a coluna de data:", data.columns)
            value_column = st.selectbox("Selecione a coluna de valores:", data.columns)

            # Filtro para escolher o número de linhas históricas
            num_history = st.slider(
                "Selecione o número de registros históricos a exibir:",
                min_value=10,
                max_value=len(data),
                value=30,
                step=1
            )

            # Processa os dados apenas se ambas as colunas forem selecionadas
            if date_column and value_column:
                # Renomeia as colunas para o formato esperado pelo Prophet
                forecast_data = data[[date_column, value_column]].rename(
                    columns={date_column: "ds", value_column: "y"}
                )
                forecast_data["ds"] = pd.to_datetime(forecast_data["ds"])

                # Seleciona apenas o número de registros históricos solicitado
                forecast_data = forecast_data.tail(num_history)

                # Criação do modelo Prophet
                model = Prophet()
                model.fit(forecast_data)

                # Escolha do tipo de forecast
                st.subheader("Escolha o tipo de Forecast")
                forecast_type = st.radio(
                    "Selecione o tipo de previsão:",
                    ("Short Forecast (3 meses)", "Long Forecast (6 meses)")
                )

                # Define o número de períodos
                periods = 3 if forecast_type == "Short Forecast (3 meses)" else 6

                # Geração do forecast
                future = model.make_future_dataframe(periods=periods, freq="M")
                forecast = model.predict(future)

                # Adicionar coluna indicando se é histórico ou forecast
                forecast['type'] = forecast['ds'].apply(
                    lambda x: 'Histórico' if x <= pd.to_datetime('today') else 'Forecast'
                )

                # Exibição do resultado com a coluna extra
                st.subheader(f"Tabela do {forecast_type} com Histórico e Forecast")
                st.dataframe(forecast[["ds", "yhat", "yhat_lower", "yhat_upper", "type"]])

                # Criação do gráfico
                fig = go.Figure()

                # Linha de dados históricos
                fig.add_trace(go.Scatter(
                    x=forecast_data["ds"],
                    y=forecast_data["y"],
                    mode='lines+markers',
                    name="Histórico",
                    line=dict(color='blue', width=2)
                ))

                # Linha de previsão (yhat)
                fig.add_trace(go.Scatter(
                    x=forecast["ds"],
                    y=forecast["yhat"],
                    mode='lines',
                    name="Previsão (yhat)",
                    line=dict(color='green', width=2)
                ))

                # Linha superior (yhat_upper)
                fig.add_trace(go.Scatter(
                    x=forecast["ds"],
                    y=forecast["yhat_upper"],
                    mode='lines',
                    name="Limite Superior (yhat_upper)",
                    line=dict(color='red', width=1, dash='dash')
                ))

                # Linha inferior (yhat_lower)
                fig.add_trace(go.Scatter(
                    x=forecast["ds"],
                    y=forecast["yhat_lower"],
                    mode='lines',
                    name="Limite Inferior (yhat_lower)",
                    line=dict(color='red', width=1, dash='dash')
                ))

                # Configuração do layout do gráfico
                fig.update_layout(
                    title=f"{forecast_type} de Valores",
                    xaxis_title="Data",
                    yaxis_title="Valor",
                    legend_title="Legenda",
                    template="plotly_white"
                )

                # Exibir o gráfico no Streamlit
                st.plotly_chart(fig)

                # Comparação de acuracidade - Verifique se valores reais estão disponíveis
                st.subheader("Comparação de Acuracidade")

                # Seleciona os dados históricos como "valores reais"
                historical_data = forecast_data[forecast_data['ds'] < pd.to_datetime("today")]

                if not historical_data.empty:
                    # Calcular as métricas de acurácia
                    mae = mean_absolute_error(historical_data['y'], forecast.loc[forecast['ds'].isin(historical_data['ds']), 'yhat'])
                    mse = mean_squared_error(historical_data['y'], forecast.loc[forecast['ds'].isin(historical_data['ds']), 'yhat'])
                    rmse = np.sqrt(mse)
                    mape = mean_absolute_percentage_error(historical_data['y'], forecast.loc[forecast['ds'].isin(historical_data['ds']), 'yhat'])

                    # Exibir as métricas
                    st.write(f"Erro Absoluto Médio (MAE): {mae:.2f}")
                    st.write(f"Erro Quadrático Médio (MSE): {mse:.2f}")
                    st.write(f"Raiz do Erro Quadrático Médio (RMSE): {rmse:.2f}")
                    st.write(f"Erro Percentual Absoluto Médio (MAPE): {mape*100:.2f}%")

                else:
                    st.warning("Não há dados históricos anteriores à data atual para comparação.")

        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")

    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
