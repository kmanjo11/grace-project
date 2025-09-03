import { BN } from "@coral-xyz/anchor";
import { Mint } from "@solana/spl-token";
import { CustodyAccount } from "./CustodyAccount";
import { OraclePrice } from "./OraclePrice";
import { PoolConfig } from "./PoolConfig";
import { PoolAccount } from "./PoolAccount";
import { MarketAccount } from "./MarketAccount";
export interface LpStats {
    lpTokenSupply: BN;
    decimals: number;
    totalPoolValueUsd: BN;
    totalPoolValueUsdUi: string;
    price: BN;
    priceUi: string;
    stableCoinPercentage: string;
    marketCap: BN;
}
export interface CustodyStats {
    symbol: string;
    priceUi: string;
    minRatio: BN;
    minRatioUi: string;
    maxRatio: BN;
    maxRatioUi: string;
    targetRatio: BN;
    targetRatioUi: string;
    currentRatio: BN;
    currentRatioUi: string;
    utilizationUi: string;
    lockedAmountUi: string;
    assetsOwnedAmountUi: string;
    totalUsdOwnedAmountUi: string;
    availableToAddAmountUi: string;
    availableToAddUsdUi: string;
    availableToRemoveAmountUi: string;
    availableToRemoveUsdUi: string;
    minCapacityAmountUi: string;
    maxCapacityAmountUi: string;
}
export declare class PoolDataClient {
    poolConfig: PoolConfig;
    pool: PoolAccount;
    lpTokenInfo: Mint;
    custodies: CustodyAccount[];
    markets: MarketAccount[];
    constructor(poolConfig: PoolConfig, pool: PoolAccount, lpTokenInfo: Mint, custodies: CustodyAccount[]);
    loadCustodies(custodies: CustodyAccount[]): void;
    loadPoolData(pool: PoolAccount): void;
    loadLpData(lpTokenInfo: Mint): void;
    getLpStats(pricesMap: Map<string, {
        price: OraclePrice;
        emaPrice: OraclePrice;
    }>): LpStats;
    getCustodyStats(pricesMap: Map<string, {
        price: OraclePrice;
        emaPrice: OraclePrice;
    }>): CustodyStats[];
}
