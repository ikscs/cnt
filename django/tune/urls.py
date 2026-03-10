from django.urls import path
from . import views

urlpatterns = [
    path('encoder/', views.DataEncoderView.as_view(), name='data_encoder'),
    path('decoder/', views.DataDecoderView.as_view(), name='data_decoder'),
    path('img/<str:image_name>.jpg', views.ImageView.as_view(), name='img_view'),
]
