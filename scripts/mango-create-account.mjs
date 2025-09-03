#!/usr/bin/env node
/*
 Minimal Mango v3 account helper
 Modes:
  - check: print existing Mango accounts for owner
  - create: create a Mango account if none exists
  - build-unsigned-tx: build unsigned transaction for account creation (for Phantom)

 Env:
  - SOLANA_RPC_URL (required)
  - GROUP (default: mainnet.1)
  - WALLET_KEYPAIR_PATH (for server-signed operations; default: deployment/keys/id.json)

 Usage:
   MODE=check node scripts/mango-create-account.mjs
   MODE=create node scripts/mango-create-account.mjs
   MODE=build-unsigned-tx OWNER=<base58_owner_pubkey> node scripts/mango-create-account.mjs
*/

import fs from 'fs';
import { Keypair, Connection, PublicKey, Transaction } from '@solana/web3.js';
import BN from 'bn.js';
import * as bs58 from 'bs58';

// Lazy import to avoid hard requirement if not used immediately
let mango;
async function loadMango() {
  if (!mango) {
    mango = await import('@blockworks-foundation/mango-client');
  }
  return mango;
}

function getEnv(name, def) {
  const v = process.env[name];
  if (v === undefined || v === '') return def;
  return v;
}

function loadKeypair(path) {
  const raw = fs.readFileSync(path, 'utf-8');
  const arr = JSON.parse(raw);
  return Keypair.fromSecretKey(Uint8Array.from(arr));
}

async function getClient(connection, groupName) {
  const { MangoClient, Config, IDS } = await loadMango();
  // Resolve group and program via Config/IDS, trying common cluster keys
  const config = new Config(IDS);
  const clustersToTry = ['mainnet', 'mainnet-beta', 'devnet'];
  let groupIds = null;
  let usedCluster = null;
  for (const c of clustersToTry) {
    const g = config.getGroup(c, groupName);
    if (g) {
      groupIds = g;
      usedCluster = c;
      break;
    }
  }
  if (!groupIds) {
    // Build a helpful error with available group names
    const available = [];
    for (const c of clustersToTry) {
      const maybe = (config?.groupsByCluster?.[c] || []).map((x) => x?.name).filter(Boolean);
      if (maybe.length) available.push(`${c}: ${maybe.join(', ')}`);
    }
    throw new Error(`Group not found: groupName=${groupName}. Tried clusters: ${clustersToTry.join(', ')}. Available: ${available.join(' | ')}`);
  }
  const client = new MangoClient(connection, groupIds.mangoProgramId);
  const group = await client.getMangoGroup(groupIds.publicKey);
  return { client, group, groupIds, cluster: usedCluster };
}

async function findAccountsForOwner(client, group, ownerPk) {
  const accounts = await client.getMangoAccountsForOwner(group, ownerPk);
  return accounts;
}

// Direct-instruction path using exported helper. Works even if client.createMangoAccount doesn't dispatch.
async function createAccountWithInstruction(client, group, groupIds, ownerKp) {
  const { makeCreateMangoAccountInstruction } = await loadMango();
  // Prefer the program id the client was constructed with
  let programIdRaw = client.programId || (groupIds && groupIds.mangoProgramId);
  if (!programIdRaw) {
    console.error(`[mango-cli] WARN: programId missing on client/groupIds. groupIds keys=${groupIds?Object.keys(groupIds):'null'}`);
    throw new Error('Mango programId not found (client.programId and groupIds.mangoProgramId are undefined)');
  }
  const programId = (programIdRaw instanceof PublicKey)
    ? programIdRaw
    : new PublicKey(programIdRaw);
  // Build ix using whichever signature this library version supports
  let ix;
  try {
    // Try legacy/simple (programId, groupPk, ownerPk, accountNumber)
    ix = makeCreateMangoAccountInstruction(
      programId,
      group.publicKey,
      ownerKp.publicKey,
      new BN(0)
    );
  } catch (_) {
    // Fallback: compute PDA and try extended signature
    const accountNumber = new BN(0);
    const [mangoAccountPk] = await PublicKey.findProgramAddress(
      [
        group.publicKey.toBytes(),
        ownerKp.publicKey.toBytes(),
        accountNumber.toBuffer('le', 8),
      ],
      programId,
    );
    ix = makeCreateMangoAccountInstruction(
      programId,
      group.publicKey,
      mangoAccountPk,
      ownerKp.publicKey,
      accountNumber,
      ownerKp.publicKey,
    );
  }
  const tx = new Transaction();
  tx.add(ix);
  tx.feePayer = ownerKp.publicKey;
  tx.recentBlockhash = (await client.connection.getLatestBlockhash()).blockhash;
  tx.partialSign(ownerKp);
  let sig;
  try {
    sig = await client.connection.sendRawTransaction(tx.serialize());
  } catch (e) {
    if (e?.getLogs) {
      const logs = await e.getLogs();
      console.error(`[mango-cli] sendRawTransaction failed (ix path). Logs:\n${JSON.stringify(logs, null, 2)}`);
    }
    throw e;
  }
  try {
    console.error(`[mango-cli] Ix path tx sig: ${sig} (awaiting confirmation)`);
    await client.connection.confirmTransaction(sig, 'confirmed');
  } catch (e) {
    console.error(`[mango-cli] confirmTransaction error (ix path): ${e?.message || e}`);
  }
  // Poll for appearance
  for (let i = 0; i < 20; i++) {
    const after = await client.getMangoAccountsForOwner(group, ownerKp.publicKey);
    if (after.length > 0) {
      const newest = after.sort((a, b) => (b.publicKey.toBase58() > a.publicKey.toBase58() ? 1 : -1))[0];
      return newest?.publicKey?.toBase58() || null;
    }
    await new Promise((r) => setTimeout(r, 1000));
  }
  return null;
}

