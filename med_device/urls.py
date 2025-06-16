from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('predict/', views.tumor_prediction_view, name='tumor_prediction'),
]