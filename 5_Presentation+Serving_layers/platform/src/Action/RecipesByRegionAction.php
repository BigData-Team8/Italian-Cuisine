<?php

namespace App\Action;

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Slim\Views\Twig;
use GuzzleHttp\Client;
use Slim\Psr7\Response;
use App\Utility\Configuration;

final class RecipesByRegionAction {
    private $twig;
    private $configuration;

    public function __construct(Twig $twig, Configuration $configuration) {
        $this->twig = $twig;
        $this->configuration = $configuration;
    }

    public function __invoke(ServerRequestInterface $request, ResponseInterface $response, $args): ResponseInterface {
        
        if ($request->getMethod() == 'GET') {

            // let's prepare the API request
            $client = new Client();
            $fullResult = [];

            $params = [
                'query' => [
                    'region' => $args['region'] ? $args['region'] : $request->getQueryParams()['region'],
                    'limit' => $request->getQueryParams()['limit']
                ]
            ];

            $baseURL = $this->configuration->getParam('APIbaseURL');
            $API_response = $client->request('GET', $baseURL . '/api/recipes/by-region', $params);

            if ($API_response->getStatusCode() == '200') {
                # print_r(json_decode($API_response->getBody(), true));
                $data = [
                    'decoded' => json_decode($API_response->getBody(), true), 
                    'raw' => $API_response->getBody()
                ];
            }

            return $this->twig->render($response, 'recipes.twig', $data);
        }
    }
}
