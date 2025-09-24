from django.urls import path
from . import views
urlpatterns = [
    path('', views.CoordinatesList.as_view()),
    path('score', views.Score.as_view()),
]