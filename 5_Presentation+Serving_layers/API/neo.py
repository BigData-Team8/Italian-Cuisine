from neo4j import GraphDatabase
import re
import random

driver = GraphDatabase.driver('bolt://bigdata1.server:7687',
    encrypted = False,
    auth = ('neo4j', ''))

def getRecipes(limit):
    db = driver.session()

    query = """
            MATCH (n:Recipe)-[:HAS_INGREDIENT]->(m:Ingredient)
            RETURN  n.title as title,
                    n.category as category,
                    collect(m.name) as ingredients
            LIMIT %s
            """ % (limit)

    results = db.run(query)
    nodes = []
    for record in results:
        nodes.append({
            'recipe_name': record['recipe_name'],
            'category': record['category'],
            'ingredients': record['ingredients']
        })

    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    return {
        'query': query,
        'entities': nodes
    }

def getCategories():
    db = driver.session()

    query = """
            MATCH (n:Recipe)
            RETURN DISTINCT n.category AS category
            ORDER BY n.category ASC
            """

    results = db.run(query)
    nodes = []
    for record in results:
        if (record['category'] != ''):
            nodes.append(record['category'])

    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    return {
        'query': query,
        'entities': nodes
    }

def getRegions():
    db = driver.session()

    query = """
            MATCH (n:Region)
            RETURN n.name AS region
            ORDER BY n.name ASC
            """

    results = db.run(query)
    nodes = []
    for record in results:
        if (record['region'] != ''):
            nodes.append(record['region'])

    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    return {
        'query': query,
        'entities': nodes
    }    

def getLevels():
    db = driver.session()

    query = """
            MATCH (n:Recipe)
            RETURN DISTINCT n.level AS level
            ORDER BY n.level ASC
            """

    results = db.run(query)
    nodes = []
    for record in results:
        if (record['level'] != ''):
            nodes.append(record['level'])

    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    return {
        'query': query,
        'entities': nodes
    }

def getIngredients():
    db = driver.session()

    query = """
            MATCH (n:Ingredient)
            RETURN n.name AS ingredient
            ORDER BY n.name ASC
            """

    results = db.run(query)
    nodes = []
    for record in results:
        nodes.append(record['ingredient'])

    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    return {
        'query': query,
        'entities': nodes
    }

def getRecipesByCategory(category, limit):
    db = driver.session()

    query = """
            MATCH (recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
            WHERE recipe.category = '%s'

            WITH recipe, collect(i.name) AS ingredients
            OPTIONAL MATCH (recipe:Recipe)-[:REGIONALITY]->(region)
            WITH recipe, ingredients, collect(region.name) AS regions

            RETURN  id(recipe) AS id,
                    recipe.title AS title,
                    recipe.category AS category,
                    regions,
                    recipe.image AS image,
                    recipe.url AS url,
                    recipe.kcal AS kcal,
                    recipe.level AS level,
                    ingredients,
                    rand() as rand

            ORDER BY rand
            LIMIT %s
            """ % (category, limit)

    results = db.run(query)
    nodes = []
    for record in results:
        nodes.append({
            'id': record['id'],
            'title': record['title'],
            'category': record['category'],
            'regions': record['regions'],
            'image': record['image'],
            'url': record['url'],
            'kcal': record['kcal'],
            'level': record['level'],
            'ingredients': record['ingredients']
        })

    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    return {
        'query': query,
        'entities': nodes
    }

def getRecipesByLevel(level, limit):
    db = driver.session()

    query = """
            MATCH (recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
            WHERE recipe.level = '%s'

            WITH recipe, collect(i.name) AS ingredients
            OPTIONAL MATCH (recipe:Recipe)-[:REGIONALITY]->(region)
            WITH recipe, ingredients, collect(region.name) AS regions

            RETURN  id(recipe) AS id,
                    recipe.title AS title,
                    recipe.category AS category,
                    regions,
                    recipe.image AS image,
                    recipe.url AS url,
                    recipe.kcal AS kcal,
                    recipe.level AS level,
                    ingredients,
                    rand() as rand

            ORDER BY rand
            LIMIT %s
            """ % (level, limit)

    results = db.run(query)
    nodes = []
    for record in results:
        nodes.append({
            'id': record['id'],
            'title': record['title'],
            'category': record['category'],
            'regions': record['regions'],
            'image': record['image'],
            'url': record['url'],
            'kcal': record['kcal'],
            'level': record['level'],
            'ingredients': record['ingredients']
        })

    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    return {
        'query': query,
        'entities': nodes
    }

