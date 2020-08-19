<?php

namespace App\Action;

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Slim\Views\Twig;
use GuzzleHttp\Client;
use Slim\Psr7\Response;
use App\Utility\Configuration;

final class RecipesByIngredientsAction {
    private $twig;
    private $configuration;

    public function __construct(Twig $twig, Configuration $configuration) {
        $this->twig = $twig;
        $this->configuration = $configuration;
    }

    public function __invoke(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface {

        if ($request->getMethod() == 'GET') {
            echo 'We do not have a page to serve for a GET request';

        } else if ($request->getMethod() == 'POST') {

            $data = $request->getParsedBody();

            // in order to send an array of ingredients through a POST request, we concatenate each ingredient using
            // a comma as separator 
            $ingredients = '';
            foreach ($data as $key => $value) {
                if (strpos($key, 'ingredient') === 0) {
                    $ingredients .= addslashes($value) . ',';
                }
            }
            $ingredients = rtrim($ingredients, ',');

            // let's prepare the API request
            $client = new Client();
            $data = $request->getParsedBody();
            $fullResult = [];

            $params = [
                'query' => [
                    'recipename' => $data['recipename'],
                    'author' => $data['author'],
                    'ingredients' => $ingredients,
                    'threshold' => $data['threshold'],
                    'limit' => $data['limit'],
                    'regionalonly' => $data['regionalonly']
                ]
            ];
            
            $baseURL = $this->configuration->getParam('APIbaseURL');
            $API_response = $client->request('GET', $baseURL .'/api/recipes/by-ingredients', $params);

            if ($API_response->getStatusCode() == '200') {
                // print_r(json_decode($API_response->getBiiody(), true));

                $decoded = json_decode($API_response->getBody(), true);
                arsort($decoded['data']['frequency']['region']);
                arsort($decoded['data']['frequency']['category']);
                arsort($decoded['data']['frequency']['level']);

                $data = [
                    'limit' => $data['limit'],
                    'decoded' => $decoded, 
                    'raw' => $API_response->getBody()
                ];
            }

            return $this->twig->render($response, 'recipes.twig', $data);
        }
    }
}