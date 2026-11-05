from django import forms


class RecipeForm(forms.Form):
    title = forms.CharField(label="Название блюда", max_length=100
    )

    cuisine = forms.CharField(
        label="Кухня",
        max_length=50
    )

    cooking_time = forms.IntegerField(
        label="Время приготовления (минуты)",
        min_value=1,
        max_value=1440
    )

    servings = forms.IntegerField(
        label="Количество порций",
        min_value=1,
        max_value=100
    )

    ingredients = forms.CharField(
        label="Ингредиенты",
        widget=forms.Textarea(attrs={"rows": 5}),
        help_text="Указывай каждый ингредиент с новой строки."
    )

    instructions = forms.CharField(
        label="Приготовление",
        widget=forms.Textarea(attrs={"rows": 7}),
        help_text="Опиши этапы приготовления по порядку."
    )

    save_to = forms.ChoiceField(
        label="Куда сохранить рецепт?",
        choices=[
            ("xml", "XML-файл"),
            ("db","База данных"),
        ]
    )


class XmlUploadForm(forms.Form):
    xml_file=forms.FileField(label="Выберите Файл")
    def clean_xml_file(self):
        upoaded_file=self.cleaned_data["xml_file"]
        if not upoaded_file.name.lower().endswith(".xml"):
            raise forms.ValidationError("Можно загружать только xml файлы")
        return upoaded_file

class RecipeShowForm(forms.Form):
    source=forms.ChoiceField(
        label="Откуда показать рецепты?",
        choices=[
            ("xml","XML-файлы"),
            ("db","База данных")
        ]
    )