
import json
import nltk
from dandelion import DataTXT

path = ""

regions = {"Lombardia":{"lombardia","lombarda"}, "Lazio":{"lazio", "laziale"}, "Campania":{"campania","campana"}, "Sicilia":{"sicilia","siciliana"},
           "Veneto":{"veneto"}, "Emilia-Romagna":{"emilia-romagna","emilia romagna","emilia","romagna","emiliana","romagnola"}, "Piemonte":{"piemonte","piemontese"},
           "Puglia":{"puglia","pugliese"}, "Toscana":{"toscana"},"Calabria":{"calabria","calabrese"}, "Sardegna":{"sardegna","sarda"},
           "Liguria":{"liguria","ligure"}, "Marche":{"marche","marchigiana"}, "Abruzzo":{"abruzzo","abruzzese"},
           "Friuli-Venezia Giulia":{"friuli-venezia giulia", "friuli venezia giulia", "friuli", "friulana"}, 
           "Trentino-Alto Adige":{"trentino-alto adige", "trentina", "altoatesina"},"Umbria":{"umbria", "umbra"}, 
           "Basilicata":{"basilicata", "lucana"}, "Molise":{"molise","molisana"}, "Valle d'Aosta":{"valle d'aosta", "val d'aosta", "valdostana"}}

tokens = ["2f9d007ee5664cd2afe97a311d9964bf", "d36829f2c99e4c20b84a95321677a6e1",
          "0d437bcfabdd493c9450e68cb1b72fb5", "594d28a9734141529eb89759f333457d",
          "c9d1515b60484882b205c63f30f8fd3d", "c208c8e22e364d078a841a2eec926a0c",
          "73c81f9d807143219e06ef0cfed45a0c", "7f1a9b68075941daab67a155a842f63c",
          "7740b8d10d9f46c8adf02a8274359ae8", "8e6dfdaadb0f48798c77d0efc5768dce"]
    

#DANDELION GIALLO ZAFFERANO

with open(path+"giallo_zafferano_final.json", encoding="utf8") as file:
    data = json.load(file)

final = data[:]

ind = 0       #index for tokens list
cont = 0      #it is reset to 0 when the token cont == 1000

for recipe in final:
    
    if cont == 950:
        ind += 1      #when 1000 calls are get, the next token will be used
        cont = 0
    
    datatxt = DataTXT(token=tokens[ind])
    response = datatxt.nex(text = recipe["main"]["presentation"], min_confidence = 0.65)  #calling Dandelion API
    
    recipe["main"]["regions"] = []
    recipe["main"]["nation"] = []
    
    for annotation in response.annotations:    #for all the entities extracted by Dandelion
        splitter = annotation.label.split()    #sometimes the entity is not a single word
        
        for word in splitter:
            find = False
            for region,s in regions.items():
                for adj in s:
                    score = nltk.edit_distance(word.lower(), adj)
                    if (score < 2) and (region not in recipe["main"]["regions"]):
                        recipe["main"]["regions"].append(region)
                        find = True
                        break
                if find:
                    break
        
    if len(recipe["main"]["regions"]) > 0:
        recipe["main"]["nation"].append("Italy")
            
    cont += 1
    
with open(path+'giallozafferano_dandelion.json', 'w', encoding = "utf8") as outfile:
    json.dump(final, outfile, indent = 2, ensure_ascii = False)


    
#DANDELION CUCCHIAIO

with open(path+"cucchiaio.json", encoding="utf8") as file:
    data = json.load(file)

final = data[:]

ind = 0       #index for tokens list
cont = 0      #it is reset to 0 when the token cont == 1000

