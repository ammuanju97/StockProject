# views.py
import json
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
from .models import CompanyShare, ShareHistory
from django.views import View
from rest_framework import viewsets
from .models import UserPortfolio, UserHoldings
from .serializers import UserPortfolioSerializer, UserHoldingsSerializer
from django.http import JsonResponse
from .models import Transaction, UserHolding, CompanyShare
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .models import Transaction, UserHolding, CompanyShare
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


class LiveUpdatesView(View):
    def get(self, request):
 
        live_data = {
            'message': 'Live updates are coming!',
            'data': {
                'price_change': '+2.00',
                'company_name': 'Example Company',
            },
        }

        
        channel_layer = get_channel_layer()

      
        async_to_sync(channel_layer.group_send)(
            "live_updates_group",  
            {
                "type": "update.message",
                "message": live_data,
            },
        )

        return JsonResponse({'status': 'success'})


class ShareHistoryView(View):
    def get(self, request, company_share_id):
      
        company_share = get_object_or_404(CompanyShare, id=company_share_id)

   
        share_history = ShareHistory.objects.filter(company_share=company_share)

        serialized_history = [
            {
                'date': history.date,
                'price': history.price,
            }
            for history in share_history
        ]

        return JsonResponse({'share_history': serialized_history})


class BuyTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        company_share_id = request.data.get('company_share_id')
        quantity = request.data.get('quantity')
        price = request.data.get('price')

        company_share = CompanyShare.objects.get(pk=company_share_id)

     
        total_cost = quantity * price

      
        user = request.user
        if user.profile.balance < total_cost:
            return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
   
        transaction = Transaction.objects.create(
            user=user,
            company_share=company_share,
            transaction_type='buy',
            quantity=quantity,
            price_per_share=price,
        )


        try:
            user_holding = UserHolding.objects.get(user_portfolio__user=user, company_share=company_share)
            user_holding.quantity += quantity
            user_holding.save()
        except UserHolding.DoesNotExist:
            UserHolding.objects.create(user_portfolio=user.profile.portfolio, company_share=company_share, quantity=quantity)


        user.profile.balance -= total_cost
        user.profile.save()

        return Response({'message': 'Share purchase successful'}, status=status.HTTP_201_CREATED)


class SellTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        company_share_id = request.data.get('company_share_id')
        quantity = request.data.get('quantity')
        price = request.data.get('price')


        company_share = CompanyShare.objects.get(pk=company_share_id)


        user = request.user
        try:
            user_holding = UserHolding.objects.get(user_portfolio__user=user, company_share=company_share)
            if user_holding.quantity < quantity:
                return Response({'error': 'Insufficient shares to sell'}, status=status.HTTP_400_BAD_REQUEST)
        except UserHolding.DoesNotExist:
            return Response({'error': 'You do not own any shares of this company'}, status=status.HTTP_400_BAD_REQUEST)


        total_earnings = quantity * price

        transaction = Transaction.objects.create(
            user=user,
            company_share=company_share,
            transaction_type='sell',
            quantity=quantity,
            price_per_share=price,
        )


        user_holding.quantity -= quantity
        user_holding.save()

    
        user.profile.balance += total_earnings
        user.profile.save()

        return Response({'message': 'Share sale successful'}, status=status.HTTP_201_CREATED)


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
     
        user = request.user
        payment_amount = request.data.get('amount')

       
        if user.profile.balance < payment_amount:
            return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)


        user.profile.balance -= payment_amount
        user.profile.save()

        return Response({'message': 'Payment processed successfully'}, status=status.HTTP_201_CREATED)



class UserRegistrationView(APIView):
    def post(self, request):
    
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')


        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)


        user = User.objects.create_user(username=username, email=email, password=password)

  
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)




class UserLoginView(APIView):
    def post(self, request):
       
        username = request.data.get('username')
        password = request.data.get('password')


        user = authenticate(request, username=username, password=password)

        if user is not None:
        
            login(request, user)
            return Response({'message': 'User logged in successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid login credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
  
    user = request.user
    profile_data = {
        'username': user.username,
        'email': user.email,

    }
    return JsonResponse(profile_data)


class UserPortfolioViewSet(viewsets.ModelViewSet):
    queryset = UserPortfolio.objects.all()
    serializer_class = UserPortfolioSerializer


class UserHoldingsViewSet(viewsets.ModelViewSet):
    queryset = UserHoldings.objects.all()
    serializer_class = UserHoldingsSerializer
