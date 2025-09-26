from django.urls import path
from . import views
urlpatterns = [
    path('', views.CoordinatesList.as_view()),
    path('score', views.ScoreList.as_view()),
    path('google/login/', views.GoogleLogin.as_view(), name='google_login'),
    path('users/me/', views.UserMe.as_view(), name='user_detail')
]