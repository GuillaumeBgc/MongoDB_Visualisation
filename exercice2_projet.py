
from pymongo import MongoClient
import pymongo

# Connexion à la base "publications" hébergée sur le serveur MongoDB Atlas
db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db_name = "publications" 
db = client[db_name]

# Liste des collections de la base
print(db.list_collection_names())

# Afficher la liste des index de la collection NYfood
coll_name = "hal_irisa_2021"
coll = db[coll_name]
print(coll.index_information())


# Afficher les 20 auteurs qui ont écrit plus de 20 publications, classés du plus au moins prolifique

agg_result = db.hal_irisa_2021.aggregate([
                        {"$unwind": "$authors"},
                        {"$group": {"_id": {"name": "$authors.name",
                                            "firstname": "$authors.firstname"},
                                     "nb": {"$sum": 1}}
                        },
                        {"$sort": {"nb": -1}},
                        {"$limit": 20}
                      ])

for i in agg_result:
    print(i)


# On doit maintenant récupérer pour chacun des 20 auteurs les plus prolifiques la liste des identifiants de ses publications
# (puis on fera une double boucle en Python pour avoir la paire des auteurs et leurs co-publications).
# Pour cela, il existe un opérateur $push.

agg_result2 = db.hal_irisa_2021.aggregate([
                        {"$unwind": "$authors"},
                        {"$group": {"_id": {"name": "$authors.name",
                                            "firstname": "$authors.firstname"},
                                    "liste_publi": { "$push":  { "halId": "$halId" } },
                                    "nb": {"$sum": 1}
                                   }
                        },
                        {"$sort": {"nb": -1}},
                        {"$limit": 20}      
                    ])

for i in agg_result2:
    print(i)

