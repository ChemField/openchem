#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import http from 'node:http';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const host = process.env.ORIGINTRAIL_GATEWAY_HOST || '127.0.0.1';
const port = Number(process.env.ORIGINTRAIL_GATEWAY_PORT || 8788);
const publicProxy = process.env.ORIGINTRAIL_PUBLIC_PROXY || 'https://www.5mart.ml/Slag/origintrail-gateway.php';
const datasetPath = resolve(repoRoot, process.env.CHEMFIELD_DATA_PATH || 'data/chemfield-compositions.json');
const datasetUrl = process.env.CHEMFIELD_DATA_URL || 'https://www.5mart.ml/Slag/chemfield-compositions.json';
const nodeEndpoint = process.env.ORIGINTRAIL_NODE_ENDPOINT || '';
const operationalWalletAddress = process.env.ORIGINTRAIL_OPERATIONAL_WALLET_ADDRESS || '';
const operationalPrivateKeyPresent = Boolean(process.env.ORIGINTRAIL_OPERATIONAL_PRIVATE_KEY);
const rewardStakeTrac = Number(process.env.ORIGINTRAIL_REWARD_STAKE_TRAC || 50000);
const rewardVpsCostsEur = (process.env.ORIGINTRAIL_REWARD_VPS_COSTS_EUR || '40,60,100')
  .split(',')
  .map((value) => Number(value.trim()))
  .filter((value) => Number.isFinite(value) && value > 0);
const startedAt = new Date().toISOString();

function sendJson(res, statusCode, payload) {
  const body = JSON.stringify(payload, null, 2);
  res.writeHead(statusCode, {
    'content-type': 'application/json; charset=utf-8',
    'cache-control': 'no-store',
    'access-control-allow-origin': '*',
  });
  res.end(`${body}\n`);
}

async function readDataset() {
  const raw = await readFile(datasetPath, 'utf8');
  const sha256 = createHash('sha256').update(raw).digest('hex');
  const data = JSON.parse(raw);
  return {
    raw,
    sha256,
    data,
    summary: {
      schemaVersion: data.schemaVersion,
      canonicalField: data.canonicalField,
      updatedAt: data.updatedAt,
      recordCount: Array.isArray(data.records) ? data.records.length : 0,
      variableCount: Array.isArray(data.variables) ? data.variables.length : 0,
      sourceCount: Array.isArray(data.sources) ? data.sources.length : 0,
      originTrailStatus: data.originTrail?.status || 'unknown',
      rootCid: data.cid || null,
      rootUal: data.ual || null,
    },
  };
}

async function statusPayload() {
  const dataset = await readDataset();
  const publisherReady = Boolean(nodeEndpoint && operationalWalletAddress && operationalPrivateKeyPresent);
  return {
    ok: true,
    service: 'openchem-origintrail-laptop-gateway',
    mode: 'headless_laptop_gateway',
    startedAt,
    now: new Date().toISOString(),
    publicProxy,
    datasetUrl,
    dataset: {
      sha256: `sha256:${dataset.sha256}`,
      ...dataset.summary,
    },
    originTrail: {
      publisherReady,
      nodeEndpointConfigured: Boolean(nodeEndpoint),
      operationalWalletAddress: operationalWalletAddress || null,
      operationalPrivateKeyPresent,
      privateKeyPolicy: 'Private key is read only from this laptop environment and is never returned by the API.',
      fullNodeEnabled: false,
      fullNodeReason: 'This gateway is a laptop-backed publisher/client bridge; it is not a full DKG core node.',
    },
  };
}

async function manifestPayload() {
  const status = await statusPayload();
  return {
    kind: 'origintrail_laptop_gateway_manifest',
    schemaVersion: 'origintrail-laptop-gateway-v1',
    status: status.originTrail.publisherReady ? 'publisher_ready' : 'publisher_pending_credentials',
    publicProxy,
    routes: {
      status: `${publicProxy}?route=status`,
      manifest: `${publicProxy}?route=manifest`,
      dataset: `${publicProxy}?route=dataset`,
      rewards: `${publicProxy}?route=rewards`,
      healthz: `${publicProxy}?route=healthz`,
    },
    data: {
      canonicalField: status.dataset.canonicalField,
      datasetUrl,
      sha256: status.dataset.sha256,
      rootCid: status.dataset.rootCid,
      rootUal: status.dataset.rootUal,
    },
    originTrail: status.originTrail,
  };
}

function round(value, decimals = 2) {
  const factor = 10 ** decimals;
  return Math.round(value * factor) / factor;
}

async function tracPricePayload() {
  const envEur = Number(process.env.ORIGINTRAIL_REWARD_PRICE_EUR || '');
  const envUsd = Number(process.env.ORIGINTRAIL_REWARD_PRICE_USD || '');
  if (Number.isFinite(envEur) && envEur > 0 && Number.isFinite(envUsd) && envUsd > 0) {
    return { eur: envEur, usd: envUsd, source: 'local_env', fetchedAt: new Date().toISOString() };
  }

  try {
    const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=origintrail&vs_currencies=usd,eur', {
      signal: AbortSignal.timeout(3500),
      headers: { accept: 'application/json' },
    });
    if (response.ok) {
      const payload = await response.json();
      const eur = Number(payload?.origintrail?.eur);
      const usd = Number(payload?.origintrail?.usd);
      if (Number.isFinite(eur) && eur > 0 && Number.isFinite(usd) && usd > 0) {
        return { eur, usd, source: 'coingecko_simple_price', fetchedAt: new Date().toISOString() };
      }
    }
  } catch {
    // Keep the gateway useful offline; the source field makes the fallback explicit.
  }

  return {
    eur: 0.237521,
    usd: 0.270365,
    source: 'fallback_snapshot_2026-06-29',
    fetchedAt: new Date().toISOString(),
  };
}

