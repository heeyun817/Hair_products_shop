from django.shortcuts import render
from shop.models import Item, Category, Manufacturer, Tag, Comment, UserProfile


# Create your views here.

def landing(request):
    manufacturers = Manufacturer.objects.all()
    categories = Category.objects.all()
    recent_posts = Item.objects.order_by('-pk')[:3]

    user_profile = None  # Initialize user_profile as None

    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)

    return render(request,'single_pages/landing.html',{
        'categories': Category.objects.all(),
        'manufacturers': Manufacturer.objects.all(),
        'recent_posts' : recent_posts,
        'user_profile': user_profile
    })

def about_me(request):
    manufacturers = Manufacturer.objects.all()
    categories = Category.objects.all()
    user_profile = None  # Initialize user_profile as None

    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)

    return render(request,'single_pages/about_me.html',{
        'categories': Category.objects.all(),
        'manufacturers': Manufacturer.objects.all(),
        'user_profile': user_profile
    })

