# from .views import TCCLBotView, UsersApi
from .views_google_docs import GoogleFormViewSet
routes = [
    # {'regex': r'tccl-bot', 'viewset': TCCLBotView, 'basename': 'TCCLBotView'},
    # {'regex': r'tccl-admin', 'viewset': UsersApi, 'basename': 'UsersApi'},

    #{'regex': r'fshare', 'viewset': FshareViewSet, 'basename': 'Fshare'},
    {'regex': r'google-form', 'viewset': GoogleFormViewSet, 'basename': 'GoogleForm'},
    # {'regex': r'ads', 'viewset': AdsViewSet, 'basename': 'Fshare'},
]
