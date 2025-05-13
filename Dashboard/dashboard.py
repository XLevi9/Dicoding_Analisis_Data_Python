import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit.components.v1 as components
import datetime

# set page config
st.set_page_config(
    page_title="E-Commerce Customer Analysis Dashboard",
    page_icon="🛒",
    layout="wide"
)

# title dashboard
st.title("E-Commerce Customer Analysis Dashboard")

# Load datanya
try:
    orders_df = pd.read_csv("Dataset/orders_dataset.csv")
    customers_df = pd.read_csv("Dataset/customers_dataset.csv")
    payments_df = pd.read_csv("Dataset/order_payments_dataset.csv")
    geo_data = pd.read_csv("Dashboard/main_data.csv")
    items_df = pd.read_csv("Dataset/order_items_dataset.csv")
    
    # Convert date columns to datetime
    orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
    
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

# Merge data for visualizations
merged_df = orders_df.merge(customers_df, on='customer_id')
merged_df = merged_df.merge(payments_df, on='order_id')

# Sidebar untuk filter
st.sidebar.header("Filters")

# Filter berdasarkan tanggal (Date Range)
min_date = orders_df['order_purchase_timestamp'].min().date()
max_date = orders_df['order_purchase_timestamp'].max().date()

with st.sidebar.expander("Filter by Date Range", expanded=True):
    start_date = st.date_input('Start Date', min_date)
    end_date = st.date_input('End Date', max_date)

# Filter berdasarkan kota (City)
all_cities = sorted(geo_data['customer_city'].unique())
with st.sidebar.expander("Filter by Cities", expanded=False):
    selected_cities = st.multiselect(
        'Select Cities',
        all_cities,
        default=all_cities[:5]  # Default pilih 5 kota teratas
    )

# Menggunakan order_statuses dan payment_types sebagai default filter tanpa opsi pilihan interaktif
order_statuses = orders_df['order_status'].unique()
selected_statuses = order_statuses

payment_types = payments_df['payment_type'].unique()
selected_payment_types = payment_types

# Apply filters to data
filtered_orders = orders_df[
    (orders_df['order_purchase_timestamp'].dt.date >= start_date) &
    (orders_df['order_purchase_timestamp'].dt.date <= end_date) &
    (orders_df['order_status'].isin(selected_statuses))
]

filtered_merged = merged_df[
    (merged_df['order_purchase_timestamp'].dt.date >= start_date) &
    (merged_df['order_purchase_timestamp'].dt.date <= end_date) &
    (merged_df['order_status'].isin(selected_statuses)) &
    (merged_df['payment_type'].isin(selected_payment_types))
]

# Filter geo_data berdasarkan kota yang dipilih
if selected_cities:
    filtered_geo_data = geo_data[geo_data['customer_city'].isin(selected_cities)].copy()
    # Recalculate percentages based on filtered cities
    total_filtered = filtered_geo_data['transaction_count'].sum()
    filtered_geo_data['percentage'] = (filtered_geo_data['transaction_count'] / total_filtered) * 100
else:
    filtered_geo_data = geo_data.copy()

# Show applied filters summary
st.sidebar.subheader("Applied Filters")
st.sidebar.write(f"Date Range: {start_date} to {end_date}")
st.sidebar.write(f"Cities: {len(selected_cities)} selected")

# Sidebar untuk pilih visualisasi
st.sidebar.header("Select Visualization")
visualization = st.sidebar.selectbox("Select the type of visualization", [
    "Geospatial Transaction Heatmap",
    "Customer Spending Segmentation",
    "Transaction Contribution by City"
])

# KPI Metrics Row
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = len(filtered_orders)
    st.metric("Total Orders", f"{total_orders:,}")

with col2:
    total_customers = filtered_merged['customer_unique_id'].nunique()
    st.metric("Unique Customers", f"{total_customers:,}")

with col3:
    total_revenue = filtered_merged['payment_value'].sum()
    st.metric("Total Revenue", f"R$ {total_revenue:,.2f}")

