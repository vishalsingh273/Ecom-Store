from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import *
from .forms import *
from .models import Banner, Category, Product
from django.shortcuts import render
from .models import Banner, Category, Product, HomePageSection
from django.db import IntegrityError, transaction
from django.core.paginator import Paginator


def home(request):
    featured_banners = Banner.objects.filter(is_active=True)[:5]
    active_sections = HomePageSection.objects.filter(is_active=True).order_by('order')
    product_list = Product.objects.filter(available=True).order_by('-created')
    paginator = Paginator(product_list, 20)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    featured_categories = Category.objects.all()[:4]
    all_categories = Category.objects.all()

    context = {
        'featured_banners': featured_banners,
        'sections': active_sections,
        'products': products,
        'featured_categories': featured_categories,
        'categories': all_categories,
    }
    return render(request, 'store/home.html', context)



def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    reviews = product.reviews.filter(active=True)
    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(data=request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.product = product
            new_review.user = request.user
            new_review.save()
            messages.success(request, 'Your review has been submitted.')
            return redirect('product_detail', id=id, slug=slug)
    else:
        review_form = ReviewForm()
    
    context = {
        'product': product,
        'reviews': reviews,
        'similar_products': similar_products,
        'review_form': review_form
    }
    return render(request, 'store/product_detail.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if not created:
        order_item.quantity += 1
        order_item.save()
        messages.success(request, f"{product.name} quantity updated in your cart.")
    else:
        messages.success(request, f"{product.name} added to your cart.")
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id)
    if order_item.order.customer.user == request.user:
        order_item.delete()
        messages.success(request, "Item removed from your cart.")
    return redirect('cart')

@login_required
def update_cart(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id)
    if request.method == 'POST' and order_item.order.customer.user == request.user:
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            order_item.quantity = quantity
            order_item.save()
            messages.success(request, "Cart updated successfully.")
        else:
            order_item.delete()
            messages.success(request, "Item removed from your cart.")
    return redirect('cart')

@login_required
def cart(request):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    
    context = {
        'order': order,
        'items': items
    }
    return render(request, 'store/cart.html', context)

@login_required
def checkout(request):
    customer = request.user.customer
    order = Order.objects.get(customer=customer, complete=False)
    items = order.orderitem_set.all()
    
    if request.method == 'POST':
        shipping_form = ShippingAddressForm(request.POST)
        if shipping_form.is_valid():
            shipping = shipping_form.save(commit=False)
            shipping.customer = customer
            shipping.order = order
            shipping.save()
            order.shipping_address = shipping.address
            order.status = 'Processing'
            order.save()
            messages.success(request, "Your order has been placed successfully!")
            return redirect('order_confirmation', order_id=order.id)
    else:
        shipping_form = ShippingAddressForm()
    
    context = {
        'order': order,
        'items': items,
        'shipping_form': shipping_form
    }
    return render(request, 'store/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer)
    return render(request, 'store/order_confirmation.html', {'order': order})


def register(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        customer_form = CustomerForm(request.POST)

        if user_form.is_valid() and customer_form.is_valid():
            try:
                user = user_form.save()

                # Remove any orphaned customer objects for safety
                Customer.objects.filter(user=user).delete()
                Customer.objects.filter(user__isnull=True).delete()

                customer = customer_form.save(commit=False)
                customer.user = user
                customer.save()

                login(request, user)
                messages.success(request, f"Welcome {user.username}! You have registered successfully.")
                return redirect('home')
            except IntegrityError:
                messages.error(request, "An account with these details already exists.")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        user_form = UserCreationForm()
        customer_form = CustomerForm()

    return render(request, 'store/register.html', {
        'user_form': user_form,
        'customer_form': customer_form,
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            # Add error message
            return render(request, 'store/login.html', {
                'error': 'Invalid email or password'
            })
    
    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        customer_form = CustomerUpdateForm(
            request.POST, 
            instance=request.user.customer
        )
        
        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        customer_form = CustomerUpdateForm(instance=request.user.customer)
    
    context = {
        'user_form': user_form,
        'customer_form': customer_form
    }
    return render(request, 'store/profile.html', context)



def category_products(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    return render(request, 'store/category_products.html', {
        'category': category,
        'products': products
    })
    
def category_list(request):
    return {'categories': Category.objects.all()}



def search(request):
    query = request.GET.get('query', '')
    category_slug = request.GET.get('category', '')

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category_slug:
        products = products.filter(category__slug=category_slug)

    context = {
        'query': query,
        'category_slug': category_slug,
        'products': products,
        'categories': Category.objects.all()
    }
    return render(request, 'store/search.html', context)


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

def add_to_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.user.is_authenticated:
        Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('wishlist') 

@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    wishlist_item.delete()
    messages.success(request, 'Product removed from your wishlist!')
    return redirect('wishlist')


def about(request):
    return render(request, 'store/about.html')


def contact(request):
    if request.method == 'POST':
        # Handle contact form submission
        messages.success(request, "Your message has been sent. We'll contact you soon!")
        return redirect('contact')
    return render(request, 'store/contact.html')


@login_required
def orders_view(request):
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer).order_by('-date_ordered')[:10]  # Last 10 orders
    
    context = {
        'orders': orders
    }
    return render(request, 'store/orders.html', context)


def todays_deals(request):
    return render(request, 'store/todays_deals.html')

def customer_service(request):
    return render(request, 'store/customer_service.html')

def registry(request):
    return render(request, 'store/registry.html')

def gift_cards(request):
    return render(request, 'store/gift_cards.html')

def sell(request):
    return render(request, 'store/sell.html')