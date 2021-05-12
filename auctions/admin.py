from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(AuctionListing)
admin.site.register(Category)
admin.site.register(Comments)
admin.site.register(Bids)
admin.site.register(User)
admin.site.register(UserWishlist)
admin.site.register(AuctionFinished)
