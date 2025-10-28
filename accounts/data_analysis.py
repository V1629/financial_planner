import matplotlib
matplotlib.use('Agg')  # ✅ Use non-GUI backend for Django
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64
from datetime import datetime


def analyze_transactions(csv_path):
    # ✅ 1. Load and Clean Data
    df = pd.read_csv(csv_path)
    if df.empty:
        return "No transactions available yet.", []

    # Ensure correct columns exist
    expected_cols = {'product_name', 'category', 'expenditure', 'date_added'}
    missing = expected_cols - set(df.columns)
    if missing:
        return f"Missing columns: {', '.join(missing)}", []

    # Convert date column properly
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df.dropna(subset=['date_added', 'expenditure'], inplace=True)
    df['month'] = df['date_added'].dt.to_period('M').astype(str)

    # Basic statistics
    total_spent = df['expenditure'].sum()
    avg_spent = df['expenditure'].mean()
    top_cat = df.groupby('category')['expenditure'].sum().idxmax()

    summary = (
        f"Total spending: ₹{total_spent:,.2f} | "
        f"Average per item: ₹{avg_spent:,.2f} | "
        f"Top category: {top_cat}"
    )

    charts = []

    # ✅ 2. Bar Chart — Category-wise Expenditure
    plt.figure(figsize=(6, 4))
    sns.barplot(x='category', y='expenditure', data=df, estimator=sum, errorbar=None, palette='Blues_d')
    plt.title("Total Expenditure by Category")
    plt.xticks(rotation=25)
    plt.tight_layout()
    charts.append(_get_base64_plot())

    # ✅ 3. Trend Chart — Monthly Spending Trend
    monthly_data = df.groupby('month')['expenditure'].sum().reset_index()
    plt.figure(figsize=(6, 4))
    sns.lineplot(x='month', y='expenditure', data=monthly_data, marker='o', color='green')
    plt.title("Monthly Spending Trend")
    plt.xticks(rotation=30)
    plt.tight_layout()
    charts.append(_get_base64_plot())

    # ✅ 4. Pie Chart — Category Share
    plt.figure(figsize=(5, 5))
    category_share = df.groupby('category')['expenditure'].sum()
    category_share.plot.pie(autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
    plt.ylabel("")
    plt.title("Category-wise Spending Share")
    plt.tight_layout()
    charts.append(_get_base64_plot())

    return summary, charts


# 🧩 Helper Function — Convert Matplotlib Plot to Base64
def _get_base64_plot():
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img_b64