def getRecipesByRegion(region, limit):
    db = driver.session()

    query = """
            MATCH (recipe:Recipe)-[:REGIONALITY]->(region)
            WHERE region.name = '%s'
            WITH recipe, collect(region.name) AS regions
            MATCH (recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
            WITH recipe, regions, collect(i.name) AS ingredients

            RETURN  id(recipe) AS id,
                    recipe.title AS title,
                    recipe.category AS category,
                    regions,
                    recipe.image AS image,
                    recipe.url AS url,
                    recipe.kcal AS kcal,
                    recipe.level AS level,
                    ingredients,
                    rand() as rand
            
            ORDER BY rand
            LIMIT %s
            """ % (region, limit)

    results = db.run(query)
    nodes = []
    for record in results:
        nodes.append({
            'id': record['id'],
            'title': record['title'],
            'category': record['category'],
            'regions': record['regions'],
            'image': record['image'],
            'url': record['url'],
            'kcal': record['kcal'],
            'level': record['level'],
            'ingredients': record['ingredients']
        })

    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    return {
        'query': query,
        'entities': nodes
    }

def getRecipesByIngredient(ingredient, limit):
    db = driver.session()

    query = """
            MATCH (recipe:Recipe)
            WHERE (recipe)-[:HAS_INGREDIENT]->(:Ingredient { name: "%s" })         

            WITH recipe
            MATCH (recipe)-[:REGIONALITY]->(region)

            WITH recipe, collect(region.name) AS regions

            RETURN  id(recipe) AS id,
                    recipe.title AS title,
                    recipe.category AS category,
                    regions,
                    recipe.image AS image,
                    recipe.url AS url,
                    recipe.kcal AS kcal,
                    recipe.level AS level,
                    [(recipe)-[:HAS_INGREDIENT]->(i) | i.name] AS ingredients,
                    rand() as rand
            
            ORDER BY rand
            LIMIT %s
            """ % (ingredient, limit)

    results = db.run(query)
    nodes = []
    for record in results:
        nodes.append({
            'id': record['id'],
            'title': record['title'],
            'category': record['category'],
            'regions': record['regions'],
            'image': record['image'],
            'url': record['url'],
            'kcal': record['kcal'],
            'level': record['level'],
            'ingredients': record['ingredients']
        })

    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    return {
        'query': query,
        'entities': nodes
    }    

def getRecipesByUsers(limit):
    db = driver.session()

    query = """
            MATCH (recipe:UserRecipe)
            WITH recipe
            MATCH (recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
            WITH recipe, collect(i.name) AS ingredients
            OPTIONAL MATCH (recipe)-[:REGIONALITY]->(region)

            RETURN  
                    id(recipe) AS id,
                    recipe.title AS title,
                    recipe.author AS author,
                    apoc.convert.toString(recipe.creation_datetime) AS creation_datetime,
                    ingredients
            
            LIMIT %s
            """ % (limit)

    results = db.run(query)
    nodes = []
    for record in results:
        nodes.append({
            'id': record['id'],
            'title': record['title'],
            'author': record['author'],
            'creation_datetime': record['creation_datetime'],
            'ingredients': record['ingredients']
        })

    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    return {
        'query': query,
        'entities': nodes
    }

