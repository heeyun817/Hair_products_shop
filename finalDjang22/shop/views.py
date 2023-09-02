from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Item, Category, Manufacturer, Tag, Comment, UserProfile
from .forms import CommentForm, UserProfileForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
# Create your views here.

class ItemUpdate(LoginRequiredMixin,UpdateView):
    model = Item
    fields = ['title','price','content','item_image','exp_date','category','manufacturer']
    template_name = 'shop/post_update_form.html'

    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated and request.user == self.get_object().author:
    #         return super(ItemUpdate,self).dispatch(request, *args, **kwargs)
    #     else:
    #         raise PermissionDenied

    def form_valid(self, form):
        response = super(ItemUpdate, self).form_valid(form)
        self.object.tags.clear()  # post가 가지고 있는tags지움
        tags_str = self.request.POST.get('tags_str')  # tags_str이라는 이름을 지닌 input 필드 값을 가져와라
        if tags_str:
            tags_str = tags_str.strip()  # 앞뒤 빈칸 없애줌
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')  # ;을 기준으로 나눈다 배열 형태로 만들어줌
            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)  # 값이 없으면 create
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)  # 한글 허용
                    tag.save()  # 저장
                self.object.tags.add(tag)
        return response

    def get_context_data(self, *, object_list=None, **kwargs):  # 카테고리 html에 추가하기
        context = super(ItemUpdate, self).get_context_data()  # 기존에 제공했던 기능을 그대로 가져와서 context에 저장
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
        context['tags_str_default'] = ';'.join(tags_str_list)
        context['categories'] = Category.objects.all()  # 'categories'라는 변수에 우변의 값(모든 카테고리)을 넣어주겠다
        context['no_category_post_count'] = Item.objects.filter(category=None).count  # post중에서 카테고리 지정 안된 포스트개수 넘겨줌
        if self.request.user.is_authenticated:
            user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            context['user_profile'] = user_profile
        else:
            context['user_profile'] = None
        return context

class ItemCreate(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    model = Item
    fields = ['title','price','content','item_image','exp_date','category','manufacturer'] #,'tags'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_staff):
            form.instance.author = current_user
            response = super(ItemCreate, self).form_valid(form)
            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()
                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')
                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            return response
        else:
            return redirect('/shop/')  # 올바른 유저 아니라면 blog페이지로..

    # 템플릿 : 모델명_form.html
    def get_context_data(self, *, object_list=None, **kwargs): #카테고리 html에 추가하기
        context = super(ItemCreate,self).get_context_data()  #기존에 제공했던 기능을 그대로 가져와서 context에 저장
        context['categories'] = Category.objects.all() #'categories'라는 변수에 우변의 값(모든 카테고리)을 넣어주겠다
        context['no_category_post_count'] = Item.objects.filter(category=None).count #post중에서 카테고리 지정 안된 포스트개수 넘겨줌
        context['manufacturers'] = Manufacturer.objects.all()
        context['no_category_post_count'] = Item.objects.filter(category=None).count()  # post중에서 카테고리 지정 안된 포스트개수 넘겨줌
        if self.request.user.is_authenticated:
            user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            context['user_profile'] = user_profile
        else:
            context['user_profile'] = None
        return context

class ItemList(ListView):
    model = Item
    ordering = '-pk'
    paginate_by = 8

    def get_context_data(self, *, object_list=None, **kwargs): #카테고리 html에 추가하기
        context = super(ItemList,self).get_context_data()  #기존에 제공했던 기능을 그대로 가져와서 context에 저장
        context['categories'] = Category.objects.all() #'categories'라는 변수에 우변의 값(모든 카테고리)을 넣어주겠다
        context['manufacturers'] = Manufacturer.objects.all()
        context['no_category_post_count'] = Item.objects.filter(category=None).count() #post중에서 카테고리 지정 안된 포스트개수 넘겨줌
        if self.request.user.is_authenticated:
            user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            context['user_profile'] = user_profile
        else:
            context['user_profile'] = None
        return context

class ItemSearch(ItemList):  # Postlist상속받음 -> ListView 상속, post_list, post_list.html
    paginate_by = None

    def get_queryset(self): #검색 결과 얻는 함수
        q = self.kwargs['q']
        item_list = Item.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q)
        ).distinct()
        return item_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ItemSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'검색어 : {q} ({self.get_queryset().count()})'
        context['manufacturers'] = Manufacturer.objects.all()
        context['no_category_post_count'] = Item.objects.filter(category=None).count()  # post중에서 카테고리 지정 안된 포스트개수 넘겨줌
        if self.request.user.is_authenticated:
            user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            context['user_profile'] = user_profile
        else:
            context['user_profile'] = None
        return context

