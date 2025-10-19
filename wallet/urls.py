from django.urls import path

from .views import CheckBalanceView, TransferAmountView
urlpatterns = [
    path('balance/',CheckBalanceView.as_view(),name='check-balance'),
    path('transfer/', TransferAmountView.as_view(), name='transfer-amount'),
]
