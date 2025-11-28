from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=200)
    cat_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['category_name']

    def __str__(self):
        return self.category_name

    def book_count(self):
        return self.book_set.count()


class Book(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('used_good', 'Used - Good'),
        ('used_fair', 'Used - Fair'),
    ]
    
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True, help_text="13-digit ISBN number")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    original_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Original price for discount calculation")
    description = models.TextField()
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True, help_text="Upload book cover image")
    cover_image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Or provide URL to book cover image")
    publisher = models.CharField(max_length=200, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    pages = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, default='English')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    stock_quantity = models.PositiveIntegerField(default=1)
    is_featured = models.BooleanField(default=False, help_text="Display on homepage")
    is_available = models.BooleanField(default=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_cover_image(self):
        """Returns cover image URL (uploaded file takes priority over URL)"""
        if self.cover_image:
            return self.cover_image.url
        elif self.cover_image_url:
            return self.cover_image_url
        return None
    
    def is_on_sale(self):
        """Check if book is on sale (has original price higher than current price)"""
        return self.original_price and self.original_price > self.price
    
    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if self.is_on_sale():
            return round(((self.original_price - self.price) / self.original_price) * 100)
        return 0
    
    def is_in_stock(self):
        """Check if book is in stock"""
        return self.stock_quantity > 0 and self.is_available
    
    def get_rating_stars(self):
        """Get star rating display"""
        full_stars = int(self.average_rating)
        half_star = 1 if (self.average_rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        return {'full': full_stars, 'half': half_star, 'empty': empty_stars}


class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['book', 'user']  # One review per user per book
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.book.title} - {self.rating} stars by {self.user.username}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.cart_items.all())
    
    def get_total_items(self):
        return sum(item.quantity for item in self.cart_items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'book']
    
    def __str__(self):
        return f"{self.quantity} x {self.book.title}"
    
    def get_total_price(self):
        return self.quantity * self.book.price


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Wishlist for {self.user.username}"
    

