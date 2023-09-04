from django.db import models
from django.contrib.auth.models import User


class CompanyShare(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_share = models.ForeignKey(CompanyShare, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=[('buy', 'Buy'), ('sell', 'Sell')])
    quantity = models.PositiveIntegerField()
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.company_share} - {self.transaction_type}"


class UserPortfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    holdings = models.ManyToManyField(CompanyShare, through='UserHolding')

    def __str__(self):
        return str(self.user)


class UserHolding(models.Model):
    user_portfolio = models.ForeignKey(UserPortfolio, on_delete=models.CASCADE)
    company_share = models.ForeignKey(CompanyShare, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user_portfolio.user} - {self.company_share}"


class VirtualCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    expiration_date = models.DateField()

    def __str__(self):
        return f"{self.user} - {self.card_number}"
    
    
class PriceChangeIndicator(models.Model):
    company_share = models.OneToOneField(CompanyShare, on_delete=models.CASCADE)
    price_change = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.company_share)