// PDA-based create path mirroring the example: derive PDA with [group, owner, accountNumber]
// and use the 6-arg makeCreateMangoAccountInstruction including payer.
async function createAccountWithPDAInstruction(client, group, groupIds, ownerKp) {
  const { makeCreateMangoAccountInstruction } = await loadMango();
  let programIdRaw = client.programId || (groupIds && groupIds.mangoProgramId);
  if (!programIdRaw) {
    console.error(`[mango-cli] WARN: programId missing on client/groupIds for PDA path.`);
    throw new Error('Mango programId not found for PDA path');
  }
  const programId = (programIdRaw instanceof PublicKey)
    ? programIdRaw
    : new PublicKey(programIdRaw);

  // Account number 0 to mirror example
  const accountNumber = new BN(0);
  const [mangoAccountPk] = await PublicKey.findProgramAddress(
    [
      group.publicKey.toBytes(),
      ownerKp.publicKey.toBytes(),
      accountNumber.toBuffer('le', 8),
    ],
    programId,
  );

  console.error(`[mango-cli] PDA create path: programId=${programId.toBase58()}`);
  console.error(`[mango-cli] PDA create path: group=${group.publicKey.toBase58()}`);
  console.error(`[mango-cli] PDA create path: owner=${ownerKp.publicKey.toBase58()}`);
  console.error(`[mango-cli] PDA create path: derived mangoAccount=${mangoAccountPk.toBase58()} (accountNumber=0)`);

  // Try extended signature first (with PDA + payer). If not available, fall back to simple
  let ix;
  try {
    ix = makeCreateMangoAccountInstruction(
      programId,
      group.publicKey,
      mangoAccountPk,
      ownerKp.publicKey,
      accountNumber,
      ownerKp.publicKey,
    );
  } catch (_) {
    // If library only supports simple signature, build that instead
    ix = makeCreateMangoAccountInstruction(
      programId,
      group.publicKey,
      ownerKp.publicKey,
      new BN(0)
    );
  }

  const tx = new Transaction();
  tx.add(ix);
  tx.feePayer = ownerKp.publicKey;
  tx.recentBlockhash = (await client.connection.getLatestBlockhash()).blockhash;
  tx.partialSign(ownerKp);
  let sig;
  try {
    sig = await client.connection.sendRawTransaction(tx.serialize());
  } catch (e) {
    if (e?.getLogs) {
      const logs = await e.getLogs();
      console.error(`[mango-cli] sendRawTransaction failed (PDA path). Logs:\n${JSON.stringify(logs, null, 2)}`);
    }
    throw e;
  }
  try {
    console.error(`[mango-cli] PDA path tx sig: ${sig} (awaiting confirmation)`);
    await client.connection.confirmTransaction(sig, 'confirmed');
  } catch (e) {
    console.error(`[mango-cli] confirmTransaction error (PDA path): ${e?.message || e}`);
  }

  // Poll for appearance
  for (let i = 0; i < 20; i++) {
    const after = await client.getMangoAccountsForOwner(group, ownerKp.publicKey);
    if (after.length > 0) {
      const newest = after.sort((a, b) => (b.publicKey.toBase58() > a.publicKey.toBase58() ? 1 : -1))[0];
      return newest?.publicKey?.toBase58() || null;
    }
    await new Promise((r) => setTimeout(r, 1000));
  }
  return null;
}