def getRecipesBySimilarity(id, threshold, limit):

    db = driver.session()

    query = """
            MATCH (src_recipe:Recipe)-[:HAS_INGREDIENT]->(src_ingredients)
            WHERE id(src_recipe) = %s

            WITH src_recipe, collect(id(src_ingredients)) AS src_id_ingredients, 
            [(src_recipe)-[:HAS_INGREDIENT]->(i) | i.name] AS src_ingredients

            MATCH (dest_recipe:Recipe)-[:HAS_INGREDIENT]->(dest_ingredients)
            WHERE src_recipe <> dest_recipe

            WITH src_recipe, src_id_ingredients, src_ingredients, dest_recipe, collect(id(dest_ingredients)) AS dest_id_ingredients,
                [(dest_recipe)-[:HAS_INGREDIENT]->(i) | i.name] AS dest_ingredients

            OPTIONAL MATCH (dest_recipe)-[:REGIONALITY]->(region:Region)
            WITH src_recipe, src_id_ingredients, src_ingredients, dest_recipe, dest_id_ingredients, dest_ingredients,
                collect(region.name) AS regions

            WHERE gds.alpha.similarity.jaccard(src_id_ingredients, dest_id_ingredients) >= %s

            RETURN  src_recipe.title AS src_recipe,
                    src_ingredients,

                    id(dest_recipe) AS id,
                    dest_recipe.title AS title,
                    dest_recipe.category AS category,
                    regions,
                    dest_recipe.image AS image,
                    dest_recipe.url AS url,
                    dest_recipe.kcal AS kcal,
                    dest_recipe.level AS level,

                    gds.alpha.similarity.jaccard(src_id_ingredients, dest_id_ingredients) AS similarity,
                    dest_ingredients AS ingredients,

                    [n IN src_ingredients WHERE n IN dest_ingredients] AS common_ingredients,
                    size([n IN src_ingredients WHERE n IN dest_ingredients]) AS intersection

            ORDER BY similarity DESC, intersection DESC
            LIMIT %s
            """ % (id, threshold, limit)

    result = db.run(query)
    nodes = []
    for record in result:

        nodes.append({
            'src_recipe': record['src_recipe'],
            'src_ingredients': record['src_ingredients'],

            'id': record['id'],
            'title': record['title'],
            'category': record['category'],
            'regions': record['regions'],
            'image': record['image'],
            'url': record['url'],
            'kcal': record['kcal'],
            'level': record['level'],
            'score': round(record['similarity'], 5),
            'ingredients': record['ingredients'],
            'common_ingredients': record['common_ingredients'],
            'intersection': record['intersection']
        })

    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    return {
        'query': query,
        'entities': nodes
    }

def getSimilarIngredients(ingredient, threshold, limit, algorithm):
    
    ingredient = str(ingredient)
    db = driver.session()

    if (algorithm == 'levenshtein'):

        query = """
                MATCH (n:Ingredient)
                WHERE apoc.text.levenshteinSimilarity(apoc.text.clean(n.name), apoc.text.clean("%s")) >= %s
                RETURN
                    apoc.text.levenshteinSimilarity(apoc.text.clean(n.name), apoc.text.clean("%s")) AS similarity,
                    n.name AS ingredient
                ORDER BY apoc.text.levenshteinSimilarity(apoc.text.clean(n.name), apoc.text.clean("%s")) DESCENDING
                LIMIT %s
                """ % (ingredient, threshold, ingredient, ingredient, limit)
    
    elif (algorithm == 'jarowinkler'):

        query = """
                MATCH (n:Ingredient)
                WHERE apoc.text.jaroWinklerDistance(apoc.text.clean(n.name), apoc.text.clean("%s")) >= %s
                RETURN
                    apoc.text.jaroWinklerDistance(apoc.text.clean(n.name), apoc.text.clean("%s")) AS similarity,
                    n.name AS ingredient
                ORDER BY apoc.text.jaroWinklerDistance(apoc.text.clean(n.name), apoc.text.clean("%s")) DESCENDING
                LIMIT %s
                """ % (ingredient, threshold, ingredient, ingredient, limit)

    nodes = []
    result = db.run(query)
    
    for record in result:
        nodes.append({ 'ingredient': record['ingredient'], 'score': round(record['similarity'], 5)})

    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    return {
        'query': query,
        'entities': nodes
    }   

