from django.urls import path
from . import views

urlpatterns=[
    path('', views.calificador, name='calificador'),
    path('solicitud/', views.solicitud, name='solicitud'),
    path('calificacion/', views.calificacion, name='calificacion'),
    path('calificacion/alternativas/', views.alternativas, name='alternativas'),
]