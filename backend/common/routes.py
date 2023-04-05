from .views import GoogleFormViewSet, GoogleDriveViewSet, FshareViewSet, ExcelViewSet

routes = [
    {'regex': r'drive', 'viewset': GoogleDriveViewSet, 'basename': 'GoogleDrive'},
    {'regex': r'fshare', 'viewset': FshareViewSet, 'basename': 'Fshare'},
    {'regex': r'google-form', 'viewset': GoogleFormViewSet, 'basename': 'GoogleForm'},
    {'regex': r'excel', 'viewset': ExcelViewSet, 'basename': 'Excel'},
    # {'regex': r'ads', 'viewset': AdsViewSet, 'basename': 'Fshare'},
]
