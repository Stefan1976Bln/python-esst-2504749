<?php
// MatchQuest Backend — DB (PDO). Standard: SQLite (kein DB-Setup nötig). MySQL optional via config.php.
function mq_cfg() {
  if (file_exists(__DIR__ . '/config.php')) return require __DIR__ . '/config.php';
  // Zero-Config-Standard: SQLite-Datei im geschützten data/-Ordner
  return ['driver' => 'sqlite', 'sqlite' => ['path' => __DIR__ . '/data/matchquest.sqlite'], 'allow_origin' => '*'];
}
function mq_db() {
  static $pdo = null;
  if ($pdo) return $pdo;
  $cfg = mq_cfg();
  if (($cfg['driver'] ?? 'sqlite') === 'sqlite') {
    $path = $cfg['sqlite']['path'];
    $dir = dirname($path);
    if (!is_dir($dir)) @mkdir($dir, 0775, true);
    $pdo = new PDO('sqlite:' . $path);
    $pdo->exec('PRAGMA journal_mode=WAL;'); // bessere Parallelität für eine Klasse
  } else {
    $m = $cfg['mysql'];
    $dsn = 'mysql:host=' . $m['host'] . ';dbname=' . $m['name'] . ';charset=' . ($m['charset'] ?? 'utf8mb4');
    $pdo = new PDO($dsn, $m['user'], $m['pass']);
  }
  $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
  mq_migrate($pdo);
  return $pdo;
}
function mq_migrate($pdo) {
  $pdo->exec("CREATE TABLE IF NOT EXISTS users(
    id VARCHAR(40) PRIMARY KEY, name VARCHAR(80), email VARCHAR(190) UNIQUE,
    pass_hash VARCHAR(255), token VARCHAR(64), points INT DEFAULT 0, xp INT DEFAULT 0,
    coins INT DEFAULT 0, correct_bets INT DEFAULT 0, challenges_done INT DEFAULT 0,
    streak INT DEFAULT 0, team_id VARCHAR(20) DEFAULT NULL, ach TEXT, updated_at VARCHAR(30))");
  $pdo->exec("CREATE TABLE IF NOT EXISTS teams(id VARCHAR(20) PRIMARY KEY, name VARCHAR(60), emoji VARCHAR(8))");
  if ((int)$pdo->query("SELECT COUNT(*) FROM teams")->fetchColumn() === 0) {
    $pdo->exec("INSERT INTO teams(id,name,emoji) VALUES('green','Team Grün','🟢'),('blue','Team Blau','🔵')");
  }
}
