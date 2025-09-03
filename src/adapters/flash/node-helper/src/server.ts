import express, { Request, Response } from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import dotenv from 'dotenv';
import fs from 'fs';
import { AnchorProvider } from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, sendAndConfirmTransaction } from '@solana/web3.js';
import { PythHttpClient, getPythProgramKeyForCluster, PriceData } from '@pythnetwork/client';
import * as Flash from 'flash-sdk';

dotenv.config();

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(express.json());

const PORT = Number(process.env.FLASH_HELPER_PORT || 9020);

// Env and defaults
const FLASH_NETWORK = process.env.FLASH_NETWORK || 'mainnet-beta';
const FLASH_RPC_URL = process.env.FLASH_RPC_URL || process.env.SOLANA_RPC_URL || '';
const FLASH_POOL = process.env.FLASH_POOL || 'Crypto.1';
const ANCHOR_WALLET = process.env.ANCHOR_WALLET || '';

// NOTE: We will wire flash-sdk shortly; this is a scaffold so adapter routes work.
// This server returns simple placeholders until SDK wiring is completed.

function getRpcUrl(): string {
  return process.env.FLASH_RPC_URL || process.env.SOLANA_RPC_URL || '';
}

function loadKeypairFromFile(filePath: string): Keypair {
  const content = fs.readFileSync(filePath, 'utf-8');
  const arr = JSON.parse(content) as number[];
  const secret = Uint8Array.from(arr);
  return Keypair.fromSecretKey(secret);
}

function getProvider(): AnchorProvider {
  const rpc = getRpcUrl();
  const connection = new Connection(rpc, {
    commitment: 'confirmed',
  });
  if (!ANCHOR_WALLET) {
    throw new Error('ANCHOR_WALLET not set');
  }
  const kp = loadKeypairFromFile(ANCHOR_WALLET);
  // Minimal wallet implementation
  const wallet = {
    publicKey: kp.publicKey,
    signTransaction: async (tx: any) => {
      tx.partialSign(kp);
      return tx;
    },
    signAllTransactions: async (txs: any[]) => {
      return txs.map((tx) => {
        tx.partialSign(kp);
        return tx;
      });
    },
  } as any;
  return new AnchorProvider(connection, wallet, {
    commitment: 'confirmed',
    preflightCommitment: 'confirmed',
    skipPreflight: true,
  } as any);
}

function getClients() {
  const provider = getProvider();
  // Resolve PoolConfig and construct PerpetualsClient with explicit program IDs per docs
  const poolConfig = (Flash as any)?.PoolConfig?.fromIdsByName?.(FLASH_POOL, FLASH_NETWORK as any);
  if (!poolConfig) {
    throw new Error('flash-sdk PoolConfig.fromIdsByName unavailable for current version');
  }
  const pc: any = poolConfig as any;
  const prioritizationFee = Number(process.env.FLASH_PRIORITY_FEE || 0);
  const PerpCtor = (Flash as any)?.PerpetualsClient;
  if (!PerpCtor) {
    throw new Error('flash-sdk PerpetualsClient unavailable for current version');
  }
  const perpClient = new PerpCtor(
    provider,
    pc.programId,
    pc.perpComposibilityProgramId,
    pc.fbNftRewardProgramId,
    pc.rewardDistributionProgram?.programId,
    {
      prioritizationFee,
    }
  );
  return { provider, perpClient, poolConfig };
}

// Load the service keypair used for server-side signing
function getServiceKeypair(): Keypair {
  if (!ANCHOR_WALLET) throw new Error('ANCHOR_WALLET not set');
  return loadKeypairFromFile(ANCHOR_WALLET);
}

async function signAndSendTransaction(tx: any, provider: AnchorProvider) {
  const kp = getServiceKeypair();
  // Ensure minimal fields
  if (!tx.feePayer) tx.feePayer = kp.publicKey;
  const latest = await provider.connection.getLatestBlockhash('confirmed');
  if (!tx.recentBlockhash) tx.recentBlockhash = latest.blockhash;
  // Sign and send
  const sig = await provider.connection.sendTransaction(tx, [kp], {
    skipPreflight: false,
    preflightCommitment: 'confirmed',
  } as any);
  await provider.connection.confirmTransaction({ signature: sig, ...latest }, 'confirmed');
  return { signature: sig };
}