async function createAccountServerSigned(client, group, ownerKp) {
  // Minimal wallet adapter for mango-client flows
  const wallet = {
    publicKey: ownerKp.publicKey,
    signTransaction: async (tx) => {
      tx.partialSign(ownerKp);
      return tx;
    },
    signAllTransactions: async (txs) => {
      txs.forEach((tx) => tx.partialSign(ownerKp));
      return txs;
    },
    sendTransaction: async (tx, connection, _opts) => {
      // Ensure fee payer and blockhash, sign and send
      tx.feePayer = tx.feePayer || ownerKp.publicKey;
      if (!tx.recentBlockhash) {
        tx.recentBlockhash = (await (connection || client.connection).getLatestBlockhash()).blockhash;
      }
      tx.partialSign(ownerKp);
      const sig = await (connection || client.connection).sendRawTransaction(tx.serialize());
      return sig;
    },
    sendAllTransactions: async (txs, connection, _opts) => {
      const sigs = [];
      for (const tx of txs) {
        tx.feePayer = tx.feePayer || ownerKp.publicKey;
        if (!tx.recentBlockhash) {
          tx.recentBlockhash = (await (connection || client.connection).getLatestBlockhash()).blockhash;
        }
        tx.partialSign(ownerKp);
        const sig = await (connection || client.connection).sendRawTransaction(tx.serialize());
        sigs.push(sig);
      }
      return sigs;
    },
  };

  // Try common signatures across versions
  const tryCalls = [
    () => client.createMangoAccount(group, ownerKp.publicKey, 0, wallet),
    () => client.createMangoAccount(group, wallet),
    () => client.createMangoAccount(group, ownerKp.publicKey, wallet),
  ];

  let lastErr;
  for (const fn of tryCalls) {
    try {
      // Count existing before
      const before = await client.getMangoAccountsForOwner(group, ownerKp.publicKey);
      const beforeCount = before.length;
      
      const maybeSig = await fn();
      // If a transaction signature is returned, confirm it
      if (typeof maybeSig === 'string' && maybeSig.length > 0) {
        try {
          console.error(`[mango-cli] Tx sig: ${maybeSig} (awaiting confirmation)`);
          await client.connection.confirmTransaction(maybeSig, 'confirmed');
        } catch (e) {
          console.error(`[mango-cli] confirmTransaction error: ${e?.message || e}`);
        }
      }

      // Poll up to ~20s for the new account to appear
      let newest = null;
      for (let i = 0; i < 20; i++) {
        const after = await client.getMangoAccountsForOwner(group, ownerKp.publicKey);
        if (after.length > beforeCount) {
          newest = after.sort((a, b) => (b.publicKey.toBase58() > a.publicKey.toBase58() ? 1 : -1))[0];
          break;
        }
        await new Promise((r) => setTimeout(r, 1000));
      }
      console.error(`[mango-cli] Accounts before=${beforeCount}, after=${(await client.getMangoAccountsForOwner(group, ownerKp.publicKey)).length}`);
      return newest?.publicKey?.toBase58() || null;
    } catch (e) {
      lastErr = e;
    }
  }
  throw new Error(`Failed to create Mango account via client.createMangoAccount: ${lastErr?.message || lastErr}`);
}

async function buildUnsignedCreateTx(client, group, ownerPk) {
  const { makeCreateMangoAccountInstruction } = await loadMango();
  // Resolve program id from client
  const programIdRaw = client.programId;
  if (!programIdRaw) throw new Error('Mango programId not found on client');
  const programId = (programIdRaw instanceof PublicKey)
    ? programIdRaw
    : new PublicKey(programIdRaw);

  // Derive PDA using [group, owner, accountNumber=0]
  const accountNumber = new BN(0);
  const [mangoAccountPk] = await PublicKey.findProgramAddress(
    [
      group.publicKey.toBytes(),
      ownerPk.toBytes(),
      accountNumber.toBuffer('le', 8),
    ],
    programId,
  );

  // Build instruction with signature fallback
  let ix;
  try {
    ix = makeCreateMangoAccountInstruction(
      programId,
      group.publicKey,
      mangoAccountPk,
      ownerPk,
      accountNumber,
      ownerPk,
    );
  } catch (_) {
    ix = makeCreateMangoAccountInstruction(
      programId,
      group.publicKey,
      ownerPk,
      new BN(0),
    );
  }

  const connection = client.connection;
  const transaction = new Transaction();
  transaction.add(ix);
  transaction.feePayer = ownerPk;
  transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;

  return {
    transaction: transaction.serialize({ requireAllSignatures: false }).toString('base64'),
    mangoAccountPubkey: mangoAccountPk.toBase58(),
  };
}

