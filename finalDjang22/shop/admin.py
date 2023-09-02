from django.contrib import admin
from .models import Item, Category, Manufacturer, Tag, Comment, UserProfile

# Register your models here.
admin.site.register(Item)

class CategoryAdmin(admin.ModelAdmin): #카테고리 만들기
    prepopulated_fields = {'slug' : ('name',)} #slug값에 지정해줄 값을 ()안에 넣음 ,변경하고 수정하는 것이 가능하도록/ 미리 어떤 특정한 필드에 대해 지정하겠다

admin.site.register(Category, CategoryAdmin)

class ManufacturerAdmin(admin.ModelAdmin): #제조사 만들기
    prepopulated_fields = {'slug' : ('name',)} #slug값에 지정해줄 값을 ()안에 넣음 ,변경하고 수정하는 것이 가능하도록/ 미리 어떤 특정한 필드에 대해 지정하겠다

admin.site.register(Manufacturer, ManufacturerAdmin)

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('name',)}


admin.site.register(Tag, TagAdmin)

admin.site.register(Comment)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'phonenum')

# Register the UserProfile model with the admin site
admin.site.register(UserProfile, UserProfileAdmin)