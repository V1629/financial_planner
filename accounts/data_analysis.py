import matplotlib
matplotlib.use('Agg')  # ✅ Use non-GUI backend for Django
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import io
import base64
from datetime import datetime
from scipy import stats

def analyze_transactions(csv_path):
    """
    Comprehensive transaction analysis with multiple visualizations
    """
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
    
    # Extract time features
    df['month'] = df['date_added'].dt.to_period('M').astype(str)
    df['day_of_week'] = df['date_added'].dt.day_name()
    df['week'] = df['date_added'].dt.isocalendar().week
    df['day'] = df['date_added'].dt.day
    
    # ✅ FIX: Check if time component exists before accessing hour
    try:
        df['hour'] = df['date_added'].dt.hour
    except:
        df['hour'] = 0  # Default to 0 if no time component
    
    # Basic statistics
    total_spent = df['expenditure'].sum()
    avg_spent = df['expenditure'].mean()
    median_spent = df['expenditure'].median()
    max_spent = df['expenditure'].max()
    min_spent = df['expenditure'].min()
    std_spent = df['expenditure'].std()
    top_cat = df.groupby('category')['expenditure'].sum().idxmax()
    transaction_count = len(df)
    
    summary = (
        f"📊 Total Spending: ₹{total_spent:,.2f} | "
        f"📈 Average: ₹{avg_spent:,.2f} | "
        f"📉 Median: ₹{median_spent:,.2f} | "
        f"🔝 Max: ₹{max_spent:,.2f} | "
        f"🔻 Min: ₹{min_spent:,.2f} | "
        f"📏 Std Dev: ₹{std_spent:,.2f} | "
        f"🏆 Top Category: {top_cat} | "
        f"🔢 Transactions: {transaction_count}"
    )
    
    charts = []
    
    # Set seaborn style
    sns.set_style("whitegrid")
    sns.set_palette("husl")
    
    # ✅ 2. Bar Chart — Category-wise Expenditure
    plt.figure(figsize=(10, 6))
    category_totals = df.groupby('category')['expenditure'].sum().sort_values(ascending=False)
    ax = sns.barplot(x=category_totals.index, y=category_totals.values, palette='viridis')
    plt.title("Total Expenditure by Category", fontsize=16, fontweight='bold')
    plt.xlabel("Category", fontsize=12)
    plt.ylabel("Total Expenditure (₹)", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on bars
    for i, v in enumerate(category_totals.values):
        ax.text(i, v + max(category_totals.values) * 0.01, f'₹{v:,.0f}', 
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    charts.append(_get_base64_plot())
    
    # ✅ 3. Trend Chart — Monthly Spending Trend
    plt.figure(figsize=(12, 6))
    monthly_data = df.groupby('month')['expenditure'].sum().reset_index()
    monthly_data['expenditure_cumsum'] = monthly_data['expenditure'].cumsum()
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Monthly spending
    ax1.plot(monthly_data['month'], monthly_data['expenditure'], 
             marker='o', color='#2ecc71', linewidth=2, label='Monthly Spending')
    ax1.fill_between(monthly_data['month'], monthly_data['expenditure'], 
                      alpha=0.3, color='#2ecc71')
    ax1.set_xlabel("Month", fontsize=12)
    ax1.set_ylabel("Monthly Expenditure (₹)", fontsize=12, color='#2ecc71')
    ax1.tick_params(axis='y', labelcolor='#2ecc71')
    ax1.tick_params(axis='x', rotation=45)
    
    # Cumulative spending
    ax2 = ax1.twinx()
    ax2.plot(monthly_data['month'], monthly_data['expenditure_cumsum'], 
             marker='s', color='#e74c3c', linewidth=2, linestyle='--', 
             label='Cumulative Spending')
    ax2.set_ylabel("Cumulative Expenditure (₹)", fontsize=12, color='#e74c3c')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    
    plt.title("Monthly Spending Trend & Cumulative Total", fontsize=16, fontweight='bold')
    fig.legend(loc='upper left', bbox_to_anchor=(0.12, 0.95))
    plt.tight_layout()
    charts.append(_get_base64_plot())
    
    # Pie Chart — Category Share
    plt.figure(figsize=(10, 8))
    category_share = df.groupby('category')['expenditure'].sum()
    colors = sns.color_palette('Set3', len(category_share))
    
    wedges, texts, autotexts = plt.pie(
        category_share.values, 
        labels=category_share.index,
        autopct=lambda pct: f'{pct:.1f}%\n(₹{pct/100*category_share.sum():,.0f})',
        startangle=90,
        colors=colors,
        explode=[0.05] * len(category_share),
        shadow=True
    )
    
    # Style improvements
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
    
    plt.title("Category-wise Spending Distribution", fontsize=16, fontweight='bold')
    plt.tight_layout()
    charts.append(_get_base64_plot())
    
    # Histogram — Expenditure Distribution
    plt.figure(figsize=(10, 6))
    plt.hist(df['expenditure'], bins=30, color='#3498db', alpha=0.7, edgecolor='black')
    plt.axvline(df['expenditure'].mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Mean: ₹{avg_spent:,.2f}')
    plt.axvline(df['expenditure'].median(), color='green', linestyle='--', 
                linewidth=2, label=f'Median: ₹{median_spent:,.2f}')
    plt.xlabel("Expenditure (₹)", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.title("Distribution of Transaction Amounts", fontsize=16, fontweight='bold')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    charts.append(_get_base64_plot())
    
    #Box Plot — Expenditure by Category
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='category', y='expenditure', palette='Set2')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Category", fontsize=12)
    plt.ylabel("Expenditure (₹)", fontsize=12)
    plt.title("Expenditure Distribution by Category (Box Plot)", fontsize=16, fontweight='bold')
    plt.tight_layout()
    charts.append(_get_base64_plot())
    
    # Violin Plot — Detailed Distribution by Category
    plt.figure(figsize=(12, 6))
    sns.violinplot(data=df, x='category', y='expenditure', palette='muted', inner='quartile')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Category", fontsize=12)
    plt.ylabel("Expenditure (₹)", fontsize=12)
    plt.title("Expenditure Distribution by Category (Violin Plot)", fontsize=16, fontweight='bold')
    plt.tight_layout()
    charts.append(_get_base64_plot())
    
    # Heatmap — Spending by Day of Week
    if len(df['day_of_week'].unique()) > 1 and len(df['category'].unique()) > 1:
        plt.figure(figsize=(10, 6))
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Create pivot table
        day_category = df.groupby(['day_of_week', 'category'])['expenditure'].sum().unstack(fill_value=0)
        
        # Reindex to ensure proper day order
        day_category = day_category.reindex([d for d in day_order if d in day_category.index])
        
        sns.heatmap(day_category, annot=True, fmt='.0f', cmap='YlOrRd', 
                    linewidths=0.5, cbar_kws={'label': 'Expenditure (₹)'})
        plt.title("Spending Heatmap: Day of Week vs Category", fontsize=16, fontweight='bold')
        plt.xlabel("Category", fontsize=12)
        plt.ylabel("Day of Week", fontsize=12)
        plt.tight_layout()
        charts.append(_get_base64_plot())
    
    # Time Series with Moving Average
    if len(df) > 7:
        plt.figure(figsize=(12, 6))
        daily_spending = df.groupby(df['date_added'].dt.date)['expenditure'].sum().reset_index()
        daily_spending.columns = ['date', 'expenditure']
        daily_spending['ma_7'] = daily_spending['expenditure'].rolling(window=7, min_periods=1).mean()
        
        plt.plot(daily_spending['date'], daily_spending['expenditure'], 
                marker='o', markersize=4, alpha=0.5, label='Daily Spending')
        plt.plot(daily_spending['date'], daily_spending['ma_7'], 
                color='red', linewidth=2, label='7-Day Moving Average')
        
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Expenditure (₹)", fontsize=12)
        plt.title("Daily Spending with 7-Day Moving Average", fontsize=16, fontweight='bold')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        charts.append(_get_base64_plot())
    
    #Top 10 Highest Transactions
    if len(df) >= 10:
        plt.figure(figsize=(12, 6))
        top_transactions = df.nlargest(10, 'expenditure')[['product_name', 'expenditure', 'category']]
        
        colors_map = plt.cm.Spectral(np.linspace(0, 1, len(top_transactions)))
        bars = plt.barh(range(len(top_transactions)), top_transactions['expenditure'], color=colors_map)
        plt.yticks(range(len(top_transactions)), 
                   [f"{name[:20]}..." if len(name) > 20 else name 
                    for name in top_transactions['product_name']])
        
        # Add value labels
        for i, (idx, row) in enumerate(top_transactions.iterrows()):
            plt.text(row['expenditure'] + max(top_transactions['expenditure']) * 0.01, 
                    i, f"₹{row['expenditure']:,.0f}", va='center', fontsize=10)
        
        plt.xlabel("Expenditure (₹)", fontsize=12)
        plt.title("Top 10 Highest Transactions", fontsize=16, fontweight='bold')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        charts.append(_get_base64_plot())
    
    # Correlation Matrix (if numerical columns exist)
    numerical_df = df.copy()
    numerical_df['month_num'] = df['date_added'].dt.month
    numerical_df['day_num'] = df['date_added'].dt.day
    numerical_df['weekday'] = df['date_added'].dt.weekday
    
    # Select only numerical columns
    corr_columns = ['expenditure', 'month_num', 'day_num', 'weekday']
    corr_data = numerical_df[corr_columns].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_data, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, linewidths=1, 
                cbar_kws={'label': 'Correlation Coefficient'})
    plt.title("Correlation Matrix: Expenditure vs Time Features", fontsize=16, fontweight='bold')
    plt.tight_layout()
    charts.append(_get_base64_plot())
    
    # Spending Patterns by Day of Month
    plt.figure(figsize=(12, 6))
    day_spending = df.groupby('day')['expenditure'].sum().reset_index()
    
    plt.bar(day_spending['day'], day_spending['expenditure'], 
            color='#9b59b6', alpha=0.7, edgecolor='black')
    plt.xlabel("Day of Month", fontsize=12)
    plt.ylabel("Total Expenditure (₹)", fontsize=12)
    plt.title("Spending Pattern by Day of Month", fontsize=16, fontweight='bold')
    plt.xticks(range(1, 32))
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    charts.append(_get_base64_plot())
    
    #Category Count Bar Chart
    plt.figure(figsize=(10, 6))
    category_counts = df['category'].value_counts()
    ax = sns.barplot(x=category_counts.index, y=category_counts.values, palette='plasma')
    plt.xlabel("Category", fontsize=12)
    plt.ylabel("Number of Transactions", fontsize=12)
    plt.title("Transaction Count by Category", fontsize=16, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels
    for i, v in enumerate(category_counts.values):
        ax.text(i, v + max(category_counts.values) * 0.01, str(v), 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    charts.append(_get_base64_plot())
    
    #Average Spending by Category (with error bars)
    plt.figure(figsize=(10, 6))
    category_stats = df.groupby('category')['expenditure'].agg(['mean', 'std']).reset_index()
    
    plt.bar(category_stats['category'], category_stats['mean'], 
            yerr=category_stats['std'], capsize=5, alpha=0.7, 
            color='#16a085', edgecolor='black', error_kw={'linewidth': 2})
    plt.xlabel("Category", fontsize=12)
    plt.ylabel("Average Expenditure (₹)", fontsize=12)
    plt.title("Average Spending by Category (with Standard Deviation)", 
              fontsize=16, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    charts.append(_get_base64_plot())
    
    #Cumulative Spending Over Time
    plt.figure(figsize=(12, 6))
    df_sorted = df.sort_values('date_added')
    df_sorted['cumulative'] = df_sorted['expenditure'].cumsum()
    
    plt.plot(df_sorted['date_added'], df_sorted['cumulative'], 
             linewidth=2, color='#e67e22')
    plt.fill_between(df_sorted['date_added'], df_sorted['cumulative'], 
                      alpha=0.3, color='#e67e22')
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Cumulative Expenditure (₹)", fontsize=12)
    plt.title("Cumulative Spending Over Time", fontsize=16, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    charts.append(_get_base64_plot())
    
    return summary, charts


#Helper Function — Convert Matplotlib Plot to Base64
def _get_base64_plot():
    """Convert current matplotlib plot to base64 string"""
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img_b64


#Additional Helper Function for Advanced Analysis
def get_spending_insights(csv_path):
    """
    Generate text-based insights from transaction data
    """
    df = pd.read_csv(csv_path)
    if df.empty:
        return []
    
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df.dropna(subset=['date_added', 'expenditure'], inplace=True)
    
    insights = []
    
    # Highest spending category
    top_category = df.groupby('category')['expenditure'].sum().idxmax()
    top_amount = df.groupby('category')['expenditure'].sum().max()
    insights.append(f"🏆 Highest spending category: {top_category} (₹{top_amount:,.2f})")
    
    # Average transaction value
    avg_transaction = df['expenditure'].mean()
    insights.append(f"💰 Average transaction value: ₹{avg_transaction:,.2f}")
    
    # Most expensive single purchase
    max_purchase = df['expenditure'].max()
    max_product = df.loc[df['expenditure'].idxmax(), 'product_name']
    insights.append(f"💎 Most expensive purchase: {max_product} (₹{max_purchase:,.2f})")
    
    # Spending trend
    df['month'] = df['date_added'].dt.to_period('M')
    monthly = df.groupby('month')['expenditure'].sum()
    if len(monthly) > 1:
        trend = "increasing" if monthly.iloc[-1] > monthly.iloc[0] else "decreasing"
        insights.append(f"📈 Spending trend: {trend}")
    
    # Most frequent category
    freq_category = df['category'].mode()[0]
    freq_count = (df['category'] == freq_category).sum()
    insights.append(f"🔄 Most frequent category: {freq_category} ({freq_count} transactions)")
    
    return insights