async function main() {
  const mode = getEnv('MODE', 'check');
  const rpcUrl = getEnv('SOLANA_RPC_URL');
  if (!rpcUrl) {
    console.error('SOLANA_RPC_URL is required');
    process.exit(1);
  }
  const groupName = getEnv('GROUP', 'mainnet.1');
  const connection = new Connection(rpcUrl, 'confirmed');
  const { client, group, groupIds } = await getClient(connection, groupName);

  if (mode === 'build-unsigned-tx') {
    const owner = getEnv('OWNER');
    if (!owner) {
      console.error('OWNER (base58) is required for build-unsigned-tx');
      process.exit(1);
    }
    const ownerPk = new PublicKey(owner);
    const existing = await findAccountsForOwner(client, group, ownerPk);
    if (existing.length > 0) {
      console.log(JSON.stringify({ ok: true, mode, owner: ownerPk.toBase58(), exists: true, accounts: existing.map(a => a.publicKey.toBase58()) }));
      return;
    }
    const built = await buildUnsignedCreateTx(client, group, ownerPk);
    console.log(JSON.stringify({ ok: true, mode, owner: ownerPk.toBase58(), exists: false, ...built }));
    return;
  }

  const walletPath = getEnv('WALLET_KEYPAIR_PATH', 'deployment/keys/id.json');
  // Log resolved signer info to stderr (won't pollute JSON stdout)
  try {
    const tmpKp = loadKeypair(walletPath);
    console.error(`[mango-cli] Using signer file: ${walletPath}`);
    console.error(`[mango-cli] Signer pubkey: ${tmpKp.publicKey.toBase58()}`);
  } catch (e) {
    console.error(`[mango-cli] Failed to read signer at ${walletPath}: ${e?.message || e}`);
  }
  const ownerKp = loadKeypair(walletPath);
  const ownerPk = ownerKp.publicKey;

  const existing = await findAccountsForOwner(client, group, ownerPk);
  if (mode === 'check') {
    console.log(JSON.stringify({ ok: true, mode, owner: ownerPk.toBase58(), accounts: existing.map(a => a.publicKey.toBase58()) }));
    return;
  }
  if (mode === 'create') {
    if (existing.length > 0) {
      console.log(JSON.stringify({ ok: true, mode, owner: ownerPk.toBase58(), created: false, accounts: existing.map(a => a.publicKey.toBase58()) }));
      return;
    }
    let mangoAccount = null;
    try {
      mangoAccount = await createAccountServerSigned(client, group, ownerKp);
    } catch (_) {
      // ignore and try ix path
    }
    if (!mangoAccount) {
      // Try PDA-based instruction path mirroring example
      try {
        mangoAccount = await createAccountWithPDAInstruction(client, group, groupIds, ownerKp);
      } catch (e) {
        console.error(`[mango-cli] PDA path failed: ${e?.message || e}`);
      }
    }
    if (!mangoAccount) {
      // Fallback to simple direct-instruction path
      mangoAccount = await createAccountWithInstruction(client, group, groupIds, ownerKp);
    }
    if (mangoAccount) {
      console.log(JSON.stringify({ ok: true, mode, owner: ownerPk.toBase58(), created: true, mangoAccount }));
    } else {
      const now = await findAccountsForOwner(client, group, ownerPk);
      console.log(JSON.stringify({ ok: true, mode, owner: ownerPk.toBase58(), created: false, accounts: now.map(a => a.publicKey.toBase58()) }));
    }
    return;
  }

  console.error(`Unknown MODE=${mode}`);
  process.exit(1);
}

main().catch((e) => {
  // Log stack to stderr for debugging but keep JSON concise on stdout
  if (e && e.stack) {
    console.error(e.stack);
  }
  console.error(JSON.stringify({ ok: false, error: e?.message || String(e) }));
  process.exit(1);
});
