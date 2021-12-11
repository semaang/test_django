# from re import search
from django.db.models.query import QuerySet
from django.http.response import HttpResponse
from rest_framework.response import Response
from rest_framework import generics, serializers, status
# from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics
from rest_framework.exceptions import APIException, ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from primeflix_app.models import Product, StreamPlatformList, Review, Customer, Order, OrderLine, ShippingAddress
from primeflix_app.api.serializers import ProductSerializer, StreamPlatformListSerializer, ReviewSerializer, CustomerSerializer, OrderSerializer, OrderLineSerializer, ShippingAddressSerializer
from primeflix_app.api.permissions import IsAdminOrReadyOnly, IsReviewUserOrReadOnly

def index(request):
    message = "Hello world"
    return HttpResponse(message)


class ReviewList(generics.ListAPIView):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Review.objects.filter(product=pk)
        

class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.all()
    
    def perform_create(self, serializer):
        pk = self.kwargs['pk']
        temp_product = Product.objects.get(pk=pk)
    
        temp_review_user = self.request.user
        review_queryset = Review.objects.filter(product=temp_product, review_user=temp_review_user)
        
        # if (review_queryset.exists()):
        #     raise ValidationError("you have already reviewed this product")
        
        if (temp_product.number_ratings == 0):
            temp_product.average_rating = serializer.validated_data['rating']
        else:
            temp_product.average_rating = ((temp_product.average_rating * temp_product.number_ratings ) + float(serializer.validated_data['rating'])) / float(temp_product.number_ratings + 1) 

        temp_product.number_ratings = temp_product.number_ratings + 1
        temp_product.save()  
        serializer.save(product=temp_product, review_user=temp_review_user)
            
    
class ReviewDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly] /////////////////////////////////////////////:
    permission_classes = [IsReviewUserOrReadOnly]
    
    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        temp_review = Review.objects.get(pk=pk)
        temp_product = Product.objects.get(pk=temp_review.product.id)
        
        if(temp_product.number_ratings > 1):      
            temp_product.average_rating = ((temp_product.average_rating * temp_product.number_ratings ) - temp_review.rating) / (temp_product.number_ratings - 1)
        else:
             temp_product.average_rating = 0
             
        temp_product.number_ratings = temp_product.number_ratings - 1 
        temp_product.save()
        return self.destroy(request, *args, **kwargs)
    
    
    def perform_update(self, serializer):
        # temp_review = Review.objects.get(pk=pk)
        pk = self.kwargs['pk']
        temp_review = Review.objects.get(pk=pk)
        temp_product = Product.objects.get(pk=temp_review.product.id)
       
        if(temp_product.number_ratings > 0):      
            temp_product.average_rating = ((temp_product.average_rating * temp_product.number_ratings ) - temp_review.rating + serializer.validated_data['rating']) / temp_product.number_ratings
        else:
             temp_product.average_rating = temp_review.rating
             
        temp_product.save()  
        serializer.save(product=temp_product)


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    
class OrderListPaid(generics.ListAPIView):
    serializer_class = OrderSerializer    

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Order.objects.filter(customer=pk, order_paid=True)
    

class OrderLines(generics.ListCreateAPIView):
    serializer_class = OrderLineSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        temp_order = Order.objects.get(customer=pk, order_paid=False)
        if temp_order:
            return OrderLine.objects.filter(customer=pk, order=temp_order) 
        else:
            return ('Error : Order doesn\'t exist in database')
            
    def perform_create(self, serializer):
            pk = self.kwargs['pk']
            temp_customer = Customer.objects.get(pk=pk)
            temp_order_user = Order.objects.get(customer=pk, order_paid=False)
            serializer.save(order=temp_order_user, customer=temp_customer)
            
            
 
class OrderLineDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer
    
    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        temp_order = Order.objects.get(order=self.retrieve, order_paid=False)
        return self.destroy(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        pk = self.kwargs['pk']
        # serializer.save()
        temp_orderline = OrderLine.objects.get(pk=pk)
        
        # temp_order = Order.objects.filter(pk=temp_orderline.order.id, order_paid=False)
        temp_order = Order.objects.get(pk=temp_orderline.order.id)
        
        if ((temp_orderline.order == temp_order) and (temp_orderline.order.order_paid == False)):
            serializer.save()
            # test_new_order = Order()
            # test_new_order.customer = temp_orderline.customer
            # test_new_order.save()
        else:
            raise APIException("Order paid")

    
class OrderDetails(APIView):
    permission_classes = [IsAdminOrReadyOnly]
    
    def get(self, request, pk):
        pk = self.kwargs['pk']
        try:
            temp_order = Order.objects.get(customer=pk, order_paid=False)
        except Order.DoesNotExist:
            return Response('Error : Order doesn\'t exist in database', status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderSerializer(temp_order)
        return Response(serializer.data) 
        
# class OrderDetails(APIView):
#     permission_classes = [IsAdminOrReadyOnly]
    
#     def get(self, request, pk):
#         pk = self.kwargs['pk']
#         try:
#             temp_order = Order.objects.get(customer=pk, order_paid=False)
#         except Order.DoesNotExist:
#             return Response('Error : Order doesn\'t exist in database', status=status.HTTP_404_NOT_FOUND)
        
#         serializer = OrderSerializer(temp_order)
#         return Response(serializer.data) 
    
   
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    
class StreamPlatformListAV(APIView):
    permission_classes = [IsAdminOrReadyOnly]

    def get(self, request):
        platforms = StreamPlatformList.objects.all()
        serializer = StreamPlatformListSerializer(platforms, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StreamPlatformListSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class ProductAV(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [IsAdminOrReadyOnly]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StreamPlatformDetailsAV(APIView):
    permission_classes = [IsAdminOrReadyOnly]

    def get(self, request, pk):
        try:
            platform = StreamPlatformList.objects.get(pk=pk)
        except StreamPlatformList.DoesNotExist:
            return Response('Error : Platform doesn\'t exist in database', status=status.HTTP_404_NOT_FOUND)
        
        serializer = StreamPlatformListSerializer(platform)
        return Response(serializer.data) 
      
    def put(self, request, pk):
        platform = StreamPlatformList.objects.get(pk=pk)
        serializer = StreamPlatformListSerializer(platform, data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors) 
    
    def delete(self, request, pk):       
            platform = StreamPlatformList.objects.get(pk=pk)
            platform.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)        


class ProductDetailsAV(APIView):
    permission_classes = [IsAdminOrReadyOnly]
    
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response('Error : Film doesn\'t exist in database', status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product)
        return Response(serializer.data) 
    
    def put(self, request, pk):
        product = Product.objects.get(pk=pk)
        serializer = ProductSerializer(product, data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors) 
    
    def delete(self, request, pk):       
            product = Product.objects.get(pk=pk)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)        
        

# # many=True :> MovieSerializer needs to consult multiple (not only a single)
# # objects in the query set and map them
# @api_view(['GET', 'POST'])
# def movie_list(request):
    
#     if (request.method == 'GET'): 
#         movies = Movie.objects.all()
#         serializer = MovieSerializer(movies, many=True)
#         return Response(serializer.data) 
      
#     if (request.method == 'POST'): 
#         serializer = MovieSerializer(data=request.data)
#         if(serializer.is_valid()):
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'PUT', 'DELETE'])
# def movie_details(request, pk):
    
#     if(request.method == 'GET'): 
#         try:
#             movie = Movie.objects.get(pk=pk)
#         except Movie.DoesNotExist:
#             return Response('Error : Film inexistant', status=status.HTTP_404_NOT_FOUND)
        
#         serializer = MovieSerializer(movie)
#         return Response(serializer.data)   
     
#     if(request.method == 'PUT'):
#         movie = Movie.objects.get(pk=pk)
#         serializer = MovieSerializer(movie, data=request.data)
#         if(serializer.is_valid()):
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors) 
           
#     if(request.method == 'DELETE'):   
#         movie = Movie.objects.get(pk=pk)
#         movie.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
