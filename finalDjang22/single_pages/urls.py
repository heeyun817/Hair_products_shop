from django.urls import path
from . import views

urlpatterns = [ # IP주소/
    path('',views.landing),   # IP주소/
    path('about/', views.about_me) # IP주소/about_me/
]
