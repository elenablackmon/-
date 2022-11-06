import pandas as pd
import random
import pickle


class Forecast:
    """
    Предсказание рейтинга блюда или его класса
    """
    list_of_ingredients_default = list(pd.read_csv(
        'data/parsed_recepies_final.csv').columns[4:302])

    def __init__(self, list_of_ingredients):
        self.list_of_ingredients = list_of_ingredients
        self.list_of_ingredients_false = []
        # задаем количество признаков, как в трейне-тесте модели
        q = len(Forecast.list_of_ingredients_default)
        zeros = [0] * q  # формируем по умолчанию нулевой датасет
        df = pd.DataFrame(zeros, index=Forecast.list_of_ingredients_default)
        self.vector = df.T

    def preprocess(self):
        """
        Этот метод преобразует список ингредиентов в структуры данных,
        которые используются в алгоритмах машинного обучения,
        чтобы сделать предсказание.
        """
        print("\n" + 'I. OUR FORECAST')
        # проверяем, есть ли все ингридиенты в нашем датасете
        list_of_ingredients_true = []
        for i in range(len(self.list_of_ingredients)):
            if self.list_of_ingredients[i] in \
                    Forecast.list_of_ingredients_default:
                list_of_ingredients_true.append(self.list_of_ingredients[i])
            else:
                self.list_of_ingredients_false.append(
                    self.list_of_ingredients[i])

        # добавляем в датафрейм колонки с заданными ингридиентами
        # если ингридиент уже есть в датасете, то
        # значение колонки с данным названием просто обновится
        for k in range(len(list_of_ingredients_true)):
            self.vector[list_of_ingredients_true[k]] = 1

        return self.list_of_ingredients_false, self.vector

    def predict_rating_category(self):
        """
        Этот метод возращает рейтинговую категорию для списка ингредиентов,
        используя классификационную модель, которая была обучена заранее.
        Помимо самого рейтинга, метод возвращает также и текст,
        который дает интерпретацию этой категории и
        дает рекомендации
        """
        loaded_model = pickle.load(open('data/best_model.sav', 'rb'))
        rating = loaded_model.predict(self.vector)
        text = " "
        rating_cat = rating[0]
        if rating_cat == 'great':
            text = "It should be something delicious!"
        elif rating_cat == 'so-so':
            text = "It is not something special, but should be normal"
        elif rating_cat == 'bad':
            text = "It is not recommended"

        if self.list_of_ingredients_false:
            text_1 = ("Probably we don't have info in our database about "
                      "following ingredients:{}".format(
                       self.list_of_ingredients_false) + "\n" +
                      "This set of ingredients is probably {}. {}".format(
                          rating_cat, text))
        else:
            text_1 = "This set of ingredients is probably {}. {}".format(
                rating_cat, text)

        print("\n" + text_1 + "\n")

        return text_1


