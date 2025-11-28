from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import HttpResponse, JsonResponse
from admin_app.models import Book, Category, Cart, CartItem, Wishlist, Review
from admin_app.forms import BookSearchForm, ReviewForm

# Create your views here.
def Register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match!'})
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already taken!'})
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully!")
        return redirect('login')
    return render(request, 'register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid Username or Password!'})
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

def home(request):
    """Modern homepage with featured books, categories, and search"""
    featured_books = Book.objects.filter(is_featured=True, is_available=True)[:6]
    latest_books = Book.objects.filter(is_available=True).order_by('-created_at')[:8]
    top_rated_books = Book.objects.filter(is_available=True, average_rating__gte=4.0).order_by('-average_rating')[:6]
    categories = Category.objects.all()[:6]
    
    # Search form
    search_form = BookSearchForm()
    
    context = {
        'featured_books': featured_books,
        'latest_books': latest_books,
        'top_rated_books': top_rated_books,
        'categories': categories,
        'search_form': search_form,
    }
    return render(request, 'home.html', context)

def book_catalog(request):
    """Book catalog with search and filtering"""
    form = BookSearchForm(request.GET or None)
    books = Book.objects.filter(is_available=True)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort_by = form.cleaned_data.get('sort_by')
        
        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(isbn__icontains=query) |
                Q(description__icontains=query)
            )
        
        if category:
            books = books.filter(category=category)
        
        if min_price:
            books = books.filter(price__gte=min_price)
        
        if max_price:
            books = books.filter(price__lte=max_price)
        
        if sort_by:
            books = books.order_by(sort_by)
    
    context = {
        'books': books,
        'form': form,
        'categories': Category.objects.all(),
    }
    return render(request, 'book_catalog.html', context)

def book_detail(request, book_id):
    """Detailed book view with reviews"""
    book = get_object_or_404(Book, id=book_id)
    reviews = book.reviews.all()[:10]
    related_books = Book.objects.filter(category=book.category, is_available=True).exclude(id=book.id)[:4]
    
    # Review form for authenticated users
    review_form = ReviewForm() if request.user.is_authenticated else None
    user_review = None
    
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(book=book, user=request.user)
        except Review.DoesNotExist:
            pass
    
    if request.method == 'POST' and request.user.is_authenticated and not user_review:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            
            # Update book's average rating
            avg_rating = book.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            book.average_rating = round(avg_rating, 2)
            book.total_reviews = book.reviews.count()
            book.save()
            
            messages.success(request, "Your review has been added!")
            return redirect('book_detail', book_id=book.id)
    
    context = {
        'book': book,
        'reviews': reviews,
        'related_books': related_books,
        'review_form': review_form,
        'user_review': user_review,
    }
    return render(request, 'book_detail.html', context)

@login_required(login_url='login')
def dashboard(request):
    """User dashboard with personalized content"""
    # Get user's cart and wishlist
    cart, created = Cart.objects.get_or_create(user=request.user)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    # Get user's recent reviews
    recent_reviews = Review.objects.filter(user=request.user)[:3]
    
    # Get recommendations based on user's reviews and wishlist
    user_categories = set()
    for review in recent_reviews:
        if review.book.category:
            user_categories.add(review.book.category)
    
    for book in wishlist.books.all():
        if book.category:
            user_categories.add(book.category)
    
    recommended_books = Book.objects.filter(
        category__in=user_categories,
        is_available=True
    ).exclude(
        id__in=[book.id for book in wishlist.books.all()]
    )[:6] if user_categories else Book.objects.filter(is_featured=True)[:6]
    
    context = {
        'cart': cart,
        'wishlist': wishlist,
        'recent_reviews': recent_reviews,
        'recommended_books': recommended_books,
        'cart_total': cart.get_total_price(),
        'cart_items_count': cart.get_total_items(),
    }
    return render(request, 'dashboard.html', context)

@login_required
def add_to_cart(request, book_id):
    """Add book to user's cart"""
    book = get_object_or_404(Book, id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f"'{book.title}' added to your cart!")
    return redirect('book_detail', book_id=book.id)

@login_required
def toggle_wishlist(request, book_id):
    """Toggle book in user's wishlist"""
    book = get_object_or_404(Book, id=book_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if book in wishlist.books.all():
        wishlist.books.remove(book)
        messages.info(request, f"'{book.title}' removed from your wishlist.")
        in_wishlist = False
    else:
        wishlist.books.add(book)
        messages.success(request, f"'{book.title}' added to your wishlist!")
        in_wishlist = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'in_wishlist': in_wishlist})
    
    return redirect('book_detail', book_id=book.id)


def session_login(request):
   if request.method == "POST":
       username = request.POST.get('username') 
       password = request.POST.get('password') 

       try:
          user=User.objects.get(username=username)

          if user.check_password(password):
            request.session['user_id'] = user.id 
            request.session['username'] = user.username 
            request.session['email'] = user.email 
            response = redirect('session_dashboard') 
            response.set_cookie('username', user.username, max_age=3600)
            response.set_cookie('email', user.email, max_age=3600)
            return response
          else: 
                return HttpResponse("Invalid Password")
       except User.DoesNotExist: 
            return HttpResponse("User does not exist")
   return render(request, 'login.html')


def session_dashboard(request):
    username_session = request.session.get('username') 
    username_cookie = request.COOKIES.get('username')
    if 'username' in request.session:
        return render(request, 'dashboard.html',{'username': username_session, 'username_cookie': username_cookie}) 
    else: 
        return redirect('session_login')
    
def session_logout(request):
    request.session.flush()
    return redirect('session_login')
