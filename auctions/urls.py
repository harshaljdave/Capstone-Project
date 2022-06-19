from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.clisting, name="create"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("comments/<int:id>", views.comment, name="comment"),
    path("arwatchlist",views.arwatchlist,name="watchlist"),
    path("watchlist",views.viewwatchlist,name="viewwatchlist"),
    path("closebid",views.close,name="closebid"),
    path("win",views.wining_auction,name="win"),
    path("closed_listing",views.closed_listing,name="closed"),
    path("view_category",views.view_category,name="viewcategory"),
    path("mylistings",views.mylistings,name="mylistings"),
    path("highest_bid",views.highest_bid,name="highest_bid")
]
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)