from grappelli.dashboard.modules import DashboardModule


class CleanupModule(DashboardModule):
    template = "pagetools/admin/dashboard_cleanup_module.html"

    def init_with_context(self, context):
        self.children = [{"a": "b"}]
        super().init_with_context(context)
        self._initialized = True
