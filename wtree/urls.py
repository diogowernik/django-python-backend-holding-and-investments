from django.urls import path
from .views import MetaMaskRegisterView, MetaMaskLoginView, MetaMaskAuthView

urlpatterns = [
    path('metamask/register/', MetaMaskRegisterView.as_view(), name='register_with_metamask'),
    path('metamask/login/', MetaMaskLoginView.as_view(), name='login_with_metamask'),
    path('metamask/auth/', MetaMaskAuthView.as_view(), name='auth_with_metamask'),
]
