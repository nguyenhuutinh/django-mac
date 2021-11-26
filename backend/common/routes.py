from .views import FshareViewSet, GoogleDriveViewSet

routes = [
    {'regex': r'drive', 'viewset': GoogleDriveViewSet, 'basename': 'Rest'},
     {'regex': r'fshare', 'viewset': FshareViewSet, 'basename': 'Download'},
]
