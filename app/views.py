from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.http import HttpResponse
from django.views import View
from .models import Product, Cart, Payment, Customer, OrderPlaced, Wishlist
from .forms import CustomerRegistrationForm, CustomerProfileForm, Customer
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from django.contrib.auth.models import User
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import AnonymousUser
import uuid  # For generating dummy order IDs


# Create your views here.

def home(request):
    if request.user.is_authenticated:
        totalitem = 0
        wishlist_count = 0
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request, 'app/home.html', locals())
    else:
        return HttpResponseRedirect('login/')


def about(request):
    totalitem = 0
    wishlist_count = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request, 'app/about.html', locals())


def contact(request):
    totalitem = 0
    wishlist_count = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request, 'app/contact.html', locals())


class CategoryView(View):
    # Add this to your CategoryView class or any view that renders products
    def get(self, request, val):
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        
        product = Product.objects.filter(category=val)
        
        # Calculate discount percentage for each product
        for prod in product:
            if prod.discounted_price < prod.selling_price:
                prod.discount_percent = int(((prod.selling_price - prod.discounted_price) * 100) / prod.selling_price)
            else:
                prod.discount_percent = 0
        
        title = Product.objects.filter(category=val).values('title')
        return render(request, 'app/category.html', locals())


class CategoryTitle(View):
    def get(self, request, val):
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request, 'app/category.html', locals())


class ProductDetail(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        totalitem = 0
        wishlist_count = 0
        wishlist_product_ids = []
        
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
            # Get all product IDs in the user's wishlist
            wishlist_product_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
        
        return render(request, 'app/productdetail.html', {
            'product': product, 
            'totalitem': totalitem, 
            'wishlist_count': wishlist_count,
            'wishlist_product_ids': wishlist_product_ids
        })


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request, 'app/customerregistration.html', locals())
    
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Congratulations! User Register Successfully')
        else:
            messages.warning(request, 'Invalid Input Data')
        return render(request, 'app/customerregistration.html', locals())


class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request, 'app/profile.html', locals())
    
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            mail = form.cleaned_data['mail']

            reg = Customer(user=user, name=name, locality=locality, mobile=mobile, city=city, state=state, zipcode=zipcode, mail=mail)
            reg.save()
            messages.success(request, 'Congratulations! Profile save Successfully')
        else:
            messages.warning(request, 'Invalid Input Data')
        return render(request, 'app/profile.html', locals())


def address(request):
    add = Customer.objects.filter(user=request.user)
    totalitem = 0
    wishlist_count = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request, 'app/address.html', locals())


class updateAddress(View):
    def get(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request, 'app/updateAddress.html', locals())
    
    def post(self, request, pk):
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
            messages.success(request, 'Congratulations! profile update successfully')
        else:
            messages.warning(request, 'Invalid Input Data')
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
            pass  # Do nothing, item is already in the cart
        else:
            # If the item doesn't exist, create a new cart item
            Cart(user=user, product=product, quantity=1).save()
            product.stock -= 1
            product.save()  # Decrease stock upon adding to cart
    else:
        # Optionally handle the case where the product is out of stock
        # You could redirect back to the product page with an error message
        pass  # For now, we'll just not add it

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
    return render(request, 'app/addtocart.html', locals())


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
                return JsonResponse({'error': 'Stock limit reached'}, status=400)  # Or handle this in your frontend
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
                    'quantity': 0,  # Indicate quantity after decrement
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
        
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        
        # Calculate total amount
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 40
        
        # Generate a dummy order ID using UUID
        dummy_order_id = str(uuid.uuid4())
        
        # Create a payment record
        payment = Payment(
            user=user,
            amount=totalamount,
            razorpay_order_id=dummy_order_id,  # Using UUID as a dummy order ID
            razorpay_payment_status='created',
        )
        payment.save()
        
        # Store order ID in session for later use
        request.session['dummy_order_id'] = dummy_order_id
        
        return render(request, 'app/checkout.html', locals())


def payment_done(request):
    if not request.user.is_authenticated:
        # Try to get user from session
        user_id = request.session.get('_auth_user_id')
        if user_id:
            user = User.objects.get(pk=user_id)
            login(request, user)  # Re-authenticate user
        else:
            return redirect('login')  # Redirect to login if session is lost

    # Get customer ID from the form
    cust_id = request.GET.get('cust_id')
    
    # Get the dummy order ID from session
    order_id = request.session.get('dummy_order_id')
    if not order_id:
        messages.error(request, "Payment session expired. Please try again.")
        return redirect('checkout')
    
    # Generate a dummy payment ID
    payment_id = f"dummy_pay_{uuid.uuid4().hex[:12]}"

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
        
        # Clear the session
        if 'dummy_order_id' in request.session:
            del request.session['dummy_order_id']
            
        messages.success(request, "Your order has been placed successfully!")
        return redirect('orders')  # Redirect to orders page

    except Customer.DoesNotExist:
        messages.error(request, "Customer not found.")
        return redirect('home')

    except Payment.DoesNotExist:
        messages.error(request, "Payment details not found.")
        return redirect('home')


