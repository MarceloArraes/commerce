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
        fields = "__all__"


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['categoryname', 'categoryimage']


class BidsForm(ModelForm):
    class Meta:
        model = Bids
        exclude = ['auction']


class CommentsForm(ModelForm):
    class Meta:
        model = Comments
        exclude = ['auction']


def index(request):
    return render(request, "auctions/index.html")


def listing(request):
    d = Category.objects.values().values_list("categoryname", "categoryimage")
    # tentar juntar os 2 em um dictionary
    return render(request, "auctions/listListing.html", {
        "listListing": AuctionListing.objects.all(),
        "categorys": d,
    })


@login_required
def new_listing(request):
    if request.method == "POST":
        form = AuctionListingForm(request.POST)
        if(form.is_valid()):
            form.save()
            return render(request, "auctions/newListing.html", {
                "listingForm": "SAVED.YEAH POST WORKING"
            })
    return render(request, "auctions/newListing.html", {
        "listingForm": AuctionListingForm(),
    })


def display(request, auction_id):
    auctiondisplay = AuctionListing.objects.get(pk=auction_id)
    auctiondisplayall = AuctionListing.objects.all()
    commentsdisplayall = Comments.objects.all()
    bidsall = Bids.objects.all()

    return render(request, "auctions/auctiondisplay.html", {
        "auctiondisplay": auctiondisplay,
        "auctiondisplayall": auctiondisplayall,
        "bidsall": bidsall.all(),
        "BidsForm": BidsForm(),
        "comment": CommentsForm(),
        "commentsall": commentsdisplayall,

    })


@login_required
def newbiding(request, auction_id):
    if request.method == "POST":
        auction1 = AuctionListing.objects.get(pk=auction_id)
        bidding = BidsForm(request.POST)
        f = bidding.save(commit=False)
        f.auction = auction1
        if bidding.is_valid():
            if f.bid > auction1.price:
                print(f.auction)
                auction1.price = f.bid
                auction1.save()
                f.save()
                print("CHANGED PRICETAG")
                return render(request, "auctions/index.html")
            else:
                print("Bidding need to get higher!")
                return render(request, "auctions/index.html")
    else:
        print("invalid bidding")
        return render(request, "auctions/index.html")


@login_required
def newcomment(request, auction_id):
    if request.method == "POST":
        auction1 = AuctionListing.objects.get(pk=auction_id)
        comment = CommentsForm(request.POST)
        f = comment.save(commit=False)
        f.auction = auction1
        if comment.is_valid():
            print(f.auction)
            f.save()
            print("COMMENT ADDED")
            return render(request, "auctions/index.html")
        else:
            print("Invalid Comment")
            return render(request, "auctions/index.html")
    else:
        print("Not METHOD POST COMMENT")
        return render(request, "auctions/index.html")


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
