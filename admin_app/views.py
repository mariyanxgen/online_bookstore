from urllib import request
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

# Create your views here.
from .models import Book, Category
from .forms import *

def is_admin(user):
    return user.is_superuser

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Enhanced admin dashboard with comprehensive stats"""
    total_books = Book.objects.count()
    total_categories = Category.objects.count()
    featured_books = Book.objects.filter(is_featured=True).count()
    out_of_stock = Book.objects.filter(stock_quantity=0).count()
    recent_books = Book.objects.all()[:5]  # Latest 5 books
    
    # Book stats by category
    category_stats = []
    for category in Category.objects.all():
        category_stats.append({
            'category': category,
            'count': Book.objects.filter(category=category).count()
        })
    
    context = {
        'total_books': total_books,
        'total_categories': total_categories,
        'featured_books': featured_books,
        'out_of_stock': out_of_stock,
        'recent_books': recent_books,
        'category_stats': category_stats,
    }
    return render(request, 'admin_dashboard.html', context)

def add_book(request):
    if request.method=='POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully!')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request,'add_book.html',{'form':form})

def book_list(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    books = Book.objects.all()
    
    if search_query:
        books = books.filter(title__icontains=search_query)
    
    if category_filter:
        books = books.filter(category__id=category_filter)
    
    categories = Category.objects.all()
    
    context = {
        'books': books,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    }
    return render(request, 'book_list.html', context)


def category_list(request):
    cat=Category.objects.all()
    return render (request,'category_list.html',{'cat':cat})


def add_category(request):
    if request.method=="POST":
        form=CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('category_list')
    else:
        form=CategoryForm()    
        return render(request,'add_category.html',{'form':form})
    
def edit_book(request, id): 
    book = get_object_or_404(Book, id=id)
    if request.method == 'POST': 
        form = BookForm(request.POST, instance=book) 
        if form.is_valid(): 
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('book_list')
    else: 
        form = BookForm(instance=book)

    return render(request, 'edit_book.html', {'form': form, 'book': book})


def delete_book(request, id):
    book = get_object_or_404(Book, id=id)
    if request.method == 'POST':
        book.delete()
        messages.success(request, f'"{book.title}" has been deleted successfully!')
        return redirect('book_list')
    return render(request, 'confirm_delete.html', {'book': book})
