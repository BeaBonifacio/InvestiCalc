import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="InvestiCalc", layout="centered")

st.title("📈 InvestiCalc: Future Investment Value Calculator")
st.write("Upload your investment data or input manually, and see what the future holds.")

# Store data
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Date", "Price"])

# Input method
with st.expander("➕ Add Entry"):
    date = st.date_input("Date")
    price = st.number_input("Price", step=0.01)
    if st.button("Add Entry"):
        new_entry = pd.DataFrame({"Date": [date], "Price": [price]})
        st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
        st.success("Entry added!")

# Upload CSV
uploaded = st.file_uploader("📤 Or Upload CSV (Date, Price)", type=["csv"])
if uploaded:
    df_uploaded = pd.read_csv(uploaded, parse_dates=["Date"])
    st.session_state.data = pd.concat([st.session_state.data, df_uploaded], ignore_index=True)
    st.success("File uploaded!")

data = st.session_state.data

# Display data
if not data.empty:
    st.subheader("📋 Data Table")
    data_sorted = data.sort_values("Date")
    data_sorted["Date"] = pd.to_datetime(data_sorted["Date"])  # ← Fix
    data_sorted.index = range(1, len(data_sorted) + 1)
    st.dataframe(data_sorted)

    # Plot
    st.subheader("📊 Price Trend")
    fig, ax = plt.subplots()
    ax.plot(data_sorted["Date"], data_sorted["Price"], marker="o", linestyle="-")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    st.pyplot(fig)

    # Prediction
    st.subheader("🔮 Predict Future Price")

    try:
        # Convert dates to numeric day offsets
        dates_numeric = (data_sorted["Date"] - data_sorted["Date"].min()).dt.days
        prices = data_sorted["Price"].values

        def lagrange_interpolation(x_values, y_values, x):
            total = 0
            n = len(x_values)
            for i in range(n):
                xi, yi = x_values[i], y_values[i]
                term = yi
                for j in range(n):
                    if i != j:
                        xj = x_values[j]
                        term *= (x - xj) / (xi - xj)
                total += term
            return total

        max_points = min(10, len(data_sorted))  # Default limit
        limit_n = st.slider("Number of recent data points to use for interpolation:", min_value=2, max_value=len(data_sorted), value=max_points)

        # Use only the last `limit_n` points
        recent_dates = dates_numeric.iloc[-limit_n:].to_numpy()
        recent_prices = prices[-limit_n:]

        days_future = st.slider("Days into the future:", 1, 60, 7)
        future_day = dates_numeric.max() + days_future
        predicted_price = lagrange_interpolation(recent_dates, recent_prices, future_day)

        future_date = data_sorted["Date"].max() + pd.Timedelta(days=days_future)
        st.markdown(f"📌 **Predicted Price on {future_date.strftime('%Y-%m-%d')}:** ${predicted_price:.2f}")

    except Exception as e:
        st.error(f"Error during interpolation: {e}")

else:
    st.info("Please add data manually or upload a CSV file.")
