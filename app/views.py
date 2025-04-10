from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render,redirect,HttpResponseRedirect,get_object_or_404
from django.http import HttpResponse
from django.views import View 
import razorpay
from .models import Product ,Cart,Payment,Customer,OrderPlaced,Wishlist
from . forms import CustomerRegistrationForm,CustomerProfileForm,Customer
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.db.models import Q 
from django.contrib.auth.models import User
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import AnonymousUser


# Create your views here.

def home(request):
    if request.user.is_authenticated:
        totalitem = 0
        wishlist_count = 0
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request,'app/home.html',locals())
    else:
        return HttpResponseRedirect('login/')

def about(request):
    totalitem = 0
    wishlist_count = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request,'app/about.html',locals())



def contact(request):
    totalitem = 0
    wishlist_count = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request,'app/contact.html',locals())

class CategoryView(View):
    def get(self,request,val):
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request,'app/category.html',locals())

class CategoryTitle(View):
    def get(self,request,val):
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request,'app/category.html',locals())


class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request,'app/productdetail.html',locals())

class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request, 'app/customerregistration.html',locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Congralution! User Register Successfully')
        else:
            messages.warning(request,'Invalid Input Data')
        return render(request, 'app/customerregistration.html',locals())

class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request,'app/profile.html',locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,'Congralutions! Profile save Successfully')
        else:
            messages.warning(request,'Invalid Input Data')
        return render(request,'app/profile.html',locals())

def address(request):
    add = Customer.objects.filter(user=request.user)
    totalitem = 0
    wishlist_count=0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request,'app/address.html',locals())


class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request,'app/updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,'Congratulations! profile update successfully')
        else:
            messages.warning(request,'Invalid Input Data')
        return redirect('address')

def Logout(request):
    return HttpResponseRedirect('/login/')

def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    if product.stock > 0:
        # Check if the product is already in the user's cart
        cart_item = Cart.objects.filter(user=user, product=product).first()

        if cart_item:
            # If the item exists, you might want to increase the quantity here
            # based on your application's logic.
            # For now, let's assume you don't want to add a duplicate.
            # You could optionally show a message to the user that the item is already in the cart.
            pass # Do nothing, item is already in the cart
        else:
            # If the item doesn't exist, create a new cart item
            Cart(user=user, product=product, quantity=1).save()
            product.stock -= 1
            product.save() # Decrease stock upon adding to cart
    else:
        # Optionally handle the case where the product is out of stock
        # You could redirect back to the product page with an error message
        pass # For now, we'll just not add it

    return redirect('/cart/')



def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    totalitem = 0
    wishlist_count = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request,'app/addtocart.html',locals())

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        try:
            cart_item = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            product = cart_item.product
            if product.stock > cart_item.quantity:
                cart_item.quantity += 1
                cart_item.save()
                product.stock -= 1
                product.save()
                user = request.user
                cart = Cart.objects.filter(user=user)
                amount = 0
                for p in cart:
                    value = p.quantity * p.product.discounted_price
                    amount = amount + value
                totalamount = amount + 40
                data = {
                    'quantity': cart_item.quantity,
                    'amount': amount,
                    'totalamount': totalamount
                }
                return JsonResponse(data)
            else:
                return JsonResponse({'error': 'Stock limit reached'}, status=400) # Or handle this in your frontend
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Item not found in cart'}, status=404)

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        try:
            cart_item = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                cart_item.product.stock += 1
                cart_item.product.save()
            else:
                # If quantity is 1, removing the item is usually the expected behavior
                cart_item.product.stock += 1
                cart_item.product.save()
                cart_item.delete()
                user = request.user
                cart = Cart.objects.filter(user=user)
                amount = 0
                for p in cart:
                    value = p.quantity * p.product.discounted_price
                    amount = amount + value
                totalamount = amount + 40
                data = {
                    'quantity': 0, # Indicate quantity after decrement
                    'amount': amount,
                    'totalamount': totalamount
                }
                return JsonResponse(data)

            user = request.user
            cart = Cart.objects.filter(user=user)
            amount = 0
            for p in cart:
                value = p.quantity * p.product.discounted_price
                amount = amount + value
            totalamount = amount + 40
            data = {
                'quantity': cart_item.quantity,
                'amount': amount,
                'totalamount': totalamount
            }
            return JsonResponse(data)
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Item not found in cart'}, status=404)


