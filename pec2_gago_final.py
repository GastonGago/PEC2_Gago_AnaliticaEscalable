# -*- coding: utf-8 -*-
"""PEC2_Gago Final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rWGTRAJhjjTJ5YeUhPIdZzGHVjSgfM16
"""

import pandas as pd
import numpy as np
import joblib
import seaborn as sns
import matplotlib as plt

from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split, cross_val_score, cross_val_predict, KFold, GridSearchCV
from sklearn.preprocessing import RobustScaler, OneHotEncoder, StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier

df = pd.read_csv('/content/insurance.csv', na_values=' ?')
df.head()

"""Cargo el dataset"""

df.isna().sum()

"""Verifico que no hayan nulos"""

df.shape

df.columns

df.columns = df.columns.str.strip()
df.columns

sns.pairplot(df[["charges"]])

sns.pairplot(np.log10(df[['charges']]))

df.info()

x, y = df.drop(["charges"], axis = 1), df["charges"]

"""Saco la variable charges del analisis ya que es mi variable dependiente"""

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(x, y, random_state=42)

X_train

y_train

from sklearn.compose import make_column_transformer
from sklearn.preprocessing import OneHotEncoder

caterogical_columns = ["sex", "smoker", "region"]
numerical_columns = ["age", "bmi", "children"]

preprocessor = make_column_transformer((OneHotEncoder(drop="if_binary"), caterogical_columns),
                                       remainder="passthrough",
                                       verbose_feature_names_out=False,)

""" Hago un preprocesador de columnas que aplica codificación one-hot a las columnas categóricas y mantiene las columnas numéricas sin transformación. El preprocesador se puede utilizar en un pipeline de aprendizaje automático para realizar transformaciones en los datos antes de entrenar un modelo."""

from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge
from sklearn.compose import TransformedTargetRegressor
import scipy as sp

model = make_pipeline(
    preprocessor,
    TransformedTargetRegressor(regressor=Ridge (alpha=1e-10), func=np.log10, inverse_func=sp.special.exp10),
)

""" Hago un pipeline que aplica el preprocesamiento de columnas y luego entreno un modelo de regresión Ridge con una transformación logarítmica en el objetivo. El pipeline se utiliza para entrenar y realizar predicciones en datos de entrada."""

model.fit(X_train, y_train)

"""Ajusto los parámetros del modelo utilizando los datos de entrenamiento"""

from sklearn.metrics import median_absolute_error

y_pred = model.predict(X_train)

mae = median_absolute_error(y_train, y_pred)
string_score = f"MAE on training set: {mae: 2f} euros"
y_pred = model.predict(X_test)
mae = median_absolute_error(y_test, y_pred)
string_score += f"\nMAR on testing set: {mae: 2f} euros"

"""Se realizan evaluaciones del rendimiento del modelo utilizando el MAE.

Almaceno las predicciones en y_pred.

Depues calculo el MAE comparando las predicciones del modelo y_pred con los valores reales del conjunto de datos de entrenamiento y_train.

Luego, se construye una cadena de texto string_score que muestra el valor del MAE en el conjunto de datos de entrenamiento.

A continuación, se utilizan las mismas operaciones para calcular el MAE en el conjunto de datos de prueba (X_test y y_test). Las predicciones se almacenan en y_pred y se calcula el MAE comparando las predicciones con los valores reales.

Finalmente, se actualiza la cadena de texto string_score para incluir el valor del MAE en el conjunto de datos de prueba.
"""

print(string_score)

"""En este caso, el valor del MAE en el conjunto de datos de entrenamiento es de 933.902042 euros, lo que significa que, en promedio, las predicciones del modelo difieren de los valores reales en aproximadamente 933.902042 euros en el conjunto de datos de entrenamiento.

El valor del MAE en el conjunto de datos de prueba es de 953.419613 euros, lo que indica que, en promedio, las predicciones del modelo difieren de los valores reales en aproximadamente 953.419613 euros en el conjunto de datos de prueba.


"""

import matplotlib.pyplot as plt

fig, ax = plt.subplots (figsize = (5,5))
plt.scatter(y_test, y_pred)
ax.plot([0, 1], [0, 1], transform=ax.transAxes, ls="--", c="red")
plt.text(50000, 20000, string_score)
plt.title("Ridge model, small regularization")
plt.ylabel("Model predictions")
plt.xlabel("Truths")

feature_names = model[:-1].get_feature_names_out()

coefs = pd.DataFrame(
    model[-1].regressor_.coef_,
    columns=["Coefficients"],
    index=feature_names
)

coefs

"""Estos coeficientes representan el impacto relativo de cada característica en la predicción del valor objetivo (en este caso, el costo del seguro). Cada coeficiente indica la dirección (positiva o negativa) y la magnitud del efecto que la característica tiene sobre el costo del seguro.

Cómo podemos ver un factor clave que influye en el precio del seguro de vida es si fuma o no.
"""

