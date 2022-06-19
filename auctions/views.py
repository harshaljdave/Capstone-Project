from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.forms import widgets
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from itertools import chain
from operator import attrgetter
from django.core.paginator import Paginator
from django import forms
from .models import User,listings, bids, comments, watchlist, wins

class createlisting(forms.ModelForm):
    class Meta:
        model = listings
        exclude = ['owner']
        labels = {'sbid':('Starting price')}

class biding(forms.ModelForm):
    class Meta:
        model = bids
        fields = '__all__'
        labels = {'nbid':('Bid'),}
        widgets = {'user' : widgets.HiddenInput(),
                    'lid' : widgets.HiddenInput()}

class commentform(forms.ModelForm):
    class Meta:
        model = comments
        fields = ('comment',)
        widgets = {'comment' : widgets.Textarea(attrs={'cols':30,'rows':4})}

class category_form(forms.ModelForm):
    class Meta:
        model = listings
        fields = ['category']

def index(request):
    item_list = listings.objects.all()
    paginator = Paginator(item_list, 5) # Show 5 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "auctions/index.html",{
        'page_obj': page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
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


@login_required
def mylistings(request):
    item_list = listings.objects.filter(owner=request.user)
    paginator = Paginator(item_list, 5) # Show 5 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "auctions/index.html",{
        'page_obj': page_obj
    })


@login_required(login_url="/login")
def clisting(request):
    if request.method == "POST":
        user = listings(owner = request.user)
        rawform = createlisting(request.POST,request.FILES)
        form = createlisting(request.POST,request.FILES,instance = user)
        form.category = "none"
        if rawform.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))

    return render(request,"auctions/clisting.html",{
        "form" : createlisting()
    })

def listing(request,id):
    cid = id

    try:
        watchlist.objects.get(listing_id = cid,user = request.user.id)
        added = True
    except:
        added = False

    if request.method == "POST":
        message = "You have to login to use desired feature"
        if request.user.is_authenticated:
            valuechk = float(request.POST["nbid"])
            bidform = biding(request.POST)
            cbid = listings.objects.get(pk=id)
            sbid = cbid.sbid
            old_times_bidded = cbid.times_bidded #Exam
            item_name = cbid.title
            if bidform.is_valid() and valuechk>sbid:
                    try:
                        if bids.objects.get(lid = id) is not None:
                            old_bid_data = bids.objects.get(lid_id=id)
                            old_bid = old_bid_data.user_id
                            old_bidder = User.objects.get(id=old_bid)
                            old_bidder_email = old_bidder.email
                            subject = 'Outbided'
                            message = f'Hi {old_bidder}, Someone just placed a bid higher than yours on {item_name}.Place a higher bid to win!'
                            email_from = settings.EMAIL_HOST_USER
                            recipient_list = [old_bidder.email, ]
                            send_mail( subject, message, email_from, recipient_list )
                            cbid.sbid = valuechk
                            cbid.times_bidded = old_times_bidded + 1 #Exam
                            cbid.save(update_fields = ['sbid','times_bidded','ldate'])
                            bidupdate = bids.objects.get(lid = id)
                            bidupdate.user = request.user
                            bidupdate.nbid = valuechk
                            bidupdate.save(update_fields = ['user','nbid'])
                            return HttpResponseRedirect(f'{id}')

                    except bids.DoesNotExist:
                        cbid.times_bidded = old_times_bidded + 1 #Exam
                        cbid.sbid = valuechk
                        cbid.save(update_fields = ['sbid','times_bidded','ldate'])
                        bidform.save()
                        return HttpResponseRedirect(f'{id}')

            else:
                return render(request,"auctions/listing.html",{
                "data" : listings.objects.get(pk = id),
                "bidform" : biding(initial={'user':request.user,'lid':id}),
                "commentform" : commentform(),
                "all_comments" : comments.objects.filter(lid = id),
                "message" : "value should be greater than bid",
                })
        else:
            return render(request,"auctions/listing.html",{
                "data" : listings.objects.get(pk = id),
                "bidform" : biding(initial={'user':request.user,'lid':id}),
                "commentform" : commentform(),
                "all_comments" : comments.objects.filter(lid = id),
                "message" : message
                })

    return render(request,"auctions/listing.html",{
        "data" : listings.objects.get(pk = id),
        "bidform" : biding(initial={'user':request.user,'lid':id}),
        "commentform" : commentform(),
        "all_comments" : comments.objects.filter(lid = id),
        "added" : added
        })

