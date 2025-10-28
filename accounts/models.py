from django.db import models

class Transaction(models.Model):
    product_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    expenditure = models.FloatField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} ({self.category}) - ₹{self.expenditure}"


class Budget(models.Model):
    total_budget = models.FloatField()
    date_set = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Budget: ₹{self.total_budget} set on {self.date_set.strftime('%Y-%m-%d')}"