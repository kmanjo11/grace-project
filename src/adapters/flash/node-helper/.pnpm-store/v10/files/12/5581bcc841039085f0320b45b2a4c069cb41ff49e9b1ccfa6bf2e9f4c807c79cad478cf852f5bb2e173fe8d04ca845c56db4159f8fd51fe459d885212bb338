import { TokenStake, WithdrawStakeLog } from "./types";
import { BN } from "@coral-xyz/anchor";
import { PublicKey } from "@solana/web3.js";
export declare class TokenStakeAccount implements TokenStake {
    owner: PublicKey;
    isInitialized: boolean;
    bump: number;
    level: number;
    withdrawRequestCount: number;
    withdrawRequest: WithdrawStakeLog[] | any;
    activeStakeAmount: BN;
    updateTimestamp: BN;
    tradeTimestamp: BN;
    tradeCounter: number;
    lastRewardEpochCount: number;
    rewardTokens: BN;
    unclaimedRevenueAmount: BN;
    revenueSnapshot: BN;
    padding: BN[];
    constructor(data: {
        owner: PublicKey;
        isInitialized: boolean;
        bump: number;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: WithdrawStakeLog[];
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        padding: BN[];
    });
    static from(decodedData: any): TokenStakeAccount;
    updateData(newData: Partial<TokenStakeAccount>): void;
}