def order_confirmation(request):
    cart_items = Cart.objects.filter(user=request.user)
    famount = 0
    for p in cart_items:
        value = p.quantity * p.product.discounted_price
        famount = famount + value
    totalamount = famount + 40
    
    # Generate a dummy payment ID for display
    dummy_payment_id = f"DP{uuid.uuid4().hex[:8].upper()}"
    
    context = {
        'amt': totalamount,
        'user': request.user,
        'payment_id': dummy_payment_id
    }

    return render(request, 'app/pay.html', context)

from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Cart, Wishlist, OrderPlaced
from datetime import datetime, timedelta

def send_order_confirmation_email(user, order_placed):
    """
    Sends an order confirmation email to the customer
    
    Args:
        user: The user who placed the order
        order_placed: The list of OrderPlaced objects
    """
    # Get Customer instance for this user
    try:
        customer = Customer.objects.get(user=user)
        recipient = customer.mail
    except Customer.DoesNotExist:
        print(f"❌ No customer record found for user: {user}")
        return

    delivery_date = datetime.now() + timedelta(days=5)
    email_subject = "🧾 Your Order Receipt - Rapunzel's Roots"
    email_body = f"Hi {customer.name},\n\nThank you for your order! Here is your receipt:\n\n"

    total_amount = 0
    for order in order_placed:
        item_total = order.product.discounted_price * order.quantity
        total_amount += item_total
        email_body += (
            f"Product: {order.product.title}\n"
            f"Quantity: {order.quantity}\n"
            f"Price per item: ₹{order.product.discounted_price}\n"
            f"Total for this item: ₹{item_total}\n\n"
        )

    email_body += (
        f"----------------------------------\n"
        f"Total Amount: ₹{total_amount}\n"
        f"Expected Delivery Date: {delivery_date.strftime('%d %B %Y')}\n"
        f"----------------------------------\n"
        f"\nIf you have any questions, feel free to contact us.\n"
        f"\nThanks for shopping with us!\nTeam Rapunzel's Roots"
    )

    sender = settings.EMAIL_HOST_USER

    # Debug logs including receiver's email
    print("\n========== EMAIL DEBUG LOG ==========")
    print(f"📤 Sender:    {sender}")
    print(f"📩 Recipient: {recipient}")
    print(f"📝 Subject:   {email_subject}")
    print(f"💰 Total:     ₹{total_amount}")
    print(f"📦 Delivery:  {delivery_date.strftime('%d %B %Y')}")
    print(f"📨 Email Body Preview:\n{email_body[:300]}{'...' if len(email_body) > 300 else ''}")
    print("=====================================\n")

    try:
        send_mail(
            email_subject,
            email_body,
            sender,
            [recipient],
            fail_silently=False
        )
        print(f"✅ Email sent successfully to {recipient}\n")
    except Exception as e:
        print(f"❌ Failed to send email to {recipient}: {str(e)}\n")

@csrf_exempt
def orders(request):
    totalitem = 0
    wishlist_count = 0
    order_placed = []

    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user_id=request.user).count()
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        order_placed = OrderPlaced.objects.filter(user=request.user)
        user = request.user

        # 📬 Send email immediately when the orders page is accessed
        send_order_confirmation_email(user, order_placed)

    context = {
        'totalitem': totalitem,
        'wishlist_count': wishlist_count,
        'order_placed': order_placed
    }
    return render(request, 'app/orders.html', context)


@csrf_exempt
def orders(request):
    totalitem = 0
    wishlist_count = 0
    order_placed = []

    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user_id=request.user).count()
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        order_placed = OrderPlaced.objects.filter(user=request.user)
        user = request.user

        # 📬 Send email immediately when the orders page is accessed
        send_order_confirmation_email(user, order_placed)

    context = {
        'totalitem': totalitem,
        'wishlist_count': wishlist_count,
        'order_placed': order_placed
    }
    return render(request, 'app/orders.html', context)


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
    query = request.GET['search']
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    product = Product.objects.filter(Q(title__icontains=query))
    return render(request, 'app/search.html', locals())


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


@login_required
def clear_cart(request):
    # Delete all cart items for the logged-in user
    Cart.objects.filter(user=request.user).delete()
    return redirect('orders')  # Redirect to cart or any desired page

def show_wishlist(request):
    user = request.user
    totalitem = 0
    wishlist_count = 0
    
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist = Wishlist.objects.filter(user=user)
        wishlist_count = wishlist.count()
        
        # Get the product objects from wishlist
        wishlist_products = [item.product for item in wishlist]
        
        # Calculate discount percentage for each product
        for product in wishlist_products:
            if product.discounted_price < product.selling_price:
                product.discount_percent = int(((product.selling_price - product.discounted_price) * 100) / product.selling_price)
            else:
                product.discount_percent = 0
    else:
        wishlist_products = []
        return redirect('login')
    
    return render(request, 'app/wishlist.html', {
        'wishlist_products': wishlist_products, 
        'totalitem': totalitem, 
        'wishlist_count': wishlist_count
    })