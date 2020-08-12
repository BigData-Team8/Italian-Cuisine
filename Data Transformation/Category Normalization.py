
import pandas as pd

data = pd.read_csv("C:/Users/flori/OneDrive/Desktop/Progetto Big Data/Finale/Recipes-Categories.csv")


dizionario = data.groupby('Category').agg({'Tag': lambda x: x.tolist()})['Tag'].to_dict()
print(dizionario)


    #CUCCHIAIO CAT

    import json
    import pandas as pd
    from collections import Counter



    with open(path+"Cucchiaio-freq2.json", encoding="utf8") as file:
        data1 = json.load(file)

    final1 = data1[:]

    for recipe in final1:
        del recipe["main"]["type"]
        find = False
        recipe["main"]["type"] = []

        if "categories" in recipe["main"]:
            for el in recipe["main"]["categories"]:
                for key in dizionario:
                    if el.lower() in dizionario[key]:
                        find = True
                        recipe["main"]["type"].append(key)
                    if find:
                        break
                if find:
                    break

        if find:
            continue      

        for el in recipe["main"]["keywords"]:
            for key in dizionario:
                    if el.lower() in dizionario[key]:
                        find = True
                        recipe["main"]["type"].append(key)
                    if find:
                        break
            if find:
                break

        if find:
            continue

        if "tags" in recipe["main"]:
            for el in recipe["main"]["tags"]:
                for key in dizionario:
                    if el.lower() in dizionario[key]:
                        find = True
                        recipe["main"]["type"].append(key)
                    if find:
                        break
                if find:
                    break

    with open(path+'Cucchiaio_final.json', 'w', encoding = "utf8") as outfile:
        json.dump(final1, outfile, indent = 2, ensure_ascii = False)     



    #GIALLOZAFFERANO CAT

    import json
    import pandas as pd
    from collections import Counter



    with open(path+"GZ-freq2.json", encoding="utf8") as file:
        data2 = json.load(file)

    final2 = data2[:]

    for recipe in final2:
        del recipe["main"]["type"]
        find = False
        recipe["main"]["type"] = []

        if "categories" in recipe["main"]:
            for el in recipe["main"]["categories"]:
                for key in dizionario:
                    if el.lower() in dizionario[key]:
                        find = True
                        recipe["main"]["type"].append(key)
                    if find:
                        break
                if find:
                    break

        if find:
            continue

        for el in recipe["main"]["keywords"]:
            for key in dizionario:
                    if el.lower() in dizionario[key]:
                        find = True
                        recipe["main"]["type"].append(key)
                    if find:
                        break
            if find:
                break



    with open(path+'GialloZafferano_final.json', 'w', encoding = "utf8") as outfile:
        json.dump(final2, outfile, indent = 2, ensure_ascii = False)        


    #RICETTEREGIONALI CAT

    import json
    import pandas as pd
    from collections import Counter



    with open(path+"RR-freq2.json", encoding="utf8") as file:
        data3 = json.load(file)

    final3 = data3[:]

    for recipe in final3:
        del recipe["main"]["type"]
        find = False
        recipe["main"]["type"] = []

        for key in dizionario:
            el = recipe["main"]["category"].lower()
            if el in dizionario[key]:
                find = True
                recipe["main"]["type"].append(key)
            if find:
                break

    with open(path+'RicetteRegionali_final.json', 'w', encoding = "utf8") as outfile:
        json.dump(final3, outfile, indent = 2, ensure_ascii = False)    



