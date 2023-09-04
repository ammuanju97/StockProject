from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'user-portfolio', views.UserPortfolioViewSet)
router.register(r'user-holdings', views.UserHoldingsViewSet)

urlpatterns = [
    path('live-updates/', views.LiveUpdatesView.as_view(), name='live-updates'),
    path('share-history/<int:company_share_id>/', views.ShareHistoryView.as_view(), name='share-history'),
    path('buy/', views.BuyTransactionView.as_view(), name='buy-transaction'),
    path('sell/', views.SellTransactionView.as_view(), name='sell-transaction'),
    path('payment/', views.PaymentView.as_view(), name='payment'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('api/', include(router.urls)),
]
