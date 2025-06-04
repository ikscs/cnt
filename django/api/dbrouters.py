class PcntRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'pcnt':
            return 'pcnt'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'pcnt':
            return 'pcnt'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'pcnt':
            return False  # Prevent migrations for this app
        return None