app.get('/health', (_req: Request, res: Response) => {
  res.json({ ok: true, network: FLASH_NETWORK, pool: FLASH_POOL, rpc: !!FLASH_RPC_URL, wallet: !!ANCHOR_WALLET });
});

app.get('/pools', (_req: Request, res: Response) => {
  // Known pool names from docs (subject to change)
  const mainnet = ['Crypto.1', 'Virtual.1', 'Governance.1', 'Community.1', 'Community.2'];
  const devnet = ['devnet.1', 'devnet.2', 'devnet.3', 'devnet.4', 'devnet.5'];
  res.json({ success: true, network: FLASH_NETWORK, pools: FLASH_NETWORK === 'mainnet-beta' ? mainnet : devnet });
});

app.get('/markets', (req: Request, res: Response) => {
  const pool = (req.query.pool as string) || FLASH_POOL;
  if (!FLASH_RPC_URL && !process.env.SOLANA_RPC_URL) {
    return res.status(500).json({ success: false, message: 'RPC URL missing. Set FLASH_RPC_URL or SOLANA_RPC_URL' });
  }
  if (!ANCHOR_WALLET) {
    return res.status(500).json({ success: false, message: 'ANCHOR_WALLET not set' });
  }
  try {
    const { poolConfig } = getClients();
    const pc: any = poolConfig as any;
    // Build a serializable view of pool/markets
    const tokens = ((pc.tokens || []) as any[]).map((t: any) => ({
      symbol: t.symbol,
      decimals: t.decimals,
      mint: t.mintKey instanceof PublicKey ? t.mintKey.toBase58() : String(t.mintKey),
      oracle: t.oracleKey ? (t.oracleKey instanceof PublicKey ? t.oracleKey.toBase58() : String(t.oracleKey)) : null,
    }));
    const markets = ((pc.perpetuals || pc.markets || []) as any[]).map((m: any) => ({
      symbol: m.symbol || m.asset || m.name,
      baseSymbol: m.baseSymbol || undefined,
      quoteSymbol: m.quoteSymbol || 'USDC',
      marketIndex: m.marketIndex ?? m.index ?? undefined,
    }));
    const resp = {
      success: true,
      network: FLASH_NETWORK,
      pool,
      poolAddress: pc.poolAddress instanceof PublicKey ? pc.poolAddress.toBase58() : String(pc.poolAddress),
      tokens,
      markets,
    };
    return res.json(resp);
  } catch (e: any) {
    return res.status(500).json({ success: false, message: e?.message || String(e) });
  }
});

// Fetch Pyth prices for all tokens in the configured pool
app.get('/prices', async (_req: Request, res: Response) => {
  try {
    const { poolConfig } = getClients();
    const pc: any = poolConfig as any;
    const tokens = (pc.tokens || []) as any[];

    if (!tokens.length) {
      return res.status(500).json({ success: false, message: 'No tokens in pool config' });
    }

    const pythUrl = process.env.PYTHNET_RPC_URL || process.env.PYTH_TRITON_URL;
    if (!pythUrl) {
      return res.status(500).json({ success: false, message: 'Missing PYTHNET_RPC_URL (or PYTH_TRITON_URL)' });
    }

    const pythConn = new Connection(pythUrl);
    const pythProgramKey = getPythProgramKeyForCluster('pythnet');
    const pythClient = new PythHttpClient(pythConn, pythProgramKey);

    const data = await pythClient.getData();

    const out: Record<string, any> = {};
    for (const token of tokens) {
      const ticker = token.pythTicker || token.symbol;
      const pd: PriceData | undefined = data.productPrice.get(ticker) as any;
      if (!pd) {
        out[token.symbol] = { success: false, error: `priceData not found for ${token.symbol}`, ticker };
        continue;
      }
      out[token.symbol] = {
        success: true,
        symbol: token.symbol,
        ticker,
        price: pd.aggregate?.priceComponent?.toString?.() ?? null,
        exponent: pd.exponent,
        confidence: pd.confidence?.toString?.() ?? null,
        emaPrice: pd.emaPrice?.valueComponent?.toString?.() ?? null,
        emaConfidence: pd.emaConfidence?.valueComponent?.toString?.() ?? null,
        timestamp: pd.timestamp?.toString?.() ?? null,
      };
    }

    return res.json({ success: true, network: FLASH_NETWORK, pool: FLASH_POOL, prices: out });
  } catch (e: any) {
    return res.status(500).json({ success: false, message: e?.message || 'Failed to fetch prices' });
  }
});

