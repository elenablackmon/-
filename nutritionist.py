import recipies
import argparse
import warnings
warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser()
parser.add_argument('menu', nargs='?')  # создаем доп ключ для программы с меню
namespace = parser.parse_args()

if namespace.menu:
    menu = recipies.Menu()
    menu1 = menu.breakfast()
    menu2 = menu.lunch()
    menu3 = menu.dinner()

else:
    list_of_ingredients = input(
        "Please enter the list of ingredients separated by commas "
        "and without quotation marks\nВведите список ингридиентов "
        "через запятую и без кавычек, на английском):")
    list_of_ingredients = list_of_ingredients.split(", ")
    res = recipies.Forecast(list_of_ingredients)
    result1 = res.preprocess()
    result2 = res.predict_rating_category()
    nutr = recipies.NutritionFacts(list_of_ingredients)
    result3 = nutr.retrieve()
    result4 = nutr.filter()
    recip = recipies.SimilarRecipes(list_of_ingredients)
    result5 = recip.find_all()
    result6 = recip.top_similar()
