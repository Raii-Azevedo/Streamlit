import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.title("Gráfico de Fechamento")

data = yf.download("AAPL", start="2022-01-01", end="2022-12-31")
st.write(data.head())

fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))
fig.update_layout(title="Fechamento Apple", xaxis_title="Data", yaxis_title="Preço (USD)")

st.plotly_chart(fig, use_container_width=True)
