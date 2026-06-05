from django.urls import path

from web.views import index
from web.views.user.account.login import LoginView
from web.views.user.account.logout import LogoutView
from web.views.user.account.refresh_token import RefreshTokenView
from web.views.user.account.register import RegisterView

urlpatterns = [
    path('user/account/login/', LoginView.as_view()),
    path('user/account/register/', RegisterView.as_view()),
    path('user/account/refresh_token/', RefreshTokenView.as_view()),
    path('user/account/logout/', LogoutView.as_view()),


    path('', index)
]
