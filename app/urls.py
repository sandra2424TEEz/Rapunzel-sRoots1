"""
URL configuration for ec project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.contrib import admin
from django.urls import path
from . import views
from app.views import CheckoutView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view 
from .forms import LoginForm,MyPasswordResetForm,MyPasswordChangeForm,MySetPasswordForm,PasswordResetForm


urlpatterns = [
    path('',views.home),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('category/<slug:val>',views.CategoryView.as_view(),name='category'),
    path('product-detail/<int:pk>',views.ProductDetail.as_view(),name='product-detail'),
    path('category-title/<val>',views.CategoryTitle.as_view(),name='category-title'),
    path('profile/',views.ProfileView.as_view(),name='profile'),
    path('address/',views.address,name='address'),
    path('updateaddress/<int:pk>',views.updateAddress.as_view(),name='updateAddress'),
    path('add-to-cart/',views.add_to_cart,name='add-to-cart'),
    path('cart/',views.show_cart,name='showcart'),
    path('pluscart/',views.plus_cart),
    path('minuscart/',views.minus_cart),
    path('removecart/',views.remove_cart),
    path('checkout/',views.CheckoutView.as_view(),name='checkout'),
    path('paymentdone/',views.payment_done,name='paymentdone'),
    path('pay/',views.order_confirmation,name='pay'),
    path('orders/',views.orders,name='orders'),
    path('pluswishlist/',views.plus_wishlist),
    path('minuswishlist/',views.minus_wishlist),
    path('search/',views.search,name='search'),

    #login authentication
    path('registration/', views.CustomerRegistrationView.as_view(), name='customerregistration'),
    path('login/',auth_view.LoginView.as_view(template_name='app/login.html',authentication_form=LoginForm),name='login'),
    
    path('passwordchange/',auth_view.PasswordChangeView.as_view(template_name='app/changepassword.html',form_class=MyPasswordChangeForm,success_url='/passwordchangedone'),name='passwordchange'),
    path('passwordchangedone/',auth_view.PasswordChangeDoneView.as_view(template_name='app/passwordchangedone.html'),name='passwordchangedone'),
    path('logout/',views.Logout,name='logout'),


    path('password-reset/',auth_view.PasswordResetView.as_view(template_name='app/password_reset.html',form_class=MyPasswordResetForm), name='password-reset'),

    path('password-reset/done/',auth_view.PasswordResetDoneView.as_view(template_name='app/password_reset_done.html'),name ='password_reset_done '),

    path('password-reset-confirm/<uidb64>/<token>/',auth_view.PasswordResetConfirmView.as_view(template_name='app/password_reset_confirm.html',form_class=MySetPasswordForm),name='password_reset_confirm'),

    path('password-reset-complete/',auth_view.PasswordResetCompleteView.as_view(template_name='app/password_reset_complete.html'),name='password_reset_complete'),



]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


# admin.site.site_header = 'DAILY DAIRY'
# admin.site.site_title = 'DAILY DAIRY'
# admin.site.site_index_title = ' WELCOME TO DAILY DAIRY'