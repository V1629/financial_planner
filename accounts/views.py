from django.shortcuts import render, redirect
from .forms import TransactionForm
from .models import Transaction
from .data_analysis import analyze_transactions
import pandas as pd
import os
from django.shortcuts import render, redirect

DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/transactions.csv')

def home(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()

            # Save/append to CSV file
            df = pd.DataFrame([form.cleaned_data])
            os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
            if not os.path.exists(DATA_PATH):
                df.to_csv(DATA_PATH, index=False)
            else:
                df.to_csv(DATA_PATH, mode='a', header=False, index=False)

            return redirect('home')
    else:
        form = TransactionForm()

    transactions = Transaction.objects.all().order_by('-date_added')
    return render(request, 'finance/home.html', {'form': form, 'transactions': transactions})


def visualize(request):
    summary, charts = analyze_transactions('data/transactions.csv')
    return render(request, 'finance/visualize.html', {
        'summary': summary,
        'charts': charts
    })