// Set Take-Profit and/or Stop-Loss on an existing position. Optional partial size.
// Expects body { market, ownerPubkey, takeProfit?, stopLoss?, size? }
// Returns unsigned tx (base64) if SDK supports building a TP/SL instruction.
app.post('/tpsl', async (req: Request, res: Response) => {
  const { market, ownerPubkey, takeProfit, stopLoss, size } = req.body || {};
  if (!market || !ownerPubkey) {
    return res.status(400).json({ success: false, message: 'market and ownerPubkey are required' });
  }
  if (!FLASH_RPC_URL && !process.env.SOLANA_RPC_URL) {
    return res.status(500).json({ success: false, message: 'RPC URL missing. Set FLASH_RPC_URL or SOLANA_RPC_URL' });
  }
  if (!ANCHOR_WALLET) {
    return res.status(500).json({ success: false, message: 'ANCHOR_WALLET not set' });
  }
  try {
    const { perpClient, poolConfig } = getClients();
    const owner = new PublicKey(ownerPubkey);

    const pc: any = poolConfig as any;
    const markets = ((pc.perpetuals || pc.markets || []) as any[]);
    const m = markets.find((x: any) => (x.symbol || x.asset || x.name) === market);
    if (!m) {
      return res.status(400).json({ success: false, message: `Unknown market: ${market}` });
    }

    const args: any = { market, owner };
    if (typeof takeProfit !== 'undefined') args.takeProfit = takeProfit;
    if (typeof stopLoss !== 'undefined') args.stopLoss = stopLoss;
    if (typeof size !== 'undefined') args.size = size;

    const candidates = [
      'buildTpSlTx',
      'setTpSlTx',
      'buildSetTpSlTx',
      'prepareTpSlTx',
    ];
    let tx: any = null;
    for (const c of candidates) {
      if (c in (perpClient as any) && typeof (perpClient as any)[c] === 'function') {
        try {
          tx = (perpClient as any)[c](args, pc);
          if (tx && typeof tx.then === 'function') tx = await tx;
          break;
        } catch (inner) {}
      }
    }

    if (!tx) {
      return res.status(501).json({ success: false, message: 'tpsl build method not available in flash-sdk' });
    }

    const serialized = tx.serialize({ requireAllSignatures: false, verifySignatures: false });
    const b64 = Buffer.from(serialized).toString('base64');
    return res.json({ success: true, market, owner: owner.toBase58(), transaction: b64 });
} catch (e: any) {
  return res.status(500).json({ success: false, message: e?.message || String(e) });
}
});

