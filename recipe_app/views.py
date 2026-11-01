from django.shortcuts import render, redirect
from .forms import RecipeForm, XmlUploadForm
import xml.etree.ElementTree as ET
from django.conf import settings

def read_xml(file_path):
    tree=ET.parse(file_path)
    root=tree.getroot()
    recipe_data={}
    for child in root:
        recipe_data[child.tag]=child.text or ""
    return recipe_data



def save_xml(recipe):
    data_dir=settings.BASE_DIR/"recipes_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path=data_dir/"recipes.xml"
    if not file_path.exists():
        root = ET.Element("recipes")
        tree = ET.ElementTree(root)

    else:
        tree = ET.parse(file_path)
        root = tree.getroot()
    recipe_element=ET.SubElement(root, "recipe")

    for field_name, value in recipe.items():
        child=ET.SubElement(recipe_element,field_name)
        child.text=str(value)

    tree.write(
        file_path,
        encoding="utf-8",
        xml_declaration=True,
    )

    
    return file_path.name
    

def validate_xml_file(xml_object):
    tree=ET.parse(xml_object)
    root=tree.getroot()
    data={}
    
    for child in root:
        data[child.tag]=child.text or ""
    required_fields=[
        "title",
        "cuisine",
        "cooking_time",
        "servings",
        "ingredients",
        "instructions",
        ]
    missing = [
        field for field in required_fields
        if field not in data
    ]
    if missing:
        raise ValueError("В XML отсутствуют поля: " + ", ".join(missing))
    try:
        cooking_time = int(data["cooking_time"])
        servings = int(data["servings"])
    except ValueError:
        raise ValueError("Время приготовления и количество порций должны быть целыми числами.") from None

def xml_upload(request):
    if request.method!="POST":
        return redirect("index")

    upload_form = XmlUploadForm(request.POST, request.FILES)
    if upload_form.is_valid():
        uploaded_file=upload_form.cleaned_data["xml_file"]
        data_dir=settings.BASE_DIR/"recipes_data"
        file_path=data_dir/"recipes.xml"
        if not file_path.exists():
            root = ET.Element("recipes")
            tree = ET.ElementTree(root)
            recipe_element=ET.SubElement(root, "recipe")
        else:
            tree = ET.parse(file_path)
            root = tree.getroot()


        try:
            validate_xml_file(uploaded_file)
        except(ET.ParseError, ValueError) as error:
            upload_form.add_error(
            "xml_file",
            f"Файл не прошёл проверку: {error}",)
        else:
            uploaded_file.seek(0)
            added_recipe=read_xml(uploaded_file)
            save_xml(added_recipe)
            return redirect('index')
            
    data_dir = settings.BASE_DIR / "recipes_data"
    recipes_file = data_dir / "recipes.xml"
    xml_recipes = []

    if recipes_file.exists():
        tree = ET.parse(recipes_file)
        root = tree.getroot()
        for recipe_element in root:
            saved_recipe = {}

            for child in recipe_element:
                saved_recipe[child.tag] = child.text or ""

            saved_recipe["filename"] = recipes_file.name
            xml_recipes.append(saved_recipe)

    context = {
        "form": RecipeForm(),
        "recipe": None,
        "xml_filename": None,
        "xml_recipes": xml_recipes,
        "upload_form": upload_form,
    }

    return render(request, "main/index.html", context)




def recipe_create(request):
    upload_form = XmlUploadForm()
    saved_recipe=None
    recipe=None
    xml_filename=None
    if request.method=="POST":
        form=RecipeForm(request.POST)
        if form.is_valid():
            recipe=form.cleaned_data
            xml_filename=save_xml(recipe)
            return redirect("index")
    if request.method=="GET":
        form=RecipeForm()

    data_dir = settings.BASE_DIR / "recipes_data"
    recipes_file = data_dir / "recipes.xml"
    xml_recipes = []
    if recipes_file.exists():
        tree = ET.parse(recipes_file)
        root = tree.getroot()
        for recipe_element in root:
            saved_recipe = {}

            for child in recipe_element:
                saved_recipe[child.tag] = child.text or ""

            saved_recipe["filename"] = recipes_file.name
            xml_recipes.append(saved_recipe)

    context = {
        "form": RecipeForm(),
        "recipe": None,
        "xml_filename": None,
        "xml_recipes": xml_recipes,
        "upload_form": upload_form,
    }
    return render(request, "main/index.html", context)
