from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from .models import *
from datetime import date


class AuctionListingForm(ModelForm):
    class Meta:
        model = AuctionListing
        exclude = ['userauction', 'openess', 'winner', 'datefinished']


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
    auctionfinish = AuctionListing.objects.filter(openess='False')
    return render(request, "auctions/index.html", {
        "listofauctions": AuctionListing.objects.all(),
        "auctionfinish": auctionfinish
    })


def auctionCat(request, category1):
    auctionfinish = AuctionListing.objects.filter(openess='False')
    return render(request, "auctions/auctioncategory.html", {
        "listofauctions": AuctionListing.objects.all(),
        "auctionfinish": auctionfinish,
        "category": category1
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
    if request.user.is_authenticated:
        if wishlists.filter(auctions=auctiondisplay, users=request.user):
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
                auction1.price = f.bid
                auction1.save()
                f.save()
                return display(request, auction_id)
            else:
                return render(request, "auctions/inputerror.html", {
                    "simplealert": f"Bidding need to get Higher than {auction1.price}"
                })
    else:
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
            return display(request, auction_id)
        else:
            return render(request, "auctions/inputerror.html", {
                "simplealert": "Invalid comment"
            })
    else:
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


@login_required
def unwishlist(request, auction_id):
    if request.method == "POST":
        auction1 = AuctionListing.objects.get(pk=auction_id)
        unwish = UserWishlist.objects.filter(
            users=request.user.id)
        for x in unwish:
            if x.auctions == auction1:
                x.delete()
        return display(request, auction_id)
        # WORKING


@login_required
def endauction(request, auction_id):
    if request.method == 'POST':
        auction1 = AuctionListing.objects.get(pk=auction_id)

        bid = Bids.objects.all()
        lastbid = bid.filter(auction=auction1).last()

        if lastbid:
            auction1.winner = lastbid.userbid.username
        else:
            auction1.winner = "No Winner"

        auction1.save()
        auction1.datefinished = date.today()
        auction1.openess = False
        auction1.save()
        return index(request)


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        print(user)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return index(request)
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
