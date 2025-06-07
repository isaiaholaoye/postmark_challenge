from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("submit/", view=views.submit_message, name="submit_message"),
    path("redirect/", views.inbound_webhook, name="inbound_webhook"),
    path("events/", views.sse_view, name="sse_view"),
    
]
