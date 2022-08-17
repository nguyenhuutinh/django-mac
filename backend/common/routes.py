from .views import TeleGramBotViewSet

routes = [
    {'regex': r'telegram-bot', 'viewset': TeleGramBotViewSet, 'basename': 'TelegramBot'},
    #{'regex': r'fshare', 'viewset': FshareViewSet, 'basename': 'Fshare'},
    #{'regex': r'google-form', 'viewset': GoogleFormViewSet, 'basename': 'GoogleForm'},
    # {'regex': r'ads', 'viewset': AdsViewSet, 'basename': 'Fshare'},
]