class NutritionFacts(Forecast):
    """
    Выдает информацию о пищевой ценности ингредиентов.
    """
    default_lst = list(pd.read_csv(
        'data/share_in_limits_final.csv').columns[1:295])
    nutrients_default_lst = list(pd.read_csv(
        'data/share_in_limits_final.csv').iloc[:, 0])

    def __init__(self, list_of_ingredients):

        super().__init__(list_of_ingredients)
        # задаем кол-во нутриентов как в базовой таблице+1 на индекс
        q = 1 + len(NutritionFacts.nutrients_default_lst)
        # формируем по умолчанию нулевой датасет для добавления новых строк
        zeros = [0] * q
        self.facts = pd.DataFrame(
            zeros, index=['index', 'Calcium, Ca', 'Cholesterol',
                          'Choline, total', 'Copper, Cu',
                          'Fatty acids, total saturated', 'Folate, total',
                          'Iron, Fe', 'Magnesium, Mg', 'Manganese, Mn',
                          'Niacin', 'Pantothenic acid', 'Phosphorus, P',
                          'Potassium, K', 'Protein', 'Riboflavin',
                          'Selenium, Se', 'Sodium, Na', 'Thiamin',
                          'Vitamin A, IU', 'Vitamin B-12', 'Vitamin B-6',
                          'Vitamin C, total ascorbic acid',
                          'Vitamin D (D2 + D3)',
                          'Vitamin E (alpha-tocopherol)',
                          'Vitamin K (Dihydrophylloquinone)', 'Zinc, Zn'])

        # считываем файл и транспонируем для удобства
        self.nutrition_facts = pd.read_csv(
            'data/share_in_limits_final.csv', index_col=0)
        self.nutrition_facts = self.nutrition_facts.T
        self.nutrition_facts = self.nutrition_facts.reset_index()
        self.facts = self.facts.T
        # выделяю основные нутриенты
        self.must_nutrients = ['Protein', 'Cholesterol', 'Vitamin D (D2 + D3)']
        self.n = 6

    def retrieve(self):
        """
        Этот метод получает всю имеющуюся информацию о пищевой ценности из
        файла с заранее собранной информацией по заданным ингредиентам.
        """
        # добавляем в датафрейм ингридиенты из заданного списка
        for i in self.list_of_ingredients:
            # при условии, что ингридиенты в базовом датафрейме
            if i in NutritionFacts.default_lst:
                facts_add = self.nutrition_facts.loc[
                    self.nutrition_facts['index'] == i]
                self.facts = pd.concat([self.facts, facts_add], axis=0)

        # удаляем нулевую строку, которая была для начала создания датасета
        self.facts = self.facts.set_index('index')
        self.facts = self.facts.drop(labels=[0], axis=0)
        self.facts = self.facts.T

        return self.facts

    def filter(self):
        """
        Этот метод отбирает из всей информации о пищевой ценности только те
        нутриенты, которые были заданы в must_nutrients,
        а также топ-n нутриентов с наибольшим значением дневной нормы
        потребления для заданного ингредиента.
        """

        print('II. NUTRITIONAL VALUE')
        text_with_facts = " "
        text_with_facts1 = '{}: {} - {}% of Daily Value'

        for i in self.list_of_ingredients:
            # по сути работаем только с продуктами из списка
            if i in NutritionFacts.default_lst:
                df2 = self.facts[i]  # Series нутриентов для каждого продукта
                df2 = df2.sort_values(ascending=False)
                df3 = pd.DataFrame(df2)
                df3 = df3.reset_index()
                # создаем нулевой датафрейм, чтобы потом нарастить данными
                nutr_top = pd.DataFrame([0], index=[0])
                # формируем датафрейм из данных для топ-нутриентов
                for k in self.must_nutrients:
                    if k in self.nutrients_default_lst:
                        nutr_top = pd.concat(
                            [nutr_top, df3.loc[df3['index'] == k]], axis=0)
                # удаляем нулевую строку и нулевой столбец,
                # которые были заданы при создании датасета
                nutr_top = nutr_top.drop(labels=0, axis=0)
                nutr_top = nutr_top.drop(labels=0, axis=1)
                df3 = df3.set_index('index')
                # удаляем топ-нутриенты из первого отсортированного
                # датафрейма, чтобы избежать дублей
                for k in self.must_nutrients:
                    if k in NutritionFacts.nutrients_default_lst:
                        df3 = df3.drop(labels=k, axis=0)
                df3 = df3.reset_index()
                # соединяем 2 датафрейма:
                # сверху топ-нутриенты+отсортированные по убыванию
                nutr_top = pd.concat([nutr_top, df3], axis=0)

                for j in range(0, self.n):
                    text_with_facts = \
                        text_with_facts + \
                        "\n" + text_with_facts1.format(
                            i, nutr_top.iloc[j, 0], round(nutr_top.iloc[j, 1]))

        print(text_with_facts + "\n")

        return text_with_facts