def comment(request,id):
    cid = id
    if request.method == "POST":
        message = "You have to login to use desired feature"
        if request.user.is_authenticated:
            form = commentform(request.POST)
            if form.is_valid():
                form = commentform(request.POST)
                form1 = form.save(commit=False)
                form1.user = request.user
                form1.lid = cid
                form1.save()
                return redirect("listing",id = cid)
            else:
                pass
        return render(request,"auctions/listing.html",{
        "data" : listings.objects.get(pk = id),
        "bidform" : biding(initial={'user':request.user,'lid':id}),
        "commentform" : commentform(),
        "all_comments" : comments.objects.filter(lid = id),
        "message":message
    })
    return redirect('listing',id = cid)

@login_required(login_url="/login")
def arwatchlist(request):
    lid = request.POST["lid"]
    guser = request.user.id
    form = watchlist()
    try:
        del_form = watchlist.objects.get(listing_id = lid,user = guser)
        del_form.delete()
        return redirect('listing',id = lid)
            
    except watchlist.DoesNotExist:
        form.user = request.user
        form.listing_id = lid
        form.save()
        return redirect('listing',id = lid)

def viewwatchlist(request):
    watch_items = watchlist.objects.filter(user = request.user)
    watch_items = watch_items.values()
    items = []
    for i in watch_items.values():
        a = i.get("listing_id")
        items.append(listings.objects.filter(pk = a))
    return render(request,"auctions/watchlist.html",{
            "items" : items
    })

@login_required
def close(request):
    if request.method == "POST":
        listing_id = request.POST["lid"]
        form = wins()
        del_form = listings.objects.get(pk = listing_id)
        item_owner = del_form.owner_id
        owner_info = User.objects.get(id=item_owner)
        owner_email = owner_info.email
        
        winner = bids.objects.get(lid = listing_id)
        winner_id = winner.user_id
        winner_info = User.objects.get(id=winner_id)
        winner_email = winner_info.email
        
        owner_subject = 'Winner Informtion'
        owner_message = f'Congratulation! {owner_info.username}, your item was auctioned successfully, E-mail of Winner is {winner_email}. You can contact them via this email' 
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [owner_email, ]
        send_mail( owner_subject, owner_message, email_from, recipient_list )
        
        winner_subject = 'Owner Informtion'
        winner_message = f'Congratulation! {winner_info.username}, You won the auction for {del_form.title}. E-mail of Owner is {owner_email}. You can contact them via this email' 
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [winner_email, ]
        send_mail( winner_subject, winner_message, email_from, recipient_list )

        winner = winner.user
        form.user = winner
        form.listing = listing_id
        form.owner = del_form.owner
        form.title = del_form.title
        form.winbid = del_form.sbid
        form.image = del_form.image
        form.ldate = del_form.ldate
        form.times_bidded = del_form.times_bidded
        form.save()
        del_form.delete()
        return redirect("index")

@login_required
def wining_auction(request):
    return render(request,"auctions/winings.html",{
        "won_items" : wins.objects.filter(user=request.user)
    })

@login_required
def closed_listing(request):
    return render(request,"auctions/closedlisting.html",{
        "closed" : wins.objects.all()
    })

def view_category(request):
    if request.method == "POST":
        sort = request.POST["category"]
        view = listings.objects.filter(category = sort)
        return render(request,"auctions/category.html",{
            "form" : category_form(),
            "sorted" : view
        })
    return render(request,"auctions/category.html",{
        "form" : category_form()
    })

@user_passes_test(lambda u: u.is_superuser)
def highest_bid(request):
    if request.method == "POST":
        sdate = request.POST.get('sdate')
        edate = request.POST.get('edate')
        ltype = request.POST.get('type')

        if ltype == "Active":
            bidcount = listings.objects.filter(ldate__gte=sdate,ldate__lte=edate).order_by("-times_bidded")
            return render(request,"auctions/highest_bid.html",{
                "abids":bidcount
            })
        elif ltype == "Closed":
            bidcount = wins.objects.filter(ldate__gte=sdate,ldate__lte=edate).order_by("-times_bidded")
            return render(request,"auctions/highest_bid.html",{
                "cbids":bidcount
            })
        # elif ltype == "Mixed":
        #     activebids = listings.objects.filter(ldate__gte=sdate,ldate__lte=edate)
        #     closebids = wins.objects.filter(ldate__gte=sdate,ldate__lte=edate)
        #     allbids = sorted(
        #         list(chain(activebids,closebids)),
        #         key=attrgetter('ldate'),reverse=True
        #         )
        #     print(allbids)
        #     return render(request,"auctions/highest_bid.html",{
        #         "bids":allbids
        #     })
    return render(request,"auctions/highest_bid.html")