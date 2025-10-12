from django.urls import path
from . import views
urlpatterns = [
    path('', views.CoordinatesList.as_view()),
    path('score', views.ScoreList.as_view()),
    path('auth/', views.RegisterView.as_view()),
    path('auth/google', views.GoogleLogin.as_view(), name='google_login'),
    path('protected-view/', views.ProtectedView.as_view()),
]