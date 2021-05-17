from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date


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
    datecreate = models.DateTimeField(auto_now_add=True)
    userauction = models.CharField(
        max_length=64)
    openess = models.BooleanField(default=True)
    winner = models.CharField(max_length=64, default="")
    datefinished = models.DateTimeField(default=date.today)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"Product: {self.title}, {self.descript}, Category: {self.category}, price: {self.price}"


# specify a title for the listing!, a text-based description!, and what the starting bid should be!. Users should
# also optionally be able to provide a URL for an image for the listing and/or a category (e.g. Fashion, Toys, Electronics, Home, etc.)


class User(AbstractUser):
    userwishes = models.ManyToManyField(
        AuctionListing, through='UserWishlist', default=None)


class UserWishlist(models.Model):
    priceonmoment = models.FloatField()
    auctions = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    users = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Favorite product: {self.auctions.title} of user: {self.users}"


class Bids(models.Model):
    bid = models.FloatField(blank=0.0)
    # date automatico pra momento, hippeninput. (!!)
    # registro de usuario com foreignkey
    auction = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="auctionbid", default=1.1)
    userbid = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="userbid")
    datecreate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bid} and {self.auction} of the user:{self.userbid}"


class Comments(models.Model):
    commentarea = models.CharField(
        max_length=256, blank="", default="")
    auction = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="auctioncomment", default="default")
    usercomment = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="usercomment")
    datecreate = models.DateTimeField(auto_now_add=True)
    # user that made the comment, aqui fica o foreight do usuario

    def __str__(self):
        return f"{self.commentarea} by {self.usercomment}"
