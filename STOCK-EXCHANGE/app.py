import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

st.set_page_config(page_title="Stock Price App", layout="wide")
st.title("📈 Stock Price App")
st.write("This app retrieves stock price data from Yahoo Finance.")

# SIDEBAR – inputs do usuário
with st.sidebar:
    company_name = st.text_input("Enter the company ticker (e.g., AAPL for Apple):", "AAPL")
    start_date = st.date_input("Start date:", date(2020, 1, 1))
    end_date = st.date_input("End date:", date.today())
    submit_button = st.button("Get Stock Price Data")

# CORPO PRINCIPAL – processamento dos dados
if submit_button:
    data = yf.download(company_name, start=start_date, end=end_date)

    if data.empty:
        st.error("❌ No data found for the given stock symbol and date range.")
    else:
        st.success(f"✅ Data retrieved for {company_name} from {start_date} to {end_date}.")

        # Gráfico de fechamento (fora das tabs)
        fig_close = go.Figure()
        fig_close.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))
        fig_close.update_layout(title=f"{company_name} Closing Price", xaxis_title="Date", yaxis_title="Price (USD)")
        st.plotly_chart(fig_close, use_container_width=True, key="main_close_chart")

        # Gráfico de volume (fora das tabs)
        fig_volume = go.Figure()
        fig_volume.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume'))
        fig_volume.update_layout(title=f"{company_name} Trading Volume", xaxis_title="Date", yaxis_title="Volume")
        st.plotly_chart(fig_volume, use_container_width=True, key="main_volume_chart")

        # Tabela de dados
        st.subheader("📊 Data Table")
        st.dataframe(data, use_container_width=True)

        # Gráficos adicionais em abas
        if data.size > 0:
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Close Chart", "📊 Volume Chart", "📉 Open Chart", "📊 High Chart"])

            with tab1:
                st.plotly_chart(fig_close, use_container_width=True, key="tab_close_chart")

            with tab2:
                st.plotly_chart(fig_volume, use_container_width=True, key="tab_volume_chart")

            with tab3:
                fig_open = go.Figure()
                fig_open.add_trace(go.Scatter(x=data.index, y=data['Open'], mode='lines', name='Open Price'))
                fig_open.update_layout(title=f"{company_name} Opening Price", xaxis_title="Date", yaxis_title="Price (USD)")
                st.plotly_chart(fig_open, use_container_width=True, key="tab_open_chart")

            with tab4:
                fig_high = go.Figure()
                fig_high.add_trace(go.Scatter(x=data.index, y=data['High'], mode='lines', name='High Price'))
                fig_high.update_layout(title=f"{company_name} High Price", xaxis_title="Date", yaxis_title="Price (USD)")
                st.plotly_chart(fig_high, use_container_width=True, key="tab_high_chart")

        # Estatísticas descritivas
        st.subheader("📌 Summary Statistics")
        st.write(data.describe())

        # Download como CSV
        csv = data.to_csv().encode('utf-8')
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"{company_name}_stock_data.csv",
            mime='text/csv',
        )
