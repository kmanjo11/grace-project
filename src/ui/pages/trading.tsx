// src/ui/pages/Trading.tsx
import React, { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import { useAuth } from '../components/AuthContext';
import { useAppState } from '../context/AppStateContext';
import { Trade } from '../api/apiTypes';
import UnifiedPriceChart from '../components/UnifiedPriceChart';
import ErrorBoundary from '../components/ErrorBoundary';
import { toast } from 'react-toastify';
import api, { API_ENDPOINTS } from '../api/apiClient';
import { GmgnApi, SmartSettingsApi } from '../api/apiClient';
import { VersionedTransaction, Transaction } from '@solana/web3.js';
import { Buffer } from 'buffer';
import { UiMarket } from '../types/market';
import { tradingEventBus } from '../components/LightweightPositionsWidget';
import gmgnTokenService from '../services/gmgnTokenService';
import flashTradeService from '../services/flashTradeService';
import state from '@project-serum/anchor/dist/cjs/program/namespace/state';
import { useSolanaWalletBridge } from '../hooks/useSolanaWalletBridge';

// Constants
const DEFAULT_LEVERAGE = 5;
const DEFAULT_STOP_LOSS = 5;
const DEFAULT_TAKE_PROFIT = 10;

// Types
type TradingState = {
  tokens: UiMarket[];
  selectedToken: UiMarket | null;
  transactions: Trade[];  // Changed from UITrade to Trade
  spotChain: 'sol' | 'eth' | 'bnb' | 'blast';
  isLoading: {
    tokens: boolean;
    transactions: boolean;
    trading: boolean;
  };
  error: string | null;
  resolution: string;
  search: string;
  tradeForm: {  // Defined inline instead of using TradeForm
    amount: string;
    leverage: number;
    isLeverage: boolean;
    isSmartTrade: boolean;
    stopLoss: number;
    takeProfit: number;
    orderType: 'market' | 'limit'; // Type of order: market or limit
    limitPrice: string; // Price for limit orders
    collateralTokenSymbol?: string;
    payoutTokenSymbol?: string;
    slippageBps?: number;
  };
};
// Initial state
const initialState: TradingState = {
  tokens: [],
  selectedToken: null,
  transactions: [],
  spotChain: 'sol',
  isLoading: {
    tokens: true,
    transactions: false,
    trading: false,
  },
  error: null,
  resolution: '1h',
  search: '',
  tradeForm: {
    amount: '',
    leverage: DEFAULT_LEVERAGE,
    isLeverage: true, // Enable leverage by default
    isSmartTrade: false,
    stopLoss: DEFAULT_STOP_LOSS,
    takeProfit: DEFAULT_TAKE_PROFIT,
    orderType: 'market', // Default to market orders
    limitPrice: '',
    collateralTokenSymbol: 'USDC',
    payoutTokenSymbol: 'USDC',
    slippageBps: 800,
  },
};

// Simple debounce helper (local)
function debounce<T extends (...args: any[]) => void>(fn: T, wait = 300) {
  let t: any;
  return (...args: Parameters<T>) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}

const Trading: React.FC = () => {
  const { user } = useAuth();
  // Get access to the app state for persistence
  const { state: appState, dispatch } = useAppState();
  
  // Initialize state with saved values from appState if available
  const savedTradingState = appState.tradingState || {};
  const [state, setState] = useState<TradingState>({
    ...initialState,
    // Restore any saved values
    selectedToken: savedTradingState.selectedToken || initialState.selectedToken,
    resolution: savedTradingState.resolution || initialState.resolution,
    search: savedTradingState.search || initialState.search,
    tradeForm: {
      ...initialState.tradeForm,
      ...(savedTradingState.tradeForm || {})
    }
  });
  
  const abortController = useRef<AbortController | null>(null);
  // Wallet bridge for Solana signing/sending
  const { ensureConnected, getPublicKey, signTx, sendSigned, connection } = useSolanaWalletBridge();
  // Smart settings and wallet info for wallet routing
  const [smartSettings, setSmartSettings] = useState<any | null>(null);
  const [walletInfo, setWalletInfo] = useState<any | null>(null);
  // Flash quote-derived metrics
  const [liqPrice, setLiqPrice] = useState<number | null>(null);
  // Local confirm modal state
  const [confirmModal, setConfirmModal] = useState<{
    open: boolean;
    details: {
      token?: string;
      action?: string;
      amount?: string;
      price?: number;
      total?: number;
      stopLoss?: number;
      takeProfit?: number;
      leverage?: number;
      liquidationPrice?: number | null;
    };
    resolve?: (v: boolean) => void;
  }>({ open: false, details: {} });

  // Save state to global persistence whenever it changes
  useEffect(() => {
    // Don't update during initial load
    if (state.tokens.length > 0 || state.selectedToken) {
      // Save to global app state
      dispatch({
        type: 'SET_TRADING_STATE',
        payload: {
          selectedToken: state.selectedToken,
          resolution: state.resolution,
          search: state.search,
          tradeForm: state.tradeForm,
          // Save positions in a compatible format for persistence
          positions: state.selectedToken ? [state.selectedToken] : []
        }
      });
    }
  }, [state.selectedToken, state.resolution, state.search, state.tradeForm, dispatch]);

  // Action creators with type safety
  const actions = useMemo(() => ({
    setTokens: (tokens: UiMarket[]) => {
      console.log('Setting tokens:', tokens);
      setState(prev => ({ ...prev, tokens }));
    },
    selectToken: (token: UiMarket | null) => {
      console.log('Selecting token:', token?.name);
      setState(prev => ({ ...prev, selectedToken: token }));
    },
    setTransactions: (transactions: Trade[]) => {
      setState(prev => ({ ...prev, transactions }));
    },
    setLoading: (loading: Partial<TradingState['isLoading']>) => {
      setState(prev => ({
        ...prev,
        isLoading: { ...prev.isLoading, ...loading }
      }));
    },
    setError: (error: string | null) => {
      console.error('Trading error:', error);
      setState(prev => ({
        ...prev,
        error,
        isLoading: { ...prev.isLoading, tokens: false, trading: false }
      }));
      if (error) {
        toast.error(error);
      }
    },
    setResolution: (resolution: string) => {
      console.log('Setting resolution:', resolution);
      setState(prev => ({
        ...prev,
        resolution,
        isLoading: { ...prev.isLoading, trading: true }
      }));
    },
    setSearch: (search: string) => {
      setState(prev => ({ ...prev, search }));
    },
    updateTradeForm: (form: Partial<TradingState['tradeForm']>) => {
      setState(prev => ({
        ...prev,
        tradeForm: { ...prev.tradeForm, ...form }
      }));
    },
    toggleLeverage: () => {
      setState(prev => ({
        ...prev,
        tradeForm: {
          ...prev.tradeForm,
          isLeverage: !prev.tradeForm.isLeverage,
          leverage: !prev.tradeForm.isLeverage ? DEFAULT_LEVERAGE : 1,
        },
      }));
    },
    toggleSmartTrade: () => {
      setState(prev => ({
        ...prev,
        tradeForm: {
          ...prev.tradeForm,
          isSmartTrade: !prev.tradeForm.isSmartTrade,
        },
      }));
    },
    toggleOrderType: () => {
      setState(prev => ({
        ...prev,
        tradeForm: {
          ...prev.tradeForm,
          orderType: prev.tradeForm.orderType === 'market' ? 'limit' : 'market',
          // Reset limitPrice when switching back to market order
          limitPrice: prev.tradeForm.orderType === 'limit' ? prev.tradeForm.limitPrice : '',
        },
      }));
    },
    setSpotChain: (chain: 'sol' | 'eth' | 'bnb' | 'blast') => {
      setState(prev => ({ ...prev, spotChain: chain }));
    },
  }), []);

  // Show trade confirmation dialog (modal-based)
  const showTradeConfirmation = async (details: {
    token: string;
    action: string;
    amount: string;
    price?: number;
    total?: number;
    stopLoss?: number;
    takeProfit?: number;
    leverage?: number;
    liquidationPrice?: number | null;
  }): Promise<boolean> => {
    return new Promise<boolean>((resolve) => {
      setConfirmModal({ open: true, details, resolve });
    });
  };

  // Execute a trade (buy/sell)
  const executeTrade = useCallback(async (side: 'buy' | 'sell') => {
    if (!state.selectedToken || !state.tradeForm.amount) {
      toast.error('Please select a token and enter an amount');
      return;
    }

    // For limit orders, validate limit price
    if (state.tradeForm.orderType === 'limit' && !state.tradeForm.limitPrice) {
      toast.error('Please enter a limit price');
      return;
    }

    // Simple confirmation dialog
    const amountNum = Number(state.tradeForm.amount);
    const priceNum = Number(state.selectedToken.price || 0);
    const total = isFinite(amountNum * priceNum) ? amountNum * priceNum : undefined;
    const confirmed = await showTradeConfirmation({
      token: state.selectedToken.symbol || state.selectedToken.name,
      action: side,
      amount: state.tradeForm.amount,
      price: priceNum || undefined,
      total,
      stopLoss: state.tradeForm.isSmartTrade ? state.tradeForm.stopLoss : undefined,
      takeProfit: state.tradeForm.isSmartTrade ? state.tradeForm.takeProfit : undefined,
      leverage: state.tradeForm.isLeverage ? state.tradeForm.leverage : undefined,
      liquidationPrice: state.tradeForm.isLeverage ? liqPrice : null,
    });
    if (!confirmed) return;

    try {
      actions.setLoading({ trading: true });
      
      if (state.tradeForm.orderType === 'limit') {
        // Handle limit order placement
        const limitOrderData = {
          market: state.selectedToken.symbol || state.selectedToken.name,
          side: side,
          price: parseFloat(state.tradeForm.limitPrice),
          size: parseFloat(state.tradeForm.amount),
          trade_type: state.tradeForm.isLeverage ? 'leverage' : 'spot',
          leverage: state.tradeForm.isLeverage ? state.tradeForm.leverage : undefined,
          reduce_only: false,
          client_id: `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
        };

        try {
          // Call the limit orders API endpoint
          const response = await api.post(API_ENDPOINTS.USER.LIMIT_ORDERS, limitOrderData);
          
          if (response.success) {
            toast.success(`${side.toUpperCase()} limit order placed successfully at $${state.tradeForm.limitPrice}`);
          } else {
            throw new Error(response.error || 'Failed to place limit order');
          }
        } catch (error: any) {
          console.error('Limit order placement error:', error);
          toast.error(`Limit order failed: ${error.message || 'Unknown error'}`);
        }
      } else {
        // If spot mode on Solana, use GMGN flow
        if (!state.tradeForm.isLeverage && state.spotChain === 'sol') {
          try {
            await handleGmgnSpotSwap(side);
            return;
          } catch (e:any) {
            console.error('GMGN spot swap failed:', e);
            toast.error(e?.message || 'GMGN spot swap failed');
            return;
          }
        }

        // Otherwise handle market order via Flash adapter (leverage or non-sol chains)
        const params = {
          market: state.selectedToken.symbol || state.selectedToken.name,
          side,
          size: parseFloat(state.tradeForm.amount),
          leverage: state.tradeForm.isLeverage ? state.tradeForm.leverage : 1,
          reduceOnly: false,
          takeProfitPrice: state.tradeForm.isSmartTrade ? Number(state.tradeForm.takeProfit) : undefined,
          stopLossPrice: state.tradeForm.isSmartTrade ? Number(state.tradeForm.stopLoss) : undefined,
          collateralTokenSymbol: state.tradeForm.collateralTokenSymbol,
          payoutTokenSymbol: state.tradeForm.payoutTokenSymbol,
          slippageBps: state.tradeForm.slippageBps ?? 800,
        } as const;

        // Determine effective wallet type (Phantom precedence)
        const isPhantomConnected = Boolean(getPublicKey());
        const configuredAuto = Boolean(smartSettings?.auto_trading_enabled);
        const pref = String(smartSettings?.wallet_preference || '').toLowerCase();
        const wantsInternal = pref === 'internal' || pref === 'auto';
        const internalReady = Boolean(walletInfo?.internal_wallet?.address);
        const walletType: 'internal' | 'phantom' = (configuredAuto && wantsInternal && internalReady && !isPhantomConnected) ? 'internal' : 'phantom';

        // If Phantom is connected, pass ownerPubkey to have server build txs for same owner
        const maybeOwner = getPublicKey()?.toBase58();
        const paramsWithOwner = maybeOwner ? { ...params, ownerPubkey: maybeOwner, walletType } : { ...params, walletType };

        const res = await flashTradeService.placeOrder(paramsWithOwner as any);
        if (res.success) {
          // If backend returned an unsigned transaction, sign and submit via wallet adapter
          const unsignedB64 = (res.data as any)?.unsigned_tx_b64 || (res.data as any)?.transaction;
          if (unsignedB64) {
            try {
              // Ensure wallet is connected and we have a pubkey
              await ensureConnected();
              if (!getPublicKey()) {
                throw new Error('Wallet not connected');
              }

              const msgBytes = Buffer.from(unsignedB64, 'base64');
              let signature: string | null = null;

              const flashToastId = toast.loading('Preparing transaction…');

              try {
                // Try v0 versioned first
                const vtx = VersionedTransaction.deserialize(Uint8Array.from(msgBytes));
                toast.update(flashToastId, { render: 'Please confirm in Phantom…', isLoading: true });
                const signed = await signTx(vtx);
                toast.update(flashToastId, { render: 'Submitting transaction…', isLoading: true });
                signature = await sendSigned(signed, connection, { skipPreflight: false, maxRetries: 3 });
              } catch {
                // Legacy fallback
                const legacy = Transaction.from(msgBytes);
                toast.update(flashToastId, { render: 'Please confirm in Phantom…', isLoading: true });
                const signedLegacy = await signTx(legacy);
                toast.update(flashToastId, { render: 'Submitting transaction…', isLoading: true });
                signature = await sendSigned(signedLegacy, connection, { skipPreflight: false, maxRetries: 3 });
              }

              if (signature) {
                toast.update(flashToastId, { render: `Order submitted. Tx: ${signature.slice(0, 8)}...`, type: 'success', isLoading: false, autoClose: 3500 });
              } else {
                toast.update(flashToastId, { render: `${side === 'buy' ? 'Buy' : 'Sell'} order placed`, type: 'success', isLoading: false, autoClose: 3000 });
              }
              // Emit global event and refresh local data for snappy UI updates
              try {
                tradingEventBus.emit('tradeConfirmed', {
                  source: 'flash',
                  type: state.tradeForm.isLeverage ? 'leverage' : 'spot',
                  action: side,
                  market: state.selectedToken?.symbol || state.selectedToken?.name,
                  amount: Number(state.tradeForm.amount),
                  signature,
                });
                // Refresh wallet and recent transactions quickly
                fetchWalletBalances();
                fetchTransactions();
              } catch {}
            } catch (e: any) {
              console.error('Flash signing/sending failed:', e);
              const raw = String(e?.message || 'Failed to sign and submit Flash transaction');
              const friendly =
                /4001|reject/i.test(raw) ? 'Signature rejected in Phantom' :
                /insufficient|balance/i.test(raw) ? 'Insufficient funds to complete transaction' :
                /blockhash/i.test(raw) ? 'Transaction expired. Please try again' :
                /slippage|price/i.test(raw) ? 'Price moved too much (slippage). Try again with higher slippage' :
                'Failed to sign and submit Flash transaction';
              toast.error(friendly);
              throw new Error(friendly);
            }
          } else {
            // No client-side signing required
            toast.success(`${side === 'buy' ? 'Buy' : 'Sell'} order placed successfully`);
            try {
              tradingEventBus.emit('tradeConfirmed', {
                source: 'flash',
                type: state.tradeForm.isLeverage ? 'leverage' : 'spot',
                action: side,
                market: state.selectedToken?.symbol || state.selectedToken?.name,
                amount: Number(state.tradeForm.amount),
              });
              fetchWalletBalances();
              fetchTransactions();
            } catch {}
          }
        } else {
          throw new Error(res.error || 'Failed to execute trade');
        }
      }
    } catch (error: any) {
      console.error('Trade execution error:', error);
      toast.error(`Trade failed: ${error.message || 'Unknown error'}`);
    } finally {
      actions.setLoading({ trading: false });
    }
  }, [state.selectedToken, state.tradeForm, actions, smartSettings, walletInfo]);

  // --- GMGN Solana spot swap flow ---
  const handleGmgnSpotSwap = useCallback(async (side: 'buy' | 'sell') => {
    if (!state.selectedToken) throw new Error('No token selected');
    const tokenCA = (state.selectedToken as any)?.tokenCA as string | undefined;
    if (!tokenCA || tokenCA.toLowerCase().startsWith('0x')) {
      throw new Error('Selected token is not a Solana token');
    }

    // Determine effective wallet type
    const isPhantomConnected = Boolean(getPublicKey());
    const configuredAuto = Boolean(smartSettings?.auto_trading_enabled);
    const pref = String(smartSettings?.wallet_preference || '').toLowerCase();
    const wantsInternal = pref === 'internal' || pref === 'auto';
    const internalReady = Boolean(walletInfo?.internal_wallet?.address);
    const walletType: 'internal' | 'phantom' = (configuredAuto && wantsInternal && internalReady && !isPhantomConnected) ? 'internal' : 'phantom';

    if (walletType === 'phantom') {
      // Ensure wallet connected via Solana Wallet Adapter
      await ensureConnected();
      if (!getPublicKey()) {
        throw new Error('Phantom wallet not connected. Connect in Wallet page and retry.');
      }
    }

    // Basic params – GMGN router expects token addresses and amount. We assume amount is in token units; backend may normalize.
    const amountStr = state.tradeForm.amount?.toString();
    if (!amountStr || Number(amountStr) <= 0) {
      throw new Error('Enter a valid amount');
    }

    // Determine direction: buying selected token with SOL (default) or selling selected token to SOL
    // For now, we default base token as SOL when side === 'buy' and tokenOut is selected token.
    const params: any = {
      tokenIn: side === 'buy' ? 'SOL' : tokenCA,
      tokenOut: side === 'buy' ? tokenCA : 'SOL',
      amount: amountStr,
      slippageBps: 100, // 1% default; TODO: expose in UI
    };

    // If we're signing client-side, ensure the router builds for our Phantom pubkey
    if (walletType === 'phantom') {
      try {
        const pk = getPublicKey()?.toBase58();
        if (pk) params.from_address = pk;
      } catch {}
    } else {
      // Request server-side signing flow
      params.wallet_type = 'internal';
    }

    // 1) Get unsigned transaction from backend -> GMGN router
    const tId = toast.loading('Preparing transaction…');
    const quote = await GmgnApi.quote(params);
    const unsignedTxB64 = quote?.tx || quote?.transaction || quote?.data?.tx;
    // If internal wallet path taken and no unsigned tx returned, assume server signed/submitted
    if (!unsignedTxB64 && walletType === 'internal') {
      toast.update(tId, { render: 'Swap submitted (server-signed)', type: 'success', isLoading: false, autoClose: 3000 });
      try {
        tradingEventBus.emit('tradeConfirmed', {
          source: 'gmgn',
          type: 'spot',
          action: side,
          token: (state.selectedToken as any)?.tokenCA || state.selectedToken?.symbol || state.selectedToken?.name,
          amount: Number(state.tradeForm.amount),
        });
        fetchWalletBalances();
        fetchTransactions();
      } catch {}
      return;
    }
    if (!unsignedTxB64) {
      console.error('GMGN quote response:', quote);
      toast.update(tId, { render: 'Failed to prepare transaction', type: 'error', isLoading: false, autoClose: 4000 });
      throw new Error('Did not receive unsigned transaction from GMGN');
    }

    // 2) Deserialize and sign with Phantom
    const msgBytes = Buffer.from(unsignedTxB64, 'base64');
    let vtx: VersionedTransaction | null = null;
    try {
      vtx = VersionedTransaction.deserialize(Uint8Array.from(msgBytes));
    } catch {
      // fallback for legacy tx (unlikely)
      try {
        const legacy = Transaction.from(msgBytes);
        toast.update(tId, { render: 'Please confirm in Phantom…', isLoading: true });
        const signedLegacy = await signTx(legacy);
        const signedB64 = Buffer.from(signedLegacy.serialize()).toString('base64');
        toast.update(tId, { render: 'Submitting transaction…', isLoading: true });
        await submitAndPollGmgn(signedB64);
        toast.update(tId, { render: 'Swap submitted', type: 'success', isLoading: false, autoClose: 3000 });
        return;
      } catch (e) {
        toast.update(tId, { render: 'Unable to parse GMGN transaction', type: 'error', isLoading: false, autoClose: 4000 });
        throw new Error('Unable to parse GMGN transaction');
      }
    }

    // Sign versioned transaction via adapter
    toast.update(tId, { render: 'Please confirm in Phantom…', isLoading: true });
    const signed = await signTx(vtx);
    const signedB64 = Buffer.from(signed.serialize()).toString('base64');

    // 3) Submit via backend -> GMGN txproxy and poll status
    toast.update(tId, { render: 'Submitting transaction…', isLoading: true });
    try {
      await submitAndPollGmgn(signedB64);
      toast.update(tId, { render: 'Swap submitted', type: 'success', isLoading: false, autoClose: 3000 });
      // After confirmed, emit and refresh balances/transactions
      try {
        tradingEventBus.emit('tradeConfirmed', {
          source: 'gmgn',
          type: 'spot',
          action: side,
          token: (state.selectedToken as any)?.tokenCA || state.selectedToken?.symbol || state.selectedToken?.name,
          amount: Number(state.tradeForm.amount),
        });
        fetchWalletBalances();
        fetchTransactions();
      } catch {}
    } catch (e: any) {
      const raw = String(e?.message || 'Submission failed');
      const friendly =
        /insufficient|balance/i.test(raw) ? 'Insufficient funds to complete transaction' :
        /blockhash/i.test(raw) ? 'Transaction expired. Please try again' :
        /slippage|price/i.test(raw) ? 'Price moved too much (slippage). Try again with higher slippage' :
        'Failed to submit transaction';
      toast.update(tId, { render: friendly, type: 'error', isLoading: false, autoClose: 5000 });
      throw new Error(friendly);
    }
  }, [state.selectedToken, state.tradeForm.amount, state.spotChain, smartSettings, walletInfo]);

  const submitAndPollGmgn = useCallback(async (signedB64: string) => {
    const submitRes = await GmgnApi.submitSigned({ signedTransaction: signedB64 });
    const txHash = submitRes?.txHash || submitRes?.signature || submitRes?.tx || submitRes?.data?.txHash;
    if (!txHash) {
      console.warn('GMGN submit response:', submitRes);
      throw new Error('Failed to get transaction signature');
    }

    // Poll until confirmed or timeout
    const start = Date.now();
    const timeoutMs = 60_000;
    let lastErr: any = null;
    while (Date.now() - start < timeoutMs) {
      try {
        const status = await GmgnApi.txStatus({ txHash });
        const ok = status?.confirmed || status?.success || status?.data?.confirmed;
        if (ok) {
          toast.success('Swap confirmed');
          return;
        }
      } catch (e) {
        lastErr = e;
      }
      await new Promise(r => setTimeout(r, 2000));
    }
    if (lastErr) console.warn('GMGN poll last error:', lastErr);
    throw new Error('Swap not confirmed before timeout');
  }, []);

  // Handle token selection with data loading
  const handleTokenSelect = useCallback(async (token: UiMarket) => {
    if (!token) {
      actions.setError('Invalid token');
      return;
    }
    console.log(`Selected token: ${token.name || token.symbol}`);
    
    // Update UI state
    actions.selectToken(token);
    actions.setSearch('');
    actions.setTokens([]);
    actions.updateTradeForm({ amount: '' });
    actions.setLoading({ trading: true });
    
    try {
      // Opportunistically refresh latest price for display
      const p = await gmgnTokenService.getPrice(token.symbol || token.name);
      if (p !== undefined) {
        actions.selectToken({ ...token, price: p });
      }
      // Reset quote-derived metrics
      setLiqPrice(null);
      
    } catch (error) {
      const errorMsg = error instanceof Error ? 
        `Failed to load token data: ${error.message}` : 
        'Failed to load token data';
        
      console.error(errorMsg, error);
      actions.setError(errorMsg);
    } finally {
      actions.setLoading({ trading: false });
    }
  }, [state.resolution, actions]);

  // Fetch liquidation price from backend; fallback to quote method for preview
  useEffect(() => {
    const run = async () => {
      try {
        if (!state.tradeForm.isLeverage || !state.selectedToken) {
          setLiqPrice(null);
          return;
        }

        // Prefer server-side liquidation price for current user/market
        const market = state.selectedToken.symbol || state.selectedToken.name;
        const ownerPubkey = getPublicKey()?.toBase58();
        try {
          // Include walletType for accurate server-side computation when internal
          const isPhantomConnected = Boolean(getPublicKey());
          const configuredAuto = Boolean(smartSettings?.auto_trading_enabled);
          const pref = String(smartSettings?.wallet_preference || '').toLowerCase();
          const wantsInternal = pref === 'internal' || pref === 'auto';
          const internalReady = Boolean(walletInfo?.internal_wallet?.address);
          const walletType: 'internal' | 'phantom' = (configuredAuto && wantsInternal && internalReady && !isPhantomConnected) ? 'internal' : 'phantom';
          const resp = await flashTradeService.getLiquidationPrice({ market, ...(ownerPubkey ? { ownerPubkey } : {}), walletType });
          const lp = (resp as any)?.data?.liquidationPrice || (resp as any)?.liquidationPrice;
          if (lp !== undefined && lp !== null && isFinite(Number(lp))) {
            setLiqPrice(Number(lp));
            return;
          }
        } catch (e) {
          // continue to fallback below
        }

        // Fallback: use quote-based estimation when user has no position yet
        const size = Number(state.tradeForm.amount || '0');
        if (!size || size <= 0) {
          setLiqPrice(null);
          return;
        }
        const q = await flashTradeService.getQuote({
          market,
          side: 'buy',
          size,
          leverage: state.tradeForm.leverage || 1,
          // Hint walletType for quote path as well
          walletType: (Boolean(smartSettings?.auto_trading_enabled) && (String(smartSettings?.wallet_preference||'').toLowerCase() === 'internal' || String(smartSettings?.wallet_preference||'').toLowerCase() === 'auto') && Boolean(walletInfo?.internal_wallet?.address) && !Boolean(getPublicKey())) ? 'internal' : 'phantom',
        } as any);
        const qLp = (q as any)?.data?.liquidationPrice || (q as any)?.quote?.liquidationPrice;
        if (qLp && isFinite(Number(qLp))) setLiqPrice(Number(qLp)); else setLiqPrice(null);
      } catch (e) {
        setLiqPrice(null);
      }
    };
    run();
  }, [state.tradeForm.isLeverage, state.tradeForm.amount, state.tradeForm.leverage, state.selectedToken, smartSettings, walletInfo]);

  // Handle interval/resolution change (UI-only validation now)
  const handleResolutionChange = useCallback((newResolution: string) => {
    try {
      if (!/^\d+[mhd]$/i.test(newResolution)) {
        throw new Error('Invalid resolution format. Use 1m, 5m, 15m, 1h, 4h, 1d');
      }
      actions.setResolution(newResolution);
    } catch (error) {
      console.error('Resolution validation error:', error);
      actions.setError(error instanceof Error ? error.message : 'Invalid resolution');
    }
  }, [actions]);
  
  // Available resolutions for unified charting (GMGN/Flash)
  const availableResolutions = useMemo(() => ({
    '1m': '1 minute',
    '5m': '5 minutes',
    '15m': '15 minutes',
    '1h': '1 hour',
    '4h': '4 hours',
    '1d': '1 day'
  }), []);

  // Fetch transaction history for the current user
  const fetchTransactions = useCallback(async () => {
    if (!user) return;
    
    try {
      actions.setLoading({ transactions: true });
      const response = await api.get(`${API_ENDPOINTS.MANGO.TRADES}?limit=10`);
      
      if (response && Array.isArray(response.data)) {
        actions.setTransactions(response.data);
      } else {
        console.warn('Invalid transaction data format:', response);
        actions.setTransactions([]);
      }
    } catch (error) {
      console.error('Error fetching transactions:', error);
      actions.setTransactions([]);
    } finally {
      actions.setLoading({ transactions: false });
    }
  }, [user, actions]);
  


  // Remove event bus usage; rely on local refresh triggers as needed

  // Fetch tokens/markets with debounce, filtered by mode
  const fetchTokens = useCallback(
    debounce(async (query: string) => {
      const searchQuery = (query || '').trim();
      const isLeverageMode = !!state.tradeForm.isLeverage;
      console.log('Searching for instruments with query:', searchQuery, 'mode:', isLeverageMode ? 'leverage' : 'spot');

      // Cancel any pending requests
      if (abortController.current) {
        console.log('Cancelling previous search request');
        abortController.current.abort();
      }
      abortController.current = new AbortController();
      actions.setLoading({ tokens: true });

      try {
        // Always hit the service. Empty query should return the full list as requested
        const all = await gmgnTokenService.searchTokens(searchQuery);
        // Mode-based filtering: leverage vs spot
        const filtered = all.filter((m) => {
          if (isLeverageMode) {
            const name = (m.name || '').toUpperCase();
            const quote = (m.quoteCurrency || '').toUpperCase();
            // Heuristics: include perpetual or USDC quoted perp-like markets
            return name.includes('-PERP') || name.includes('/PERP') || quote === 'USDC';
          }
          // Spot: must have a token contract address for GMGN embed
          const ca = (m as any).tokenCA as string | undefined;
          if (!ca) return false;
          const isEvmChain = state.spotChain !== 'sol';
          const isEvmCA = typeof ca === 'string' && ca.toLowerCase().startsWith('0x');
          return isEvmChain ? isEvmCA : !isEvmCA;
        });

        console.log(`Displaying ${filtered.length} items after mode filtering`);
        actions.setTokens(filtered);
        actions.setError(null);
      } catch (error) {
        if ((error as any).name === 'AbortError') {
          console.log('Search was cancelled');
          return;
        }
        console.error('Error fetching tokens:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch tokens';
        actions.setError(errorMessage);
        actions.setTokens([]);
      } finally {
        actions.setLoading({ tokens: false });
      }
    }, 300),
    [state.tradeForm.isLeverage, state.spotChain]
  );

  // Handle search input change
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    actions.setSearch(value);
    // Always fetch; empty string returns full list per requirement
    fetchTokens(value);
  }, [fetchTokens, actions]);

  // Fetch wallet balances
  const [walletBalances, setWalletBalances] = useState<{
    balances: { [key: string]: number };
    loading: boolean;
    error: string | null;
    loaded?: boolean;
  }>({
    balances: {},
    loading: false,
    error: null,
    loaded: false
  });

  // Fetch wallet balances
  const fetchWalletBalances = useCallback(async () => {
    if (!user) return;
    
    try {
      setWalletBalances(prev => ({ ...prev, loading: true, error: null }));
      
      const response = await api.get(API_ENDPOINTS.WALLET.BALANCE);
      
      if (response.success && response.data) {
        const balanceData = response.data;
        const formattedBalances: { [key: string]: number } = {};
        
        // Format balances to a usable format
        if (Array.isArray(balanceData.tokens)) {
          balanceData.tokens.forEach((token: any) => {
            if (token.symbol && typeof token.amount === 'number') {
              formattedBalances[token.symbol.toUpperCase()] = token.amount;
            }
          });
        }
        
        console.log('Wallet balances loaded:', formattedBalances);
        setWalletBalances({
          balances: formattedBalances,
          loading: false,
          error: null,
          loaded: true
        });
      } else {
        throw new Error(response.error || 'Failed to load wallet balances');
      }
    } catch (error) {
      console.error('Error fetching wallet balances:', error);
      setWalletBalances(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load wallet balances'
      }));
    }
  }, [user]);

  // Initial data fetch
  useEffect(() => {
    // Load initial tokens
    fetchTokens('');
    // Load initial balances and set periodic refresh
    fetchWalletBalances();
    // Load smart settings and wallet data to determine walletType routing
    const loadPrefs = async () => {
      try {
        const ss = await SmartSettingsApi.get();
        if (ss?.success) setSmartSettings(ss.settings || {});
      } catch (e) {
        console.warn('Failed to load smart settings', e);
      }
      try {
        const wd = await api.get(API_ENDPOINTS.WALLET.DATA);
        if (wd?.success) setWalletInfo(wd.data || null);
      } catch (e) {
        console.warn('Failed to load wallet data', e);
      }
    };
    loadPrefs();
    const balInterval = setInterval(() => {
      fetchWalletBalances();
    }, 60_000);
    
    // Cleanup function to abort any pending requests
    return () => {
      if (abortController.current) {
        abortController.current.abort();
      }
      clearInterval(balInterval);
    };
  }, [fetchTokens, fetchWalletBalances]);

  // Refresh list when mode toggles (spot <-> leverage)
  useEffect(() => {
    fetchTokens(state.search);
  }, [state.tradeForm.isLeverage]);

  // Refresh list and clear selection when spot chain changes
  useEffect(() => {
    actions.selectToken(null);
    actions.setTokens([]);
    fetchTokens(state.search);
  }, [state.spotChain]);

  // Render token list
  const renderTokenList = () => (
    <div className="bg-gray-900 rounded-lg p-4 h-full">
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search tokens..."
          className="w-full p-2 bg-gray-800 text-white rounded"
          value={state.search}
          onChange={handleSearchChange}
        />
      </div>
      <div className="space-y-2 max-h-[500px] overflow-y-auto">
        {state.tokens.map((token) => (
          <div
            key={token.symbol || token.name}
            className={`p-3 rounded-lg cursor-pointer hover:bg-gray-800 ${
              state.selectedToken?.symbol === token.symbol ? 'bg-blue-900' : 'bg-gray-800'
            }`}
            onClick={() => handleTokenSelect(token)}
          >
            <div className="flex justify-between items-center">
              <div>
                <div className="font-medium">{token.symbol}</div>
                <div className="text-sm text-gray-400">{token.name}</div>
                {/* Show trading pair information clearly */}
                {token.baseCurrency && token.quoteCurrency && (
                  <div className="text-xs text-blue-400 mt-1">
                    {token.baseCurrency}/{token.quoteCurrency}
                  </div>
                )}
              </div>
              <div className="text-right">
                <div>${token.price?.toFixed(6) || 'N/A'}</div>
                <div className={`text-sm ${
                  (token.change_24h || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {token.change_24h ? `${token.change_24h.toFixed(2)}%` : 'N/A'}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {state.isLoading.tokens && (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        )}
        
        {!state.isLoading.tokens && state.tokens.length === 0 && state.search && (
          <div className="text-center py-4 text-gray-400">
            No tokens found
          </div>
        )}
      </div>
    </div>
  );

  // Check if user has enough balance for the trade
  const checkWalletBalance = useCallback((token: string, amount: string): boolean => {
    if (!amount || isNaN(parseFloat(amount))) return true; // Don't show error if amount is empty
    
    // Find the token in wallet balances
    const tokenSymbol = token.toUpperCase();
    const balance = walletBalances.balances[tokenSymbol] || 0;
    
    return parseFloat(amount) <= balance;
  }, [walletBalances.balances]);
  
  // Render wallet balances section
  const renderWalletBalances = () => {
    const relevantBalances = Object.entries(walletBalances.balances)
      .filter(([symbol]) => {
        // Show all balances, but prioritize the selected token if available
        if (state.selectedToken && state.selectedToken.symbol === symbol) return true;
        // Only show non-zero balances or top 3 tokens
        return true;
      })
      .sort((a, b) => b[1] - a[1]) // Sort by balance value, highest first
      .slice(0, 5); // Show top 5 balances
    
    return (
      <div className="mb-4 p-3 bg-gray-800 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-400">Wallet Balances</h3>
          <button
            className="text-xs px-2 py-1 rounded bg-gray-700 hover:bg-gray-600"
            onClick={fetchWalletBalances}
            disabled={walletBalances.loading}
          >
            {walletBalances.loading ? 'Refreshing…' : 'Refresh'}
          </button>
        </div>
        
        {walletBalances.loading ? (
          <div className="text-center py-1">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        ) : walletBalances.error ? (
          <div className="text-xs text-red-400">{walletBalances.error}</div>
        ) : relevantBalances.length > 0 ? (
          <div className="space-y-1">
            {relevantBalances.map(([symbol, amount]) => (
              <div key={symbol} className="flex justify-between items-center">
                <span className="text-sm font-medium">{symbol}</span>
                <span className="text-sm text-gray-300">{amount.toFixed(6)}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs text-gray-500">No balances available</div>
        )}
      </div>
    );
  };

  // Render trading form
  const renderTradingForm = () => (
    <div className="bg-gray-900 rounded-lg p-4">
      {state.selectedToken ? (
        <>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">
              {state.selectedToken.symbol}
              <span className="ml-2 text-sm text-gray-400">
                ${state.selectedToken.price?.toFixed(6) || 'N/A'}
              </span>
            </h2>
            <div className={`text-sm ${
              (state.selectedToken.change_24h || 0) >= 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              {state.selectedToken.change_24h ? `${state.selectedToken.change_24h.toFixed(2)}%` : 'N/A'}
            </div>
          </div>
          
          <div className="space-y-4">
            {/* Show wallet balances above the trading form */}
            {renderWalletBalances()}
            
            {/* Order Type Toggle (Market/Limit) */}
            <div className="flex items-center justify-between bg-gray-800 rounded p-2">
              <div className="text-sm text-gray-400">Order Type:</div>
              <div className="flex bg-gray-700 rounded overflow-hidden">
                <button
                  className={`px-3 py-1 text-sm ${state.tradeForm.orderType === 'market' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                  onClick={() => state.tradeForm.orderType !== 'market' && actions.toggleOrderType()}
                >
                  Market
                </button>
                <button
                  className={`px-3 py-1 text-sm ${state.tradeForm.orderType === 'limit' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                  onClick={() => state.tradeForm.orderType !== 'limit' && actions.toggleOrderType()}
                >
                  Limit
                </button>
              </div>
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Amount</label>
              <input
                type="number"
                className={`w-full p-2 ${state.selectedToken && walletBalances.loaded && !checkWalletBalance(state.selectedToken.symbol, state.tradeForm.amount) ? 'bg-red-900/30 border border-red-500' : 'bg-gray-800'} text-white rounded`}
                value={state.tradeForm.amount}
                onChange={(e) => actions.updateTradeForm({ amount: e.target.value })}
                placeholder="0.0"
              />
              {state.selectedToken && walletBalances.loaded && !checkWalletBalance(state.selectedToken.symbol, state.tradeForm.amount) && (
                <div className="text-xs text-red-400 mt-1">
                  Insufficient balance for {state.selectedToken.symbol}
                </div>
              )}
            </div>
            
            {/* Limit Price field - only shown for limit orders */}
            {state.tradeForm.orderType === 'limit' && (
              <div>
                <label className="block text-sm text-gray-400 mb-1">Limit Price ($)</label>
                <input
                  type="number"
                  className="w-full p-2 bg-gray-800 text-white rounded"
                  value={state.tradeForm.limitPrice}
                  onChange={(e) => actions.updateTradeForm({ limitPrice: e.target.value })}
                  placeholder={state.selectedToken?.price?.toFixed(6) || "0.0"}
                />
              </div>
            )}
            
            <div className="flex items-center justify-between">
              <button
                className={`px-3 py-1 rounded ${
                  state.tradeForm.isLeverage
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
                onClick={actions.toggleLeverage}
              >
                Leverage
              </button>
              
              {state.tradeForm.isLeverage && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-400">Leverage:</span>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    className="w-16 p-1 bg-gray-800 text-white rounded text-center"
                    value={state.tradeForm.leverage}
                    onChange={(e) => 
                      actions.updateTradeForm({ 
                        leverage: Math.min(20, Math.max(1, Number(e.target.value) || 1)) 
                      })
                    }
                  />
                  <span className="text-sm">x</span>
                </div>
              )}
              
              <button
                className={`px-3 py-1 rounded ${
                  state.tradeForm.isSmartTrade
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
                onClick={actions.toggleSmartTrade}
              >
                Smart Trade
              </button>
            </div>
            
            {state.tradeForm.isSmartTrade && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Stop Loss (%)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    className="w-full p-2 bg-gray-800 text-white rounded"
                    value={state.tradeForm.stopLoss}
                    onChange={(e) => 
                      actions.updateTradeForm({ 
                        stopLoss: Math.max(0, Number(e.target.value) || 0) 
                      })
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Take Profit (%)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    className="w-full p-2 bg-gray-800 text-white rounded"
                    value={state.tradeForm.takeProfit}
                    onChange={(e) => 
                      actions.updateTradeForm({ 
                        takeProfit: Math.max(0, Number(e.target.value) || 0) 
                      })
                    }
                  />
                </div>
              </div>
            )}
            
            {/* Advanced params */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Collateral Token</label>
                <input
                  type="text"
                  className="w-full p-2 bg-gray-800 text-white rounded"
                  value={state.tradeForm.collateralTokenSymbol || ''}
                  onChange={(e) => actions.updateTradeForm({ collateralTokenSymbol: e.target.value.toUpperCase() })}
                  placeholder="USDC"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Payout Token</label>
                <input
                  type="text"
                  className="w-full p-2 bg-gray-800 text-white rounded"
                  value={state.tradeForm.payoutTokenSymbol || ''}
                  onChange={(e) => actions.updateTradeForm({ payoutTokenSymbol: e.target.value.toUpperCase() })}
                  placeholder="USDC"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Slippage (bps)</label>
                <input
                  type="number"
                  min="1"
                  className="w-full p-2 bg-gray-800 text-white rounded"
                  value={Number(state.tradeForm.slippageBps ?? 800)}
                  onChange={(e) => actions.updateTradeForm({ slippageBps: Math.max(1, Number(e.target.value) || 1) })}
                  placeholder="800"
                />
              </div>
            </div>

            {/* Leverage-only info */}
            {state.tradeForm.isLeverage && (
              <div className="mt-2 text-xs text-gray-300">
                {liqPrice ? (
                  <span className="inline-block px-2 py-1 rounded bg-gray-800">
                    Est. Liq Price: <span className="text-red-300">${liqPrice.toFixed(4)}</span>
                  </span>
                ) : (
                  <span className="inline-block px-2 py-1 rounded bg-gray-800 text-gray-400">
                    Enter amount/leverage to see est. liquidation price
                  </span>
                )}
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              {(() => {
                const amountOk = !!state.tradeForm.amount && Number(state.tradeForm.amount) > 0;
                const limitOk = state.tradeForm.orderType === 'market' || (!!state.tradeForm.limitPrice && Number(state.tradeForm.limitPrice) > 0);
                const disabled = state.isLoading.trading || !amountOk || !limitOk;
                return (
              <>
              <button
                className={`bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded ${state.isLoading.trading ? 'opacity-50 cursor-not-allowed' : ''}`}
                onClick={() => executeTrade('buy')}
                disabled={disabled}
              >
                {state.isLoading.trading ? 'Processing...' : 'Buy'}
              </button>
              <button
                className={`bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded ${state.isLoading.trading ? 'opacity-50 cursor-not-allowed' : ''}`}
                onClick={() => executeTrade('sell')}
                disabled={disabled}
              >
                {state.isLoading.trading ? 'Processing...' : 'Sell'}
              </button>
              </>
                );
              })()}
            </div>
          </div>
        </>
      ) : (
        <div className="text-center py-8 text-gray-400">
          Select a token to start trading
        </div>
      )}
    </div>
  );

  // Map UI resolution to leverage/GMGN intervals
  const mapInterval = (res: string, isLeverage: boolean): string => {
    if (!isLeverage) return res; // GMGN accepts 1m,5m,15m,1h,4h,1d
    const lut: Record<string, string> = {
      '1m': '1',
      '5m': '5',
      '15m': '15',
      '1h': '60',
      '4h': '240',
      '1d': '1D',
    };
    return lut[res] || '60';
  };

  // Inline confirmation modal component
  const ConfirmModal: React.FC = () => {
    if (!confirmModal.open) return null;
    const d = confirmModal.details || {};
    const fmt = (n?: number | null, digits = 6) =>
      n === undefined || n === null || !isFinite(Number(n)) ? 'N/A' : Number(n).toLocaleString(undefined, { maximumFractionDigits: digits });
    const onCancel = () => {
      confirmModal.resolve?.(false);
      setConfirmModal({ open: false, details: {} });
    };
    const onConfirm = () => {
      confirmModal.resolve?.(true);
      setConfirmModal({ open: false, details: {} });
    };
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <div className="absolute inset-0 bg-black/60" onClick={onCancel} />
        <div className="relative z-10 w-full max-w-md bg-gray-900 border border-gray-700 rounded-lg shadow-xl p-5">
          <h3 className="text-lg font-semibold mb-3">Confirm Trade</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-gray-400">Action</span><span className="font-medium capitalize">{d.action}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Token</span><span className="font-medium">{d.token}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Amount</span><span className="font-medium">{d.amount}</span></div>
            {d.price !== undefined && <div className="flex justify-between"><span className="text-gray-400">Price</span><span className="font-medium">${fmt(d.price)}</span></div>}
            {d.total !== undefined && <div className="flex justify-between"><span className="text-gray-400">Total</span><span className="font-medium">${fmt(d.total)}</span></div>}
            {d.leverage !== undefined && <div className="flex justify-between"><span className="text-gray-400">Leverage</span><span className="font-medium">{d.leverage}x</span></div>}
            {d.liquidationPrice !== undefined && d.liquidationPrice !== null && (
              <div className="flex justify-between"><span className="text-gray-400">Est. Liq Price</span><span className="font-medium text-red-300">${fmt(d.liquidationPrice, 4)}</span></div>
            )}
            {d.stopLoss !== undefined && <div className="flex justify-between"><span className="text-gray-400">Stop Loss</span><span className="font-medium">${fmt(d.stopLoss)}</span></div>}
            {d.takeProfit !== undefined && <div className="flex justify-between"><span className="text-gray-400">Take Profit</span><span className="font-medium">${fmt(d.takeProfit)}</span></div>}
            <div className="text-xs text-gray-400 pt-1">You will still need to approve in Phantom to finalize this trade.</div>
          </div>
          <div className="mt-4 flex justify-end gap-3">
            <button className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded" onClick={onCancel}>Cancel</button>
            <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded" onClick={onConfirm}>Confirm</button>
          </div>
        </div>
      </div>
    );
  };

// Render price chart (Unified)
const renderPriceChart = () => {
  const isLeverage = !!state.tradeForm.isLeverage;
  const interval = mapInterval(state.resolution, isLeverage);
  const market = state.selectedToken?.name || state.selectedToken?.symbol || '';
  const theme: 'light' | 'dark' = 'dark';
  const chain = state.spotChain;
  const tokenCA = (state.selectedToken as any)?.tokenCA || '';

  return (
    <div className="bg-gray-900 rounded-lg p-4 h-full">
      {state.selectedToken ? (
        <div className="h-full flex flex-col">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-lg font-medium">Price Chart</h3>
            <div className="flex items-center space-x-2">
              {!isLeverage && (
                <div className="flex bg-gray-800 rounded overflow-hidden">
                  {(['sol','eth','bnb','blast'] as const).map(ch => (
                    <button
                      key={ch}
                      className={`px-2 py-1 text-sm ${chain === ch ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}
                      onClick={() => actions.setSpotChain(ch)}
                    >
                      {ch.toUpperCase()}
                    </button>
                  ))}
                </div>
              )}
              {Object.entries(availableResolutions).map(([res, label]) => (
                <button
                  key={res}
                  className={`px-2 py-1 text-sm rounded ${
                    state.resolution === res
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                  onClick={() => handleResolutionChange(res)}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
          <div className="flex-1 min-h-[420px]">
            <UnifiedPriceChart
              key={`chart-${isLeverage ? 'lev' : 'spot'}-${isLeverage ? market : tokenCA}-${chain}-${interval}`}
              mode={isLeverage ? 'leverage' : 'spot'}
              chain={chain}
              tokenCA={!isLeverage ? tokenCA : undefined}
              market={isLeverage ? market : undefined}
              interval={interval as any}
              theme={theme}
              height={460}
            />
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center h-full text-gray-400">
          Select a token to view chart
        </div>
      )}
    </div>
  );
};

// Render transaction history
const renderTransactionHistory = () => (
  <div className="bg-gray-900 rounded-lg p-4 h-full">
    <h3 className="text-lg font-medium mb-4">Recent Trades</h3>
    {state.isLoading.transactions ? (
      <div className="text-center py-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
      </div>
    ) : state.transactions.length > 0 ? (
      <div className="space-y-2">
        {state.transactions.map((tx: any, index: number) => {
          const side = tx?.side?.toLowerCase() === 'sell' ? 'sell' : 'buy';
          const symbol = tx?.symbol || 'TOKEN';
          const amount = tx?.amount ? Number(tx.amount).toFixed(4) : '0';
          const price = tx?.price ? `$${Number(tx.price).toFixed(6)}` : '$0';
          const timestamp = tx?.timestamp ? new Date(tx.timestamp).toLocaleString() : 'Just now';

          return (
            <div key={index} className="flex justify-between items-center p-2 bg-gray-800 rounded">
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full mr-2 ${side === 'buy' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="font-medium">{symbol}</span>
              </div>
              <div className="text-right">
                <div className={side === 'buy' ? 'text-green-400' : 'text-red-400'}>
                  {side.toUpperCase()} {amount} @ {price}
                </div>
                <div className="text-xs text-gray-400">{timestamp}</div>
              </div>
            </div>
          );
        })}
      </div>
    ) : (
      <div className="text-center py-8 text-gray-400">No recent trades found</div>
    )}
  </div>
);

  return (
    <ErrorBoundary>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Trading</h1>
        <ConfirmModal />
        
        {state.error && (
          <div className="bg-red-900/50 border border-red-500 text-white px-4 py-3 rounded mb-4">
            {state.error}
          </div>
        )}
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-1">
            {renderTokenList()}
          </div>
          <div className="lg:col-span-2">
            {renderTradingForm()}
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            {renderPriceChart()}
          </div>
          <div className="lg:col-span-1">
            {renderTransactionHistory()}
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
};

// Define props for the TradingPage component
interface TradingPageProps {}

const TradingPage: React.FC<TradingPageProps> = () => {
  return (
    <ErrorBoundary>
      <Trading />
    </ErrorBoundary>
  );
};

export default TradingPage;