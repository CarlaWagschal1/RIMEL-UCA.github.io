#!/usr/bin/env python
# coding: utf-8

# # Машинное обучение, ФКН ВШЭ
# 
# # Практическое задание 7. Бустинговое
# 
# ## Общая информация
# 
# Дата выдачи: 13.12.2022
# 
# Мягкий дедлайн: 20.12.2022 23:59 MSK
# 
# Жёсткий дедлайн: 20.12.2022 23:59 MSK
# 
# ## Оценивание и штрафы
# 
# Каждая из задач имеет определенную «стоимость» (указана в скобках около задачи). Максимально допустимая оценка за работу — 10 баллов.
# 
# Сдавать задание после указанного срока сдачи нельзя. При выставлении неполного балла за задание в связи с наличием ошибок на усмотрение проверяющего предусмотрена возможность исправить работу на указанных в ответном письме условиях.
# 
# Задание выполняется самостоятельно. «Похожие» решения считаются плагиатом и все задействованные студенты (в том числе те, у кого списали) не могут получить за него больше 0 баллов (подробнее о плагиате см. на странице курса). Если вы нашли решение какого-то из заданий (или его часть) в открытом источнике, необходимо указать ссылку на этот источник в отдельном блоке в конце вашей работы (скорее всего вы будете не единственным, кто это нашел, поэтому чтобы исключить подозрение в плагиате, необходима ссылка на источник).
# 
# Неэффективная реализация кода может негативно отразиться на оценке.
# 
# ## Формат сдачи
# Задания сдаются через систему anytask. Посылка должна содержать:
# * Ноутбук homework-practice-07-Username.ipynb
# 
# Username — ваша фамилия на латинице

# ## О задании
# 
# В этом задании вам предстоит вручную запрограммировать один из самых мощных алгоритмов машинного обучения — бустинг.

# In[ ]:


from warnings import filterwarnings

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.sparse import load_npz
from sklearn.model_selection import train_test_split


sns.set(style='darkgrid')
filterwarnings('ignore')

# In[ ]:


x = load_npz('x.npz')
y = np.load('y.npy')

# Разделим на обучающую, валидационную и тестовую выборки (`random_state` оставьте равным 1337 для воспроизводимости).

# In[ ]:


x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=1337)

x_test, x_valid, y_test, y_valid = train_test_split(x_test, y_test, test_size=0.5, random_state=1337)

x_train.shape, x_valid.shape, x_test.shape

# ## Задание 1. Реализация градиентного бустингового (4 балла)
# 
# Вам нужно дописать код в файлике `boosting.py`. Для вас уже подготовлен шаблон класса `Boosting`, вы можете менять его по своему усмотрению.
# 
# ### Инструкции для функций:
# 
# #### `__init__`
# 
# В `__init__` приходит кучка параметров, распишем что есть что:
# 
#  - `base_model_class` - класс базовой модели нашего бустинга
#  - `base_model_params` - словарь с гиперпараметрами для базовой модели
#  - `n_estimators` - какое количество базовых моделей нужно обучить
#  - `learning_rate` - темп обучения, должен быть из полуинтервала $(0, 1]$
#  - `subsample` - доля объектов, на которой будет обучаться базовая модель (какую часть составляет бутстрапная выборка от исходной обучающей)
#  - `early_stopping_rounds` - число итераций, после которых при отсутствии улучшения качества на валидационной выборке обучение останавливается
#  - `plot` - строить ли после обучения всех базовых моделей график с качеством
# 
# #### `fit`
# 
# В `fit` приходит две выборки, обучающая и валидационная. На обучающей мы обучаем новые базовые модели, на валидационной считаем качество для ранней остановки (если это предусматривают параметры).
# 
# Сначала нам нужно сделать какую-то нулевую модель, сделать предсказания для обучающей и валидационной выборок (в шаблоне это нулевая модель, соответственно предсказания это просто `np.zeros`). После этого нужно обучить `n_estimators` базовых моделей (как и на что обучаются базовые модели смотрите в лекциях и семинарах). После каждой обученной базовой модели мы должны обновить текущие предсказания, посчитать ошибку на обучающей и валидационной выборках (используем `loss_fn` для этого), проверить на раннюю остановку.
# 
# После всего цикла обучения надо нарисовать график (если `plot`).
# 
# 
# #### `fit_new_base_model`
# 
# В `fit_new_base_model` приходит обучающая выборка (целиком) и текущие предсказания для неё. Мы должны сгенерировать бутстрап выборку для обучения базовой модели и обучить базовую модель. После обучения модели запускаем поиск оптимальной гаммы, добавляем новую модель и гамму (не забываем про темп обучения) в соответствующие списки.
# 
# #### `predict_proba`
# 
# В `predict_proba` приходит выборка, нужно предсказать вероятности для неё. Суммируем предсказания базовых моделей на этой выборке (не забываем про гаммы) и накидываем сигмоиду.

