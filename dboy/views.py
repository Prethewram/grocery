from django.shortcuts import render
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from django.core.mail import send_mail
import random
from django.utils import timezone

# Create your views here.

class CreateDeliveryBoyView(APIView):
    def post(self, request):
        serializer = DeliveryBoySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Delivery Boy created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeliveryBoyListView(generics.ListAPIView):
    queryset = DeliveryBoy.objects.all().order_by('-created_at')
    serializer_class = DeliveryBoySerializer

# View to retrieve a specific delivery boy by ID
class DeliveryBoyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DeliveryBoy.objects.all()
    serializer_class = DeliveryBoySerializer
    lookup_field = 'id'  



def generate_and_send_otp(delivery_boy):
    otp = f"{random.randint(100000, 999999)}"
    delivery_boy.otp = otp
    delivery_boy.save()
    
    # Send OTP to the delivery boy's email
    send_mail(
        'Your Login OTP',
        f'Your OTP for login is {otp}.',
        'noreply@yourapp.com',  # Replace with your sender email
        [delivery_boy.email],
        fail_silently=False,
    )

class DeliveryBoyLoginView(APIView):
    def post(self, request):
        serializer = DeliveryBoyLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Check if the delivery boy exists
        try:
            delivery_boy = DeliveryBoy.objects.get(email=email)
        except DeliveryBoy.DoesNotExist:
            return Response({"error": "Delivery boy not found"}, status=status.HTTP_404_NOT_FOUND)

        # Generate and send OTP
        generate_and_send_otp(delivery_boy)

        return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)


class DeliveryBoyOTPVerifyView(APIView):
    def post(self, request):
        serializer = DeliveryBoyOTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        # Verify OTP
        try:
            delivery_boy = DeliveryBoy.objects.get(email=email, otp=otp)
        except DeliveryBoy.DoesNotExist:
            return Response({"error": "Invalid OTP or email"}, status=status.HTTP_400_BAD_REQUEST)

        # Clear OTP after successful login
        delivery_boy.otp = None
        delivery_boy.save()

        return Response({"message": "Login successful","delivery_boy_id": delivery_boy.id}, status=status.HTTP_200_OK)
    
class DeliveryBoyStatusUpdateView(APIView):
    def post(self, request, delivery_boy_id):
        try:
            delivery_boy = DeliveryBoy.objects.get(id=delivery_boy_id)
        except DeliveryBoy.DoesNotExist:
            return Response({"error": "Delivery boy not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DeliveryBoyStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update the status
        serializer.update(delivery_boy, serializer.validated_data)
        
        return Response({"message": "Status updated successfully", "delivery_boy_id": delivery_boy.id, "is_working": delivery_boy.is_working},
                         status=status.HTTP_200_OK)
    
class ActiveDeliveryBoysView(APIView):
    def get(self, request):
        active_delivery_boys = DeliveryBoy.objects.filter(is_working=True)       
        serializer = DeliveryBoySerializer(active_delivery_boys, many=True)       
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class InactiveDeliveryBoysView(APIView):
    def get(self, request):
        inactive_delivery_boys = DeliveryBoy.objects.filter(is_working=False)      
        serializer = DeliveryBoySerializer(inactive_delivery_boys, many=True)        
        return Response(serializer.data, status=status.HTTP_200_OK)

class AssignOrderToDeliveryBoyView(APIView):
    def post(self, request, order_ids, delivery_boy_id):
        try:
            delivery_boy = DeliveryBoy.objects.get(id=delivery_boy_id)
        except DeliveryBoy.DoesNotExist:
            return Response({"error": "Delivery boy not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            order = Order.objects.get(order_ids=order_ids)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        assignment = OrderAssignment.objects.filter(order=order).first()
        
        if assignment:
            assignment.delivery_boy = delivery_boy
            assignment.save()
            message = "Order reassigned to new delivery boy successfully."
        else:
            OrderAssignment.objects.create(order=order, delivery_boy=delivery_boy)
            message = "Order assigned to delivery boy successfully."
        return Response({"message": message}, status=status.HTTP_200_OK)


class AllAssignedOrdersView(generics.ListAPIView):
    serializer_class = OrderAssignmentSerializer

    def get_queryset(self):
        return OrderAssignment.objects.all()
    
class DeliveryBoyAssignedOrdersView(generics.ListAPIView):
    serializer_class = OrderDboySerializer

    def get_queryset(self):
        delivery_boy_id = self.kwargs['delivery_boy_id']
        return OrderAssignment.objects.filter(delivery_boy_id=delivery_boy_id)
    
 
class Singleorderview(generics.RetrieveAPIView):
    queryset = OrderAssignment.objects.all()
    serializer_class = SingleorderSerializer

class CompletedOrdersView(generics.ListAPIView):
    serializer_class = CompletedOrderSerializer

    def get_queryset(self):
        delivery_boy_id = self.kwargs['delivery_boy_id']
        return OrderAssignment.objects.filter(delivery_boy_id=delivery_boy_id, order__status='DELIVERED')
    
class deliveryboyprofileview(generics.RetrieveUpdateDestroyAPIView):
    queryset = DeliveryBoy.objects.all()
    serializer_class = deliveryboyserializer
    lookup_field = 'id'


class assigned_order_listview(generics.ListAPIView):
    serializer_class = Assignedorderserializer
    queryset = OrderAssignment.objects.all()

class DeliveryBoynameView(generics.ListAPIView):
    serializer_class = DeliveryBoyByOrderIDSerializer

    def get(self, request, order_id, *args, **kwargs):
        order_assignments = OrderAssignment.objects.filter(order__order_ids=order_id)
        
        if not order_assignments.exists():
            return Response({"error": "No assignments found for the specified order ID"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(order_assignments, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
