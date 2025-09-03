import { PublicKey } from "@solana/web3.js";
import { Market, MarketPermissions, PositionStats, Side } from "./types";
import BN from "bn.js";
import { PositionAccount } from "./PositionAccount";
export declare class MarketAccount implements Market {
    publicKey: PublicKey;
    pool: PublicKey;
    targetCustody: PublicKey;
    collateralCustody: PublicKey;
    side: Side;
    correlation: boolean;
    maxPayoffBps: BN;
    permissions: MarketPermissions;
    openInterest: BN;
    collectivePosition: PositionStats;
    targetCustodyUid: number;
    padding: number[];
    collateralCustodyUid: number;
    padding2: number[];
    bump: number;
    constructor(publicKey: PublicKey, parseData: Market);
    static from(publicKey: PublicKey, parseData: Market): MarketAccount;
    updateMarketData(market: Market): void;
    getCollectivePosition(): PositionAccount;
}
