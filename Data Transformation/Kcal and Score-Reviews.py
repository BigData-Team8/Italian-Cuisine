

import json

with open(path+"GialloZafferano.json", encoding="utf8") as file:
    data = json.load(file)



final = data[:]

for recipe in final:

    if "nutrition" not in recipe:
        continue

    if len(recipe["nutrition"]) > 0:

        tmp = recipe["nutrition"][0].split()
        recipe["main"]["kcal"] = []

        for el in tmp:
            if el.strip().isdigit():
                recipe["main"]["kcal"].append(int(el))
                break

for recipe in final:
    cont += 1
    if "rating" in recipe["main"]:
        mod += 1
        recipe["main"]["reviews"] = int(str(recipe["main"]["rating"][1]).strip())

        try:
            recipe["main"]["score"] = int(recipe["main"]["rating"][0].strip())
        except ValueError:
            try:
                recipe["main"]["score"] = float(recipe["main"]["rating"][0].replace(",",".").strip())
            except ValueError:
                recipe["main"]["score"] = 0


        del recipe["main"]["rating"]




with open(path+"GZ_final", 'w', encoding = "utf8") as outfile:
    json.dump(final, outfile, indent = 2, ensure_ascii = False) 

