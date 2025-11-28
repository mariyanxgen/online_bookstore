from django import forms
from django.contrib.auth.models import User
from .models import * 

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'category', 'price', 'original_price',
            'description', 'cover_image_url', 'publisher', 'publication_date',
            'pages', 'language', 'condition', 'stock_quantity', 'is_featured'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter book title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter author name'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 13-digit ISBN'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'original_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Book description...'}),
            'cover_image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/image.jpg'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Publisher name'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pages': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of pages'}),
            'language': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Language'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        labels = {
            'title': 'Book Title',
            'author': 'Author',
            'isbn': 'ISBN',
            'category': 'Category',
            'price': 'Current Price ($)',
            'original_price': 'Original Price ($)',
            'description': 'Description',
            'cover_image_url': 'Cover Image URL',
            'publisher': 'Publisher',
            'publication_date': 'Publication Date',
            'pages': 'Number of Pages',
            'language': 'Language',
            'condition': 'Condition',
            'stock_quantity': 'Stock Quantity',
            'is_featured': 'Feature on Homepage',
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'cat_description']

        labels = {
            'category_name': 'Category Name',
            'cat_description': 'Description',
        }

        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'cat_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter category descriptions'}),
        }

        help_texts = {
            'category_name': 'Enter a short and unique name for the category.',
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Review title (optional)'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your review...'}),
        }
        
        labels = {
            'rating': 'Rating',
            'title': 'Review Title',
            'comment': 'Your Review',
        }


class BookSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search books by title, author, or ISBN...',
            'autocomplete': 'off'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'step': '0.01'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'step': '0.01'
        })
    )
    
    SORT_CHOICES = [
        ('', 'Default'),
        ('title', 'Title A-Z'),
        ('-title', 'Title Z-A'),
        ('price', 'Price Low to High'),
        ('-price', 'Price High to Low'),
        ('-average_rating', 'Highest Rated'),
        ('-created_at', 'Newest First'),
    ]
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )