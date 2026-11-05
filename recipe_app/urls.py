from django.urls import path
from . import views
urlpatterns = [
path("", views.recipe_create, name="index"),
path("upload-xml/", views.xml_upload, name="xml_upload"),
path("show_recipes/", views.show_recipes, name="show_recipes"),
path("recipe_edit/<int:recipe_id>/",views.recipe_edit,name="recipe_edit"),
path("recipe_delete/<int:recipe_id>/",views.recipe_delete,name="recipe_delete"),
path("search_recipes/", views.recipe_search, name="recipe_search"),
]