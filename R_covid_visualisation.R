
#Requete MDB
#Rennes = {"type": "Point","coordinates": [-1.68333, 48.083328]}
#db.getCollection('dump_Jan2022').find({"location": {$near: {$geometry: Rennes, $maxDistance: 50000}}})


# Chargement des packages
library("mongolite")
# library(tidyverse)
library(leaflet)


# Récupération des données
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

data.bonus <- mdb$aggregate


##### Question principale #####

### Modification du jeu de données ### 

# Renommage de la colonne '_id'
colnames(data.nb_rdv)[1] <- 'centre'


# Séparation en deux de la colonne coord

coord <- data.nb_rdv$coord
long <- numeric(length(coord))
lat <- numeric(length(coord))

for (i in 1:length(coord)){
  long[i] <- coord[[i]][1]
  lat[i] <- coord[[i]][2]
}

# On les ajoute au jeu de données
data.nb_rdv$long <- long
data.nb_rdv$lat <- lat


# Répartition de la variable 'nb' en 3 classes (couleurs) en fixant des seuils 
# qui nous semblent judicieux :

couleurs <- numeric(nrow(data.nb_rdv))
for (i in 1:nrow(data.nb_rdv)){
  if (data.nb_rdv$nb[i] < 100){
    couleurs[i] <- 'red'
  }
  else if (data.nb_rdv$nb[i] >= 100 & data.nb_rdv$nb[i] <= 150){
    couleurs[i] <- 'orange'
  }
  else if (data.nb_rdv$nb[i] > 150){
    couleurs[i] <- 'green'
  }
}

# On l'ajoute au jeu de données
data.nb_rdv$couleurs <- couleurs


### Cartographie ### 

leaflet(data = data.nb_rdv) %>% 
  addTiles() %>%
  addCircleMarkers(~long, ~lat, 
                   popup = ~paste(centre, "Nombre de doses disponibles : ", as.character(nb), sep="<br/>"),
                   radius=5, fillOpacity=1, color=couleurs)



##### Bonus #####

### Modification du jeu de données ### 

# Renommage de la colonne '_id'
colnames(data.bonus)[1] <- 'centre'


# Séparation en deux de la colonne coord

coord <- data.bonus$coord
long <- numeric(length(coord))
lat <- numeric(length(coord))

for (i in 1:length(coord)){
  long[i] <- coord[[i]][1]
  lat[i] <- coord[[i]][2]
}

# On les ajoute au jeu de données
data.bonus$long <- long
data.bonus$lat <- lat


# Répartition de la variable 'nb' en 3 classes (couleurs) en fixant des seuils 
# qui nous semblent judicieux :

couleurs <- numeric(nrow(data.bonus))
for (i in 1:nrow(data.bonus)){
  if (data.bonus$nb[i] < 100){
    couleurs[i] <- 'red'
  }
  else if (data.bonus$nb[i] >= 100 & data.bonus$nb[i] <= 150){
    couleurs[i] <- 'orange'
  }
  else if (data.bonus$nb[i] > 150){
    couleurs[i] <- 'green'
  }
}

# On l'ajoute au jeu de données
data.bonus$couleurs <- couleurs


### Cartographie ### 

leaflet(data = data.bonus) %>% 
  addTiles() %>%
  addCircleMarkers(~long, ~lat, 
                   popup = ~paste(centre, "Nombre de 1ères doses disponibles : ", as.character(nb), sep="<br/>"),
                   radius=5, fillOpacity=1, color=couleurs)