// Execute: build, sign with ANCHOR_WALLET, send and confirm
app.post('/order/execute', async (req: Request, res: Response) => {
  const { market, side, size, leverage, reduceOnly, payoutTokenSymbol, collateralTokenSymbol, ownerPubkey } = req.body || {};
  if (!market || !side || !size || !ownerPubkey) {
    return res.status(400).json({ success: false, message: 'market, side, size, ownerPubkey are required' });
  }
  if (!FLASH_RPC_URL && !process.env.SOLANA_RPC_URL) {
    return res.status(500).json({ success: false, message: 'RPC URL missing. Set FLASH_RPC_URL or SOLANA_RPC_URL' });
  }
  if (!ANCHOR_WALLET) {
    return res.status(500).json({ success: false, message: 'ANCHOR_WALLET not set' });
  }
  try {
    const { perpClient, poolConfig, provider } = getClients();
    const owner = new PublicKey(ownerPubkey);

    const pc: any = poolConfig as any;
    const markets = ((pc.perpetuals || pc.markets || []) as any[]);
    const m = markets.find((x: any) => (x.symbol || x.asset || x.name) === market);
    if (!m) {
      return res.status(400).json({ success: false, message: `Unknown market: ${market}` });
    }

    // Build the order transaction first (unsigned)
    const args: any = { market, side, size, leverage, owner };
    if (typeof reduceOnly !== 'undefined') args.reduceOnly = !!reduceOnly;
    if (payoutTokenSymbol) args.payoutTokenSymbol = String(payoutTokenSymbol);
    if (collateralTokenSymbol) args.collateralTokenSymbol = String(collateralTokenSymbol);
    const buildCandidates = [
      'buildOrderTx',
      'buildOpenPositionTx',
      'createOrderTransaction',
      'prepareOrderTx',
    ];
    let tx: any = null;
    for (const c of buildCandidates) {
      if (c in (perpClient as any) && typeof (perpClient as any)[c] === 'function') {
        try {
          tx = (perpClient as any)[c](args, pc);
          if (tx && typeof tx.then === 'function') tx = await tx;
          break;
        } catch (inner) {}
      }
    }

    if (!tx) {
      return res.status(501).json({ success: false, message: 'order build method not available in flash-sdk' });
    }

    // Sign and send with the server's ANCHOR_WALLET
    const { signature } = await signAndSendTransaction(tx, provider);
    return res.json({ success: true, market, owner: owner.toBase58(), signature });
  } catch (e: any) {
    return res.status(500).json({ success: false, message: e?.message || String(e) });
  }
});

// Compute or retrieve the liquidation price for a user on a given market.
// Expects body { market, ownerPubkey }
// Returns { success, market, owner, liquidationPrice }
app.post('/liquidation-price', async (req: Request, res: Response) => {
  const { market, ownerPubkey } = req.body || {};
  if (!market || !ownerPubkey) {
    return res.status(400).json({ success: false, message: 'market and ownerPubkey are required' });
  }
  if (!FLASH_RPC_URL && !process.env.SOLANA_RPC_URL) {
    return res.status(500).json({ success: false, message: 'RPC URL missing. Set FLASH_RPC_URL or SOLANA_RPC_URL' });
  }
  if (!ANCHOR_WALLET) {
    return res.status(500).json({ success: false, message: 'ANCHOR_WALLET not set' });
  }
  try {
    const { perpClient, poolConfig } = getClients();
    const owner = new PublicKey(ownerPubkey);

    const pc: any = poolConfig as any;
    const markets = ((pc.perpetuals || pc.markets || []) as any[]);
    const m = markets.find((x: any) => (x.symbol || x.asset || x.name) === market);
    if (!m) {
      return res.status(400).json({ success: false, message: `Unknown market: ${market}` });
    }

    const args: any = { market, owner };
    const candidates = ['getLiquidationPrice', 'liquidationPrice', 'computeLiquidationPrice'];
    let price: any = null;
    for (const c of candidates) {
      if (c in (perpClient as any) && typeof (perpClient as any)[c] === 'function') {
        try {
          price = (perpClient as any)[c](args, pc);
          if (price && typeof price.then === 'function') price = await price;
          break;
        } catch (inner) {}
      }
    }

    if (price === null || typeof price === 'undefined') {
      return res.status(501).json({ success: false, message: 'liquidation price method not available in flash-sdk' });
    }

    // Ensure numeric
    const liquidationPrice = typeof price === 'object' && 'toNumber' in (price as any)
      ? (price as any).toNumber()
      : Number(price);
    return res.json({ success: true, market, owner: owner.toBase58(), liquidationPrice });
  } catch (e: any) {
    return res.status(500).json({ success: false, message: e?.message || String(e) });
  }
});

