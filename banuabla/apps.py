from django.apps import AppConfig
from django.core.signals import request_finished


class BanuablaConfig(AppConfig):
    name = 'banuabla'

    # def page_exit(self, sender, **kwargs):
    #     print("asdas")
    #     # print(sender, **kwargs)
    #     # original_path = reverse("buy")
    #     # if sender.get_full_path(sender) != original_path:
    #     #     del sender.session["buy"]
    #
    # def ready(self):
    #     request_finished.connect(self.page_exit)
