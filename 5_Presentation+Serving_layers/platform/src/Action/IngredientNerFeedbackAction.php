<?php

namespace App\Action;

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Slim\Views\Twig;
use GuzzleHttp\Client;
use Slim\Psr7\Response;
use App\Utility\Configuration;

final class IngredientNerFeedbackAction {
    private $twig;
    private $configuration;

    public function __construct(Twig $twig, Configuration $configuration) {
        $test = new Configuration();
        $this->twig = $twig;
        $this->configuration = $configuration;
    }

    public function __invoke(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface {

        if ($request->getMethod() == 'GET') {
            echo 'We do not have a page to serve for a GET request';

        } else if ($request->getMethod() == 'POST') {

            // prepares the API request
            $client = new Client();
            $data = $request->getParsedBody();
            $fullResult = [];

            $ingredient = addslashes(trim($data['ingredient']));
            $amount = addslashes(trim($data['amount']));

            $params = [
                'query' => [
                    'raw' => $data['raw'],
                    'ingredient' => $ingredient,
                    'amount' => $amount
                ]
            ];
    
            $baseURL = $this->configuration->getParam('APIbaseURL');
            $API_response = $client->request('POST', $baseURL .'/api/ingredient/ner-feedback', $params);

            # print_r(json_decode($API_response->getBody(), true));
            $fullResult[] = [
                'decoded' => json_decode($API_response->getBody(), true), 
            ];

            $response->getBody()->write(json_encode($fullResult));
            return $response->withHeader('Content-Type', 'application/json');

        }
    }
}
