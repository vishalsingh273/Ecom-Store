from .models import Order, Wishlist
from .models import Category


def categories(request):
    return {
        'categories': Category.objects.all()
    }
def cart_counter(request):
    count = 0
    if request.user.is_authenticated:
        try:
            order = Order.objects.get(customer=request.user.customer, complete=False)
            count = order.get_cart_items
        except Order.DoesNotExist:
            pass
    return {'cart_count': count}

def wishlist_counter(request):
    count = 0
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user=request.user).count()
    return {'wishlist_count': count}



def categories_processor(request):
    categories = Category.objects.all()
    return {'categories': categories}


def category_list(request):
    return {'categories': Category.objects.all()}