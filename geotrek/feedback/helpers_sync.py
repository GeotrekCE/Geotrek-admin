import os

from geotrek.feedback import views


class SyncRando:
    def __init__(self, sync):
        self.global_sync = sync

    def sync(self, lang):
        self.global_sync.sync_view(lang, views.CategoryList.as_view(),
                                   os.path.join('api', lang, 'feedback', 'categories.json'),
                                   zipfile=self.global_sync.zipfile)
        self.global_sync.sync_view(lang, views.FeedbackOptionsView.as_view(),
                                   os.path.join('api', lang, 'feedback', 'options.json'),
                                   zipfile=self.global_sync.zipfile)
