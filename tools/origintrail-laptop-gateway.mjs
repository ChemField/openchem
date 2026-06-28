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
