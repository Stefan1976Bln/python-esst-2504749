<?php
// MatchQuest Backend — einzelne JSON-API (POST {action, ...}). Geteilte Konten, Punkte, Ranglisten, Teams.
require __DIR__ . '/db.php';
$cfg = require __DIR__ . '/config.php';

header('Access-Control-Allow-Origin: ' . ($cfg['allow_origin'] ?? '*'));
header('Access-Control-Allow-Headers: Content-Type');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Content-Type: application/json; charset=utf-8');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

function out($x) { echo json_encode($x); exit; }
function body() { $j = json_decode(file_get_contents('php://input'), true); return is_array($j) ? $j : []; }
function pub($u) {
  return [
    'id' => $u['id'], 'name' => $u['name'], 'email' => $u['email'],
    'points' => (int)$u['points'], 'xp' => (int)$u['xp'], 'coins' => (int)$u['coins'],
    'correctBets' => (int)$u['correct_bets'], 'challengesDone' => (int)$u['challenges_done'],
    'streak' => (int)$u['streak'], 'teamId' => $u['team_id'],
    'ach' => $u['ach'] ? json_decode($u['ach'], true) : [],
  ];
}
function userByToken($pdo, $t) {
  if (!$t) return null;
  $s = $pdo->prepare("SELECT * FROM users WHERE token=?"); $s->execute([$t]);
  return $s->fetch(PDO::FETCH_ASSOC) ?: null;
}

try {
  $pdo = mq_db();
  $in = body();
  $a = $in['action'] ?? '';

  if ($a === 'register') {
    $name = trim($in['name'] ?? '');
    $email = strtolower(trim($in['email'] ?? ''));
    $pw = $in['password'] ?? '';
    if (!$email || !$pw) out(['ok' => false, 'error' => 'E-Mail und Passwort nötig']);
    $s = $pdo->prepare("SELECT id FROM users WHERE email=?"); $s->execute([$email]);
    if ($s->fetch()) out(['ok' => false, 'error' => 'E-Mail bereits registriert']);
    $id = bin2hex(random_bytes(8)); $tok = bin2hex(random_bytes(16));
    $ins = $pdo->prepare("INSERT INTO users(id,name,email,pass_hash,token,coins,ach,updated_at) VALUES(?,?,?,?,?,?,?,?)");
    $ins->execute([$id, $name ?: explode('@', $email)[0], $email, password_hash($pw, PASSWORD_DEFAULT), $tok, 50, '[]', gmdate('c')]);
    out(['ok' => true, 'token' => $tok, 'user' => pub(userByToken($pdo, $tok))]);
  }

  if ($a === 'login') {
    $email = strtolower(trim($in['email'] ?? '')); $pw = $in['password'] ?? '';
    $s = $pdo->prepare("SELECT * FROM users WHERE email=?"); $s->execute([$email]);
    $u = $s->fetch(PDO::FETCH_ASSOC);
    if (!$u || !password_verify($pw, $u['pass_hash'])) out(['ok' => false, 'error' => 'E-Mail oder Passwort falsch']);
    $tok = bin2hex(random_bytes(16));
    $pdo->prepare("UPDATE users SET token=? WHERE id=?")->execute([$tok, $u['id']]);
    $u['token'] = $tok;
    out(['ok' => true, 'token' => $tok, 'user' => pub($u)]);
  }

  $me = userByToken($pdo, $in['token'] ?? '');

  if ($a === 'me') { if (!$me) out(['ok' => false, 'error' => 'auth']); out(['ok' => true, 'user' => pub($me)]); }

  if ($a === 'submit') {
    if (!$me) out(['ok' => false, 'error' => 'auth']);
    $clamp = function ($v, $max) { $v = (int)$v; return $v < 0 ? 0 : ($v > $max ? $max : $v); };
    $pdo->prepare("UPDATE users SET name=?,points=?,xp=?,coins=?,correct_bets=?,challenges_done=?,streak=?,team_id=?,ach=?,updated_at=? WHERE id=?")
        ->execute([
          substr($in['name'] ?? $me['name'], 0, 80),
          $clamp($in['points'] ?? 0, 1000000), $clamp($in['xp'] ?? 0, 1000000), $clamp($in['coins'] ?? 0, 1000000),
          $clamp($in['correctBets'] ?? 0, 100000), $clamp($in['challengesDone'] ?? 0, 100000), $clamp($in['streak'] ?? 0, 100000),
          $in['teamId'] ?? $me['team_id'], json_encode($in['ach'] ?? []), gmdate('c'), $me['id'],
        ]);
    out(['ok' => true]);
  }

  if ($a === 'joinTeam') {
    if (!$me) out(['ok' => false, 'error' => 'auth']);
    $pdo->prepare("UPDATE users SET team_id=? WHERE id=?")->execute([$in['teamId'] ?? null, $me['id']]);
    out(['ok' => true]);
  }

  if ($a === 'leaderboard') {
    $rows = $pdo->query("SELECT name,points,correct_bets,xp,team_id FROM users ORDER BY correct_bets DESC, points DESC LIMIT 200")->fetchAll(PDO::FETCH_ASSOC);
    out(['ok' => true, 'rows' => array_map(function ($r) {
      return ['name' => $r['name'], 'points' => (int)$r['points'], 'correctBets' => (int)$r['correct_bets'], 'level' => intdiv((int)$r['xp'], 100) + 1, 'teamId' => $r['team_id']];
    }, $rows)]);
  }

  if ($a === 'teams') {
    $teams = $pdo->query("SELECT * FROM teams")->fetchAll(PDO::FETCH_ASSOC);
    $res = [];
    foreach ($teams as $t) {
      $s = $pdo->prepare("SELECT COUNT(*) c, COALESCE(SUM(points),0) p FROM users WHERE team_id=?"); $s->execute([$t['id']]);
      $agg = $s->fetch(PDO::FETCH_ASSOC);
      $res[] = ['id' => $t['id'], 'name' => $t['name'], 'emoji' => $t['emoji'], 'members' => (int)$agg['c'], 'points' => (int)$agg['p']];
    }
    usort($res, function ($a, $b) { return $b['points'] - $a['points']; });
    out(['ok' => true, 'teams' => $res]);
  }

  out(['ok' => false, 'error' => 'unknown action']);
} catch (Exception $e) {
  http_response_code(500);
  out(['ok' => false, 'error' => 'server']);
}