# In[ ]:


% load_ext autoreload

# In[ ]:


% autoreload 2

from boosting import Boosting

# ### Проверка кода
# 
# У автора задания всё учится около одной секунды.

# In[ ]:


boosting = Boosting()

% time boosting.fit(x_train, y_train, x_valid, y_valid)

assert len(boosting.models) == boosting.n_estimators
assert len(boosting.gammas) == boosting.n_estimators

assert boosting.predict_proba(x_test).shape == (x_test.shape[0], 2)

print(f'Train ROC-AUC {boosting.score(x_train, y_train):.4f}')
print(f'Valid ROC-AUC {boosting.score(x_valid, y_valid):.4f}')
print(f'Test ROC-AUC {boosting.score(x_test, y_test):.4f}')

# ## Задание 2. Обучение градиентного бустингового (1 балл)
# 
# Оцените качество на тестовой выборке вашей имплементации бустинга для различной максимальной глубины решающего дерева в качестве базовой модели. Здесь и далее мы будем использовать метрику ROC-AUC.
# 
# Перебирайте максимальную глубину от 1 до 30 с шагом 2 (остальные параметры бустинга стоит оставить равными по умолчанию). Постройте график зависимости качества на обучающей и тестовой выборке в зависимости от глубины.

# In[ ]:


results = {}

depths = range(1, 30, 2)

# YOUR CODE:

# **Какая из моделей имеет лучшее качество? Как вы можете это объяснить?**
# 
# `### ваше решение тут ###`

# ## Задание 3. Подбираем гиперпараметры и ищем лучшую модель (3 балла)
# 
# Подберите по валидационной выборке основные гиперпараметры для вашей модели бустинга. Следует подобрать все основные параметры для самого градиентного бустинга и для самих базовых моделей. Существуют библиотеки для подбора гиперпараметров, попробуйте использовать какую-нибудь из следующих двух - [Hyperopt](https://github.com/hyperopt/hyperopt), [Optuna](https://optuna.org/).

# In[ ]:


# YOUR CODE:

# ## Задание 4. Интерпретация бустингового (2 балл)
# 
# Постройте калибровочную кривую для вашей лучшей модели бустинга. Насколько хорошо бустинг оценивает вероятности? Постройте также калибровочную кривую для логистической регрессии, сравните их между собой. Проанализируйте полученные результаты.

# In[ ]:


# YOUR CODE:

# Теперь попробуем оценить важность признаков для бустинга.
# 
# Поскольку наша базовая модель - это дерево из `sklearn`, мы можем вычислить важность признака отдельно для каждого дерева и усреднить (воспользуйтесь `feature_importances_` у `DecisionTreeRegressor`), после этого нормировать значения, чтобы они суммировались в единицу (обратите внимание, что они должны быть неотрицательными - иначе вы что-то сделали не так).
# 
# Допишите в вашей реализации бустинга функцию `feature_importances_` чтобы она возвращала описанные выше важности признаков.
# 
# Нарисуйте столбчатую диаграмму важности признаков. На соседнем графике нарисуйте важность признаков для логистической регрессии, для этого используйте модули весов. Сравните графики. Проанализируйте полученные результаты.

# In[ ]:


# YOUR CODE:

# Кстати, чаще всего излишние признаки могут вредить качеству бустинга. Попробуйте отфильтровать на основании диаграммы хвост наименее важных признаков и снова обучить модель (с теми же гиперпараметрами). Стало ли лучше?

# In[ ]:


# YOUR CODE:

# ## Задание 5 (бонус). Блендинговое (1 балл)
# 
# Реализуйте блендинг над вашей лучшей моделью и логистической регрессией. Улучшилось ли качество?

# In[ ]:


# YOUR CODE:

# ## Задание 6 (бонус). Катбустовое (1 балл)
# 
# Запустите [CatBoost](https://catboost.ai/en/docs/concepts/python-quickstart) на наших данных, сравните с вашей реализацией. Где получилось лучше?

# In[ ]:


# YOUR CODE:

# ## Социализационный бонус. Новогоднее 🎆 (0.5 балла)
# 
# Сфотографируйтесь с наряженной новогодней или рождественской ёлкой! Приложите фотографию, опишите свои впечатления, чего вы ждете от нового 2023 года?
