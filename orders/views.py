from rest_framework import generics
from .models import Cart, Order
from .serializers import *
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Cart, Product
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F
import razorpay
import random
import string
from decimal import Decimal  
from django.utils.dateparse import parse_date
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
import hmac
import hashlib
from django.utils.encoding import force_bytes

User = get_user_model()

class AddToCartView(APIView):
    def post(self, request, user_id, product_id):
        user = get_object_or_404(User, pk=user_id)
        product = get_object_or_404(Product, pk=product_id)
        
        quantity = request.data.get('quantity', 1)
        selected_weight = request.data.get('weight')

        if not selected_weight:
            return Response({"error": "Please select a weight"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the price for the selected weight (handles both dict and list)
        selected_price = product.get_price_for_weight(selected_weight)
        if selected_price is None:
            return Response({"error": "Invalid weight selection"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = Cart.objects.get_or_create(user=user, product=product)

        if created:
            cart_item.quantity = quantity
            cart_item.selected_weight = selected_weight
            cart_item.price = selected_price
            cart_item.save()
            serializer = CartSerializer(cart_item, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Item already in cart, no changes made"}, status=status.HTTP_200_OK)

        
class UpdateCartItemQuantityView(APIView):
    def put(self, request, user_id, product_id):
        return self.update_cart_item(request, user_id, product_id, partial=False)

    def patch(self, request, user_id, product_id):
        return self.update_cart_item(request, user_id, product_id, partial=True)

    def update_cart_item(self, request, user_id, product_id, partial):
        user = get_object_or_404(User, pk=user_id)
        product = get_object_or_404(Product, pk=product_id)
        
        quantity = request.data.get('quantity')
        selected_weight = request.data.get('weight')

        
        if not partial or 'quantity' in request.data:
            if quantity is None or not str(quantity).isdigit() or int(quantity) < 1:
                return Response({"detail": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if not partial or 'weight' in request.data:
            if not selected_weight:
                return Response({"detail": "Selected weight is required"}, status=status.HTTP_400_BAD_REQUEST)

        
        cart_item = get_object_or_404(Cart, user=user, product=product)

        
        if selected_weight:
            selected_weight_price = product.get_price_for_weight(selected_weight)
            if selected_weight_price is None:
                return Response({"detail": "Invalid weight selection"}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.selected_weight = selected_weight
            cart_item.price = selected_weight_price
        
        
        if quantity:
            cart_item.quantity = int(quantity)
        
        
        cart_item.total_price = cart_item.quantity * cart_item.price
        cart_item.save()

        
        total_cart_price = Cart.objects.filter(user=user).aggregate(total=Sum(F('quantity') * F('price')))['total']

        
        serializer = CartSerializer(cart_item, context={'request': request})

        
        response_data = {
            'cart_item': serializer.data,
            'total_cart_price': total_cart_price
        }

        return Response(response_data, status=status.HTTP_200_OK)

class UserCartView(APIView):
    def get(self, request, user_id):
        cart_items = Cart.objects.filter(user_id=user_id).prefetch_related('product')
        total_cart_price = Decimal('0.00') 

        for cart_item in cart_items:
            product = cart_item.product
            selected_weight = cart_item.selected_weight

           
            selected_weight_price = Decimal(product.get_price_for_weight(selected_weight))  
            cart_item.total_price = cart_item.quantity * selected_weight_price

            total_cart_price += cart_item.total_price

        serializer = CartSerializer(cart_items, context={'request': request}, many=True)
        response_data = {
            'message': 'Products Retrieved Successfully',
            'cart_items': serializer.data,
            'total_cart_price': total_cart_price
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
class RemoveCartItemView(APIView):
    def delete(self, request, user_id, cart_id):
        user = get_object_or_404(User, pk=user_id)
        cart_item = get_object_or_404(Cart, pk=cart_id, user=user)
        cart_item.delete()
        return Response({"detail": "Item removed from cart"})
    
# Razorpay client initialization
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


from django.db import transaction

# COD Checkout View
class CheckoutCODView(APIView):
    permission_classes = []

    def generate_order_id(self):
        """Generate a unique order ID."""
        prefix = "ORD"
        random_number = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{random_number}"

    def generate_delivery_pin(self):
        """Generate a 4-digit random delivery pin."""
        return ''.join(random.choices(string.digits, k=4))

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_404_NOT_FOUND)

        total_price = 0
        total_cart_items = cart_items.count()
        product_ids = []
        product_names = []
        selected_weights = []
        quantities = []

        for cart_item in cart_items:
            product = cart_item.product
            selected_weight = cart_item.selected_weight

            weight_data = next((w for w in product.weights if w.get("weight") == selected_weight), None)

            if weight_data is None:
                return Response({"error": f"{selected_weight} not available for {product.name}"}, status=status.HTTP_400_BAD_REQUEST)

            stock_quantity = int(weight_data.get("quantity", 0))
            selected_weight_price = float(weight_data.get("price", product.price))

            if stock_quantity < cart_item.quantity:
                return Response({"error": f"Not enough stock for {product.name} ({selected_weight})"}, status=status.HTTP_400_BAD_REQUEST)

            total_price += selected_weight_price * cart_item.quantity
            product_ids.append(str(product.id))
            product_names.append(product.name)
            selected_weights.append(cart_item.selected_weight)
            quantities.append(str(cart_item.quantity))

            # Update stock quantity
            weight_data["quantity"] = stock_quantity - cart_item.quantity
            product.save()

        unique_order_id = self.generate_order_id()
        delivery_pin = self.generate_delivery_pin()

        # Create the order
        order = Order.objects.create(
            user=user,
            payment_method='COD',
            product_ids=",".join(product_ids),
            product_names=",".join(product_names),
            total_price=total_price,
            total_cart_items=total_cart_items,
            selected_weights=",".join(selected_weights),
            quantities=",".join(quantities),
            order_ids=unique_order_id,
            delivery_pin=delivery_pin
        )

        # Clear the user's cart
        cart_items.delete()

        return Response({
            "message": "Checkout successful",
            "total_price": total_price,
            "total_cart_items": total_cart_items,
            "order_id": order.order_ids,
            "delivery_pin": delivery_pin
        }, status=status.HTTP_201_CREATED)



class CheckoutRazorpayView(APIView):
    permission_classes = []

    def generate_order_id(self):
        """Generate a unique order ID."""
        prefix = "ORD"
        random_number = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{random_number}"

    def generate_delivery_pin(self):
        """Generate a 4-digit random delivery pin."""
        return ''.join(random.choices(string.digits, k=4))

    def post(self, request, user_id):
        # Verify the user and retrieve cart items
        user = get_object_or_404(User, id=user_id)
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_404_NOT_FOUND)

        total_price = 0
        total_cart_items = cart_items.count()
        product_ids = []
        product_names = []
        selected_weights = []
        quantities = []

        for cart_item in cart_items:
            product = cart_item.product
            selected_weight = cart_item.selected_weight

            # Fetch weight data
            weight_data = next((w for w in product.weights if w.get("weight") == selected_weight), None)

            if weight_data is None:
                return Response({"error": f"{selected_weight} not available for {product.name}"}, status=status.HTTP_400_BAD_REQUEST)

            stock_quantity = int(weight_data.get("quantity", 0))
            selected_weight_price = float(weight_data.get("price", product.price))

            # Check stock quantity
            if stock_quantity < cart_item.quantity:
                return Response({"error": f"Not enough stock for {product.name} ({selected_weight})"}, status=status.HTTP_400_BAD_REQUEST)

            total_price += selected_weight_price * cart_item.quantity
            product_ids.append(str(product.id))
            product_names.append(product.name)
            selected_weights.append(cart_item.selected_weight)
            quantities.append(str(cart_item.quantity))

            # Deduct the purchased quantity from stock
            weight_data["quantity"] = stock_quantity - cart_item.quantity
            product.save()

        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': int(total_price * 100),  # Amount in paise
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Create the order in the database with Razorpay order ID
        unique_order_id = self.generate_order_id()
        delivery_pin = self.generate_delivery_pin()

        order = Order.objects.create(
            user=user,
            payment_method="Razorpay",
            total_price=total_price,
            status="WAITING FOR CONFIRMATION",
            razorpay_order_id=razorpay_order['id'],
            order_ids=unique_order_id,
            delivery_pin=delivery_pin,
            product_ids=",".join(product_ids),
            product_names=",".join(product_names),
            selected_weights=",".join(selected_weights),
            quantities=",".join(quantities),
            total_cart_items=total_cart_items
        )

        return Response({
            "message": "Checkout initiated successfully",
            "razorpay_order_id": razorpay_order['id'],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": total_price,
            "currency": "INR",
        }, status=status.HTTP_200_OK)


class CompletePaymentView(APIView):

    def post(self, request, razorpay_order_id):
        # Retrieve the order using the razorpay_order_id
        order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)

        if order.status != "WAITING FOR CONFIRMATION":
            return Response({"error": "Order already processed"}, status=status.HTTP_400_BAD_REQUEST)

        # Update order status to completed
        order.status = "WAITING FOR CONFIRMATION"
        order.save()

        # Store details before deletion
        total_price = order.total_price
        total_cart_items = order.total_cart_items
        unique_order_id = order.order_ids
        delivery_pin = order.delivery_pin

        # Delete the order and cart items for the user associated with the order
        Cart.objects.filter(user=order.user).delete()

        return Response({
            "message": "Payment successful",
            "total_price": total_price,
            "status": True
        }, status=status.HTTP_200_OK)


# class CompletePaymentView(APIView):

#     def generate_order_id(self):
#         """Generate a unique order ID."""
#         prefix = "ORD"
#         random_number = ''.join(random.choices(string.digits, k=6))
#         return f"{prefix}{random_number}"

#     def generate_delivery_pin(self):
#         """Generate a 4-digit random delivery pin."""
#         return ''.join(random.choices(string.digits, k=4))

#     def post(self, request, razorpay_order_id):
#         # Retrieve the order using the razorpay_order_id
#         order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)

#         if order.status != "WAITING FOR CONFIRMATION":
#             return Response({"error": "Order already processed"}, status=status.HTTP_400_BAD_REQUEST)

#         # Generate unique order ID and delivery pin
#         unique_order_id = self.generate_order_id()
#         delivery_pin = self.generate_delivery_pin()

#         # Update the order status and finalize the order
#         order.status = "COMPLETED"  # Update based on your workflow
#         order.order_ids = unique_order_id
#         order.delivery_pin = delivery_pin
#         order.save()

#         # Delete cart items for the user associated with the order
#         Cart.objects.filter(user=order.user).delete()  # Ensure order.user refers to the correct user

#         return Response({
#             "message": "Payment successful",
#             "total_price": order.total_price,
#             "total_cart_items": order.total_cart_items,
#             "order_ids": order.order_ids,
#             "delivery_pin": order.delivery_pin,
#             "order_id": order.id,
#             "status": True
#         }, status=status.HTTP_200_OK)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Order.objects.filter(user_id=user_id).order_by('-created_at') 

class OrderDetailView(APIView):
    def get(self, request, user_id, order_ids):

        user = get_object_or_404(User, id=user_id)
        order = get_object_or_404(Order, user=user, order_ids=order_ids)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
class AllOrdersListView(generics.ListAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = AllOrdersSerializer
    permission_classes = []

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        response_data = {
            'total_count': queryset.count(),
            'results': serializer.data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class Allorderdetailview(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = AllOrdersSerializer
    permission_classes = []  
    
    lookup_field = 'pk'  

    def get_object(self):
        order_id = self.kwargs.get(self.lookup_field)
        return generics.get_object_or_404(Order, id=order_id)
 

    # Handle retrieving an order
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # Handle updating an order
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    # Handle deleting an order
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class StockAndRevenueView(APIView):
    def get(self, request):
        total_stock_quantity = 0
        initial_investment = Decimal('0.00')

        # Calculate total stock quantity and initial investment amount
        for product in Product.objects.all():
            wholesale_price = Decimal(product.whole_sale_price)  # Ensure wholesale price is Decimal
            if isinstance(product.weights, dict):
                # Process weights when stored as a dictionary
                for weight, details in product.weights.items():
                    if isinstance(details, dict):
                        quantity = int(details.get('quantity', 0))  # Convert quantity to integer
                        total_stock_quantity += quantity
                        initial_investment += wholesale_price * quantity

            elif isinstance(product.weights, list):
                # Process weights when stored as a list of dictionaries
                for weight_data in product.weights:
                    if isinstance(weight_data, dict):
                        quantity = int(weight_data.get('quantity', 0))  # Convert quantity to integer
                        total_stock_quantity += quantity
                        initial_investment += wholesale_price * quantity

        # Calculate total amount received from all orders
        total_amount_received = Order.objects.aggregate(
            total_received=Sum('total_price')
        )['total_received'] or Decimal('0.00')

        # Calculate profit as the difference between received and invested amounts
        profit = float(total_amount_received) - float(initial_investment)

        data = {
            "total_stock_quantity": total_stock_quantity,
            "initial_investment": float(initial_investment),
            "total_amount_received": float(total_amount_received),
            "profit": profit
        }

        return Response(data, status=status.HTTP_200_OK)



class UpdateOrderStatusView(APIView):
    permission_classes = []

    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = UpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order.status = serializer.validated_data['status']
        order.save()

        return Response({
            "message": "Order status updated successfully",
            "order_id": order.order_ids,
            "new_status": order.status
        }, status=status.HTTP_200_OK)




  
class UserOrdersListView(generics.ListAPIView):
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        return Order.objects.filter(user=user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        total_orders = queryset.count()

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'total_orders': total_orders,
            'orders': serializer.data
        })
    

class FilterOrdersByDateView(generics.ListAPIView):
    serializer_class = AllOrdersSerializer
    permission_classes = []

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)

            if not start_date or not end_date:
                return Order.objects.none()  

            return Order.objects.filter(created_at__date__range=[start_date, end_date]).order_by('-created_at')
        else:
            return Order.objects.none()  

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "No orders found for the given date range."}, status=status.HTTP_404_NOT_FOUND)
        
class BulkDeleteSelectedOrdersView(APIView):
    """
    View to handle bulk deletion of selected orders.
    Accepts a list of order IDs in the request body and deletes the corresponding orders.
    """
    permission_classes = []  

    def delete(self, request, *args, **kwargs):
        selected_order_ids = request.data.get('selected_order_ids', [])

        if not isinstance(selected_order_ids, list) or not selected_order_ids:
            return Response({"error": "Please provide a list of selected order IDs to delete."}, status=status.HTTP_400_BAD_REQUEST)

        orders_to_delete = Order.objects.filter(id__in=selected_order_ids)

        if not orders_to_delete.exists():
            return Response({"error": "No orders found for the provided IDs."}, status=status.HTTP_404_NOT_FOUND)

        count, _ = orders_to_delete.delete()

        return Response({"message": f"Successfully deleted {count} selected orders."}, status=status.HTTP_200_OK)


class VerifyDeliveryPinView(APIView):
    permission_classes = []  # You can set proper permissions based on your use case

    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        delivery_pin = request.data.get("delivery_pin")

        if not order_id or not delivery_pin:
            return Response({"error": "Order ID and Delivery Pin are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the order using the order ID
        order = get_object_or_404(Order, order_ids=order_id)

        # Verify if the entered delivery pin matches the one in the order
        if order.delivery_pin == delivery_pin:
            # Update the status of the order to 'DELIVERED'
            order.status = "DELIVERED"
            order.save()

            return Response({
                "message": "Delivery pin verified successfully. Order status updated to DELIVERED."
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid delivery pin."}, status=status.HTTP_400_BAD_REQUEST)
        

class TotalPriceAllUsersView(APIView):
    def get(self, request, *args, **kwargs):
        total_price = Order.objects.aggregate(Sum('total_price'))['total_price__sum']
        total_price = total_price or 0.00  # In case there are no orders

        return Response({"total_price_all_users": total_price}, status=status.HTTP_200_OK)  
    
class TotalPriceByUserView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        try:
            # Ensure the user exists
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Aggregate total price for the specific user
        total_price_by_user = Order.objects.filter(user=user).aggregate(Sum('total_price'))['total_price__sum']
        total_price_by_user = total_price_by_user or 0.00  # Handle None case

        return Response({"total_price_by_user": total_price_by_user}, status=status.HTTP_200_OK)
    

class ProductOrderAnalyticsView(APIView):
    """
    Returns the daily, weekly, and monthly analytics for products ordered.
    """
    
    def get(self, request):
        today = timezone.now().date()
        
        # Daily orders
        daily_orders = (
            Order.objects.filter(created_at__date=today)
            .annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(total_orders=Count('id'))
            .order_by('-day')
        )

        # Weekly orders
        weekly_orders = (
            Order.objects.filter(created_at__gte=today - timezone.timedelta(days=7))
            .annotate(week=TruncWeek('created_at'))
            .values('week')
            .annotate(total_orders=Count('id'))
            .order_by('-week')
        )

        # Monthly orders
        monthly_orders = (
            Order.objects.filter(created_at__gte=today - timezone.timedelta(days=30))
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total_orders=Count('id'))
            .order_by('-month')
        )

        data = {
            "daily_orders": list(daily_orders),
            "weekly_orders": list(weekly_orders),
            "monthly_orders": list(monthly_orders),
        }
        
        return Response(data, status=status.HTTP_200_OK)