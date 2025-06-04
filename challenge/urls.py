from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("submit/", view=views.submit_message, name="submit_message"),
    path("events/", views.sse_view, name="sse_view"),
    
]