async function rewardsPayload() {
  const price = await tracPricePayload();
  const aprScenarios = [
    { label: 'testnet_or_gateway', apr: 0, note: 'Headless gateway/testnet route: no economic node rewards.' },
    { label: 'low_activity', apr: 0.03, note: 'Illustrative low mainnet activity case.' },
    { label: 'base_case', apr: 0.05, note: 'Illustrative conservative break-even case.' },
    { label: 'strong_activity', apr: 0.1, note: 'Illustrative higher activity/delegation case, not guaranteed.' },
  ];

  return {
    ok: true,
    service: 'openchem-origintrail-laptop-gateway',
    kind: 'origintrail_full_node_reward_estimate',
    schemaVersion: 'origintrail-reward-estimate-v1',
    now: new Date().toISOString(),
    caveat: 'OriginTrail Core Node rewards are not fixed APR. Rewards depend on paid DKG activity, node ask, stake/delegation, uptime, proofs, operator fee, and network selection.',
    sourceBasis: [
      'OriginTrail docs describe Core Nodes as hosting public DKG data, serving knowledge assets, participating in random-sampling proofs, and token incentives.',
      'Docs mention a Core Node minimum stake example of 50,000 TRAC and dashboard fields for node ask, operator fee, stake, and reward statistics.',
      'Node price factor / Lambda controls which paid jobs a data holder accepts; this calculator is therefore a scenario model, not a promise.',
    ],
    assumptions: {
      stakeTrac: rewardStakeTrac,
      minimumCoreNodeStakeTrac: 50000,
      price,
      vpsCostsEur: rewardVpsCostsEur,
    },
    scenarios: aprScenarios.map((scenario) => {
      const monthlyTrac = rewardStakeTrac * scenario.apr / 12;
      return {
        ...scenario,
        monthlyTrac: round(monthlyTrac, 4),
        monthlyEur: round(monthlyTrac * price.eur, 2),
        monthlyUsd: round(monthlyTrac * price.usd, 2),
      };
    }),
    breakEven: rewardVpsCostsEur.map((monthlyCostEur) => ({
      monthlyCostEur,
      requiredMonthlyTrac: round(monthlyCostEur / price.eur, 2),
      requiredAprOnStake: round((monthlyCostEur / price.eur) * 12 / rewardStakeTrac, 4),
      requiredAprPercent: round((monthlyCostEur / price.eur) * 12 / rewardStakeTrac * 100, 2),
    })),
    recommendation: 'Use the MacBook route as a publisher/client test. Do not buy VPS capacity for rewards alone until the staking dashboard or indexer shows enough current reward history for the target chain/node class.',
  };
}

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url || '/', `http://${host}:${port}`);
    if (req.method === 'OPTIONS') {
      res.writeHead(204, {
        'access-control-allow-origin': '*',
        'access-control-allow-methods': 'GET,POST,OPTIONS',
        'access-control-allow-headers': 'content-type',
      });
      res.end();
      return;
    }

    if (req.method === 'GET' && (url.pathname === '/' || url.pathname === '/status')) {
      sendJson(res, 200, await statusPayload());
      return;
    }

    if (req.method === 'GET' && url.pathname === '/manifest') {
      sendJson(res, 200, await manifestPayload());
      return;
    }

    if (req.method === 'GET' && url.pathname === '/dataset') {
      const dataset = await readDataset();
      sendJson(res, 200, dataset.data);
      return;
    }

    if (req.method === 'GET' && url.pathname === '/rewards') {
      sendJson(res, 200, await rewardsPayload());
      return;
    }

    if (req.method === 'GET' && url.pathname === '/healthz') {
      sendJson(res, 200, { ok: true, service: 'openchem-origintrail-laptop-gateway' });
      return;
    }

    if (req.method === 'POST' && url.pathname === '/publish') {
      if (!nodeEndpoint || !operationalWalletAddress || !operationalPrivateKeyPresent) {
        sendJson(res, 503, {
          ok: false,
          error: 'origintrail_publish_not_configured',
          requiredLocalEnv: [
            'ORIGINTRAIL_NODE_ENDPOINT',
            'ORIGINTRAIL_OPERATIONAL_WALLET_ADDRESS',
            'ORIGINTRAIL_OPERATIONAL_PRIVATE_KEY',
          ],
        });
        return;
      }

      sendJson(res, 501, {
        ok: false,
        error: 'dkg_publish_client_not_installed',
        nextStep: 'Install and wire dkg.js after testnet credentials are present.',
      });
      return;
    }

    sendJson(res, 404, { ok: false, error: 'not_found' });
  } catch (error) {
    sendJson(res, 500, {
      ok: false,
      error: 'gateway_error',
      message: error instanceof Error ? error.message : String(error),
    });
  }
});

server.listen(port, host, () => {
  console.log(`OpenChem OriginTrail laptop gateway listening on http://${host}:${port}`);
});
