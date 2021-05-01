from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms


class User(AbstractUser):
    pass


class Category(models.Model):
    categoryname = models.CharField(max_length=32)
    categoryimage = models.URLField(
        blank=True, default='blank')

    def __str__(self):
        return f"{self.categoryname}"


class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    descript = models.CharField(max_length=128)
    image = models.URLField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="auctioncategory")
    price = models.FloatField(blank=0.0, default=1.0)

    def __str__(self):
        return f"Product: {self.title}, {self.descript}, Category: {self.category}, price: {self.price}"

# specify a title for the listing!, a text-based description!, and what the starting bid should be!. Users should
    # also optionally be able to provide a URL for an image for the listing and/or a category (e.g. Fashion, Toys, Electronics, Home, etc.)


class Bids(models.Model):
    bid = models.FloatField(blank=0.0, default=1.0)
    # date automatico pra momento, hippeninput. (!!)
    # registro de usuario com foreignkey
    auction = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="auctionbid", default=1.1)

    def __str__(self):
        return f"{self.bid} and {self.auction}"


class Comments(models.Model):
    commentarea = models.CharField(max_length=256, blank="", default="")
    auction = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="auctioncomment", default="default")
    # user that made the comment, aqui fica o foreight do usuario

    def __str__(self):
        return f"{self.commentarea}"
