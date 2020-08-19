<?php

use Slim\App;

return function (App $app) {
    $app->get('/', \App\Action\HomeAction::class)->setName('home');
    $app->get('/about', \App\Action\AboutAction::class)->setName('about');
    $app->get('/ingredients/ner', \App\Action\IngredientsNerAction::class)->setName('ingredients-ner-get');
    $app->post('/ingredients/ner', \App\Action\IngredientsNerAction::class)->setName('ingredients-ner-post');
    $app->post('/recipes/by-ingredients', \App\Action\RecipesByIngredientsAction::class)->setName('recipes-by-ingredients-post');
    $app->get('/empty-fridge', \App\Action\EmptyFridgeAction::class)->setName('empty-fridge-get');
    $app->get('/recipes/by-category/{category}', \App\Action\RecipesByCategoryAction::class)->setName('recipes-by-category-param-get');
    $app->get('/recipes/by-region/{region}', \App\Action\RecipesByRegionAction::class)->setName('recipes-by-region-param-get');
    $app->get('/recipes/by-level/{level}', \App\Action\RecipesByLevelAction::class)->setName('recipes-by-level-param-get');
    $app->get('/recipes/by-ingredient/{ingredient}', \App\Action\RecipesByIngredientAction::class)->setName('recipes-by-ingredient-param-get');
    $app->get('/recipes/by-category', \App\Action\RecipesByCategoryAction::class)->setName('recipes-by-category-get');
    $app->get('/recipes/by-region', \App\Action\RecipesByRegionAction::class)->setName('recipes-by-region-get');
    $app->get('/recipes/by-level', \App\Action\RecipesByLevelAction::class)->setName('recipes-by-level-get');
    $app->get('/recipes/by-ingredient', \App\Action\RecipesByIngredientAction::class)->setName('recipes-by-ingredient-get');
    $app->get('/recipes/by-users', \App\Action\RecipesByUsersAction::class)->setName('recipes-by-users-get');
    $app->get('/recipes/by-similarity/{id}', \App\Action\RecipesBySimilarityAction::class)->setName('recipes-by-similarity-get');
    $app->post('/ingredient/ner-feedback', \App\Action\IngredientNerFeedbackAction::class)->setName('ingredient-ner-feedback-post');
};