class ItemDetail(DetailView):
    model = Item

    def get_context_data(self, **kwargs): #카테고리 html에 추가하기
        context = super(ItemDetail,self).get_context_data()
        context['categories'] = Category.objects.all()
        context['manufacturers'] = Manufacturer.objects.all()
        context['no_category_post_count'] = Item.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        if self.request.user.is_authenticated:
            user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            context['user_profile'] = user_profile
        else:
            context['user_profile'] = None
        return context

#카테고리
def category_page(request, slug):  #카테고리 함수 FBV방식
    if slug == 'no_category': #no_category넘어가면 미분류라는 문자열 저장
        category = '기타'
        item_list = Item.objects.filter(category=None)
    else : #아니면 category모델의 레코드 저장
        category = Category.objects.get(slug=slug)
        item_list = Item.objects.filter(category=category)
    user_profile = None  # Initialize user_profile as None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
    return render(request, "shop/item_list.html", {
        'manufacturers' : Manufacturer.objects.all(),
        'category' : category,
        'item_list' : item_list,
        'categories' : Category.objects.all(),  #post.objects.all() 데이터베이스에서 레코드 가져옴 왼쪽은 html로 넘겨줄 때 이름
        'no_category_post_count' : Item.objects.filter(category=None).count(),
        'user_profile': user_profile
    })

#제조사
def manufacturer_page(request, slug):  #카테고리 함수 FBV방식
    if slug == 'no_manufacturer': #no_category넘어가면 미분류라는 문자열 저장
        manufacturer = '기타'
        item_list = Item.objects.filter(category=None)
    else : #아니면 category모델의 레코드 저장
        manufacturer = Manufacturer.objects.get(slug=slug)
        item_list = Item.objects.filter(manufacturer=manufacturer)

    user_profile = None  # Initialize user_profile as None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)

    return render(request, "shop/item_list.html", {
        'manufacturer' : manufacturer,
        'item_list' : item_list,
        'categories' : Category.objects.all(),
        'manufacturers' : Manufacturer.objects.all(),
        'no_manufacturer_post_count' : Item.objects.filter(manufacturer=None).count(),
        'user_profile': user_profile
    })

#태그 검색 페이지
def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    item_list = tag.item_set.all()
    user_profile = None  # Initialize user_profile as None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
    return render(request, "shop/item_list.html",{
        'tag' : tag,
        'item_list' : item_list,
        'categories': Category.objects.all(),
        'no_category_post_count': Item.objects.filter(category=None).count(),
        'user_profile': user_profile,
        'manufacturers': Manufacturer.objects.all(),
    })

#새 댓글 작성
def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Item,pk=pk)  #왼쪽 pk는 post의 필드 오른쪽 pk는 매개변수
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else: # GET
            return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

#댓글 수정
class CommentUpdate(LoginRequiredMixin,UpdateView):
    model = Comment
    form_class = CommentForm
    # CreateView, UpdateView, form을 사용하면
    # 템플릿이 모델명_forms : comment_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 여기에서 user_profile 값을 가져와서 컨텍스트에 추가합니다.
        user_profile = UserProfile.objects.get(user=self.request.user)
        context['user_profile'] = user_profile

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

#댓글 삭제
def delete_comment(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied


#마이페이지
@login_required
def mypage(request, pk):
    current_User = request.user
    items = Item.objects.filter(author=current_User)
    comments = Comment.objects.filter(author=current_User)
    user_profile = UserProfile.objects.get(user=current_User)
    return render(request, "shop/mypage.html", {
        'user':current_User,
        'items': items,
        'comments': comments,
        'categories': Category.objects.all(),
        'manufacturers': Manufacturer.objects.all(),
        'likes': Item.objects.filter(like_users=current_User),
        'user_profile': user_profile,
    })
    return render(request, 'shop/mypage.html', context)

#프로필 수정

def edit_mypage(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            # Redirect the user to the profile page or another appropriate page.
            return redirect('mypage', pk=request.user.pk)
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'shop/edit_mypage.html', {'form': form, 'user_profile': user_profile,})



#좋아요
def likes(request, pk):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, pk=pk)

        if item.like_users.filter(pk=request.user.pk).exists():
            item.like_users.remove(request.user)
        else:
            item.like_users.add(request.user)
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    raise  redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))