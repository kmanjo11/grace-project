import { Keypair } from '@solana/web3.js';
import fs from 'fs';
import path from 'path';

// Create a Solana-compatible keypair JSON (array of 64 bytes secret key)
function toSolanaKeypairJson(kp: Keypair): string {
  return JSON.stringify(Array.from(kp.secretKey));
}

async function main() {
  const defaultOut = path.resolve(process.cwd(), '../../../deployment/keys/flash_anchor.json');
  const outPath = process.env.OUT || defaultOut;

  // Ensure parent dir
  fs.mkdirSync(path.dirname(outPath), { recursive: true });

  const kp = Keypair.generate();
  const json = toSolanaKeypairJson(kp);
  fs.writeFileSync(outPath, json, { encoding: 'utf-8', flag: 'w' });

  // Restrict permissions (0600) on Unix-like systems
  try {
    fs.chmodSync(outPath, 0o600);
  } catch {}

  // Print
  console.log('\nGenerated service wallet:');
  console.log(`Public Key: ${kp.publicKey.toBase58()}`);
  console.log(`Path: ${outPath}`);
  console.log('\nSet ANCHOR_WALLET to this path, and fund it with some SOL for fees.');
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
