from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('try_it_out/', views.try_it_out, name='try_it_out'),
    path('request_demo/', views.request_demo, name='request_demo'),
    path('receive_screening_data/', views.receive_screening_data, name='receive_screening_data'),
    path('predict/', views.predict_diagnosis, name='prediction'),
    path('receive_screening_data/<int:screening_id>/', views.receive_screening_data, name='receive_screening_data_with_id'),    
    path('predict_diagnosis/<int:screening_id>/', views.predict_diagnosis, name='predict_diagnosis'),
]