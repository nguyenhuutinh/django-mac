from .views import TCCLBotView
routes = [
    {'regex': r'tccl-bot', 'viewset': TCCLBotView, 'basename': 'TCCLBotView'},
    {'regex': r'health', 'viewset': TCCLBotView, 'basename': 'IndexView'},

    # {'regex': r'tccl-admin', 'viewset': UsersApi, 'basename': 'UsersApi'},

    #{'regex': r'fshare', 'viewset': FshareViewSet, 'basename': 'Fshare'},
    # {'regex': r'google-form', 'viewset': GoogleFormViewSet, 'basename': 'GoogleForm'},
    # {'regex': r'ads', 'viewset': AdsViewSet, 'basename': 'Fshare'},
]
