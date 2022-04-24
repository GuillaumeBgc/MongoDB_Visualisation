
from cProfile import label
from turtle import width
from pymongo import MongoClient
import pymongo
import networkx as nx
import matplotlib.pyplot as plt
from bokeh.plotting import figure, from_networkx
from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool,
                          MultiLine, Plot, Range1d, ResetTool)
from bokeh.layouts import row, column
from bokeh.palettes import Viridis
from bokeh.models import Div

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

res_col = []
for i in agg_result:
    res_col.append(i)


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

res=[]
for i in agg_result2:
    res.append(i)
   
ls_auteur_w = [] 
dict_reseau = {}

for a1 in res:
    ls1= list(a1.values())
    ls_publi_w=[]
    name1=(ls1[0]['name']+' '+ls1[0]['firstname'])
    ls_auteur_w.append((ls1[0]['name']+' '+ls1[0]['firstname']))
    ls_co_auteur=[]
    
    for a2 in res : 
        dict_nb = {}
        cpt = 0
        ls2_auteur_w = [] 
        ls2= list(a2.values())
        name = (ls2[0]['name']+' '+ls2[0]['firstname'])
        if ( name!=name1):
            for i in ls2[1]:
                if (i in ls1[1]) :
                    cpt+=1
            for i in ls2[1]:
                if((i in ls1[1]) and  (dict_nb not in ls_co_auteur)):
                    dict_nb[name]= {'weight':cpt/4}
                    ls_co_auteur.append(dict_nb)
    dict_reseau[ls1[0]['name']+' '+ls1[0]['firstname']]=ls_co_auteur
    
g = nx.Graph()
g.add_nodes_from(dict_reseau.keys())

for k, v in dict_reseau.items():
    if(len(v)!=0):
        for dic in v:
            for k2,v2 in dic.items():
                g.add_weighted_edges_from([(k, k2,v2['weight'])])
        
colors=[0 for i in range(len(res_col))]
for i in range(len(res_col)):
    if res_col[i]['nb']<12:
        colors[i]=Viridis[10][0]
    elif (res_col[i]['nb']<16) and (res_col[i]['nb']>=12):
        
        colors[i]=Viridis[10][9]
    else:
        colors[i]=Viridis[10][4]

# set nodes attributes : 
node_color = {}
for i in range(len(g.nodes())):
    node_color[list(g.nodes())[i]]=colors[i]
    
print(Viridis[10][0])
nx.set_node_attributes(g, node_color, 'node_color')


graph_renderer = from_networkx(g, nx.spring_layout, scale=1, center=(0, 0))
graph_renderer.node_renderer.glyph = Circle(size=15, fill_color='node_color')
plot = figure(title="Liens entre les 20 auteurs les plus prolifiques", x_range=(-1.1,1.1), y_range=(-1.1,1.1),
              tools="", toolbar_location=None)
graph_renderer.edge_renderer.data_source.data["line_width"] = [g.get_edge_data(a,b)['weight'] for a, b in g.edges()]
graph_renderer.edge_renderer.glyph.line_width = {'field': 'line_width'}
plot.renderers.append(graph_renderer)

#Création de la légende
plot.circle(20,30, color=Viridis[10][0], legend_label="moins de 12 articles écrits")
plot.circle(30,20, color=Viridis[10][9], legend_label="entre 12 et 16 articles écrits")
plot.circle(30,20, color=Viridis[10][4], legend_label="plus de 16 articles écrits")
plot.xgrid.grid_line_color = None
plot.legend.location = "bottom_right"
plot.legend.orientation = "horizontal"

print(list(g.nodes()))
node_hover_tool = HoverTool(tooltips=[ ("Auteur", "@index")])
plot.add_tools(node_hover_tool, BoxZoomTool(), ResetTool())

div = Div(text="""
<a href="index.html ">Accueil</a>""")


layout = column(div,plot)
output_file("interactive_graphs.html")
show(layout)