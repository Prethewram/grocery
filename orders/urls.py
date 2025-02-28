from django.urls import path
from .views import *

urlpatterns = [

#add to cart
    path('add-to-cart/<int:user_id>/<int:product_id>/', AddToCartView.as_view(), name='cart-add-product'),
#view cart
    path('view-cart/<int:user_id>/', UserCartView.as_view(), name='user_cart'),
#update cart 
    path('cart/update/<int:user_id>/<int:product_id>/', UpdateCartItemQuantityView.as_view(), name='update_cart_item_quantity'),
#remove cart
    path('cart/remove/<int:user_id>/<int:cart_id>/', RemoveCartItemView.as_view(), name='remove_cart_item'),

    path('checkout/cod/<int:user_id>/', CheckoutCODView.as_view(), name='checkout_cod'),
    path('checkout/razorpay/<int:user_id>/', CheckoutRazorpayView.as_view(), name='checkout_razorpay'),
    path('complete-payment/<str:razorpay_order_id>/', CompletePaymentView.as_view(), name='complete_payment'),

    path('orders/<int:user_id>/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:user_id>/<str:order_ids>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/', AllOrdersListView.as_view(), name='all-orders-list'),
    path('order/<int:pk>/', Allorderdetailview.as_view(), name='order-detail'),

    path('orders/filter-by-date/', FilterOrdersByDateView.as_view(), name='filter-orders-by-date'),


    path('api/orders/<int:order_id>/status/', UpdateOrderStatusView.as_view(), name='update_order_status'),
    path('user/<int:user_id>/orders/', UserOrdersListView.as_view(), name='user-orders-list'),

    path('orders/delete-selected/', BulkDeleteSelectedOrdersView.as_view(), name='delete-selected-orders'),
    path('verify-delivery-pin/', VerifyDeliveryPinView.as_view(), name='verify_delivery_pin'),


    path('stock-revenue/', StockAndRevenueView.as_view(), name='stock-revenue'),  
    path('total-price/all-users/', TotalPriceAllUsersView.as_view(), name='total_price_all_users'),
 
    path('total-price/user/<int:user_id>/', TotalPriceByUserView.as_view(), name='total_price_by_user'),
    path('analytics/orders/', ProductOrderAnalyticsView.as_view(), name='product-order-analytics'),



]