// --- Liquidity Endpoints ---
// Adds liquidity to the selected pool/market depending on SDK design.
// Expects body: { tokenSymbol, amount, ownerPubkey, slippageBps? }
app.post('/liquidity/add', async (req: Request, res: Response) => {
  const { tokenSymbol, amount, ownerPubkey, slippageBps } = req.body || {};
  if (!tokenSymbol || !amount || !ownerPubkey) {
    return res.status(400).json({ success: false, message: 'tokenSymbol, amount, ownerPubkey are required' });
  }
  if (!FLASH_RPC_URL && !process.env.SOLANA_RPC_URL) {
    return res.status(500).json({ success: false, message: 'RPC URL missing. Set FLASH_RPC_URL or SOLANA_RPC_URL' });
  }
  if (!ANCHOR_WALLET) {
    return res.status(500).json({ success: false, message: 'ANCHOR_WALLET not set' });
  }
  try {
    const { perpClient, poolConfig } = getClients();
    const owner = new PublicKey(ownerPubkey);

    const pc: any = poolConfig as any;
    // Find token config from pool by symbol
    const token = ((pc.tokens || []) as any[]).find((t: any) => t.symbol === tokenSymbol);
    if (!token) {
      return res.status(400).json({ success: false, message: `Unknown tokenSymbol: ${tokenSymbol}` });
    }

    const args = { tokenSymbol, amount, owner, slippageBps };
    const candidates = [
      'buildAddLiquidityTx',
      'addLiquidityTx',
      'buildProvideLiquidityTx',
      'provideLiquidityTx',
      'addLiquidity',
      'provideLiquidity',
    ];
    let tx: any = null;
    for (const m of candidates) {
      if (m in (perpClient as any) && typeof (perpClient as any)[m] === 'function') {
        try {
          tx = (perpClient as any)[m](args, pc);
          if (tx && typeof tx.then === 'function') tx = await tx;
          break;
        } catch (inner) {}
      }
    }

    if (!tx) {
      return res.status(501).json({ success: false, message: 'add liquidity build method not available in flash-sdk' });
    }

    const serialized = tx.serialize({ requireAllSignatures: false, verifySignatures: false });
    const b64 = Buffer.from(serialized).toString('base64');
    return res.json({ success: true, owner: owner.toBase58(), tokenSymbol, transaction: b64 });
  } catch (e: any) {
    return res.status(500).json({ success: false, message: e?.message || String(e) });
  }
});

// Removes liquidity from the pool.
// Expects body: { shares, ownerPubkey, slippageBps? } or { tokenSymbol, amount, ownerPubkey }
app.post('/liquidity/remove', async (req: Request, res: Response) => {
  const { shares, tokenSymbol, amount, ownerPubkey, slippageBps } = req.body || {};
  if ((!shares && !amount) || !ownerPubkey) {
    return res.status(400).json({ success: false, message: 'shares or amount, and ownerPubkey are required' });
  }
  if (!FLASH_RPC_URL && !process.env.SOLANA_RPC_URL) {
    return res.status(500).json({ success: false, message: 'RPC URL missing. Set FLASH_RPC_URL or SOLANA_RPC_URL' });
  }
  if (!ANCHOR_WALLET) {
    return res.status(500).json({ success: false, message: 'ANCHOR_WALLET not set' });
  }
  try {
    const { perpClient, poolConfig } = getClients();
    const owner = new PublicKey(ownerPubkey);

    const pc: any = poolConfig as any;
    let token: any = null;
    if (tokenSymbol) {
      token = ((pc.tokens || []) as any[]).find((t: any) => t.symbol === tokenSymbol);
      if (!token) {
        return res.status(400).json({ success: false, message: `Unknown tokenSymbol: ${tokenSymbol}` });
      }
    }

    const args = { shares, tokenSymbol, amount, owner, slippageBps };
    const candidates = [
      'buildRemoveLiquidityTx',
      'removeLiquidityTx',
      'buildWithdrawLiquidityTx',
      'withdrawLiquidityTx',
      'removeLiquidity',
      'withdrawLiquidity',
    ];
    let tx: any = null;
    for (const m of candidates) {
      if (m in (perpClient as any) && typeof (perpClient as any)[m] === 'function') {
        try {
          tx = (perpClient as any)[m](args, pc);
          if (tx && typeof tx.then === 'function') tx = await tx;
          break;
        } catch (inner) {}
      }
    }

    if (!tx) {
      return res.status(501).json({ success: false, message: 'remove liquidity build method not available in flash-sdk' });
    }

    const serialized = tx.serialize({ requireAllSignatures: false, verifySignatures: false });
    const b64 = Buffer.from(serialized).toString('base64');
    return res.json({ success: true, owner: owner.toBase58(), tokenSymbol, shares, amount, transaction: b64 });
  } catch (e: any) {
    return res.status(500).json({ success: false, message: e?.message || String(e) });
  }
});

