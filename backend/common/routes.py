from .views import AuthViewSet, RestViewSet

routes = [
    {'regex': r'rest', 'viewset': RestViewSet, 'basename': 'Rest'},
     {'regex': r'auth', 'viewset': AuthViewSet, 'basename': 'Auth'},
]
