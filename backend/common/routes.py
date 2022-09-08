from .views import TCCLBotView

routes = [
    {'regex': r'tccl-bot', 'viewset': TCCLBotView, 'basename': 'TCCLBotView'},
    #{'regex': r'fshare', 'viewset': FshareViewSet, 'basename': 'Fshare'},
    #{'regex': r'google-form', 'viewset': GoogleFormViewSet, 'basename': 'GoogleForm'},
    # {'regex': r'ads', 'viewset': AdsViewSet, 'basename': 'Fshare'},
]
