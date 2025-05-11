import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit.components.v1 as components

# title dashboard
st.title("E-Commerce Customer Analysis Dashboard")

# Load datanya
try:
    orders_df = pd.read_csv("Dataset/orders_dataset.csv")
    customers_df = pd.read_csv("Dataset/customers_dataset.csv")
    payments_df = pd.read_csv("Dataset/order_payments_dataset.csv")
    geo_data = pd.read_csv("Dashboard/main_data.csv")
    
    # Hitung persentase per kotanya
    total_transactions = geo_data['transaction_count'].sum()
    geo_data['percentage'] = (geo_data['transaction_count'] / total_transactions) * 100
    
except Exception as e:
    st.error(f"Error membaca file: {str(e)}")
    st.error("Pastikan:")
    st.error("1. File ada di lokasi yang benar")
    st.error("2. Tidak ada typo di nama file/folder")
    st.error(f"Struktur folder saat ini: {os.listdir()}")
    st.stop()

# Merge data for other visualizations
merged_df = orders_df.merge(customers_df, on='customer_id').merge(payments_df, on='order_id')

# Sidebar untuk pilih visualisasi
st.sidebar.header("Select Visualization")
visualization = st.sidebar.selectbox("Select the type of visualization", [
    "Geospatial Transaction Heatmap",
    "Customer Spending Segmentation",
    "Transaction Contribution by City"
])

# Visualisasi 1, Geospatial Transaction Heatmap
if visualization == "Geospatial Transaction Heatmap":
    st.subheader("Geospatial Transaction Heatmap")
    
    # Check jika HTML filenya ada dan cek di beberapa lokasi untuk hindari masalah path
    possible_paths = [
        "transaction_heatmap.html",
        "../transaction_heatmap.html",
        os.path.join("..", "transaction_heatmap.html"),
        os.path.join(os.getcwd(), "..", "transaction_heatmap.html")
    ]
    
    html_found = False
    for html_path in possible_paths:
        if os.path.exists(html_path):
            # Read the HTML file
            with open(html_path, 'r') as f:
                html_content = f.read()
            
            # Display the HTML content
            components.html(html_content, width=800, height=600)
            html_found = True
            break
    
    if not html_found:
        st.error("File transaction_heatmap.html tidak ditemukan.")
        st.error("Lokasi yang sudah dicoba:")
        for path in possible_paths:
            st.error(f"- {path}")
        st.error("Pastikan file HTML heat map berada di salah satu lokasi tersebut.")

# Visualisasi 2, Customer Spending Segmentation
elif visualization == "Customer Spending Segmentation":
    st.subheader("Customer Spending Segmentation")
    
    # Hitung total pengeluaran per pelanggan
    customer_spending = merged_df.groupby('customer_unique_id')['payment_value'].sum().reset_index()
    customer_spending.columns = ['customer_unique_id', 'total_spending']
    
    # Hitung kuartil
    q1, q3 = customer_spending['total_spending'].quantile([0.25, 0.75])
    
    # Kategorisasi pengeluaran
    def categorize_spending(value):
        if value <= q1:
            return 'Low Spender'
        elif value <= q3:
            return 'Medium Spender'
        else:
            return 'High Spender'
    
    customer_spending['spending_category'] = customer_spending['total_spending'].apply(categorize_spending)
    
    # Hitung persentase
    category_pct = customer_spending['spending_category'].value_counts(normalize=True) * 100
    
    # Visualisasi
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x=category_pct.index,
        y=category_pct.values,
        order=['Low Spender', 'Medium Spender', 'High Spender'],
        palette='viridis',
        hue=category_pct.index,
        dodge=False
    )
    ax.set_title(f'Customer Spending Segmentation (Q1={q1:.2f}, Q3={q3:.2f})')
    ax.set_xlabel('Spending Category')
    ax.set_ylabel('Percentage of Customers (%)')
    ax.set_ylim(0, 100)
    
    # Tambah anotasi persentase
    for p in ax.patches:
        ax.annotate(
            f'{p.get_height():.1f}%', 
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center', va='center', 
            xytext=(0, 10), 
            textcoords='offset points'
        )
    
    plt.tight_layout()
    st.pyplot(fig)

# Visualisasi 3, Transaction Contribution by City
elif visualization == "Transaction Contribution by City":
    st.subheader("Transaction Contribution by City")
    st.dataframe(
        geo_data[['customer_city', 'transaction_count', 'percentage']]
        .sort_values('percentage', ascending=False)
        .style.format({'percentage': '{:.2f}%'})
    )