
from pymongo import MongoClient
import pymongo

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

agg_result = db.NYfood.aggregate([
                {"$group": {"_id": "$cuisine", 
                            "nb_restos": {"$sum": 1}
                            }
                },
                {"$match": {"nb_restos": {"$gt": 700}}},
                {"$sort": {"nb_restos": -1}}
            ])

ls1=[]
for i in agg_result:
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

ls=[]
for i in agg_result2:
    ls.append(i)
print(ls)
