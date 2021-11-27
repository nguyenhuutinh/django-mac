from django.urls import path

from . import views

app_name = 'common'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('drive/<str:file_name>', views.IndexView.as_view(), name='index'),
    path('fshare', views.IndexView.as_view(), name='index'),

    # path('auth', views.IndexView.as_view(), name='index'),
]