class SimilarRecipes(Forecast):  # с наследованием 1го класса
    """
    Рекомендация похожих рецептов с дополнительной информацией
    """
    indexes = []  # сразу задаем список индексов
    default_lst = list(pd.read_csv(
        'data/parsed_recepies_final.csv').columns[4:302])
    df_recipes = pd.read_csv(
        'data/parsed_recepies_final.csv', index_col=0)
    # сохраняем датасет в Т-виде и первончальном для удобства
    df_recipesT = df_recipes.T

    w = len(df_recipes)  # кол-во колонок в трансформиррованном датасете
    # в виде словаря формируем строку в Т-версии датасета,
    # где в ячеках будут списки с названиями ингридиентов
    dict_ingr = {}
    lst_ingr = []
    for j in range(0, w):
        for i in default_lst:
            if df_recipesT.loc[i, j] == 1:
                lst_ingr.append(i)
        dict_ingr[j] = lst_ingr
        lst_ingr = []
    # из полученного словаря формируем датафрейм со списком ингридиентов
    df_tot_ingr = pd.DataFrame([dict_ingr])
    # объединяем Т-версию исходного датафрейма со списками ингредиентов
    df_total_ingr_rep = pd.concat([df_recipesT, df_tot_ingr], axis=0)
    df_total_ingr_repT = df_total_ingr_rep.T

    def __init__(self, list_of_ingredients):

        super().__init__(list_of_ingredients)
        # задаем список только тех ингридиентов,
        # которые в самом начальном датасете
        self.list_of_ingredients_true = []

    def find_all(self):
        """
        Этот метод возвращает список индексов рецептов,
        которые содержат заданный список ингредиентов.
        """
        print('III. TOP-3 SIMILAR RECIPES' + "\n")

        for i in self.list_of_ingredients:
            if i in SimilarRecipes.default_lst:
                self.list_of_ingredients_true.append(i)
        # обработака ошибки,если ни одного ингридиента нет в нашем списке
        if not self.list_of_ingredients_true:
            print("Sorry, there are no recipes for such set of ingredients")
        else:  # собственно формируем список индексов с рецептами
            for j in range(len(SimilarRecipes.df_total_ingr_repT)):
                if set(self.list_of_ingredients_true).issubset(
                        SimilarRecipes.df_total_ingr_rep.iloc[-1, j]):
                    SimilarRecipes.indexes.append(j)

        if not SimilarRecipes.indexes:
            print("Probably we don't have similar recipes in "
                  "our database for such set. Please try another set" + "\n")

        return SimilarRecipes.indexes

    def top_similar(self):
        """
        Этот метод возвращает текст с информацией о рецептах:
        с заголовком, рейтингом и URL. Чтобы это сделать, он вначале
        находит топ-n наиболее похожих рецептов с точки зрения
        количества дополнительных ингредиентов, которые потребуются
        в этих рецептах. Наиболее похожим будет тот, в котором не
        требуется никаких других ингредиентов.  Далее идет тот,
        у которого появляется 1 доп. ингредиент. Далее – 2.
        Если рецепт нуждается в более, чем 5 доп. ингредиентах,
        то такой рецепт не выводится.
        """
        text_with_recipes = " "
        text_with_recipes1 = "- {}, rating: {}, URL:{} "
        n = 3
        try:  # формируем датафрейм с отобранными индексами
            df_similar_recipes = \
                SimilarRecipes.df_total_ingr_rep[SimilarRecipes.indexes]
            # сохраняем датасет также в Т-виде для дальнейших циклов
            df_similar_recipes_t = df_similar_recipes.T
            # переименовываем колонку со списком продуктов для удобства
            df_similar_recipes_t = \
                df_similar_recipes_t.rename(columns={0: 'set'})

            # создаем колонку с кол-вом продуктов для каждого рецепта
            df_similar_recipes_t['q-ty of ingr'] = df_similar_recipes_t.apply(
                lambda x: len(x['set']), axis=1)
            # подсчитываем кол-во продуктов в заданном списке
            s = len(self.list_of_ingredients_true)
            # создаем колонку, где подсчитываем, сколько продуктов не хватает
            df_similar_recipes_t = df_similar_recipes_t.assign(f_sort=(
                    df_similar_recipes_t['q-ty of ingr'] - s))
            # отбираем только те рецепты, где не хватает 5 и менее продуктов
            df_similar_recipes_t_final = \
                df_similar_recipes_t.loc[df_similar_recipes_t['f_sort'] <= 5]
            # сортируем датафрейм так, что сначала идут рецепты,
            # где почти все ингридиенты уже есть
            df_similar_recipes_t_final = \
                df_similar_recipes_t_final.sort_values(by='f_sort')
            # дропаем индекс, чтобы было проще идти по порядку
            df_similar_recipes_t_final = \
                df_similar_recipes_t_final.reset_index()

            q = min(n, len(df_similar_recipes_t_final))
            if q == 0:
                text_with_recipes = "Probably we don't have similar recipes " \
                                    "in our database for such set. " \
                                    "Please try another set"
            else:
                for m in range(0, q):  # печатаем топ-n
                    text_with_recipes = \
                        text_with_recipes + "\n" + \
                        text_with_recipes1.format(
                            df_similar_recipes_t_final.iloc[m, 1],
                            df_similar_recipes_t_final.iloc[m, 2],
                            df_similar_recipes_t_final.iloc[m, 3])

            print(text_with_recipes)

        except (ValueError, TypeError):
            pass

        return text_with_recipes


