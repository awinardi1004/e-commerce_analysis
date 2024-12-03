import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_sum_orders_category_df(df):
    sum_order_category_df = ( df.groupby("product_category_name")
                             .size()
                             .reset_index(name="total_quantity")
                             .sort_values(by="total_quantity", ascending=False))
    
    return sum_order_category_df

def create_cust_bycity_df(df):
    cust_bycity = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    cust_bycity.rename(columns={
        "customer_id" : "customer_count"
    }, inplace=True)

    return cust_bycity

def create_sellers_bycity_df(df):
    sellers_bycity = df.groupby(by="seller_city").seller_id.nunique().reset_index()
    sellers_bycity.rename(columns={
        "seller_id" : "seller_count"
    }, inplace=True)

    return sellers_bycity

def create_order_status_df(df):
    order_status_df = df.groupby(by='order_status').agg({
        "order_id": "nunique",
        "freight_value": "mean"
    }).rename(columns={
        "order_id": "total_order",
        "freight_value": "avg_shipping_costs"
    })
    
    return order_status_df

def create_delivery_diff_status_df(df):
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    df["estimated_delivery_time_diff"] = (df['order_estimated_delivery_date'] - df['order_purchase_timestamp']).dt.days
    
    delivery_diff_status_df = df[["order_status", "estimated_delivery_time_diff"]]
    
    return delivery_diff_status_df

def create_product_performance_df(df):
    sales_count = df.groupby('product_id')['order_item_id'].count().reset_index(name='sales_count')
    df = pd.merge(df, sales_count, on='product_id', how='left')
    correlation_matrix = df[['product_name_lenght', 'product_description_lenght', 'product_photos_qty', 'sales_count']].corr()

    return  df, correlation_matrix



# Load cleaned data
all_df = pd.read_csv("data/all_data.csv")

# create fillter data
datetime_columns = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# # Menyiapkan berbagai dataframe
daily_orders_df = create_daily_orders_df(main_df)
sum_orders_category_df = create_sum_orders_category_df(main_df)
cust_bycity_df = create_cust_bycity_df(main_df)
sellers_bycity_df = create_sellers_bycity_df(main_df)
order_status_df = create_order_status_df(main_df)
delivery_diff_status_df = create_delivery_diff_status_df(main_df)
update_df, corr_matrix = create_product_performance_df(main_df)

# plot number of daily orders (2021)
st.header('Dicoding Collection Dashboard :sparkles:')
st.subheader('Daily Orders')

col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)


st.subheader('Total Number of Daily Transactions') 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader('Total Revenue of Daily Sales')
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["revenue"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

# Product performance
st.subheader("Best and Worst Performing Product by Number of Sales")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(40, 20))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="total_quantity", y="product_category_name", data=sum_orders_category_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="total_quantity", y="product_category_name", data=sum_orders_category_df.sort_values(by="total_quantity", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)


#Top 10 Customer Cities by Customer Count
st.subheader("Top 10 Customer Cities by Customer Count")

top_cust_cities = cust_bycity_df.nlargest(10, "customer_count")

fig, ax = plt.subplots(figsize=(12, 8))  
ax.barh(top_cust_cities["customer_city"], top_cust_cities["customer_count"], color="#72BCD4")
ax.set_xlabel("Number of Customers")
ax.set_ylabel("Customer City")
ax.invert_yaxis()

st.pyplot(fig)

# Top 10 Customer Cities by Customer Count
st.subheader("Top 10 Customer Cities by Customer Count")

top_seller_city = sellers_bycity_df.nlargest(10, "seller_count")

fig, ax = plt.subplots(figsize=(12,8))
ax.barh(top_seller_city['seller_city'], top_seller_city["seller_count"], color="#72BCD4")
ax.set_xlabel("Number of Sellers")
ax.set_ylabel("Seller City")
ax.invert_yaxis()

st.pyplot(fig)

# Order Status Distribution by Total Orders
st.subheader('Order Status Distribution by Total Orders')

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(order_status_df.index, order_status_df['total_order'], color="#72BCD4")

# ax.set_title("Order Status Distribution by Total Orders")
ax.set_xlabel("Order Status")
ax.set_ylabel("Total Orders")
ax.set_xticks(range(len(order_status_df.index)))
ax.set_xticklabels(order_status_df.index, rotation=45, ha='right')

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 1,  # Posisi teks di atas bar
            f'{int(height)}',  # Nilai yang ditampilkan (total_order)
            ha='center', va='bottom', fontsize=10)

st.pyplot(fig)

# Average Freight Value by Order Status
st.subheader('Average Freight Value by Order Status')

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(order_status_df.index, order_status_df['avg_shipping_costs'], color="#72BCD4")

ax.set_xlabel("Order Status")
ax.set_ylabel("Average Freight Value")
ax.set_xticks(range(len(order_status_df.index)))
ax.set_xticklabels(order_status_df.index, rotation=45, ha='right')

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 1, 
            f'{int(height)}', 
            ha='center', va='bottom', fontsize=10)

st.pyplot(fig)

# Estimated Delivery Time Difference by Order Status"
st.subheader("Estimated Delivery Time Difference by Order Status")

fig, ax = plt.subplots(figsize=(12, 6))
sns.boxplot(x='order_status', y='estimated_delivery_time_diff', data=delivery_diff_status_df, palette="Set2", ax=ax)

ax.set_xlabel("Order Status", fontsize=12)
ax.set_ylabel("Estimated Delivery Time Difference (Days)", fontsize=12)

st.pyplot(fig)


# Product Performance Analysis
st.subheader('Product Performance Analysis')

# Korelasi Antara Detail Produk dan Jumlah Penjualan
st.markdown(
    "<p style='font-size:16px; font-weight:bold;'>Korelasi Antara Detail Produk dan Jumlah Penjualan</p>", 
    unsafe_allow_html=True
)


fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')

st.pyplot(fig)

# Hubungan Panjang Nama Produk dan Jumlah Penjualan
st.markdown(
    "<p style='font-size:16px; font-weight:bold;'>Hubungan Panjang Nama Produk dan Jumlah Penjualan</p>", 
    unsafe_allow_html=True
)

fig, ax= plt.subplots(figsize=(8, 6))
sns.scatterplot(data=update_df, x='product_name_lenght', y='sales_count', hue='product_photos_qty', palette='viridis')
ax.set_xlabel('Panjang Nama Produk')
ax.set_ylabel('Jumlah Penjualan')

st.pyplot(fig)

# Hubungan Panjang Deskripsi Produk dan Jumlah Penjualan
st.markdown(
    "<p style='font-size:16px; font-weight:bold;'>Hubungan Panjang Deskripsi Produk dan Jumlah Penjualan</p>", 
    unsafe_allow_html=True
)

fig, ax=plt.subplots(figsize=(8, 6))
sns.scatterplot(data=update_df, x='product_description_lenght', y='sales_count', hue='product_photos_qty', palette='viridis')
ax.set_xlabel('Panjang Deskripsi Produk')
ax.set_ylabel('Jumlah Penjualan')

st.pyplot(fig)

# Hubungan Jumlah Foto Produk dan Jumlah Penjualan
st.markdown(
    "<p style='font-size:16px; font-weight:bold;'>Hubungan Jumlah Foto Produk dan Jumlah Penjualan</p>", 
    unsafe_allow_html=True
)
fig, ax=plt.subplots(figsize=(8, 6))
sns.boxplot(data=update_df, x='product_photos_qty', y='sales_count', palette='Set2')
ax.set_xlabel('Jumlah Foto Produk')
ax.set_ylabel('Jumlah Penjualan')

st.pyplot(fig)