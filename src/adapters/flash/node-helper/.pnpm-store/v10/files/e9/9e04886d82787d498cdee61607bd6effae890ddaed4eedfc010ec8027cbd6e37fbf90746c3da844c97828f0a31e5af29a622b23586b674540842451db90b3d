import { BN } from "@coral-xyz/anchor";
import { ContractOraclePrice } from "./types";
export declare class OraclePrice {
    price: BN;
    exponent: BN;
    confidence: BN;
    timestamp: BN;
    constructor(parseData: {
        price: BN;
        exponent: BN;
        confidence: BN;
        timestamp?: BN;
    });
    static from(parseData: {
        price: BN;
        exponent: BN;
        confidence: BN;
        timestamp: BN;
    }): OraclePrice;
    toContractOraclePrice(): ContractOraclePrice;
    cmp(other: OraclePrice): -1 | 0 | 1;
    getDivergenceFactor(other: OraclePrice): BN;
    scale_to_exponent(target_exponent: BN): OraclePrice;
    getTokenAmount(asset_amount_usd: BN, token_decimals: number): BN;
    getAssetAmountUsd(token_amount: BN, token_decimals: number): BN;
    toUiPrice(precision: number): string;
}