class Menu:
    """
    Рекомендации рецептов дневного меню на каждый день
    """

    def __init__(self):
        """
        Данные предобработаны предварительно
        """
        self.df_breakfast = pd.read_csv(
            'data/breakfast_final.csv', index_col=0)
        self.df_lunch = pd.read_csv('data/lunch_final.csv', index_col=0)
        self.df_dinner = pd.read_csv('data/dinner_final.csv', index_col=0)

    def breakfast(self):
        """
        rating great
        """
        rng = range(0, len(self.df_breakfast))
        k = random.choice(rng)
        n = self.df_breakfast.iloc[k, -1]
        n = n.replace(',', '')
        n = n.replace('[', '')
        n = n.replace(']', '')
        n = n.replace("'", "")
        n = n.split(' ')

        text_1 = ("BREAKFAST:" + "\n" + "---------------------" + "\n" +
                  "{} (rating: {} )".format(self.df_breakfast.iloc[k, 0],
                                            self.df_breakfast.iloc[k, 1])
                  + "\n" + "   " + "\n" +
                  "Ingredients:" + "\n" + ",\n".join(map(str, n)) + "\n"
                  + "   " + "\n" +
                  "Nutrients:" + "\n" + "calories: " + str(round(
                    self.df_breakfast.iloc[k, 2], 1)) + "%," + "\n" +
                  "protein: " + str(round(self.df_breakfast.iloc[k, 3], 1))
                  + "%," + "\n" +
                  "fat: " + str(round(self.df_breakfast.iloc[k, 4], 1))
                  + "%," + "\n" +
                  "sodium: " + str(round(self.df_breakfast.iloc[k, 5], 1))
                  + "%" + "\n"
                  + "URL: {} ".format(self.df_breakfast.iloc[k, -3]) + "\n")
        print(text_1)

        return text_1

    def lunch(self):
        """
        rating great
        """
        rng = range(0, len(self.df_lunch))
        k = random.choice(rng)
        n = self.df_lunch.iloc[k, -1]
        n = n.replace(',', '')
        n = n.replace('[', '')
        n = n.replace(']', '')
        n = n.replace("'", "")
        n = n.split(' ')

        text_1 = ("LUNCH:" + "\n" + "---------------------" + "\n" +
                  "{} (rating: {} )".format(self.df_lunch.iloc[k, 0],
                                            self.df_lunch.iloc[k, 1])
                  + "\n" + "   " + "\n" +
                  "Ingredients:" + "\n" + ",\n".join(map(str, n)) +
                  "\n" + "   " + "\n" +
                  "Nutrients:" + "\n" + "calories: " + str(round(
                    self.df_lunch.iloc[k, 2], 1)) + "%," + "\n" +
                  "protein: " + str(round(self.df_lunch.iloc[k, 3], 1))
                  + "%," + "\n" +
                  "fat: " + str(round(self.df_lunch.iloc[k, 4], 1))
                  + "%," + "\n" +
                  "sodium: " + str(round(self.df_lunch.iloc[k, 5], 1))
                  + "%" + "\n"
                  + "URL: {} ".format(self.df_lunch.iloc[k, -3]) + "\n")
        print(text_1)

        return text_1

    def dinner(self):
        """
        rating great
        """
        rng = range(0, len(self.df_dinner))
        k = random.choice(rng)
        n = self.df_dinner.iloc[k, -1]
        n = n.replace(',', '')
        n = n.replace('[', '')
        n = n.replace(']', '')
        n = n.replace("'", "")
        n = n.split(' ')

        text_1 = ("DINNER:" + "\n" + "---------------------" + "\n" +
                  "{} (rating: {} )".format(self.df_dinner.iloc[k, 0],
                                            self.df_dinner.iloc[k, 1])
                  + "\n" + "   " + "\n" + "Ingredients:" + "\n" +
                  ",\n".join(map(str, n)) + "\n" + "   " + "\n" +
                  "Nutrients:" + "\n" + "calories: " + str(round(
                    self.df_dinner.iloc[k, 2], 1)) + "%," + "\n" +
                  "protein: " + str(round(self.df_dinner.iloc[k, 3], 1))
                  + "%," + "\n" +
                  "fat: " + str(round(self.df_dinner.iloc[k, 4], 1))
                  + "%," + "\n" +
                  "sodium: " + str(round(self.df_dinner.iloc[k, 5], 1))
                  + "%" + "\n"
                  + "URL: {} ".format(self.df_dinner.iloc[k, -3]))

        print(text_1)

        return text_1
