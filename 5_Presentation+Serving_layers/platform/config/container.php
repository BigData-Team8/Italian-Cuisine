<?php

use Psr\Container\ContainerInterface;
use Slim\App;
use Slim\Factory\AppFactory;
use Slim\Middleware\ErrorMiddleware;
use Selective\BasePath\BasePathMiddleware;

use Slim\Views\Twig;
use Slim\Views\TwigMiddleware;
use App\Utility\Configuration;

return [
    'settings' => function () {
        return require __DIR__ . '/settings.php';
    },

    App::class => function (ContainerInterface $container) {
        AppFactory::setContainer($container);

        return AppFactory::create();
    },

    BasePathMiddleware::class => function (ContainerInterface $container) {
        return new BasePathMiddleware($container->get(App::class));
    },

    ErrorMiddleware::class => function (ContainerInterface $container) {
        $app = $container->get(App::class);
        $settings = $container->get('settings')['error'];

        return new ErrorMiddleware(
            $app->getCallableResolver(),
            $app->getResponseFactory(),
            (bool)$settings['display_error_details'],
            (bool)$settings['log_errors'],
            (bool)$settings['log_error_details']
        );
    },

    // Twig templates
    Twig::class => function (ContainerInterface $container) {
        $settings = $container->get('settings');
        $twigSettings = $settings['twig'];

        $options = $twigSettings['options'];
        $options['cache'] = $options['cache_enabled'] ? $options['cache_path'] : false;

        $twig = Twig::create($twigSettings['paths'], $options);
        
        return $twig;
    },

    // https://discourse.slimframework.com/t/solved-how-to-get-access-to-settings-in-action-class/3533/
    Configuration::class => function (ContainerInterface $container) {
        $configuration = new Configuration();
        $configuration->setParam('APIbaseURL', $container->get('settings')['APIbaseURL']);
        return $configuration;
        /*
        return new Configuration([
            'APIbaseURL' => $container->get('settings')['APIbaseURL']
        ]);
        */
    },

    TwigMiddleware::class => function (ContainerInterface $container) {
        return TwigMiddleware::createFromContainer(
            $container->get(App::class),
            Twig::class
        );
    },    

];
