from django.urls import include, path

from . import views, views_google_docs

app_name = 'common'
urlpatterns = [
    # path('', views.IndexView.as_view(), name='index'),
    # path('drive/<str:file_name>', views.IndexView.as_view(), name='index'),
    # path('fshare', views.IndexView.as_view(), name='index'),
    path('api/google-form', views_google_docs.GoogleFormViewSet.as_view()),
    # path('ads', views.IndexView.as_view(), name='index'),
    # path('tccl-bot', views.IndexView.as_view(), name='index'),
    path('api/tccl-admin/users', views.UsersApi.as_view()),
    path('api/tccl-admin/messages', views.MessageApi.as_view()),
    # path('auth/', include('knox.urls'))

]
