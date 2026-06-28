<?php
declare(strict_types=1);

$route = $_GET['route'] ?? 'status';
$allowedRoutes = ['status', 'manifest', 'dataset', 'rewards', 'healthz'];

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('Access-Control-Allow-Origin: *');

if (!is_string($route) || !in_array($route, $allowedRoutes, true)) {
    http_response_code(404);
    echo json_encode([
        'ok' => false,
        'error' => 'unknown_origintrail_gateway_route',
        'allowedRoutes' => $allowedRoutes,
    ], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . PHP_EOL;
    exit;
}

$defaultTargetBase = 'http://127.0.0.1:18788';
$targetBase = $defaultTargetBase;
$tunnelConfigPath = __DIR__ . '/origintrail-tunnel.json';

if (is_file($tunnelConfigPath)) {
    $configRaw = file_get_contents($tunnelConfigPath);
    $config = is_string($configRaw) ? json_decode($configRaw, true) : null;
    if (is_array($config) && isset($config['activeTunnelBaseUrl']) && is_string($config['activeTunnelBaseUrl'])) {
        $candidate = rtrim($config['activeTunnelBaseUrl'], '/');
        if (preg_match('/^https:\/\/[a-z0-9.-]+$/i', $candidate)) {
            $targetBase = $candidate;
        }
    }
}

$target = $targetBase . '/' . $route;
$statusCode = 200;

if (function_exists('curl_init')) {
    $client = curl_init($target);
    curl_setopt_array($client, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 3,
        CURLOPT_TIMEOUT => 6,
        CURLOPT_HTTPHEADER => ['Accept: application/json'],
    ]);
    $body = curl_exec($client);
    $curlStatus = curl_getinfo($client, CURLINFO_HTTP_CODE);
    if (is_int($curlStatus) && $curlStatus > 0) {
        $statusCode = $curlStatus;
    }
    curl_close($client);
} else {
    $context = stream_context_create([
        'http' => [
            'method' => 'GET',
            'timeout' => 6,
            'ignore_errors' => true,
            'header' => "Accept: application/json\r\n",
        ],
    ]);
    $body = @file_get_contents($target, false, $context);
}

if ($body === false) {
    http_response_code(503);
    echo json_encode([
        'ok' => false,
        'error' => 'laptop_gateway_offline',
        'detail' => 'Start the laptop gateway and SSH reverse tunnel: node tools/origintrail-laptop-gateway.mjs; ssh -N -R 127.0.0.1:18788:127.0.0.1:8788 5martml@5martm.ssh.transip.me',
    ], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . PHP_EOL;
    exit;
}

http_response_code($statusCode);
echo $body;
