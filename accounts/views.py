from django.shortcuts import render, redirect
from .forms import TransactionForm
from .models import Transaction
from .data_analysis import analyze_transactions, get_spending_insights
import pandas as pd
import os
import csv
from django.contrib import messages

DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/transactions.csv')

def home(request):
    form = TransactionForm()
    transactions = Transaction.objects.all().order_by('-date_added')[:10]  # Show more recent transactions

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save() 

            # Save to CSV as well
            csv_path = 'data/transactions.csv'
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            
            file_exists = os.path.isfile(csv_path)

            try:
                with open(csv_path, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    if not file_exists:
                        # Write headers only once
                        writer.writerow(['product_name', 'category', 'expenditure', 'date_added'])
                    writer.writerow([
                        transaction.product_name,
                        transaction.category,
                        transaction.expenditure,
                        transaction.date_added.strftime('%Y-%m-%d %H:%M:%S')  
                    ])
                
                messages.success(request, 'Transaction added successfully!')
                
            except Exception as e:
                messages.error(request, f'Error saving transaction: {str(e)}')
                
            return redirect('home')

    # Calculate quick stats for dashboard
    total_transactions = Transaction.objects.count()
    try:
        if os.path.isfile('data/transactions.csv'):
            df = pd.read_csv('data/transactions.csv')
            if not df.empty:
                total_spent = df['expenditure'].sum()
                avg_spent = df['expenditure'].mean()
                top_category = df.groupby('category')['expenditure'].sum().idxmax()
            else:
                total_spent = avg_spent = 0
                top_category = 'N/A'
        else:
            total_spent = avg_spent = 0
            top_category = 'N/A'
    except Exception as e:
        print(f"Error calculating stats: {e}")
        total_spent = avg_spent = 0
        top_category = 'N/A'

    context = {
        'form': form, 
        'transactions': transactions,
        'total_transactions': total_transactions,
        'total_spent': total_spent,
        'avg_spent': avg_spent,
        'top_category': top_category
    }
    return render(request, 'finance/home.html', context)


def visualize(request):
    """
    Enhanced visualization view with comprehensive analytics
    """
    csv_path = 'data/transactions.csv'
    
    # Check if CSV file exists
    if not os.path.isfile(csv_path):
        context = {
            'summary': 'No transaction data available yet. Please add transactions first.',
            'charts': [],
            'insights': [],
            'has_data': False
        }
        return render(request, 'finance/visualize.html', context)
    
    try:
        # Get comprehensive analysis
        summary, charts = analyze_transactions(csv_path)
        
        # Get text-based insights
        insights = get_spending_insights(csv_path)
        
        # Read data for additional context
        df = pd.read_csv(csv_path)
        
        # Calculate additional statistics for template
        if not df.empty:
            df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
            df.dropna(subset=['date_added', 'expenditure'], inplace=True)
            
            total_spent = df['expenditure'].sum()
            avg_spent = df['expenditure'].mean()
            median_spent = df['expenditure'].median()
            max_spent = df['expenditure'].max()
            min_spent = df['expenditure'].min()
            std_spent = df['expenditure'].std()
            transaction_count = len(df)
            
            # Category breakdown
            category_totals = df.groupby('category')['expenditure'].sum().to_dict()
            category_counts = df['category'].value_counts().to_dict()
            
            # Top category
            top_category = df.groupby('category')['expenditure'].sum().idxmax()
            top_category_amount = df.groupby('category')['expenditure'].sum().max()
            
            # Most frequent category
            most_frequent_category = df['category'].mode()[0] if len(df) > 0 else 'N/A'
            
            # Top 5 transactions
            top_transactions = df.nlargest(5, 'expenditure')[['product_name', 'expenditure', 'category', 'date_added']].to_dict('records')
            
            # Monthly trend
            df['month'] = df['date_added'].dt.to_period('M').astype(str)
            monthly_totals = df.groupby('month')['expenditure'].sum().to_dict()
            
            has_data = True
        else:
            # Default values if no data
            total_spent = avg_spent = median_spent = max_spent = min_spent = std_spent = 0
            transaction_count = 0
            category_totals = {}
            category_counts = {}
            top_category = 'N/A'
            top_category_amount = 0
            most_frequent_category = 'N/A'
            top_transactions = []
            monthly_totals = {}
            has_data = False
        
        context = {
            'summary': summary,
            'charts': charts,
            'insights': insights,
            'has_data': has_data,
            
            # Statistics
            'total_spent': round(total_spent, 2),
            'avg_spent': round(avg_spent, 2),
            'median_spent': round(median_spent, 2),
            'max_spent': round(max_spent, 2),
            'min_spent': round(min_spent, 2),
            'std_spent': round(std_spent, 2),
            'transaction_count': transaction_count,
            
            # Category data
            'category_totals': category_totals,
            'category_counts': category_counts,
            'top_category': top_category,
            'top_category_amount': round(top_category_amount, 2),
            'most_frequent_category': most_frequent_category,
            
            # Transaction lists
            'top_transactions': top_transactions,
            
            # Trends
            'monthly_totals': monthly_totals,
        }
        
    except FileNotFoundError:
        context = {
            'summary': 'Transaction file not found. Please add some transactions first.',
            'charts': [],
            'insights': [],
            'has_data': False
        }
    except pd.errors.EmptyDataError:
        context = {
            'summary': 'No transaction data available. The file is empty.',
            'charts': [],
            'insights': [],
            'has_data': False
        }
    except Exception as e:
        context = {
            'summary': f'Error analyzing transactions: {str(e)}',
            'charts': [],
            'insights': [],
            'has_data': False,
            'error_message': str(e)
        }
    
    return render(request, 'finance/visualize.html', context)


def delete_transaction(request, transaction_id):
    """
    Delete a transaction from both database and CSV
    """
    if request.method == 'POST':
        try:
            # Delete from database
            transaction = Transaction.objects.get(id=transaction_id)
            transaction.delete()
            
            # Update CSV file - remove the deleted transaction
            csv_path = 'data/transactions.csv'
            if os.path.isfile(csv_path):
                df = pd.read_csv(csv_path)
                # Note: This is a simple approach, you might need to match by multiple fields
                # depending on your data structure
                df = df[df['product_name'] != transaction.product_name]
                df.to_csv(csv_path, index=False)
            
            messages.success(request, 'Transaction deleted successfully!')
            
        except Transaction.DoesNotExist:
            messages.error(request, 'Transaction not found!')
        except Exception as e:
            messages.error(request, f'Error deleting transaction: {str(e)}')
    
    return redirect('home')


def export_data(request):
    """
    Export transactions as CSV download
    """
    from django.http import HttpResponse
    import csv
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="financial_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Product Name', 'Category', 'Expenditure', 'Date Added'])
    
    transactions = Transaction.objects.all().order_by('-date_added')
    for transaction in transactions:
        writer.writerow([
            transaction.product_name,
            transaction.category,
            transaction.expenditure,
            transaction.date_added.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


def clear_all_data(request):
    """
    Clear all transactions (use with caution!)
    """
    if request.method == 'POST':
        try:
            # Delete from database
            Transaction.objects.all().delete()
            
            # Clear CSV file
            csv_path = 'data/transactions.csv'
            if os.path.isfile(csv_path):
                with open(csv_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['product_name', 'category', 'expenditure', 'date_added'])
            
            messages.success(request, 'All transactions cleared successfully!')
            
        except Exception as e:
            messages.error(request, f'Error clearing data: {str(e)}')
    
    return redirect('home')