coefs.plot.barh(figsize=(9,7))
plt.title("Ridge model, small regularization")
plt.axvline(x=0, color=".5")
plt.xlabel("Raw coefficient values")
plt.subplots_adjust(left=0.3)

"""Aca podemos ver un gráfico de barras horizontales que muestra los coeficientes del modelo de regresión, lo que te da la importancia relativa de cada característica en la predicción del costo del seguro de vida."""

X_train_preprocessed = pd.DataFrame(
    model[:-1].transform(X_train), columns=feature_names
)

X_train_preprocessed.std(axis=0).plot.barh(figsize=(9,7))
plt.title("Feature ranges")
plt.xlabel("Std. dev. of feature values")
plt.subplots_adjust(left=0.3)

"""Aca vemos un gráfico de barras horizontales que muestra las desviaciones estándar de las características en el conjunto de entrenamiento preprocesado. Esto te permite visualizar la variabilidad de las características y tener una idea de la escala y rango de valores de cada una.

 Podemos ver que "age" y "bmi" tienen barras más largas, significa que estas características tienen una mayor desviacion estaandar en comparacion con las demás características.
"""

coefs = pd.DataFrame(
    model[-1].regressor_.coef_ * X_train_preprocessed.std(axis=0),
    columns=["Coefficient importance"],
    index=feature_names,
)
coefs.plot(kind="barh", figsize=(9,7))
plt.xlabel("Coefficient values corrected by the feature's std. dev.")
plt.title("Ridge model, small regularization")
plt.axvline(x=0, color=".5")
plt.subplots_adjust(left=0.3)

"""En este gráfico podemos ver una representación visual de la importancia relativa de cada característica corrigiendo los coeficientes por la desviación estándar. Ayuda a identificar qué características tienen una mayor influencia en el resultado del modelo en comparación con otras características.

Cómo es evidente la edad y si fuma o no, son las que tienen mayor influencia en el precio del seguro.
"""

from sklearn.model_selection import cross_validate, RepeatedKFold
from sklearn.metrics import make_scorer
from sklearn.compose import TransformedTargetRegressor
import pandas as pd

cv = RepeatedKFold(n_splits=5, n_repeats=5, random_state=0)
cv_model = cross_validate(
    model,
    x,
    y,
    cv=cv,
    return_estimator=True,
    n_jobs=2,
)
coefs = pd.DataFrame(
    [
        est[-1].regressor_.coef_
        for est, (train_idx, _) in zip(cv_model["estimator"], cv.split(x, y))
    ],
    columns=feature_names,
)

coefs

"""En este código, se realiza una validación cruzada repetida para evaluar el rendimiento del modelo en múltiples divisiones del conjunto de datos.


Cada fila del DataFrame representa los coeficientes de un modelo ajustado en una división específica.
"""

plt.figure(figsize=(5, 5))
sns.stripplot(data=coefs, orient="h", color="k", alpha=0.5)
sns.boxplot(data=coefs, orient="h", color="cyan", saturation=0.5)
plt.axvline(x=0, color="0.5")
plt.title("Coeficiente de importancia y su variabilidad")
plt.xlabel("Coeficiente de importancia")
plt.show()

"""Este último gráfico muestra la importancia relativa de los coeficientes del modelo y su variabilidad a través de la validación cruzada. Los puntos individuales representan los valores de los coeficientes en cada división, y las cajas resumen la distribución de los valores.

Vemos que fumar o no es muy relevante y se considera un coeficiente importante.

# EJERCICIO 2
"""

import pickle

with open('modelo.pkl', 'wb') as file:
    pickle.dump(model, file)

# Cargar el modelo desde el archivo pkl
with open('modelo.pkl', 'rb') as file:
     model = pickle.load(file)

"""# EJERCICIO 3"""

from flask import Flask, request, jsonify
import pickle

# Cargar el modelo entrenado desde el archivo pkl
with open('modelo.pkl', 'rb') as file:
    model = pickle.load(file)

# Inicializar la aplicación Flask
app = Flask(__name__)

# Definir la ruta y el método para realizar predicciones
@app.route('/predict', methods=['POST'])
def predict():
    # Obtener los datos de la solicitud
    data = request.json

    # Realizar la predicción utilizando el modelo cargado
    prediction = model.predict([data['features']])

    # Devolver la predicción como respuesta en formato JSON
    response = {'prediction': prediction.tolist()}
    return jsonify(response)

# Especificar la configuración para ejecutar la aplicación en todas las interfaces de red
if __name__ == '__main__':
    app.run()



"""# EXTRA"""

pip install tox

!tox

