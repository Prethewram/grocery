from django.urls import path
from .views import *

urlpatterns = [
    
    path('create-delivery-boy/', CreateDeliveryBoyView.as_view(), name='create-delivery-boy'),
    path('delivery-boys/', DeliveryBoyListView.as_view(), name='delivery-boy-list'),
    path('delivery-boys/<int:id>/', DeliveryBoyDetailView.as_view(), name='delivery-boy-detail'),
    path('delivery-boy/login/', DeliveryBoyLoginView.as_view(), name='delivery-boy-login'),
    path('delivery-boy/verify-otp/', DeliveryBoyOTPVerifyView.as_view(), name='delivery-boy-verify-otp'),
    path('delivery-boy/<int:delivery_boy_id>/update-status/', DeliveryBoyStatusUpdateView.as_view(), name='update-delivery-boy-status'),
    path('delivery-boys/active/', ActiveDeliveryBoysView.as_view(), name='active-delivery-boys'),
    path('delivery-boys/inactive/', InactiveDeliveryBoysView.as_view(), name='inactive-delivery-boys'),
    path('admin/assign-order/<str:order_ids>/<int:delivery_boy_id>/', AssignOrderToDeliveryBoyView.as_view(), name='assign_order'),
    path('delivery-boy/assigned-orders/', AllAssignedOrdersView.as_view(), name='all_assigned_orders'),
    path('delivery-boy/assigned-orders/<int:delivery_boy_id>/', DeliveryBoyAssignedOrdersView.as_view(), name='assigned_orders'),
    path('delivery-boy/single-order/<int:pk>/', Singleorderview.as_view(), name='single-orders-view'),
    path('delivery-boy/<int:delivery_boy_id>/completed-orders/', CompletedOrdersView.as_view(), name='completed-orders'),
    path('profile/<int:id>/', deliveryboyprofileview.as_view(), name='profile'),
    path('order-assignment-list/', assigned_order_listview.as_view(), name='Assigned-order-list'),
    path('delivery-boy-by-order-id/<str:order_id>/', DeliveryBoynameView.as_view(), name='delivery_boy_by_order_id'),



] 