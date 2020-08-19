<?php

namespace App\Action;

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Slim\Views\Twig;
use GuzzleHttp\Client;
use Slim\Psr7\Response;
use App\Utility\Configuration;

final class EmptyFridgeAction {
    private $twig;
    private $configuration;

    public function __construct(Twig $twig, Configuration $configuration) {
        $this->twig = $twig;
        $this->configuration = $configuration;
    }

    public function __invoke(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface {

        $client = new Client();
        
        $baseURL = $this->configuration->getParam('APIbaseURL');
        $API_response = $client->request('GET', $baseURL . '/api/regions');

        if ($API_response->getStatusCode() == '200') {
            $regionsFullResult = [
                'decoded' => json_decode($API_response->getBody(), true), 
                'raw' => $API_response->getBody()
            ];
        }

        $baseURL = $this->configuration->getParam('APIbaseURL');
        $API_response = $client->request('GET', $baseURL . '/api/categories');      

        if ($API_response->getStatusCode() == '200') {
            $categoriesFullResult = [
                'decoded' => json_decode($API_response->getBody(), true), 
                'raw' => $API_response->getBody()
            ];
        }

        $baseURL = $this->configuration->getParam('APIbaseURL');
        $API_response = $client->request('GET', $baseURL . '/api/levels');      

        if ($API_response->getStatusCode() == '200') {
            $levelsFullResult = [
                'decoded' => json_decode($API_response->getBody(), true), 
                'raw' => $API_response->getBody()
            ];
        }        

        $data = [
            'data' => [
                'regions' => $regionsFullResult,
                'categories' => $categoriesFullResult,
                'levels' => $levelsFullResult
            ]
        ];

        return $this->twig->render($response, 'empty_fridge.twig', $data);
    }
}
