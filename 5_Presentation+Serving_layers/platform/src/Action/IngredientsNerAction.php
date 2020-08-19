<?php

namespace App\Action;

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Slim\Views\Twig;
use GuzzleHttp\Client;
use Slim\Psr7\Response;
use App\Utility\Configuration;

final class IngredientsNerAction {
    private $twig;
    private $configuration;

    public function __construct(Twig $twig, Configuration $configuration) {
        $test = new Configuration();
        $this->twig = $twig;
        $this->configuration = $configuration;
    }

    public function __invoke(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface {

        if ($request->getMethod() == 'GET') {            
            return $this->twig->render($response, 'ingredients_ner_request.twig');

        } else if ($request->getMethod() == 'POST') {

            // prepares the API request
            $client = new Client();
            $data = $request->getParsedBody();
            $fullResult = [];

            foreach (preg_split('/\r\n|[\r\n]/', $data['ingredients-list']) as $ingredient) {
                if (strlen($ingredient) <= 1) { continue; }

                // sanitizing
                # $ingredient = filter_var($ingredient, FILTER_SANITIZE_STRING, FILTER_FLAG_STRIP_HIGH);
                # on the API level we have a stripslashes function
                $ingredient = addslashes(trim($ingredient));

                $params = [
                    'query' => [
                        'ingredient' => $ingredient,
                        'threshold' => $data['threshold'],
                        'limit' => $data['limit'],
                        'algorithm' => $data['algorithm']
                    ]
                ];
            
                $baseURL = $this->configuration->getParam('APIbaseURL');
                $API_response = $client->request('GET', $baseURL .'/api/ingredient/ner', $params);

                if ($API_response->getStatusCode() == '200') {
                    # print_r(json_decode($API_response->getBody(), true));
                    $fullResult[] = [
                        'decoded' => json_decode($API_response->getBody(), true), 
                        'raw' => $API_response->getBody()
                    ];
                }
            }

            $data = [ 
                'data' => $fullResult,
            ];

            return $this->twig->render($response, 'ingredients_ner_response.twig', $data);
        }
    }
}
