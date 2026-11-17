import streamlit as st
import requests
import pandas as pd
import io

st.set_page_config(page_title="SuperKart Sales Forecaster", layout="wide")

st.title("🏪 SuperKart Sales Forecasting Service")
st.write("Predict total sales revenue for products across various SuperKart store outlets.")

# Sidebar URL configuration
backend_url = st.sidebar.text_input(
    "Backend Service API URL",
    value="http://backend:7860"
)

tab1, tab2 = st.tabs(["Online Single Prediction", "Batch CSV Forecast"])

with tab1:
    st.header("Single Product Sales Predictor")
    
    col1, col2 = st.columns(2)
    with col1:
        product_weight = st.number_input("Product Weight", min_value=0.0, max_value=100.0, value=12.5)
        product_sugar = st.selectbox("Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        allocated_area = st.number_input("Allocated Display Area Ratio", min_value=0.0, max_value=1.0, value=0.05, format="%.4f")
        product_mrp = st.number_input("Product MRP (Maximum Retail Price)", min_value=0.0, value=110.0)
        product_id_char = st.selectbox("Product ID Category (First 2 letters)", ["FD", "DR", "NC"])
        
    with col2:
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        city_type = st.selectbox("Store City Type", ["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Supermarket Type3", "Departmental Store", "Food Mart"])
        store_age = st.number_input("Store Age (Years)", min_value=0, max_value=100, value=15)
        product_category = st.selectbox("Product Category Type", ["Perishables", "Non Perishables"])

    if st.button("Predict Sales"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar,
            "Product_Allocated_Area": allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": store_age,
            "Product_Type_Category": product_category
        }
        
        try:
            response = requests.post(f"{backend_url}/v1/predict", json=payload)
            if response.status_code == 200:
                prediction = response.json()["prediction"]
                st.success(f"🎯 Estimated Total Store Sales: **${prediction:,.2f}**")
            else:
                st.error(f"Error from backend: {response.text}")
        except Exception as e:
            st.error(f"Could not connect to backend service: {e}")

with tab2:
    st.header("Batch File Forecasting")
    st.write("Upload a CSV file containing multiple products and outlet characteristics to generate forecasts in bulk.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df_preview = pd.read_csv(uploaded_file)
        st.write("### Input File Preview")
        st.dataframe(df_preview.head())
        
        # Reset buffer pointer for uploading
        uploaded_file.seek(0)
        
        if st.button("Generate Batch Predictions"):
            try:
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}
                response = requests.post(f"{backend_url}/v1/predictbatch", files=files)
                
                if response.status_code == 200:
                    predictions_dict = response.json()
                    # Convert dictionary predictions to series and align with dataframe
                    preds_series = pd.Series(predictions_dict).sort_index()
                    df_preview["Predicted_Store_Sales_Total"] = preds_series.values
                    
                    st.success("🎉 Batch Predictions Completed Successfully!")
                    st.write("### Results Preview")
                    st.dataframe(df_preview)
                    
                    # Download link
                    csv_buffer = io.StringIO()
                    df_preview.to_csv(csv_buffer, index=False)
                    st.download_button(
                        label="📥 Download Complete Forecasts as CSV",
                        data=csv_buffer.getvalue(),
                        file_name="SuperKart_Sales_Forecasts.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(f"Error from backend: {response.text}")
            except Exception as e:
                st.error(f"Could not process batch file: {e}")
