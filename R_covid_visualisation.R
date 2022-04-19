
#Requete MDB
#Rennes = {"type": "Point","coordinates": [-1.68333, 48.083328]}
#db.getCollection('dump_Jan2022').find({"location": {$near: {$geometry: Rennes, $maxDistance: 50000}}})

library("mongolite")

url="mongodb://etudiant:ur2@clusterm1-shard-00-00.0rm7t.mongodb.net:27017,clusterm1-shard-00-01.0rm7t.mongodb.net:27017,clusterm1-shard-00-02.0rm7t.mongodb.net:27017/?ssl=true&replicaSet=atlas-l4xi61-shard-0"

mdb = mongo(collection="dump_Jan2022", db="doctolib",
            url=url,
            verbose=TRUE)

q = 'Rennes = {"type": "Point","coordinates": [-1.68333, 48.083328]}
db.getCollection("dump_Jan2022").find({"location": {$near: {$geometry: Rennes, $maxDistance: 50000}}})'

print(mdb$find(query = q))
