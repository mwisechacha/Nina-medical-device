from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('try_it_out/', views.try_it_out, name='try_it_out'),
    path('request_demo/', views.request_demo, name='request_demo'),
    path('receive_screening_data/', views.receive_screening_data, name='receive_screening_data'),
    path('check_data_ready/', views.check_data_ready, name='check_data_ready'),
    path('show_data_received/<int:screening_id>/', views.show_data_received, name='show_data_received'),
    path('show_tumor_data/<int:screening_id>/', views.show_tumor_data, name='rule_based_result'), 
    path('predict_diagnosis/<int:screening_id>/', views.predict_diagnosis, name='predict_diagnosis'),
    path('prediction_result/<int:screening_id>/', views.prediction_result, name='prediction_result'),
]