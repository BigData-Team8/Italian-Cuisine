<?php

namespace App\Action;

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Slim\Views\Twig;
use App\Utility\Configuration;

final class HomeAction {
    private $twig;
    private $configuration;

    public function __construct(Twig $twig, Configuration $configuration) {
        $this->twig = $twig;
        $this->configuration = $configuration;
    }

    public function __invoke(ServerRequestInterface $request, ResponseInterface $response): ResponseInterface {
        return $this->twig->render($response, 'home.twig', []);
    }
}