with col4:
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    st.metric("Average Order Value", f"R$ {avg_order_value:,.2f}")

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
    customer_spending = filtered_merged.groupby('customer_unique_id')['payment_value'].sum().reset_index()
    customer_spending.columns = ['customer_unique_id', 'total_spending']
    
    # Pilihan untuk kustomisasi visualization
    col1, col2 = st.columns(2)
    with col1:
        quartile_type = st.selectbox("Segmentation Method", ["Quartiles (25%-75%)", "Custom Range"])
    
    with col2:
        if quartile_type == "Quartiles (25%-75%)":
            # Hitung kuartil
            q1, q3 = customer_spending['total_spending'].quantile([0.25, 0.75])
        else:
            # Custom range slider
            min_val = float(customer_spending['total_spending'].min())
            max_val = float(customer_spending['total_spending'].max())
            q1, q3 = st.slider("Custom Spending Range (R$)", 
                               min_value=min_val,
                               max_value=max_val,
                               value=(min_val + (max_val-min_val)*0.25, min_val + (max_val-min_val)*0.75))
    
    # Kategorisasi pengeluaran
    def categorize_spending(value):
        if value <= q1:
            return 'Low Spender'
        elif value <= q3:
            return 'Medium Spender'
        else:
            return 'High Spender'
    
    customer_spending['spending_category'] = customer_spending['total_spending'].apply(categorize_spending)
    
    # Hitung persentasenya
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
    ax.set_title(f'Customer Spending Segmentation (Q1=R$ {q1:.2f}, Q3=R$ {q3:.2f})')
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

    # Show data table
    if st.checkbox("Show Customer Segmentation Data"):
        segment_summary = customer_spending.groupby('spending_category').agg(
            customer_count=('customer_unique_id', 'count'),
            avg_spending=('total_spending', 'mean'),
            min_spending=('total_spending', 'min'),
            max_spending=('total_spending', 'max')
        ).reset_index()
        
        st.dataframe(segment_summary.style.format({
            'avg_spending': 'R$ {:.2f}',
            'min_spending': 'R$ {:.2f}',
            'max_spending': 'R$ {:.2f}'
        }))

# Visualisasi 3, Transaction Contribution by City
elif visualization == "Transaction Contribution by City":
    st.subheader("Transaction Contribution by City")
    
    # Opsi sorting
    sort_option = st.selectbox("Sort by", ["Transaction Count (Highest First)", 
                                          "Transaction Count (Lowest First)", 
                                          "City Name (A-Z)",
                                          "City Name (Z-A)"])
    
    # Terapin sorting
    if sort_option == "Transaction Count (Highest First)":
        sorted_data = filtered_geo_data.sort_values('transaction_count', ascending=False)
    elif sort_option == "Transaction Count (Lowest First)":
        sorted_data = filtered_geo_data.sort_values('transaction_count', ascending=True)
    elif sort_option == "City Name (A-Z)":
        sorted_data = filtered_geo_data.sort_values('customer_city', ascending=True)
    else:
        sorted_data = filtered_geo_data.sort_values('customer_city', ascending=False)
    
    # Display data
    st.dataframe(
        sorted_data[['customer_city', 'transaction_count', 'percentage']]
        .style.format({'percentage': '{:.2f}%'})
    )
    
    # Visualisasi top cities bar chartnya
    num_top_cities = st.slider("Number of top cities to show", 5, 20, 10)
    
    top_cities = sorted_data.sort_values('transaction_count', ascending=False).head(num_top_cities)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        x='transaction_count', 
        y='customer_city', 
        data=top_cities,
        palette='viridis'
    )
    ax.set_title(f'Top {num_top_cities} Cities by Transaction Count')
    ax.set_xlabel('Number of Transactions')
    ax.set_ylabel('City')
    
    # Tambah anotasi persentase
    for i, v in enumerate(top_cities['transaction_count']):
        ax.text(v + 0.5, i, f"{top_cities['percentage'].iloc[i]:.1f}%", va='center')
    
    plt.tight_layout()
    st.pyplot(fig)

# Footer
st.markdown("---")
st.markdown("E-Commerce Customer Analysis Dashboard - Created for Dicoding Submission by Oky Askal")