from data_models import models
from data_models import cache


class ImportInterface:
    def __init__(self):
        self.data_models = models
        self.cache_models = cache