app.get('/positions', async (req: Request, res: Response) => {
  const ownerPubkey = (req.query.owner as string) || '';
  if (!ownerPubkey) return res.status(400).json({ success: false, message: 'ownerPubkey is required as ?owner=' });
  if (!FLASH_RPC_URL && !process.env.SOLANA_RPC_URL) {
    return res.status(500).json({ success: false, message: 'RPC URL missing. Set FLASH_RPC_URL or SOLANA_RPC_URL' });
  }
  if (!ANCHOR_WALLET) {
    return res.status(500).json({ success: false, message: 'ANCHOR_WALLET not set' });
  }
  try {
    const { perpClient, poolConfig } = getClients();
    const owner = new PublicKey(ownerPubkey);
    // Try a few common method names to fetch positions safely without assuming SDK API
    let positions: any = null;
    const candidateMethods = [
      'getUserPositions',
      'getPositions',
      'positions',
      'fetchUserPositions',
    ];
    for (const m of candidateMethods) {
      if (m in (perpClient as any) && typeof (perpClient as any)[m] === 'function') {
        try {
          positions = (perpClient as any)[m](owner, poolConfig as any);
          // Await if returns a promise
          if (positions && typeof positions.then === 'function') {
            positions = await positions;
          }
          break;
        } catch (inner) {
          // try next method
        }
      }
    }

    if (!positions) {
      return res.status(501).json({ success: false, message: 'positions method not available in flash-sdk', ownerPubkey });
    }

    // Ensure serializable response
    const isBNLike = (v: any) => {
      return (
        v &&
        typeof v === 'object' &&
        typeof (v as any).toString === 'function' &&
        ((v as any).constructor?.name === 'BN' || /^(\d+)$/.test((v as any).toString()))
      );
    };
    const serialize = (p: any) => {
      const out: any = {};
      for (const k in (p || {})) {
        const v: any = (p as any)[k];
        if (v instanceof PublicKey) out[k] = v.toBase58();
        else if (isBNLike(v)) out[k] = v.toString();
        else out[k] = v;
      }
      return out;
    };
    const data = Array.isArray(positions) ? positions.map(serialize) : serialize(positions);
    return res.json({ success: true, owner: owner.toBase58(), positions: data });
  } catch (e: any) {
    return res.status(500).json({ success: false, message: e?.message || String(e) });
  }
});

