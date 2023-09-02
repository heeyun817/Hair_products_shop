from django.db import models
from django.contrib.auth.models import User
import os

# Create your models here.
#태그
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self): #IP주소/shop/tag/slug/
        return f'/shop/tag/{self.slug}/'

 #카테고리 모델
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    image = models.ImageField(upload_to='shop/images/categories/', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self): #카테고리
        return f'/shop/category/{self.slug}'

    class Meta:
        verbose_name_plural = 'Categories'

#제조사
class Manufacturer(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    address = models.CharField(max_length=100) #주소
    number = models.CharField(max_length=20) #번호
    email = models.CharField(max_length=30,blank=True)  # 이메일
    def __str__(self):
        return self.name

    def get_absolute_url(self):  # 제조사
        return f'/shop/manufacturer/{self.slug}'

#게시글
class Item(models.Model):
    title = models.CharField(max_length=100) #상품명
    price = models.CharField(max_length=30) #가격
    content = models.TextField() #상품설명
    item_image = models.ImageField(upload_to='shop/images/%Y/%m/%d/')  # 상품사진
    exp_date = models.DateField(blank=True)  # 유통기한
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL) #카테고리
    manufacturer = models.ForeignKey(Manufacturer, null=True, on_delete=models.SET_NULL) #제조사
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL) #사용자 삭제되도 글 남겨두고 author필드값만 null로 바뀜
    like_users = models.ManyToManyField(User,related_name='like_shopping',blank=True) #좋아요
    def __str__(self):
        return f'[{self.pk}]{self.title}'

    def get_absolute_url(self):  # 10 링크연결해주기
        return f'/shop/{self.pk}/'


#프로필
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='shop/images/profile/%Y/%m/%d/', null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    phonenum = models.CharField(max_length=20, null=True, blank=True)  # 번호

    def __str__(self):
        return self.user.username

#댓글
class Comment(models.Model):
    post = models.ForeignKey(Item, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f'{self.author} : {self.content}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'

    def get_avatar_url(self):
        if self.author.userprofile.image:
            return self.author.userprofile.image.url
        elif self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return 'https://dummyimage.com/50x50/ced4da/6c757d.jpg'
