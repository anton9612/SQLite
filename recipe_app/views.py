from django.shortcuts import render, redirect
from .forms import RecipeForm, XmlUploadForm, RecipeShowForm, RecipeEditForm
import xml.etree.ElementTree as ET
from django.conf import settings
from .models import Recipe
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q

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

    xml_recipes=[]
    source_form=RecipeShowForm(
        data=request.GET or None,
        initial={"source": "xml"},
    )
    context = {
        "form": RecipeForm(),
        "recipe": None,
        "xml_filename": None,
        "xml_recipes": xml_recipes,
        "upload_form": upload_form,
        "source_form":source_form,
    }

    return render(request, "main/index.html", context)

def save_bd(recipe):
    if Recipe.objects.filter(
        title=recipe["title"],
        cuisine=recipe["cuisine"]
    ).exists():
        raise ValueError("Этот рецепт уже существует")
    new_recipe = Recipe(
        title=recipe["title"],
        cuisine=recipe["cuisine"],
        cooking_time=recipe["cooking_time"],
        servings=recipe["servings"],
        ingredients=recipe["ingredients"],
        instructions=recipe["instructions"]
    )
    new_recipe.save()

def show_recipes(request):
    selected_type=None
    xml_recipes = []
    if request.method=="GET":
        recipe_type=RecipeShowForm(request.GET)
        if recipe_type.is_valid():
            selected_type=recipe_type.cleaned_data["source"]
            recipe_type=recipe_type.cleaned_data
            if selected_type=="xml":

                data_dir = settings.BASE_DIR / "recipes_data"
                recipes_file = data_dir / "recipes.xml"
                if recipes_file.exists():
                    tree = ET.parse(recipes_file)
                    root = tree.getroot()
                    for recipe_element in root:
                        saved_recipe = {}

                        for child in recipe_element:
                            saved_recipe[child.tag] = child.text or ""
                        saved_recipe["filename"] = recipes_file.name
                        xml_recipes.append(saved_recipe)
            elif selected_type=="db":
                xml_recipes=Recipe.objects.all().values()
    source_form=RecipeShowForm(
        data=request.GET or None,
        initial={"source": "xml"},
    )
    context = {
        "form": RecipeForm(),
        "recipe": None,
        "xml_filename": None,
        "xml_recipes": xml_recipes,
        "upload_form": XmlUploadForm(),
        "source_form":source_form,
        "selected_type":selected_type,
    }
    return render(request, "main/index.html", context)

def recipe_edit(request, recipe_id):

    recipe=Recipe.objects.filter(id=recipe_id).first()
    if request.method=="POST":
        form=RecipeEditForm(request.POST)
        if form.is_valid():
            recipe.title = form.cleaned_data["title"]
            recipe.cuisine = form.cleaned_data["cuisine"]
            recipe.cooking_time = form.cleaned_data["cooking_time"]
            recipe.servings = form.cleaned_data["servings"]
            recipe.ingredients = form.cleaned_data["ingredients"]
            recipe.instructions = form.cleaned_data["instructions"]
            recipe.save()
            return redirect("index")
    else:
        form = RecipeEditForm(instance=recipe)

        return render(request, "main/recipe_edit.html",{
            "form":form
    })


def recipe_delete(request, recipe_id):
    if request.method == "POST":
        recipe = Recipe.objects.filter(id=recipe_id).first()
        if recipe:
            recipe.delete()
    return redirect("index")

def recipe_search(request):
    query = request.GET.get("q", "")

    recipes = Recipe.objects.filter(
        Q(title__icontains=query) |
        Q(cuisine__icontains=query) |
        Q(ingredients__icontains=query) |
        Q(instructions__icontains=query)
    ).values(
        "id",
        "title",
        "cuisine",
        "cooking_time",
        "servings",
        "ingredients",
        "instructions"
    )

    return JsonResponse(list(recipes), safe=False)

def recipe_create(request):
    upload_form = XmlUploadForm()
    source_form=RecipeShowForm(
        data=request.GET or None,
        initial={"source": "xml"},
    )
    saved_recipe=None
    recipe=None
    xml_filename=None
    form=RecipeForm()
    if request.method=="POST":
        print("Запрос дошёл до recipe_create!")
        form=RecipeForm(request.POST)
        if form.is_valid():
            print("Форма прошла проверку!")
            recipe=form.cleaned_data.copy()
            save_to=recipe.pop("save_to")
            print("Выбран способ сохранения:", save_to)
            if save_to=="xml":
                xml_filename=save_xml(recipe)
                return redirect("index")
            elif save_to=="db":
                try:
                    save_bd(recipe)
                except (ValueError) as error:
                    form.add_error(
                    "title",
                    f"Файл не прошёл проверку: {error}")
                else:
                    return redirect("index")
        else:
            print("Ошибки формы:", form.errors)



    if request.method=="GET":
        form=RecipeForm()

    data_dir = settings.BASE_DIR / "recipes_data"
    recipes_file = data_dir / "recipes.xml"
    xml_recipes = []

    context = {
        "form": form,
        "recipe": None,
        "xml_filename": None,
        "xml_recipes": None,
        "upload_form": upload_form,
        "source_form":source_form,
    }
    return render(request, "main/index.html", context)
