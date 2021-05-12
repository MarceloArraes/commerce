from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from . import models
from django import forms
from django.forms import ModelForm
from .models import *


class AuctionListingForm(ModelForm):
    class Meta:
        model = AuctionListing
        exclude = ['userauction']


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['categoryname', 'categoryimage']


class BidsForm(ModelForm):
    class Meta:
        model = Bids
        exclude = ['userbid', 'auction', 'datecreate']


class CommentsForm(ModelForm):
    class Meta:
        model = Comments
        exclude = ['auction', 'usercomment', 'datecreate']


def index(request):
    auctionfinish = AuctionFinished.objects.all()
    return render(request, "auctions/index.html", {
        "listofauctions": AuctionListing.objects.all(),
        "auctionfinish": auctionfinish
    })


def inputerror(request):
    return render(request, "auctions/inputerror.html")


def listing(request):
    d = Category.objects.values().values_list("categoryname", "categoryimage")
    # tentar juntar os 2 em um dictionary
    listing = AuctionListing.objects.all()
    return render(request, "auctions/listListing.html", {
        "listListing": listing,
        "categorys": d,
    })


@login_required
def new_listing(request):
    if request.method == "POST":
        form = AuctionListingForm(request.POST)
        f = form.save(commit=False)
        f.userauction = request.user
        if(form.is_valid()):
            f.save()
            return render(request, "auctions/newListing.html", {
                "listingForm": "SAVED. YEAH POST WORKING"
            })
    return render(request, "auctions/newListing.html", {
        "isnew": True,
        "listingForm": AuctionListingForm(),
    })


def display(request, auction_id):
    auctiondisplay = AuctionListing.objects.get(pk=auction_id)
    auctiondisplayall = AuctionListing.objects.all()
    commentsdisplayall = Comments.objects.all()
    bidsall = Bids.objects.all()
    wishlists = UserWishlist.objects.all()

    onwithlist = True
    endauction = False
    if wishlists.filter(auctions=auctiondisplay, users=request.user):
        print(wishlists.filter(auctions=auctiondisplay))
        onwithlist = False
    if auctiondisplay.userauction == request.user.username:
        endauction = True

    return render(request, "auctions/auctiondisplay.html", {
        "auctiondisplay": auctiondisplay,
        "auctiondisplayall": auctiondisplayall,
        "bidsall": reversed(bidsall.all()),
        "BidsForm": BidsForm(),
        "comment": CommentsForm(),
        "commentsall": reversed(commentsdisplayall),
        "wishlists": wishlists,
        "onwithlist": onwithlist,
        "endauction": endauction,

    })


@login_required
def newbiding(request, auction_id):
    if request.method == "POST":
        auction1 = AuctionListing.objects.get(pk=auction_id)
        bidding = BidsForm(request.POST)
        f = bidding.save(commit=False)
        f.auction = auction1
        f.userbid = User.objects.get(pk=request.user.id)
        if bidding.is_valid():
            if f.bid > auction1.price:
                print(f.auction)
                auction1.price = f.bid
                auction1.save()
                f.save()
                print("CHANGED PRICETAG")
                return display(request, auction_id)
            else:
                print("Bidding need to get higher!")
                return render(request, "auctions/inputerror.html", {
                    "simplealert": f"Bidding need to get Higher than {auction1.price}"
                })
    else:
        print("invalid bidding")
        return display(request, auction_id)


@login_required
def newcomment(request, auction_id):
    if request.method == "POST":
        auction1 = AuctionListing.objects.get(pk=auction_id)
        comment = CommentsForm(request.POST)
        f = comment.save(commit=False)
        f.auction = auction1
        f.usercomment = User.objects.get(pk=request.user.id)
        if comment.is_valid():
            f.save()
            print("COMMENT ADDED")
            return display(request, auction_id)
        else:
            print("Invalid Comment")
            return render(request, "auctions/inputerror.html", {
                "simplealert": "Invalid comment"
            })
    else:
        print("Not METHOD POST COMMENT")
        return render(request, "auctions/index.html")


@login_required
def wishlistpage(request):
    return render(request, "auctions/wishlistpage.html")


@login_required
def wishlist(request, auction_id):
    if request.method == "POST":
        auction1 = AuctionListing.objects.get(pk=auction_id)
        user1 = User.objects.get(pk=request.user.id)

        wish = UserWishlist(auctions=auction1,
                            priceonmoment=auction1.price, users=user1)
        wish.save()
        return display(request, auction_id)
        # Working i guess


@login_required
def unwishlist(request, auction_id):
    if request.method == "POST":
        auction1 = AuctionListing.objects.get(pk=auction_id)
        unwish = UserWishlist.objects.filter(
            users=request.user.id)
        for x in unwish:
            if x.auctions == auction1:
                x.delete()
        print(unwish)
        return display(request, auction_id)
        # WORKING


@login_required
def endauction(request, auction_id):
    if request.method == 'POST':
        auction1 = AuctionListing.objects.get(pk=auction_id)
        auctionfinal = AuctionFinished()
        auctionfinal.title = auction1.title
        auctionfinal.descript = auction1.descript
        auctionfinal.price = auction1.price
        auctionfinal.image = auction1.image
        auctionfinal.userauction = auction1.userauction
        auctionfinal.datecreate = auction1.datecreate
        auctionfinal.save()
        auction1.delete()
        # auction1.save()
        print(auctionfinal)
        return index(request)


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

    # Things that its missing
    # Warning screen when posting the same price or lower.
    # Date atribute on comment, auction listening, bid and whatever it needs
    # Uppercase in the user name
    # Maybe make the styles.css work
    # AUTH user authentication (lower priority)
    # WISHLIST of the user. ManytoMany field.
    #
    #
