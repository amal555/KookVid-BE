from django.apps import AppConfig

class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'

    def ready(self):
        print("Recipes app is ready")
        import recipes.signals