app.post('/quote', async (req: Request, res: Response) => {
  // Expects body { market, side, size, leverage?, ownerPubkey }
  const { market, side, size, leverage, ownerPubkey } = req.body || {};
  if (!market || !side || !size || !ownerPubkey) {
    return res.status(400).json({ success: false, message: 'market, side, size, ownerPubkey are required' });
  }
  if (!FLASH_RPC_URL && !process.env.SOLANA_RPC_URL) {
    return res.status(500).json({ success: false, message: 'RPC URL missing. Set FLASH_RPC_URL or SOLANA_RPC_URL' });
  }
  if (!ANCHOR_WALLET) {
    return res.status(500).json({ success: false, message: 'ANCHOR_WALLET not set' });
  }
  try {
    const { perpClient, poolConfig } = getClients();
    const owner = new PublicKey(ownerPubkey);

    // Resolve market from poolConfig (by symbol)
    const pc: any = poolConfig as any;
    const markets = ((pc.perpetuals || pc.markets || []) as any[]);
    const m = markets.find((x: any) => (x.symbol || x.asset || x.name) === market);
    if (!m) {
      return res.status(400).json({ success: false, message: `Unknown market: ${market}` });
    }

    // Try candidate quote methods safely
    const args = { market, side, size, leverage, owner };
    const candidates = ['getQuote', 'quote', 'simulateQuote', 'simulate'];
    let quote: any = null;
    for (const c of candidates) {
      if (c in (perpClient as any) && typeof (perpClient as any)[c] === 'function') {
        try {
          quote = (perpClient as any)[c](args, pc);
          if (quote && typeof quote.then === 'function') quote = await quote;
          break;
        } catch (inner) {}
      }
    }
    if (!quote) {
      return res.status(501).json({ success: false, message: 'quote method not available in flash-sdk' });
    }

    const isBNLike2 = (v: any) => {
      return (
        v &&
        typeof v === 'object' &&
        typeof (v as any).toString === 'function' &&
        ((v as any).constructor?.name === 'BN' || /^(\d+)$/.test((v as any).toString()))
      );
    };
    const toPlain = (obj: any) => {
      const out: any = {};
      for (const k in (obj || {})) {
        const v: any = (obj as any)[k];
        if (v instanceof PublicKey) out[k] = v.toBase58();
        else if (isBNLike2(v)) out[k] = v.toString();
        else out[k] = v;
      }
      return out;
    };

    return res.json({ success: true, market, owner: owner.toBase58(), quote: toPlain(quote) });
  } catch (e: any) {
    return res.status(500).json({ success: false, message: e?.message || String(e) });
  }
});

app.post('/order', async (req: Request, res: Response) => {
  // Expects body { market, side, size, leverage?, reduceOnly?, payoutTokenSymbol?, collateralTokenSymbol?, ownerPubkey }
  // Should return unsigned tx (base64) and instructions for client to sign.
  const { market, side, size, leverage, reduceOnly, payoutTokenSymbol, collateralTokenSymbol, ownerPubkey } = req.body || {};
  if (!market || !side || !size || !ownerPubkey) {
    return res.status(400).json({ success: false, message: 'market, side, size, ownerPubkey are required' });
  }
  if (!FLASH_RPC_URL && !process.env.SOLANA_RPC_URL) {
    return res.status(500).json({ success: false, message: 'RPC URL missing. Set FLASH_RPC_URL or SOLANA_RPC_URL' });
  }
  if (!ANCHOR_WALLET) {
    return res.status(500).json({ success: false, message: 'ANCHOR_WALLET not set' });
  }
  try {
    const { perpClient, poolConfig, provider } = getClients();
    const owner = new PublicKey(ownerPubkey);

    const pc: any = poolConfig as any;
    const markets = ((pc.perpetuals || pc.markets || []) as any[]);
    const m = markets.find((x: any) => (x.symbol || x.asset || x.name) === market);
    if (!m) {
      return res.status(400).json({ success: false, message: `Unknown market: ${market}` });
    }

    // Try candidate builders for unsigned tx
    const args: any = { market, side, size, leverage, owner };
    if (typeof reduceOnly !== 'undefined') args.reduceOnly = !!reduceOnly;
    if (payoutTokenSymbol) args.payoutTokenSymbol = String(payoutTokenSymbol);
    if (collateralTokenSymbol) args.collateralTokenSymbol = String(collateralTokenSymbol);
    const buildCandidates = [
      'buildOrderTx',
      'buildOpenPositionTx',
      'createOrderTransaction',
      'prepareOrderTx',
    ];
    let tx: any = null;
    for (const c of buildCandidates) {
      if (c in (perpClient as any) && typeof (perpClient as any)[c] === 'function') {
        try {
          tx = (perpClient as any)[c](args, pc);
          if (tx && typeof tx.then === 'function') tx = await tx;
          break;
        } catch (inner) {}
      }
    }

    if (!tx) {
      return res.status(501).json({ success: false, message: 'order build method not available in flash-sdk' });
    }

    // Ensure it's unsigned and return base64
    const serialized = tx.serialize({ requireAllSignatures: false, verifySignatures: false });
    const b64 = Buffer.from(serialized).toString('base64');
    return res.json({ success: true, market, owner: owner.toBase58(), transaction: b64 });
  } catch (e: any) {
    return res.status(500).json({ success: false, message: e?.message || String(e) });
  }
});

