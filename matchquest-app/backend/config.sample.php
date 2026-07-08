<?php
// MatchQuest Backend — Konfiguration.
// Diese Datei nach "config.php" kopieren und ausfüllen (config.php NICHT ins Git committen).
return [
  // 'mysql' für IONOS, 'sqlite' nur für lokale Tests
  'driver' => 'mysql',
  'mysql' => [
    'host'    => 'dbXXXX.hosting-data.io', // aus dem IONOS-Kundenmenü (MySQL-Datenbank)
    'name'    => 'dbsXXXXXXX',
    'user'    => 'dboXXXXXXX',
    'pass'    => 'DEIN_DB_PASSWORT',
    'charset' => 'utf8mb4',
  ],
  'sqlite' => ['path' => __DIR__ . '/matchquest.sqlite'],
  // Für Produktion auf die eigene Domain beschränken, z.B. 'https://www.altenau-harz.de'
  'allow_origin' => '*',
];
