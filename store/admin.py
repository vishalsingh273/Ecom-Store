# from django.contrib import admin
# from .models import *
# from django.contrib import admin
# from .models import Banner



# @admin.register(Banner)
# class BannerAdmin(admin.ModelAdmin):
#     list_display = ('title', 'is_active', 'created_at')
#     list_filter = ('is_active',)
#     search_fields = ('title',)
# admin.site.register(Category)
# admin.site.register(Product)
# admin.site.register(Customer)
# admin.site.register(Order)
# admin.site.register(OrderItem)

from django.contrib import admin
from .models import Banner, Category, Product, Customer, Order, OrderItem
from django import forms

from django.contrib import admin
from .models import HomePageSection, SectionContent

class SectionContentInline(admin.TabularInline):
    model = SectionContent
    extra = 1
    filter_horizontal = ('products', 'categories')

@admin.register(HomePageSection)
class HomePageSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'section_type', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    inlines = [SectionContentInline]

@admin.register(SectionContent)
class SectionContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'order')
    list_filter = ('section',)
    filter_horizontal = ('products', 'categories')

# Custom Form for Product Admin
class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all categories are available in the dropdown
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].widget.attrs.update({'class': 'form-select'})

# Admin Classes
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'category', 'price', 'stock', 'available')
    list_filter = ('category', 'available')
    search_fields = ('name', 'category__name')
    list_select_related = ('category',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city')
    search_fields = ('user__username', 'phone')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date_ordered', 'complete', 'status')
    list_filter = ('complete', 'status')
    search_fields = ('id', 'customer__user__username')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'quantity', 'date_added')
    list_select_related = ('product', 'order')
    
    
    
def get_form(self, request, obj=None, **kwargs):
    form = super().get_form(request, obj, **kwargs)
    form.base_fields['category'].queryset = Category.objects.all()
    return form