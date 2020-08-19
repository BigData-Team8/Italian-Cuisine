<?php

namespace App\Utility;

final class Configuration {
    private $params;

    public function __construct() {

    }
    
    public function setParam($key, $value) {
    	$this->params[$key] = $value;
    }

    public function getParams() {
    	return $this->params;
    }

    public function getParam($key) {
    	return $this->params[$key];
    }

}