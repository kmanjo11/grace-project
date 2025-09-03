import { useCallback } from 'react';
import { useWallet, useConnection } from '@solana/wallet-adapter-react';
import type {
  Transaction,
  VersionedTransaction,
  Connection,
  SendOptions,
  PublicKey,
} from '@solana/web3.js';

// A thin, adapter-first signing bridge with a window.solana fallback.
// Use this from spot (GMGN) and leverage (Flash) flows for consistent signing.
export function useSolanaWalletBridge() {
  const { publicKey, signTransaction, sendTransaction, connect, connected, wallet, disconnect } = useWallet();
  const { connection } = useConnection();

  const getPublicKey = useCallback((): PublicKey | null => {
    return publicKey ?? null;
  }, [publicKey]);

  const ensureConnected = useCallback(async () => {
    if (!connected) {
      // Tries adapter connect() which will trigger the wallet modal if needed
      await connect();
    }
  }, [connected, connect]);

  const signTx = useCallback(
    async <T extends Transaction | VersionedTransaction>(tx: T): Promise<T> => {
      // Prefer adapter signer
      if (signTransaction) {
        return await signTransaction(tx) as T;
      }
      // Fallback: window.solana if injected (Phantom)
      const provider: any = (globalThis as any).solana;
      if (provider && provider.signTransaction) {
        return await provider.signTransaction(tx);
      }
      throw new Error('No wallet signer available. Connect Phantom and try again.');
    },
    [signTransaction]
  );

  const sendSigned = useCallback(
    async (
      tx: Transaction | VersionedTransaction,
      conn?: Connection,
      options?: SendOptions,
    ): Promise<string> => {
      const c = conn ?? connection;
      // If adapter has sendTransaction, it will sign+send. Use only if tx is unsigned.
      // For pre-signed tx, use c.sendRawTransaction instead.
      // Here we assume tx is already signed; detect via signatures length when possible.
      // VersionedTransaction has .serialize(), Transaction has .serialize() after partialSign/sign.
      // If the adapter is connected and you want sign+send in one call, you can still use sendTransaction upstream.
      const maybeSigned = (tx as any);
      if (maybeSigned.signatures && maybeSigned.signatures.length > 0) {
        const raw = (tx as any).serialize();
        return await c.sendRawTransaction(raw, options);
      }
      if (sendTransaction) {
        return await sendTransaction(tx as any, c, options);
      }
      // Final fallback: try window.solana.signAndSendTransaction if available
      const provider: any = (globalThis as any).solana;
      if (provider && provider.signAndSendTransaction) {
        const res = await provider.signAndSendTransaction(tx as any);
        return res?.signature || res; // Phantom returns { signature }
      }
      throw new Error('No wallet send capability available.');
    },
    [connection, sendTransaction]
  );

  const disconnectWallet = useCallback(async () => {
    try {
      await disconnect();
    } catch {}
  }, [disconnect]);

  return {
    connection,
    publicKey,
    connected,
    wallet,
    ensureConnected,
    getPublicKey,
    signTx,
    sendSigned,
    disconnectWallet,
  };
}