// Close or reduce a position, optionally receiving collateral in a different token.
// Expects body { market, size?, payoutTokenSymbol?, ownerPubkey }
// If size is omitted, close full position. Returns unsigned tx (base64).
app.post('/close', async (req: Request, res: Response) => {
  const { market, size, payoutTokenSymbol, ownerPubkey } = req.body || {};
  if (!market || !ownerPubkey) {
    return res.status(400).json({ success: false, message: 'market and ownerPubkey are required' });
  }
  if (!FLASH_RPC_URL && !process.env.SOLANA_RPC_URL) {
    return res.status(500).json({ success: false, message: 'RPC URL missing. Set FLASH_RPC_URL or SOLANA_RPC_URL' });
  }
  if (!ANCHOR_WALLET) {
    return res.status(500).json({ success: false, message: 'ANCHOR_WALLET not set' });
  }
  try {
    const { perpClient, poolConfig } = getClients();
    const owner = new PublicKey(ownerPubkey);

    const pc: any = poolConfig as any;
    const markets = ((pc.perpetuals || pc.markets || []) as any[]);
    const m = markets.find((x: any) => (x.symbol || x.asset || x.name) === market);
    if (!m) {
      return res.status(400).json({ success: false, message: `Unknown market: ${market}` });
    }

    // Try candidate builders for reduce-only close with optional payout token
    const args: any = { market, owner };
    if (typeof size !== 'undefined') args.size = size;
    if (payoutTokenSymbol) args.payoutTokenSymbol = String(payoutTokenSymbol);
    // Prefer explicit close/reduce methods, then fallback to generic order with reduceOnly
    const buildCandidates = [
      'buildClosePositionTx',
      'closePositionTx',
      'buildReducePositionTx',
      'reducePositionTx',
      'buildReduceOnlyOrderTx',
    ];
    let tx: any = null;
    for (const c of buildCandidates) {
      if (c in (perpClient as any) && typeof (perpClient as any)[c] === 'function') {
        try {
          tx = (perpClient as any)[c](args, pc);
          if (tx && typeof tx.then === 'function') tx = await tx;
          break;
        } catch (inner) {}
      }
    }

    // Fallback: use order builder with reduceOnly=true and side auto-resolved by SDK
    if (!tx) {
      const orderArgs: any = { market, owner, reduceOnly: true };
      if (typeof size !== 'undefined') orderArgs.size = size;
      if (payoutTokenSymbol) orderArgs.payoutTokenSymbol = String(payoutTokenSymbol);
      const orderBuilders = ['buildOrderTx', 'buildOpenPositionTx', 'prepareOrderTx', 'createOrderTransaction'];
      for (const b of orderBuilders) {
        if (b in (perpClient as any) && typeof (perpClient as any)[b] === 'function') {
          try {
            tx = (perpClient as any)[b](orderArgs, pc);
            if (tx && typeof tx.then === 'function') tx = await tx;
            break;
          } catch (inner) {}
        }
      }
    }

    if (!tx) {
      return res.status(501).json({ success: false, message: 'close position build method not available in flash-sdk' });
    }

    const serialized = tx.serialize({ requireAllSignatures: false, verifySignatures: false });
    const b64 = Buffer.from(serialized).toString('base64');
    return res.json({ success: true, market, owner: owner.toBase58(), transaction: b64 });
  } catch (e: any) {
    return res.status(500).json({ success: false, message: e?.message || String(e) });
  }
});

app.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`[flash-node-helper] listening on http://127.0.0.1:${PORT}`);
});
