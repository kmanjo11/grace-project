#!/usr/bin/env node
// Sends a base64-encoded unsigned Solana transaction after refreshing blockhash and signing.
// Env:
//   - TX_BASE64 (required)
//   - WALLET_KEYPAIR_PATH (default: deployment/keys/id.json)
//   - SOLANA_RPC_URL (required)

import fs from 'fs';
import { Connection, Keypair, Transaction } from '@solana/web3.js';

async function main() {
  const txB64 = process.env.TX_BASE64;
  const keypairPath = process.env.WALLET_KEYPAIR_PATH || 'deployment/keys/id.json';
  const rpc = process.env.SOLANA_RPC_URL;
  if (!txB64) throw new Error('TX_BASE64 is required');
  if (!rpc) throw new Error('SOLANA_RPC_URL is required');

  const conn = new Connection(rpc, 'confirmed');
  const tx = Transaction.from(Buffer.from(txB64, 'base64'));
  const secret = JSON.parse(fs.readFileSync(keypairPath, 'utf-8'));
  const kp = Keypair.fromSecretKey(Uint8Array.from(secret));

  // Ensure up-to-date blockhash and correct fee payer before signing
  tx.feePayer = kp.publicKey;
  tx.recentBlockhash = (await conn.getLatestBlockhash()).blockhash;
  tx.sign(kp);

  try {
    const sig = await conn.sendRawTransaction(tx.serialize());
    console.error(`[send-unsigned-tx] sent: ${sig}`);
    await conn.confirmTransaction(sig, 'confirmed');
    console.log(JSON.stringify({ ok: true, sig }));
  } catch (e) {
    // If SendTransactionError, print logs if available
    if (e?.getLogs) {
      try {
        const logs = await e.getLogs();
        console.error(`[send-unsigned-tx] on-chain logs:\n${JSON.stringify(logs, null, 2)}`);
      } catch {}
    }
    console.error(e);
    process.exit(1);
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
