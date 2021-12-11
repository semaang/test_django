from django.urls import path, include
###### from primeflix.primelist_app.models import Review
# from primelist_app.api.views import movie_list, movie_details
from primeflix_app.api.views import ProductAV, ProductDetailsAV, StreamPlatformListAV, StreamPlatformDetailsAV, ReviewList, ReviewCreate, ReviewDetails, OrderListPaid, OrderDetails, OrderLines, OrderLineDetails, ShippingAddress

urlpatterns = [
    path('list/', ProductAV.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailsAV.as_view(), name='product-details'),
    path('platform/', StreamPlatformListAV.as_view(), name='platform-list'),
    path('platform/<int:pk>/', StreamPlatformDetailsAV.as_view(), name='platform-details'),
    # path('review/', ReviewList.as_view(), name="review-list"),
    # path('review/<int:pk>/', ReviewDetails.as_view(), name="review-details"),
    path('<int:pk>/reviews/', ReviewList.as_view(), name="review-list"),
    path('<int:pk>/review-create/', ReviewCreate.as_view(), name="review-create"),
    path('review/<int:pk>/', ReviewDetails.as_view(), name="review-details"),
    # path('order/<int:pk>/', OrderDetailsAV.as_view(), name="cart-details"),
    path('<int:pk>/orders-paid/', OrderListPaid.as_view(), name="orders-paid"),
    path('<int:pk>/order/', OrderDetails.as_view(), name="order"),
    path('<int:pk>/orderlines/', OrderLines.as_view(), name="orderlines"),
    path('<int:pk>/orderline/', OrderLineDetails.as_view(), name="orderline-details"),
]
# urlpatterns = [
#     path('list/', movie_list, name='moviiie-list'),
#     path('<int:pk>', movie_details, name='movie-details'),
# ]
