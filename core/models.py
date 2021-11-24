from django.db import models
from django.contrib.auth.models import User

class UserDetail(models.Model):
    objects=None
    fname = models.CharField( max_length=50)
    lname = models.CharField( max_length=50)
    contact = models.BigIntegerField()
    purpose = models.CharField( max_length=50)
    city = models.CharField( max_length=50)
    plan = models.CharField( max_length=50, choices=[("Monthly","Monthly"), ("Half Yearly","Half Yearly"), ("Yearly","Yearly")])
    payed_on = models.DateTimeField( auto_now=True)
    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))
    subscribed = models.BooleanField(choices=BOOL_CHOICES, default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return str(self.fname + self.lname)

class transaction(models.Model):
    objects=None
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    transaction_amount = models.IntegerField(max_length=10, default=0)
    transaction_type = models.CharField(max_length=50, default=None)
    date = models.DateTimeField(auto_now=True)
    transactionID=models.CharField(max_length=50)

    def __str__(self):
        return str(self.user)
