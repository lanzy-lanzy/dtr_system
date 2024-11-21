from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('time-in/', views.time_in, name='time_in'),
    path('time-out/', views.time_out, name='time_out'),
    path('login/', auth_views.LoginView.as_view(
        template_name='dtr_app/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dtr-form/', views.dtr_form, name='dtr_form'),
    path('export-dtr-pdf/', views.export_dtr_pdf, name='export_dtr_pdf'),
]
