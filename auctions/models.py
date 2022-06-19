from typing import ClassVar
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

class User(AbstractUser):
    pass

class listings(models.Model):

    categories = [('fashion',"fashion"),
                    ('toys',"toys"),
                    ('electronics',"electronics"),
                    ('antique',"antique"),
                    ('laptop',"laptop"),
                    ('book',"books"),
                    ('furniture',"furniture")]

    owner = models.ForeignKey(User,on_delete=models.CASCADE,related_name="created")
    title = models.CharField(max_length = 50)
    description = models.TextField()
    sbid = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to="images/")
    category = models.CharField(max_length = 20,choices=categories,blank=True,default="none")
    times_bidded = models.IntegerField(default=0)
    ldate = models.DateField(auto_now=True)

class bids(models.Model):
    lid = models.ForeignKey(listings,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="bidder")
    nbid = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])

class comments(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="writer")
    comment = models.TextField()
    lid = models.IntegerField()

class watchlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    listing_id = models.IntegerField()

class wins(models.Model):
    user = models.CharField(max_length=64)
    listing = models.IntegerField()
    owner = models.CharField(max_length=64,null=True)
    title = models.CharField(max_length = 50,null=True)
    winbid = models.DecimalField(max_digits=10,decimal_places=2,null=True)
    image = models.ImageField(upload_to='c_images/')
    times_bidded = models.IntegerField(default=0)
    ldate = models.DateField(auto_now=True)