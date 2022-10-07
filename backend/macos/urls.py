from django.urls import include
from django.urls import path
# from django.contrib import admin
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenBlacklistView

# import django_js_reverse.views
from rest_framework.routers import DefaultRouter
from users.views import UserApi
from users.views import RegisterApi

from common.routes import routes as common_routes

router = DefaultRouter()

routes = common_routes
for route in routes:
    router.register(route['regex'], route['viewset'], basename=route['basename'])

urlpatterns = [
    path("", include("common.urls"), name="common"),

    # path("admin/", admin.site.urls, name="admin"),
    # path("jsreverse/", django_js_reverse.views.urls_js, name="js_reverse"),
    # path(r'api/captcha/', include('rest_captcha.urls')),
    path("api/", include(router.urls), name="api"),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterApi.as_view()),
      path('api/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('api/user/me', UserApi.as_view()),

]
