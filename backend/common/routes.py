from .views import FshareViewSet, GoogleDriveViewSet

routes = [
    {'regex': r'drive', 'viewset': GoogleDriveViewSet, 'basename': 'GoogleDrive'},
     {'regex': r'fshare', 'viewset': FshareViewSet, 'basename': 'Fshare'},
]