def getRecipesByIngredients(recipe_name, author, ingredients, threshold, limit, regional_only):

    db = driver.session()
    queries = []

    recipeTitle = recipe_name if (recipe_name != '') else 'user-recipe-' + str(random.randint(0, 9999999))
    author = author if (author != '') else 'anonymous'

    query = """
            CREATE (n:UserRecipe { 
                title: "%s",
                author: "%s",
                creation_datetime: datetime({ timezone: 'Europe/Rome' })
            })
            RETURN id(n) AS recipe_id
            """ % (recipeTitle, author)
    
    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    queries.append(query)
    result = db.run(query)
    for record in result: userRecipeId = record['recipe_id']

    for ingredientName in ingredients.split(','):

        query = """
                MATCH (n:UserRecipe), (m:Ingredient { name: "%s" })
                WHERE id(n) = %s
                CREATE (n)-[:HAS_INGREDIENT]->(m)
                """ % (ingredientName.strip(), userRecipeId)

        query = re.sub(' +', ' ', query).replace('\n', '').strip()
        queries.append(query)
        result = db.run(query)

    # prepares a string with joined ingredients comma separated; e.g.: ['pane', 'acqua']
    quotedIngredients = ', '.join('"{0}"'.format(token) for token in ingredients.split(','))

    optional = ' OPTIONAL ' if regional_only == 'no' else ''
    limit = 'LIMIT ' + str(limit) if limit else ''

    query = """
            MATCH (src_recipe:UserRecipe)-[:HAS_INGREDIENT]->(src_ingredients)
            WHERE id(src_recipe) = %s

            WITH src_recipe, collect(id(src_ingredients)) AS src_id_ingredients

            MATCH (dest_recipe:Recipe)-[:HAS_INGREDIENT]->(dest_ingredients)
            WHERE src_recipe <> dest_recipe
            AND any(i in [%s] WHERE exists( (dest_recipe)-[:HAS_INGREDIENT]->(:Ingredient {name: i})) )

            WITH src_recipe, src_id_ingredients, dest_recipe, collect(id(dest_ingredients)) AS dest_id_ingredients,
            [(dest_recipe)-[:HAS_INGREDIENT]->(i) | i.name] AS ingredients

            %s MATCH (dest_recipe)-[:REGIONALITY]->(region:Region)
            WITH src_recipe, src_id_ingredients, dest_recipe, dest_id_ingredients, ingredients,
                collect(region.name) AS regions

            WHERE gds.alpha.similarity.jaccard(src_id_ingredients, dest_id_ingredients) >= %s

            RETURN  src_recipe.title AS user_recipe,

                    id(dest_recipe) AS id,
                    dest_recipe.title AS title,
                    dest_recipe.category AS category,
                    regions,
                    dest_recipe.image AS image,
                    dest_recipe.url AS url,
                    dest_recipe.kcal AS kcal,
                    dest_recipe.level AS level,

                    gds.alpha.similarity.jaccard(src_id_ingredients, dest_id_ingredients) AS similarity,
                    ingredients,

                    [n IN [%s] WHERE n IN ingredients] AS common_ingredients,
                    size([n IN [%s] WHERE n IN ingredients]) AS intersection

            ORDER BY intersection DESC, similarity DESC
            %s
            """ % (userRecipeId, quotedIngredients, optional, threshold, quotedIngredients, quotedIngredients, limit)

    query = re.sub(' +', ' ', query).replace('\n', '').strip()
    queries.append(query)
    result = db.run(query)

    nodes = []
    for record in result:

        nodes.append({
            'id': record['id'],
            'title': record['title'],
            'category': record['category'],
            'regions': record['regions'],
            'image': record['image'],
            'url': record['url'],
            'kcal': record['kcal'],
            'level': record['level'],
            'score': round(record['similarity'], 5),
            'ingredients': record['ingredients'],
            'common_ingredients': record['common_ingredients'],
            'intersection': record['intersection']
        })

    return {
        'query': query,
        'entities': nodes,
        'user_recipe_id': userRecipeId
    }

driver.session().close()
