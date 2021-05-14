from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("auctions/inputerror", views.inputerror, name="inputerror"),
    path("accounts/login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("auctions/listListing", views.listing, name="listListing"),
    path("auctions/newListing", views.new_listing, name="newListing"),
    path("auctions/<int:auction_id>", views.display, name="auctiondisplay"),
    path("auctions/<int:auction_id>/bid",
         views.newbiding, name="newbiding"),
    path("auctions/<int:auction_id>/comment",
         views.newcomment, name="newcomment"),
    path("auctions/<int:auction_id>/wishlist",
         views.wishlist, name="wishlist"),
    path("auctions/<int:auction_id>/unwishlist",
         views.unwishlist, name="unwishlist"),
    path("auctions/wishlistpage", views.wishlistpage, name="wishlistpage"),
    path("auctions/<int:auction_id>/endauction",
         views.endauction, name="endauction"),
    path("auctions/<str:category1>",
         views.auctionCat, name="auctionCat"),

]
