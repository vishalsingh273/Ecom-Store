from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth.models import User
from .models import Review, Customer, ShippingAddress
from django import forms
from .models import Product, Category


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['phone', 'address', 'city', 'state', 'zip_code', 'country']

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['address', 'city', 'state', 'zipcode']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)
    
class UserUpdateForm(UserChangeForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['phone', 'address', 'city', 'state', 'zip_code', 'country']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        
        


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'image', 'stock', 'available']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all active categories are shown
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].widget.attrs.update({'class': 'form-select'})