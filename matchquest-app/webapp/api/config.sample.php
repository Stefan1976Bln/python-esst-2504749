<?php
// OPTIONAL. Standard ist SQLite (kein Setup). Für MySQL diese Datei nach "config.php"
// kopieren und ausfüllen. config.php wird NICHT ins Git übernommen.
return [
  'driver' => 'mysql',
  'mysql' => [
    'host'    => 'dbXXXX.hosting-data.io',
    'name'    => 'dbsXXXXXXX',
    'user'    => 'dboXXXXXXX',
    'pass'    => 'DEIN_DB_PASSWORT',
    'charset' => 'utf8mb4',
  ],
  'allow_origin' => 'https://www.altenau-harz.de',
];
