from django.shortcuts import render, redirect
from .forms import TransactionForm
from .models import Transaction
from .data_analysis import analyze_transactions
import pandas as pd
import os, csv
from django.shortcuts import render, redirect

DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/transactions.csv')

def home(request):
    form = TransactionForm()
    transactions = Transaction.objects.all().order_by('-date_added')[:5]

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save()  # ✅ Django will auto-set date_added

            # ✅ Save to CSV as well
            csv_path = 'data/transactions.csv'
            file_exists = os.path.isfile(csv_path)

            with open(csv_path, 'a', newline='') as file:
                writer = csv.writer(file)
                if not file_exists:
                    # Write headers only once
                    writer.writerow(['product_name', 'category', 'expenditure', 'date_added'])
                writer.writerow([
                    transaction.product_name,
                    transaction.category,
                    transaction.expenditure,
                    transaction.date_added.strftime('%Y-%m-%d %H:%M:%S')  # ✅ Add auto date
                ])

            return redirect('home')

    context = {'form': form, 'transactions': transactions}
    return render(request, 'finance/home.html', context)

def visualize(request):
    summary, charts = analyze_transactions('data/transactions.csv')
    return render(request, 'finance/visualize.html', {
        'summary': summary,
        'charts': charts
    })