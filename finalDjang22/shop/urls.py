from django.urls import path
from . import views


urlpatterns = [ # IP주소/blog/
    path('', views.ItemList.as_view(), name='item_list'),
    path('<int:pk>/', views.ItemDetail.as_view(), name='item_detail'),
    path('<int:pk>/new_comment/',views.new_comment),
    path('update_comment/<int:pk>/', views.CommentUpdate.as_view()),
    path('delete_comment/<int:pk>/', views.delete_comment),
    path('category/<str:slug>/', views.category_page), # IP주소/blog/category/slug
    path('manufacturer/<str:slug>/', views.manufacturer_page),
    path('tag/<str:slug>/', views.tag_page),  # IP주소/blog/tag/slug
    path('create_post/',views.ItemCreate.as_view()),
    path('update_post/<int:pk>/',views.ItemUpdate.as_view()),
    path('search/<str:q>/', views.ItemSearch.as_view()),
    path('<int:pk>/mypage/', views.mypage, name='mypage'),
    path('<int:pk>/likes/', views.likes),
    path('edit_mypage/', views.edit_mypage, name='edit_mypage'),
]

