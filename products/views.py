from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from .models import Category, Product
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, filters



class CustomProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


from users.permissions import HasPermissionForAction

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None

    # Add the required permission for sub-admins
    required_permission = 'can_view_categories'  # Customize the permission name based on your setup
    
    # Apply the custom permission
    permission_classes = [HasPermissionForAction]
    

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None

class SubCategoryListView(generics.ListCreateAPIView):
    queryset = SubCategories.objects.all()
    serializer_class = SubCategorySerializer
    pagination_class=None

class SubCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategories.objects.all()
    serializer_class = SubCategorySerializer
    pagination_class = None

class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    pagination_class = CustomProductPagination
    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     if not queryset.exists():
    #         return Response({"results": []})

    #     # If there are products, proceed with the default paginated response
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response({"results": serializer.data})
class ProductcompleteListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = None

    def retrieve(self, request, *args, **kwargs):
        """
        Handle GET request to retrieve a product
        """
        try:
            product = self.get_object()  
            serializer = self.get_serializer(product)
            return Response({
                'message': 'Product retrieved successfully!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found!'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        """
        Handle PUT or PATCH request to update a product
        """
        partial = kwargs.pop('partial', False)  
        try:
            product = self.get_object()  
            serializer = self.get_serializer(product, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                'message': 'Product updated successfully!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Handle DELETE request to delete a product
        """
        try:
            product = self.get_object()  
            self.perform_destroy(product)
            return Response({
                'message': 'Product deleted successfully!'
            }, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class ProductImageCreateView(APIView):
    def post(self, request, product_id, *args, **kwargs):
        """
        Create multiple product images for a given product.
        """
        product = get_object_or_404(Product, id=product_id)
        
        # Loop over the uploaded images and save them
        images = request.FILES.getlist('image')  # 'image' is the key in form-data
        for image in images:
            ProductImage.objects.create(product=product, image=image)
        
        return Response({"message": "Images uploaded successfully"}, status=status.HTTP_201_CREATED)

class ProductImageDetailView(APIView):

    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve a product image by ID.
        """
        product_image = get_object_or_404(ProductImage, pk=pk)
        serializer = ProductImageSerializer(product_image)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        """
        Update a product image by ID.
        """
        product_image = get_object_or_404(ProductImage, pk=pk)
        serializer = ProductImageSerializer(product_image, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        """
        Delete a product image by ID.
        """
        product_image = get_object_or_404(ProductImage, pk=pk)
        product_image.delete()
        return Response({"message": "Product image deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class singleProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = singleProductSerializer



class ProductByCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = CustomProductPagination


    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Product.objects.filter(category__id=category_id)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     if not queryset.exists():
    #         return Response({"results": []})

    #     # If there are products, proceed with the default paginated response
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response({"results": serializer.data})


#offer and popular product view
class OfferProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = None

    def get_queryset(self):
        return Product.objects.filter(is_offer_product=True)

class PopularProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = None

    def get_queryset(self):
        return Product.objects.filter(is_popular_product=True)
    
#carousel Section

class CarouselItemListCreateView(generics.ListCreateAPIView):
    queryset = CarouselItem.objects.all()
    serializer_class = CarouselItemSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        images = request.FILES.getlist('image')  
        data_list = []

        for image in images:
            data = {
                'title': request.data.get('title'),  
                'image': image
            }
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            data_list.append(serializer.data)

        return Response(data_list, status=status.HTTP_201_CREATED)

class CarouselItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CarouselItem.objects.all()
    serializer_class = CarouselItemSerializer
    pagination_class = None

class CarouselItemListCreateView2(generics.ListCreateAPIView):
    queryset = CarouselItem.objects.all()
    serializer_class = CarouselItemSerializer2
    pagination_class = None

    def create(self, request, *args, **kwargs):
        images = request.FILES.getlist('image')  
        data_list = []

        for image in images:
            data = {
                'title': request.data.get('title'),  
                'image': image
            }
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            data_list.append(serializer.data)

        return Response(data_list, status=status.HTTP_201_CREATED)

class CarouselItemRetrieveUpdateDestroyView2(generics.RetrieveUpdateDestroyAPIView):
    queryset = CarouselItem.objects.all()
    serializer_class = CarouselItemSerializer2
    pagination_class = None

class SubCategoryListByCategoryView(generics.ListAPIView):
    serializer_class = SubCategorySerializer
    pagination_class = None

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SubCategories.objects.filter(Category_id=category_id)
    
class SubCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategories.objects.all()
    serializer_class = SubCategorySerializer


class ProductListBySubCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class=CustomProductPagination

    def get_queryset(self):
        sub_category_id = self.kwargs['sub_category_id']
        return Product.objects.filter(sub_category_id=sub_category_id)
    

class ProductWeightsView(APIView):
    def get(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        serializer = ProductWeightsSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductSearchFilterView(APIView):
    pagination_class = CustomProductPagination  

    def get(self, request):
        serializer = ProductSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        search_query = serializer.validated_data['search_query']
         
        products = Product.objects.filter(name__icontains=search_query)

        if not products.exists():
            return Response({"detail": "No products found"}, status=status.HTTP_404_NOT_FOUND)

        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(products, request)
         
        product_serializer = ProductSerializer(paginated_products, many=True, context={'request': request})  
        response_data = {
            'results': product_serializer.data,
            'count': products.count(),  
            'next': paginator.get_next_link(),  
            'previous': paginator.get_previous_link(),  
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
class ProductStockListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by('-created_at')  
    serializer_class = ProductStockSerializer
    pagination_class = CustomProductPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'category__name', 'sub_category__name']




class PosterImageListCreateView(generics.ListCreateAPIView):
    queryset = PosterImage.objects.all()
    serializer_class = PosterImageSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        images_data = request.FILES.getlist('poster_image')  # Use request.FILES to get the images

        poster_heading = request.data.get('poster_heading')
        poster_title = request.data.get('poster_title')
        poster_sub_title = request.data.get('poster_sub_title')

        if not images_data:
            return Response({"error": "No images uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        poster_images = []
        for image in images_data:
            poster_image = PosterImage(
                poster_heading=poster_heading,
                poster_title=poster_title,
                poster_sub_title=poster_sub_title,
                poster_image=image
            )
            poster_images.append(poster_image)

        # Bulk create the images
        PosterImage.objects.bulk_create(poster_images)

        return Response({"message": "Images uploaded successfully"}, status=status.HTTP_201_CREATED)



class PosterImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PosterImage.objects.all()
    serializer_class = PosterImageSerializer
    pagination_class = None


class HomePageImageListCreateView(generics.ListCreateAPIView):
    queryset = HomePageImage.objects.all()
    serializer_class = HomePageImageSerializer
    pagination_class=None


class HomePageImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HomePageImage.objects.all()
    serializer_class = HomePageImageSerializer
    pagination_class = None

class LowStockProductListView(APIView):
    pagination_class = CustomProductPagination

    def get(self, request, *args, **kwargs):
        low_stock_products = []

        
        products = Product.objects.all()

        for product in products:
            stock_info = []  
            
            
            if isinstance(product.weights, dict):
                for weight, details in product.weights.items():
                    if isinstance(details, dict):
                        try:
                            quantity = int(details.get('quantity', 0))
                        except (ValueError, TypeError):
                            quantity = 0

                        if quantity < 10:
                            stock_info.append({
                                "weight": weight,
                                "price": details.get("price", 0),
                                "quantity": quantity,
                                "is_in_stock": details.get("is_in_stock", False)
                            })

            elif isinstance(product.weights, list):
                for weight_data in product.weights:
                    if isinstance(weight_data, dict):
                        try:
                            quantity = int(weight_data.get('quantity', 0))
                        except (ValueError, TypeError):
                            quantity = 0

                        if quantity < 10:
                            stock_info.append({
                                "weight": weight_data.get("weight"),
                                "price": weight_data.get("price", 0),
                                "quantity": quantity,
                                "is_in_stock": weight_data.get("is_in_stock", False)
                            })
                      
            if stock_info:
                low_stock_products.append({
                    "id": product.id,
                    "category_name": product.category.name,
                    "sub_category_name": product.sub_category.name if product.sub_category else None,
                    "product_name": product.name,
                    "weight_measurement": product.weight_measurement,
                    "stock_info": stock_info  
                })
        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(low_stock_products, request)
        return paginator.get_paginated_response(paginated_products)