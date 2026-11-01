from django.urls import path
from . import views
urlpatterns = [
path("", views.recipe_create, name="index"),
path("upload-xml/", views.xml_upload, name="xml_upload"),
]