def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        try:
            cart_item = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            product = cart_item.product
            product.stock += cart_item.quantity  # Increase stock by the quantity in the cart
            product.save()
            cart_item.delete()
            user = request.user
            cart = Cart.objects.filter(user=user)
            amount = 0
            for p in cart:
                value = p.quantity * p.product.discounted_price
                amount = amount + value
            totalamount = amount + 40
            data = {
                'amount': amount,
                'totalamount': totalamount
            }
            return JsonResponse(data)
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Item not found in cart'}, status=404)

class CheckoutView(View):
    def get(self, request):
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 40
        razorpayamount = int(totalamount*100)
        print(totalamount)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
        data = {"amount":razorpayamount,"currency":"INR","receipt":"order_rcptid_12"}
        payment_response=client.order.create(data=data)
        print(payment_response)
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status = order_status,
            )
            payment.save()
        
        return render(request, 'app/checkout.html', locals())

from django.contrib.auth import login

def payment_done(request):
    if not request.user.is_authenticated:
        # Try to get user from session
        user_id = request.session.get('_auth_user_id')
        if user_id:
            user = User.objects.get(pk=user_id)
            login(request, user)  # Re-authenticate user
        else:
            return redirect('login')  # Redirect to login if session is lost

    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')

    user = request.user  # Ensure user is authenticated

    try:
        customer = Customer.objects.get(id=cust_id)
        payment = Payment.objects.get(razorpay_order_id=order_id)
        payment.paid = True  # Mark payment as successful
        payment.razorpay_payment_id = payment_id
        payment.save()

        cart = Cart.objects.filter(user=user)
        for c in cart:
            OrderPlaced.objects.create(
                user=user,
                customer=customer,
                product=c.product,
                quantity=c.quantity,
                payment=payment
            ).save()
            c.delete()  # Clear cart after placing order
        
        return redirect('orders')  # Redirect to orders page

    except Customer.DoesNotExist:
        messages.error(request, "Customer not found.")
        return redirect('home')

    except Payment.DoesNotExist:
        messages.error(request, "Payment details not found.")
        return redirect('home')


def order_confirmation(request):
    cart_items=Cart.objects.filter(user=request.user)
    famount = 0
    for p in cart_items:
        value = p.quantity * p.product.discounted_price
        famount = famount + value
    totalamount = famount + 40
    razorpayamount = int(totalamount * 100)
    client = razorpay.Client(auth=("rzp_test_9BZyJ3buu1pncT", "6QKQl4eZL8qSwxmeZy02o4tv"))
    data = { "amount": razorpayamount, "currency": "INR", "receipt": "order_rcptid_11" }
    payment = client.order.create(data=data)
    context={
        'amt': razorpayamount,'user':request.user
    }

    return render(request,'app/pay.html',context)

@csrf_exempt
def orders(request):
    totalitem = 0
    wishlist_count = 0
    order_placed = []
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user_id=request.user).count()
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        order_placed=OrderPlaced.objects.filter(user=request.user)
        user = request.user
    context={
        'totalitem':totalitem,
        'wishlist_count':wishlist_count,
        'order_placed':order_placed
    }
    return render(request,'app/orders.html',context)


def plus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        if not Wishlist.objects.filter(user=user, product=product).exists():
            Wishlist(user=user, product=product).save()

        data = {'message': 'Wishlist Added Successfully'}
        return JsonResponse(data)

def minus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist.objects.filter(user=user, product=product).delete()

        data = {'message': 'Wishlist Removed Successfully'}
        return JsonResponse(data)

        

def search(request):
    query=request.GET['search']
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    product = Product.objects.filter(Q(title__icontains=query))
    return render(request,'app/search.html',locals())



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from .models import Product, OrderPlaced, Customer, Payment
from .forms import ProductForm

# Ensure only admin users can access the dashboard
def admin_required(user):
    return user.is_staff  # Only allow staff members (admin) to access

@user_passes_test(admin_required)
def admin_dashboard(request):
    total_products = Product.objects.count()
    total_orders = Payment.objects.count()
    total_customers = Customer.objects.count()
    total_revenue = Payment.objects.filter(paid=True).aggregate(total_amount=models.Sum('amount'))['total_amount'] or 0
    pending_orders = OrderPlaced.objects.filter(status='Pending').count()

    # Product form for adding a product
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')  # Redirect to refresh the dashboard
    else:
        form = ProductForm()

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'form': form,  # Pass form to template
    }
    
    return render(request, 'app/admin_dashboard.html', context)


from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Cart

@login_required
def clear_cart(request):
    # Delete all cart items for the logged-in user
    Cart.objects.filter(user=request.user).delete()
    return redirect('orders')  # Redirect to cart or any desired page
