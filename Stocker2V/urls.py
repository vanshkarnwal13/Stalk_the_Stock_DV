"""todowoo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth
    path("signup/", views.signupuser, name="signupuser"),
    path("logout/", views.logoutuser, name="logoutuser"),
    path("login/", views.loginuser, name="loginuser"),

    #Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='core/password_reset.html'), name='reset_password'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), name='password_reset_complete'),
    
    # Dashboard
    path("", views.home, name="home"),
    path("stockdata/", views.stockdata, name="stockdata"),
    path("globalindices/", views.global_indices, name="global_indices"),
    path("premium/", views.premium, name="premium"),
    path("stockdata/<str:ticker>/", views.graphs, name="graphs"),
    path("stockdata/<str:ticker>/analysis1", views.analysis1, name="analysis1"),
    path("stockdata/analysis2/<str:sec>", views.analysis2, name="analysis2"),
    path("transaction/", views.transaction_form, name="transaction"),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
