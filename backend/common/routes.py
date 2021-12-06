from .views import AdsViewSet, FshareViewSet, GoogleDriveViewSet

routes = [
    {'regex': r'drive', 'viewset': GoogleDriveViewSet, 'basename': 'GoogleDrive'},
     {'regex': r'fshare', 'viewset': FshareViewSet, 'basename': 'Fshare'},
     {'regex': r'ads', 'viewset': AdsViewSet, 'basename': 'Fshare'},
]
