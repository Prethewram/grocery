from django.urls import path
from .views import *

urlpatterns = [
#categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
#sub categories
    path('Subcategories/', SubCategoryListView.as_view(), name='sub-category-list'),
    path('Subcategories/<int:pk>/', SubCategoryDetailView.as_view(), name='sub-category-detail'),
#products
    path('products/', ProductListView.as_view(), name='product-list'),
    path('total/products/', ProductcompleteListView.as_view(), name='product-complete-list'),
#for complete product details
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/images/<int:pk>/', ProductImageDetailView.as_view(), name='product-image-detail'),

#for single page
    path('singleproducts/<int:pk>/', singleProductDetailView.as_view(), name='product-detail'),
#products by category
    path('products-category/<int:category_id>/', ProductByCategoryView.as_view(), name='product-by-category'),
#for filter subcategories by category
    path('subcategories/<int:category_id>/', SubCategoryListByCategoryView.as_view(), name='subcategories-by-category'),
#for filter products by sub categories
    path('products/subcategory/<int:sub_category_id>/', ProductListBySubCategoryView.as_view(), name='products-by-sub-category'),
#subcategory details
    path('subcategory/<int:pk>/', SubCategoryDetailView.as_view(), name='subcategory-detail'),
#offer product and popular product
    path('products/offer/', OfferProductListView.as_view(), name='offer-products'),
    path('products/popular/', PopularProductListView.as_view(), name='popular-products'),
#products get by weights
    path('product/<int:product_id>/weights/', ProductWeightsView.as_view(), name='product-weights'),
#product adding images
    path('products/<int:product_id>/images/', ProductImageCreateView.as_view(), name='product-image-create'),
    path('product-images/<int:pk>/', ProductImageDetailView.as_view(), name='product-image-detail'),
#product search
    path('products/search/', ProductSearchFilterView.as_view(), name='product-search'),
#carousel
    path('carousel/', CarouselItemListCreateView.as_view(), name='carousel-list-create'),
    path('carousel/<int:pk>/', CarouselItemRetrieveUpdateDestroyView.as_view(), name='carousel-detail'),
#carousel-2
    path('carousel/2/', CarouselItemListCreateView2.as_view(), name='carousel-list-create-2'),
    path('carousel/2/<int:pk>/', CarouselItemRetrieveUpdateDestroyView2.as_view(), name='carousel-detail-2'),
#poster image
    path('poster-image/', PosterImageListCreateView.as_view(), name='poster-create'),
    path('poster/<int:pk>/', PosterImageRetrieveUpdateDestroyView.as_view(), name='poster-detail'),
#home page image
    path('Home-image/', HomePageImageListCreateView.as_view(), name='poster-create'),
    path('Home-image/<int:pk>/', HomePageImageRetrieveUpdateDestroyView.as_view(), name='poster-detail'),
#stock
    path('products/stock/', ProductStockListView.as_view(), name='product-stock-list'),
#low stock
    path('products/low-stock/', LowStockProductListView.as_view(), name='low_stock_product_list'),





]

