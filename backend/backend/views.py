from django.http import HttpResponse
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.response import Response

def home (req):
    return HttpResponse("Home Page")
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data

        refresh_token = data.get('refresh')

        if 'refresh' in data:
            del data['refresh']

        new_response = Response(data, status=response.status_code)

        new_response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,        # Use True in production (HTTPS)
            samesite='None',    # Required for cross-site requests (e.g., if frontend on localhost:5173)
            max_age=7 * 24 * 60 * 60,  # 7 days
        )

        return new_response


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({"detail": "Refresh token missing."}, status=400)

        data = request.data.copy()
        data['refresh'] = refresh_token
        request._full_data = data

        return super().post(request, *args, **kwargs)