

from pymongo import MongoClient
import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show, output_file
from bokeh.transform import dodge
from bokeh.layouts import column
from bokeh.models import Div, HoverTool

# Connexion à la base "food" hébergée sur le serveur MongoDB Atlas
db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db_name = "food" 
db = client[db_name]

# Liste des collections de la base
print(db.list_collection_names())

# Afficher la liste des index de la collection NYfood
coll_name = "NYfood"
coll = db[coll_name]
print(coll.index_information())


# Nous souhaitons représenter un diagramme en barres pour visualiser les types de restaurants.
# Pour cela, nous devons compter le nombre de fois qu'apparaît chaque modalité de "cuisine".
# Nous ne conservons que les types de cuisine comportant au moins 700 restaurants.

agg_result1 = db.NYfood.aggregate([
                {"$group": {"_id": "$cuisine", 
                            "nb_restos": {"$sum": 1}
                            }
                },
                {"$match": {"nb_restos": {"$gt": 700}}},
                {"$sort": {"nb_restos": -1}}
            ])

ls1=[]
for i in agg_result1:
    ls1.append(i)
print(ls1)


# On aimerait savoir si les note attribuées dépendent du quartiers dans lesquels ils se trouvent.
# Ainsi, pour chaque quartier, on souhaite récupérer le nombre de fois que chaque note apparaît.
# On ne prend pas en compte les quartiers et les notes qui ne sont pas renseignés.

agg_result2 = db.NYfood.aggregate([
                {"$unwind": "$grades"},
                {"$match": {"grades.grade": {"$ne": "Not Yet Graded"}}},
                {"$match": {"borough": {"$ne": "Missing"}}},
                {"$group": {"_id": {"quartier": "$borough",
                            "note": "$grades.grade"},
                            "nb": {"$sum": 1}}
                },
                {"$sort": {"_id.quartier": 1, "nb": -1}}  
            ])

ls2=[]
for i in agg_result2:
    ls2.append(i)
print(ls2)


# Diagramme en barres

# On commence par mettre le résultat de l'aggrégation dans un dataframe

df1 = pd.DataFrame(ls2)
df1 = pd.DataFrame(df1['_id'].values.tolist(), index=df1.index)

df2 = pd.DataFrame(ls2)

df = pd.concat([df1, df2], axis=1)
df.pop('_id')

df_ok = df.pivot('quartier','note')

df_ok.columns = ['A', 'B', 'C', 'P', 'Z']

df_ok['quartier'] = list(df_ok.index)
df_ok.index = list(range(0, len(df_ok)))

# Pour gommer l'effet taille, on prend la proportion de chaque note
# parmi les notes attribuées au quartier, plutôt que l'effectif des notes.
df_prop = df_ok.copy(deep=True)
df_prop["somme"] = df_prop.sum(axis=1)
df_prop = df_prop.loc[:,"A":"Z"].div(df_prop["somme"], axis=0)
df_prop['quartier'] = df_ok['quartier']


# On convertit notre datafame en ColumnDataSource
source = ColumnDataSource(data=df_prop)


# Figure
p = figure(x_range=df_prop.quartier, title="Pourcentage des notes en fonction du quartier",
           height=600, toolbar_location=None, tools="", width=1000)

p.vbar(x=dodge('quartier', -0.35, range=p.x_range), top='A', source=source,
       width=0.12, color="springgreen", legend_label="A")

p.vbar(x=dodge('quartier', -0.2,  range=p.x_range), top='B', source=source,
       width=0.12, color="cornflowerblue", legend_label="B")

p.vbar(x=dodge('quartier',  -0.05, range=p.x_range), top='C', source=source,
       width=0.12, color="burlywood", legend_label="C")

p.vbar(x=dodge('quartier',  0.1, range=p.x_range), top='P', source=source,
       width=0.12, color="coral", legend_label="P")

p.vbar(x=dodge('quartier',  0.25, range=p.x_range), top='Z', source=source,
       width=0.12, color="red", legend_label="Z")

p.x_range.range_padding = 0.1
p.xgrid.grid_line_color = None
p.legend.location = "top_right"
p.legend.orientation = "horizontal"



div = Div(text="""
<a href="index.html ">Accueil</a>""")

layout = column(div,p)

output_file("exo3_MongoDB.html")

show(layout) 


  



