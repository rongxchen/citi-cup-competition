from django.db import models


"""
the way to create a table with django
table name = app01_accountinfo
fields:
    - username varchar(32)
    - password varchar(64)
    - balance double/float (10, 2)
"""


class AccountInfo(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