for recipe in final:
    
    if cont == 800:
        ind += 1      #when 1000 calls are get, the next token will be used
        cont = 0
    
    recipe["main"]["regions"] = []
    recipe["main"]["nation"] = []
    
    datatxt = DataTXT(token=tokens[ind])
    
    if "presentation" in recipe["main"]:
        try:
            response = datatxt.nex(text = recipe["main"]["presentation"], min_confidence = 0.65)  #calling Dandelion API
        except Exception:
            try:
                response = datatxt.nex(text = recipe["main"]["description"], min_confidence = 0.65)  #calling Dandelion API
            except Exception:
                pass
            
            continue
    
    for annotation in response.annotations:    #for all the entities extracted by Dandelion
        splitter = annotation.label.split()    #sometimes the entity is not a single word
        
        for word in splitter:
            find = False
            for region,s in regions.items():
                for adj in s:
                    score = nltk.edit_distance(word.lower(), adj)
                    if (score < 2) and (region not in recipe["main"]["regions"]):
                        recipe["main"]["regions"].append(region)
                        find = True
                        break
                if find:
                    break
        
    if len(recipe["main"]["regions"]) > 0:
        recipe["main"]["nation"].append("Italy")
            
    cont += 1
    
with open(path+'cucchiaio_dandelion.json', 'w', encoding = "utf8") as outfile:
    json.dump(final, outfile, indent = 2, ensure_ascii = False)


    
#CLEANING GIALLO ZAFFERANO

with open(path+"GZ_final.json", encoding="utf8") as file:
    data = json.load(file)

final = data[:]
cont = 0
for recipe in final:
    if "region" in recipe["main"]:
        for region in recipe["main"]["region"]:
            for label in regions:
                find = False
                new = label.replace("-", " ")
                score = nltk.edit_distance(region.lower(), new.lower())
                if (score < 3):
                    find = True
                    recipe["main"]["region"].append(label)
                    recipe["main"]["region"].remove(region)
                if find:
                    break
        recipe["main"]["regions"].extend(recipe["main"]["region"])
        del recipe["main"]["region"]
    recipe["main"]["regionality"] = list(set(recipe["main"]["regions"]))
    del recipe["main"]["regions"]
    
    recipe["main"]["nationality"] = []
    del recipe["main"]["nation"]
    if len(recipe["main"]["regionality"]) > 0:
        recipe["main"]["nationality"].append("Italy")
        
        
    
        
with open(path+'Giallo-Zafferano.json', 'w', encoding = "utf8") as outfile:
    json.dump(final, outfile, indent = 2, ensure_ascii = False)    



#CLEANING CUCCHIAIO

with open(path+"cucchiaio_final.json", encoding="utf8") as file:
    data = json.load(file)

final = data[:]

for recipe in final:
    tmp = []
    if "region" in recipe["main"]:
        for label in regions:
            new = label.replace("-", " ")
            for region in recipe["main"]["region"]:
                find = False
                score = nltk.edit_distance(region.lower(), new.lower())
                if score < 2:
                    tmp.append(label)
                    find = True
                if find:
                    break
                    
    recipe["main"]["regions"].extend(tmp)
    
    recipe["main"]["regionality"] = list(set(recipe["main"]["regions"]))
    del recipe["main"]["regions"]
    if "region" in recipe["main"]:
        del recipe["main"]["region"]
    
    recipe["main"]["nationality"] = []
    del recipe["main"]["nation"]
    if len(recipe["main"]["regionality"]) > 0:
        recipe["main"]["nationality"].append("Italy")
        
        
    
        
with open(path+'Cucchiaio2.json', 'w', encoding = "utf8") as outfile:
    json.dump(final, outfile, indent = 2, ensure_ascii = False)    




#CLEANING RICETTEREGIONALI



with open(path+'ricetteregionali.json', encoding="utf8") as file:
    data = json.load(file)

final = data[:]
for recipe in final:
    recipe["main"]["regionality"] = []
    for label in regions:
        find = False
        for reg in regions[label]:
            score = nltk.edit_distance(recipe["main"]["region"].lower(), reg.lower())
            if score < 2:
                recipe["main"]["regionality"].append(label)
                find = True
            if find:
                break
    
    del recipe["main"]["region"]
    
    if len(recipe["main"]["regionality"]) > 0:
        recipe["main"]["nationality"] = ["Italy"]
        
        
    
        
with open(path+'Ricette-Regionali.json', 'w', encoding = "utf8") as outfile:
    json.dump(final, outfile, indent = 2, ensure_ascii = False)    

