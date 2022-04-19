
#Requete MDB
#Rennes = {"type": "Point","coordinates": [-1.68333, 48.083328]}
#db.getCollection('dump_Jan2022').find({"location": {$near: {$geometry: Rennes, $maxDistance: 50000}}})

library("mongolite")

url="mongodb://etudiant:ur2@clusterm1-shard-00-00.0rm7t.mongodb.net:27017,clusterm1-shard-00-01.0rm7t.mongodb.net:27017,clusterm1-shard-00-02.0rm7t.mongodb.net:27017/?ssl=true&replicaSet=atlas-l4xi61-shard-0"

mdb = mongo(collection="dump_Jan2022", db="doctolib",
            url=url,
            verbose=TRUE)

q1 = '[
{"$geoNear": {"near": {"type": "Point","coordinates": [-1.68333, 48.083328]},
"distanceField": "distance",
"maxDistance": 50000}},

{"$match": {"$nor":[{"visit_motives": {"$size": 0}}]}},
{"$unwind" : "$visit_motives"},
{"$match": {"$nor":[{"visit_motives.slots": {"$size": 0}}]}},
{"$unwind" : "$visit_motives.slots"},
{"$match": {"visit_motives.slots": {"$gte": {"$date": "2022-01-26T00:00:00Z"}, "$lt": {"$date": "2022-01-30T00:00:00Z"}}}},
{"$group" : {"_id": "$name",
"nb": {"$sum": 1},
"coord":{"$max":"$location.coordinates"}}}
]'

data.nb_rdv <- mdb$aggregate(q1)

qBonus = '[
{"$geoNear": {"near": {"type": "Point","coordinates": [-1.68333, 48.083328]},
"distanceField": "distance",
"maxDistance": 50000}},

{"$match": {"$nor":[{"visit_motives": {"$size": 0}}]}},
{"$unwind" : "$visit_motives"},
{"$match": {"$nor":[{"visit_motives.slots": {"$size": 0}}]}},
{"$unwind" : "$visit_motives.slots"},
{"$match": {"visit_motives.slots": {"$gte": {"$date": "2022-01-01T00:00:00Z"}, "$lt": {"$date": "2022-06-02T00:00:00Z"}}}},
{"$match": {"visit_motives.name": {"$regex": "^1re", "$options" : "i"}}},
{"$group" : {"_id": "$name",
"nb": {"$sum": 1},
"coord":{"$max":"$location.coordinates"}}}
]'
data.bonus <- mdb$aggregate(qBonus)
