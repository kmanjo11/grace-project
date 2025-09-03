import { Program, AnchorProvider, BN } from "@coral-xyz/anchor";
import { PublicKey, TransactionInstruction, Commitment, Signer, AddressLookupTableAccount, VersionedTransaction } from "@solana/web3.js";
import { PoolAccount } from "./PoolAccount";
import { PositionAccount } from "./PositionAccount";
import { AddLiquidityAmountAndFee, InternalPrice, BorrowRateParams, ExitPriceAndFee, Fees, OracleParams, Permissions, PricingParams, RemoveCollateralData, RemoveLiquidityAmountAndFee, Side, TokenRatios, MinAndMaxPrice, FeesAction, ContractOraclePrice, Privilege, PerpetualsAccount, Trading, EntryPriceAndFeeV2, EntryPriceAndFee, TokenPermissions, TokenStake, InternalEmaPrice } from "./types";
import { OraclePrice } from "./OraclePrice";
import { CustodyAccount } from "./CustodyAccount";
import { Perpetuals } from "./idl/perpetuals";
import { PerpComposability } from "./idl/perp_composability";
import { FbnftRewards } from "./idl/fbnft_rewards";
import { RewardDistribution } from "./idl/reward_distribution";
import { SendTransactionOpts } from "./utils/rpc";
import { MarketConfig, PoolConfig, Token } from "./PoolConfig";
import { MarketAccount } from "./MarketAccount";
export type PerpClientOptions = {
    postSendTxCallback?: ({ txid }: {
        txid: string;
    }) => void;
    prioritizationFee?: number;
    txConfirmationCommitment?: Commitment;
};
export declare class PerpetualsClient {
    provider: AnchorProvider;
    program: Program<Perpetuals>;
    programPerpComposability: Program<PerpComposability>;
    programFbnftReward: Program<FbnftRewards>;
    programRewardDistribution: Program<RewardDistribution>;
    admin: PublicKey;
    programId: PublicKey;
    composabilityProgramId: PublicKey;
    multisig: {
        publicKey: PublicKey;
        bump: number;
    };
    authority: {
        publicKey: PublicKey;
        bump: number;
    };
    perpetuals: {
        publicKey: PublicKey;
        bump: number;
    };
    addressLookupTables: AddressLookupTableAccount[];
    eventAuthority: {
        publicKey: PublicKey;
        bump: number;
    };
    eventAuthorityRewardDistribution: {
        publicKey: PublicKey;
        bump: number;
    };
    prioritizationFee: number;
    minimumBalanceForRentExemptAccountLamports: number;
    private postSendTxCallback?;
    private useExtOracleAccount;
    private txConfirmationCommitment;
    private viewHelper;
    constructor(provider: AnchorProvider, programId: PublicKey, composabilityProgramId: PublicKey, fbNftRewardProgramId: PublicKey, rewardDistributionProgramId: PublicKey, opts: PerpClientOptions, useExtOracleAccount?: boolean);
    setPrioritizationFee: (fee: number) => void;
    loadAddressLookupTable: (poolConfig: PoolConfig) => Promise<void>;
    findProgramAddress: (label: string, extraSeeds?: any) => {
        publicKey: PublicKey;
        bump: number;
    };
    findProgramAddressFromProgramId: (label: string, extraSeeds?: any, programId?: PublicKey) => {
        publicKey: PublicKey;
        bump: number;
    };
    adjustTokenRatios: (ratios: TokenRatios[]) => {
        target: BN;
        min: BN;
        max: BN;
    }[];
    getPerpetuals: () => Promise<{
        pool: PublicKey;
        mint: PublicKey;
        tokenAccount: PublicKey;
        decimals: number;
        isStable: boolean;
        depegAdjustment: boolean;
        isVirtual: boolean;
        distributeRewards: boolean;
        oracle: {
            intOracleAccount: PublicKey;
            extOracleAccount: PublicKey;
            oracleType: {
                none?: Record<string, never>;
                custom?: Record<string, never>;
                pyth?: Record<string, never>;
            };
            maxDivergenceBps: BN;
            maxConfBps: BN;
            maxPriceAgeSec: number;
            maxBackupAgeSec: number;
        };
        pricing: {
            tradeSpreadMin: BN;
            tradeSpreadMax: BN;
            swapSpread: BN;
            minInitialLeverage: BN;
            maxInitialLeverage: BN;
            maxLeverage: BN;
            minCollateralUsd: BN;
            delaySeconds: BN;
            maxUtilization: BN;
            maxPositionLockedUsd: BN;
            maxExposureUsd: BN;
        };
        permissions: {
            allowSwap: boolean;
            allowAddLiquidity: boolean;
            allowRemoveLiquidity: boolean;
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
            allowLiquidation: boolean;
            allowLpStaking: boolean;
            allowFeeDistribution: boolean;
            allowUngatedTrading: boolean;
            allowFeeDiscounts: boolean;
            allowReferralRebates: boolean;
        } | {
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
        };
        fees: {
            mode: {
                fixed?: Record<string, never>;
                linear?: Record<string, never>;
            };
            swapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            swapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            addLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            removeLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            openPosition: BN;
            closePosition: BN;
            volatility: BN;
        };
        borrowRate: {
            baseRate: BN;
            slope1: BN;
            slope2: BN;
            optimalUtilization: BN;
        };
        rewardThreshold: BN;
        assets: {
            collateral: BN;
            owned: BN;
            locked: BN;
        };
        feesStats: {
            accrued: BN;
            distributed: BN;
            paid: BN;
            rewardPerLpStaked: BN;
            protocolFee: BN;
        };
        borrowRateState: {
            currentRate: BN;
            cumulativeLockFee: BN;
            lastUpdate: BN;
        };
        bump: number;
        tokenAccountBump: number;
        token22: boolean;
        uid: number;
        reservedAmount: BN;
        minReserveUsd: BN;
        limitPriceBufferBps: BN;
        padding: number[] | number[] | BN[] | number[] | BN[] | number[] | number[] | BN[] | BN[];
        owner: PublicKey;
        stakeStats: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardSnapshot: BN;
        unclaimedRewards: BN;
        feeShareBps: BN;
        isInitialized: number | boolean;
        targetCustody: PublicKey;
        collateralCustody: PublicKey;
        side: {
            none?: Record<string, never>;
            long?: Record<string, never>;
            short?: Record<string, never>;
        };
        correlation: boolean;
        maxPayoffBps: BN;
        openInterest: BN;
        collectivePosition: {
            openPositions: BN;
            updateTime: BN;
            averageEntryPrice: {
                price: BN;
                exponent: number;
            };
            sizeAmount: BN;
            sizeUsd: BN;
            lockedAmount: BN;
            lockedUsd: BN;
            collateralAmount: BN;
            collateralUsd: BN;
            unsettledFeeUsd: BN;
            cumulativeLockFeeSnapshot: BN;
            sizeDecimals: number;
            lockedDecimals: number;
            collateralDecimals: number;
        };
        targetCustodyUid: number;
        collateralCustodyUid: number;
        padding2: number[] | BN[] | BN[];
        numSigners: number;
        numSigned: number;
        minSignatures: number;
        instructionAccountsLen: number;
        instructionDataLen: number;
        instructionHash: BN;
        signers: PublicKey[];
        signed: number[];
        price: BN;
        expo: number;
        conf: BN;
        ema: BN;
        publishTime: BN;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        pools: PublicKey[];
        collections: PublicKey[];
        voltageMultiplier: {
            volume: BN;
            rewards: BN;
            rebates: BN;
        };
        tradingDiscount: BN[];
        referralRebate: BN[];
        defaultRebate: BN;
        inceptionTime: BN;
        transferAuthorityBump: number;
        perpetualsBump: number;
        tradeLimit: number;
        rebateLimitUsd: number;
        name: string;
        lpMint: PublicKey;
        oracleAuthority: PublicKey;
        stakedLpVault: PublicKey;
        rewardCustody: PublicKey;
        custodies: PublicKey[];
        ratios: {
            target: BN;
            min: BN;
            max: BN;
        }[];
        markets: PublicKey[];
        maxAumUsd: BN;
        aumUsd: BN;
        totalStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        stakingFeeShareBps: BN;
        lpMintBump: number;
        stakedLpVaultBump: number;
        vpVolumeFactor: number;
        uniqueCustodyCount: number;
        stakingFeeBoostBps: BN[];
        compoundingMint: PublicKey;
        compoundingLpVault: PublicKey;
        compoundingStats: {
            activeAmount: BN;
            totalSupply: BN;
            rewardSnapshot: BN;
            feeShareBps: BN;
            lastCompoundTime: BN;
        };
        compoundingMintBump: number;
        compoundingLpVaultBump: number;
        minLpPriceUsd: BN;
        maxLpPriceUsd: BN;
        lpPrice: BN;
        compoundingLpPrice: BN;
        lastUpdatedTimestamp: BN;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        key: PublicKey;
        feeAmount: BN;
        refererTokenStakeAccount: PublicKey;
        refererBoosterAccount: PublicKey;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: unknown;
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        tokenMint: PublicKey;
        tokenVaultTokenAccount: PublicKey;
        tokenPermissions: {
            allowDeposits: boolean;
            allowWithdrawal: boolean;
            allowRewardWithdrawal: boolean;
        };
        withdrawTimeLimit: BN;
        withdrawInstantFee: BN;
        withdrawInstantFeeEarned: BN;
        stakeLevel: BN[];
        tokensStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardTokensToDistribute: BN;
        rewardTokensPaid: BN;
        tokensToDistribute: BN;
        tokensDistributed: BN;
        rewardTokensDistributed: BN;
        revenueTokenAccountBump: number;
        revenuePerFafStaked: BN;
        revenueAccrued: BN;
        revenueDistributed: BN;
        revenuePaid: BN;
        nftMint: PublicKey;
        voltagePoints: BN;
        stats: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        snapshot: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        timestamp: BN;
        counter: BN;
        tokenStakeAccount: PublicKey;
        burnt: boolean;
    }>;
    getPoolKey: (name: string) => PublicKey;
    getPool: (name: string) => Promise<{
        pool: PublicKey;
        mint: PublicKey;
        tokenAccount: PublicKey;
        decimals: number;
        isStable: boolean;
        depegAdjustment: boolean;
        isVirtual: boolean;
        distributeRewards: boolean;
        oracle: {
            intOracleAccount: PublicKey;
            extOracleAccount: PublicKey;
            oracleType: {
                none?: Record<string, never>;
                custom?: Record<string, never>;
                pyth?: Record<string, never>;
            };
            maxDivergenceBps: BN;
            maxConfBps: BN;
            maxPriceAgeSec: number;
            maxBackupAgeSec: number;
        };
        pricing: {
            tradeSpreadMin: BN;
            tradeSpreadMax: BN;
            swapSpread: BN;
            minInitialLeverage: BN;
            maxInitialLeverage: BN;
            maxLeverage: BN;
            minCollateralUsd: BN;
            delaySeconds: BN;
            maxUtilization: BN;
            maxPositionLockedUsd: BN;
            maxExposureUsd: BN;
        };
        permissions: {
            allowSwap: boolean;
            allowAddLiquidity: boolean;
            allowRemoveLiquidity: boolean;
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
            allowLiquidation: boolean;
            allowLpStaking: boolean;
            allowFeeDistribution: boolean;
            allowUngatedTrading: boolean;
            allowFeeDiscounts: boolean;
            allowReferralRebates: boolean;
        } | {
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
        };
        fees: {
            mode: {
                fixed?: Record<string, never>;
                linear?: Record<string, never>;
            };
            swapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            swapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            addLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            removeLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            openPosition: BN;
            closePosition: BN;
            volatility: BN;
        };
        borrowRate: {
            baseRate: BN;
            slope1: BN;
            slope2: BN;
            optimalUtilization: BN;
        };
        rewardThreshold: BN;
        assets: {
            collateral: BN;
            owned: BN;
            locked: BN;
        };
        feesStats: {
            accrued: BN;
            distributed: BN;
            paid: BN;
            rewardPerLpStaked: BN;
            protocolFee: BN;
        };
        borrowRateState: {
            currentRate: BN;
            cumulativeLockFee: BN;
            lastUpdate: BN;
        };
        bump: number;
        tokenAccountBump: number;
        token22: boolean;
        uid: number;
        reservedAmount: BN;
        minReserveUsd: BN;
        limitPriceBufferBps: BN;
        padding: number[] | number[] | BN[] | number[] | BN[] | number[] | number[] | BN[] | BN[];
        owner: PublicKey;
        stakeStats: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardSnapshot: BN;
        unclaimedRewards: BN;
        feeShareBps: BN;
        isInitialized: number | boolean;
        targetCustody: PublicKey;
        collateralCustody: PublicKey;
        side: {
            none?: Record<string, never>;
            long?: Record<string, never>;
            short?: Record<string, never>;
        };
        correlation: boolean;
        maxPayoffBps: BN;
        openInterest: BN;
        collectivePosition: {
            openPositions: BN;
            updateTime: BN;
            averageEntryPrice: {
                price: BN;
                exponent: number;
            };
            sizeAmount: BN;
            sizeUsd: BN;
            lockedAmount: BN;
            lockedUsd: BN;
            collateralAmount: BN;
            collateralUsd: BN;
            unsettledFeeUsd: BN;
            cumulativeLockFeeSnapshot: BN;
            sizeDecimals: number;
            lockedDecimals: number;
            collateralDecimals: number;
        };
        targetCustodyUid: number;
        collateralCustodyUid: number;
        padding2: number[] | BN[] | BN[];
        numSigners: number;
        numSigned: number;
        minSignatures: number;
        instructionAccountsLen: number;
        instructionDataLen: number;
        instructionHash: BN;
        signers: PublicKey[];
        signed: number[];
        price: BN;
        expo: number;
        conf: BN;
        ema: BN;
        publishTime: BN;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        pools: PublicKey[];
        collections: PublicKey[];
        voltageMultiplier: {
            volume: BN;
            rewards: BN;
            rebates: BN;
        };
        tradingDiscount: BN[];
        referralRebate: BN[];
        defaultRebate: BN;
        inceptionTime: BN;
        transferAuthorityBump: number;
        perpetualsBump: number;
        tradeLimit: number;
        rebateLimitUsd: number;
        name: string;
        lpMint: PublicKey;
        oracleAuthority: PublicKey;
        stakedLpVault: PublicKey;
        rewardCustody: PublicKey;
        custodies: PublicKey[];
        ratios: {
            target: BN;
            min: BN;
            max: BN;
        }[];
        markets: PublicKey[];
        maxAumUsd: BN;
        aumUsd: BN;
        totalStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        stakingFeeShareBps: BN;
        lpMintBump: number;
        stakedLpVaultBump: number;
        vpVolumeFactor: number;
        uniqueCustodyCount: number;
        stakingFeeBoostBps: BN[];
        compoundingMint: PublicKey;
        compoundingLpVault: PublicKey;
        compoundingStats: {
            activeAmount: BN;
            totalSupply: BN;
            rewardSnapshot: BN;
            feeShareBps: BN;
            lastCompoundTime: BN;
        };
        compoundingMintBump: number;
        compoundingLpVaultBump: number;
        minLpPriceUsd: BN;
        maxLpPriceUsd: BN;
        lpPrice: BN;
        compoundingLpPrice: BN;
        lastUpdatedTimestamp: BN;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        key: PublicKey;
        feeAmount: BN;
        refererTokenStakeAccount: PublicKey;
        refererBoosterAccount: PublicKey;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: unknown;
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        tokenMint: PublicKey;
        tokenVaultTokenAccount: PublicKey;
        tokenPermissions: {
            allowDeposits: boolean;
            allowWithdrawal: boolean;
            allowRewardWithdrawal: boolean;
        };
        withdrawTimeLimit: BN;
        withdrawInstantFee: BN;
        withdrawInstantFeeEarned: BN;
        stakeLevel: BN[];
        tokensStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardTokensToDistribute: BN;
        rewardTokensPaid: BN;
        tokensToDistribute: BN;
        tokensDistributed: BN;
        rewardTokensDistributed: BN;
        revenueTokenAccountBump: number;
        revenuePerFafStaked: BN;
        revenueAccrued: BN;
        revenueDistributed: BN;
        revenuePaid: BN;
        nftMint: PublicKey;
        voltagePoints: BN;
        stats: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        snapshot: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        timestamp: BN;
        counter: BN;
        tokenStakeAccount: PublicKey;
        burnt: boolean;
    }>;
    getPools: () => Promise<{
        pool: PublicKey;
        mint: PublicKey;
        tokenAccount: PublicKey;
        decimals: number;
        isStable: boolean;
        depegAdjustment: boolean;
        isVirtual: boolean;
        distributeRewards: boolean;
        oracle: {
            intOracleAccount: PublicKey;
            extOracleAccount: PublicKey;
            oracleType: {
                none?: Record<string, never>;
                custom?: Record<string, never>;
                pyth?: Record<string, never>;
            };
            maxDivergenceBps: BN;
            maxConfBps: BN;
            maxPriceAgeSec: number;
            maxBackupAgeSec: number;
        };
        pricing: {
            tradeSpreadMin: BN;
            tradeSpreadMax: BN;
            swapSpread: BN;
            minInitialLeverage: BN;
            maxInitialLeverage: BN;
            maxLeverage: BN;
            minCollateralUsd: BN;
            delaySeconds: BN;
            maxUtilization: BN;
            maxPositionLockedUsd: BN;
            maxExposureUsd: BN;
        };
        permissions: {
            allowSwap: boolean;
            allowAddLiquidity: boolean;
            allowRemoveLiquidity: boolean;
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
            allowLiquidation: boolean;
            allowLpStaking: boolean;
            allowFeeDistribution: boolean;
            allowUngatedTrading: boolean;
            allowFeeDiscounts: boolean;
            allowReferralRebates: boolean;
        } | {
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
        };
        fees: {
            mode: {
                fixed?: Record<string, never>;
                linear?: Record<string, never>;
            };
            swapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            swapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            addLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            removeLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            openPosition: BN;
            closePosition: BN;
            volatility: BN;
        };
        borrowRate: {
            baseRate: BN;
            slope1: BN;
            slope2: BN;
            optimalUtilization: BN;
        };
        rewardThreshold: BN;
        assets: {
            collateral: BN;
            owned: BN;
            locked: BN;
        };
        feesStats: {
            accrued: BN;
            distributed: BN;
            paid: BN;
            rewardPerLpStaked: BN;
            protocolFee: BN;
        };
        borrowRateState: {
            currentRate: BN;
            cumulativeLockFee: BN;
            lastUpdate: BN;
        };
        bump: number;
        tokenAccountBump: number;
        token22: boolean;
        uid: number;
        reservedAmount: BN;
        minReserveUsd: BN;
        limitPriceBufferBps: BN;
        padding: number[] | number[] | BN[] | number[] | BN[] | number[] | number[] | BN[] | BN[];
        owner: PublicKey;
        stakeStats: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardSnapshot: BN;
        unclaimedRewards: BN;
        feeShareBps: BN;
        isInitialized: number | boolean;
        targetCustody: PublicKey;
        collateralCustody: PublicKey;
        side: {
            none?: Record<string, never>;
            long?: Record<string, never>;
            short?: Record<string, never>;
        };
        correlation: boolean;
        maxPayoffBps: BN;
        openInterest: BN;
        collectivePosition: {
            openPositions: BN;
            updateTime: BN;
            averageEntryPrice: {
                price: BN;
                exponent: number;
            };
            sizeAmount: BN;
            sizeUsd: BN;
            lockedAmount: BN;
            lockedUsd: BN;
            collateralAmount: BN;
            collateralUsd: BN;
            unsettledFeeUsd: BN;
            cumulativeLockFeeSnapshot: BN;
            sizeDecimals: number;
            lockedDecimals: number;
            collateralDecimals: number;
        };
        targetCustodyUid: number;
        collateralCustodyUid: number;
        padding2: number[] | BN[] | BN[];
        numSigners: number;
        numSigned: number;
        minSignatures: number;
        instructionAccountsLen: number;
        instructionDataLen: number;
        instructionHash: BN;
        signers: PublicKey[];
        signed: number[];
        price: BN;
        expo: number;
        conf: BN;
        ema: BN;
        publishTime: BN;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        pools: PublicKey[];
        collections: PublicKey[];
        voltageMultiplier: {
            volume: BN;
            rewards: BN;
            rebates: BN;
        };
        tradingDiscount: BN[];
        referralRebate: BN[];
        defaultRebate: BN;
        inceptionTime: BN;
        transferAuthorityBump: number;
        perpetualsBump: number;
        tradeLimit: number;
        rebateLimitUsd: number;
        name: string;
        lpMint: PublicKey;
        oracleAuthority: PublicKey;
        stakedLpVault: PublicKey;
        rewardCustody: PublicKey;
        custodies: PublicKey[];
        ratios: {
            target: BN;
            min: BN;
            max: BN;
        }[];
        markets: PublicKey[];
        maxAumUsd: BN;
        aumUsd: BN;
        totalStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        stakingFeeShareBps: BN;
        lpMintBump: number;
        stakedLpVaultBump: number;
        vpVolumeFactor: number;
        uniqueCustodyCount: number;
        stakingFeeBoostBps: BN[];
        compoundingMint: PublicKey;
        compoundingLpVault: PublicKey;
        compoundingStats: {
            activeAmount: BN;
            totalSupply: BN;
            rewardSnapshot: BN;
            feeShareBps: BN;
            lastCompoundTime: BN;
        };
        compoundingMintBump: number;
        compoundingLpVaultBump: number;
        minLpPriceUsd: BN;
        maxLpPriceUsd: BN;
        lpPrice: BN;
        compoundingLpPrice: BN;
        lastUpdatedTimestamp: BN;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        key: PublicKey;
        feeAmount: BN;
        refererTokenStakeAccount: PublicKey;
        refererBoosterAccount: PublicKey;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: unknown;
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        tokenMint: PublicKey;
        tokenVaultTokenAccount: PublicKey;
        tokenPermissions: {
            allowDeposits: boolean;
            allowWithdrawal: boolean;
            allowRewardWithdrawal: boolean;
        };
        withdrawTimeLimit: BN;
        withdrawInstantFee: BN;
        withdrawInstantFeeEarned: BN;
        stakeLevel: BN[];
        tokensStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardTokensToDistribute: BN;
        rewardTokensPaid: BN;
        tokensToDistribute: BN;
        tokensDistributed: BN;
        rewardTokensDistributed: BN;
        revenueTokenAccountBump: number;
        revenuePerFafStaked: BN;
        revenueAccrued: BN;
        revenueDistributed: BN;
        revenuePaid: BN;
        nftMint: PublicKey;
        voltagePoints: BN;
        stats: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        snapshot: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        timestamp: BN;
        counter: BN;
        tokenStakeAccount: PublicKey;
        burnt: boolean;
    }[]>;
    getPoolLpTokenKey: (name: string) => PublicKey;
    getPoolCompoundingTokenKey: (name: string) => PublicKey;
    getCustodyKey: (poolName: string, tokenMint: PublicKey) => PublicKey;
    getCustodyTokenAccountKey: (poolName: string, tokenMint: PublicKey) => PublicKey;
    getTradingAccount: (tradingAccount: PublicKey) => Promise<{
        pool: PublicKey;
        mint: PublicKey;
        tokenAccount: PublicKey;
        decimals: number;
        isStable: boolean;
        depegAdjustment: boolean;
        isVirtual: boolean;
        distributeRewards: boolean;
        oracle: {
            intOracleAccount: PublicKey;
            extOracleAccount: PublicKey;
            oracleType: {
                none?: Record<string, never>;
                custom?: Record<string, never>;
                pyth?: Record<string, never>;
            };
            maxDivergenceBps: BN;
            maxConfBps: BN;
            maxPriceAgeSec: number;
            maxBackupAgeSec: number;
        };
        pricing: {
            tradeSpreadMin: BN;
            tradeSpreadMax: BN;
            swapSpread: BN;
            minInitialLeverage: BN;
            maxInitialLeverage: BN;
            maxLeverage: BN;
            minCollateralUsd: BN;
            delaySeconds: BN;
            maxUtilization: BN;
            maxPositionLockedUsd: BN;
            maxExposureUsd: BN;
        };
        permissions: {
            allowSwap: boolean;
            allowAddLiquidity: boolean;
            allowRemoveLiquidity: boolean;
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
            allowLiquidation: boolean;
            allowLpStaking: boolean;
            allowFeeDistribution: boolean;
            allowUngatedTrading: boolean;
            allowFeeDiscounts: boolean;
            allowReferralRebates: boolean;
        } | {
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
        };
        fees: {
            mode: {
                fixed?: Record<string, never>;
                linear?: Record<string, never>;
            };
            swapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            swapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            addLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            removeLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            openPosition: BN;
            closePosition: BN;
            volatility: BN;
        };
        borrowRate: {
            baseRate: BN;
            slope1: BN;
            slope2: BN;
            optimalUtilization: BN;
        };
        rewardThreshold: BN;
        assets: {
            collateral: BN;
            owned: BN;
            locked: BN;
        };
        feesStats: {
            accrued: BN;
            distributed: BN;
            paid: BN;
            rewardPerLpStaked: BN;
            protocolFee: BN;
        };
        borrowRateState: {
            currentRate: BN;
            cumulativeLockFee: BN;
            lastUpdate: BN;
        };
        bump: number;
        tokenAccountBump: number;
        token22: boolean;
        uid: number;
        reservedAmount: BN;
        minReserveUsd: BN;
        limitPriceBufferBps: BN;
        padding: number[] | number[] | BN[] | number[] | BN[] | number[] | number[] | BN[] | BN[];
        owner: PublicKey;
        stakeStats: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardSnapshot: BN;
        unclaimedRewards: BN;
        feeShareBps: BN;
        isInitialized: number | boolean;
        targetCustody: PublicKey;
        collateralCustody: PublicKey;
        side: {
            none?: Record<string, never>;
            long?: Record<string, never>;
            short?: Record<string, never>;
        };
        correlation: boolean;
        maxPayoffBps: BN;
        openInterest: BN;
        collectivePosition: {
            openPositions: BN;
            updateTime: BN;
            averageEntryPrice: {
                price: BN;
                exponent: number;
            };
            sizeAmount: BN;
            sizeUsd: BN;
            lockedAmount: BN;
            lockedUsd: BN;
            collateralAmount: BN;
            collateralUsd: BN;
            unsettledFeeUsd: BN;
            cumulativeLockFeeSnapshot: BN;
            sizeDecimals: number;
            lockedDecimals: number;
            collateralDecimals: number;
        };
        targetCustodyUid: number;
        collateralCustodyUid: number;
        padding2: number[] | BN[] | BN[];
        numSigners: number;
        numSigned: number;
        minSignatures: number;
        instructionAccountsLen: number;
        instructionDataLen: number;
        instructionHash: BN;
        signers: PublicKey[];
        signed: number[];
        price: BN;
        expo: number;
        conf: BN;
        ema: BN;
        publishTime: BN;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        pools: PublicKey[];
        collections: PublicKey[];
        voltageMultiplier: {
            volume: BN;
            rewards: BN;
            rebates: BN;
        };
        tradingDiscount: BN[];
        referralRebate: BN[];
        defaultRebate: BN;
        inceptionTime: BN;
        transferAuthorityBump: number;
        perpetualsBump: number;
        tradeLimit: number;
        rebateLimitUsd: number;
        name: string;
        lpMint: PublicKey;
        oracleAuthority: PublicKey;
        stakedLpVault: PublicKey;
        rewardCustody: PublicKey;
        custodies: PublicKey[];
        ratios: {
            target: BN;
            min: BN;
            max: BN;
        }[];
        markets: PublicKey[];
        maxAumUsd: BN;
        aumUsd: BN;
        totalStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        stakingFeeShareBps: BN;
        lpMintBump: number;
        stakedLpVaultBump: number;
        vpVolumeFactor: number;
        uniqueCustodyCount: number;
        stakingFeeBoostBps: BN[];
        compoundingMint: PublicKey;
        compoundingLpVault: PublicKey;
        compoundingStats: {
            activeAmount: BN;
            totalSupply: BN;
            rewardSnapshot: BN;
            feeShareBps: BN;
            lastCompoundTime: BN;
        };
        compoundingMintBump: number;
        compoundingLpVaultBump: number;
        minLpPriceUsd: BN;
        maxLpPriceUsd: BN;
        lpPrice: BN;
        compoundingLpPrice: BN;
        lastUpdatedTimestamp: BN;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        key: PublicKey;
        feeAmount: BN;
        refererTokenStakeAccount: PublicKey;
        refererBoosterAccount: PublicKey;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: unknown;
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        tokenMint: PublicKey;
        tokenVaultTokenAccount: PublicKey;
        tokenPermissions: {
            allowDeposits: boolean;
            allowWithdrawal: boolean;
            allowRewardWithdrawal: boolean;
        };
        withdrawTimeLimit: BN;
        withdrawInstantFee: BN;
        withdrawInstantFeeEarned: BN;
        stakeLevel: BN[];
        tokensStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardTokensToDistribute: BN;
        rewardTokensPaid: BN;
        tokensToDistribute: BN;
        tokensDistributed: BN;
        rewardTokensDistributed: BN;
        revenueTokenAccountBump: number;
        revenuePerFafStaked: BN;
        revenueAccrued: BN;
        revenueDistributed: BN;
        revenuePaid: BN;
        nftMint: PublicKey;
        voltagePoints: BN;
        stats: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        snapshot: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        timestamp: BN;
        counter: BN;
        tokenStakeAccount: PublicKey;
        burnt: boolean;
    }>;
    getMarketPk(targetCustody: PublicKey, collateralCustody: PublicKey, side: Side): PublicKey;
    getPositionKey(owner: PublicKey, targetCustody: PublicKey, collateralCustody: PublicKey, side: Side): PublicKey;
    getOrderAccountKey(owner: PublicKey, targetCustody: PublicKey, collateralCustody: PublicKey, side: Side): PublicKey;
    getPosition: (postionKey: PublicKey) => Promise<{
        pool: PublicKey;
        mint: PublicKey;
        tokenAccount: PublicKey;
        decimals: number;
        isStable: boolean;
        depegAdjustment: boolean;
        isVirtual: boolean;
        distributeRewards: boolean;
        oracle: {
            intOracleAccount: PublicKey;
            extOracleAccount: PublicKey;
            oracleType: {
                none?: Record<string, never>;
                custom?: Record<string, never>;
                pyth?: Record<string, never>;
            };
            maxDivergenceBps: BN;
            maxConfBps: BN;
            maxPriceAgeSec: number;
            maxBackupAgeSec: number;
        };
        pricing: {
            tradeSpreadMin: BN;
            tradeSpreadMax: BN;
            swapSpread: BN;
            minInitialLeverage: BN;
            maxInitialLeverage: BN;
            maxLeverage: BN;
            minCollateralUsd: BN;
            delaySeconds: BN;
            maxUtilization: BN;
            maxPositionLockedUsd: BN;
            maxExposureUsd: BN;
        };
        permissions: {
            allowSwap: boolean;
            allowAddLiquidity: boolean;
            allowRemoveLiquidity: boolean;
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
            allowLiquidation: boolean;
            allowLpStaking: boolean;
            allowFeeDistribution: boolean;
            allowUngatedTrading: boolean;
            allowFeeDiscounts: boolean;
            allowReferralRebates: boolean;
        } | {
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
        };
        fees: {
            mode: {
                fixed?: Record<string, never>;
                linear?: Record<string, never>;
            };
            swapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            swapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            addLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            removeLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            openPosition: BN;
            closePosition: BN;
            volatility: BN;
        };
        borrowRate: {
            baseRate: BN;
            slope1: BN;
            slope2: BN;
            optimalUtilization: BN;
        };
        rewardThreshold: BN;
        assets: {
            collateral: BN;
            owned: BN;
            locked: BN;
        };
        feesStats: {
            accrued: BN;
            distributed: BN;
            paid: BN;
            rewardPerLpStaked: BN;
            protocolFee: BN;
        };
        borrowRateState: {
            currentRate: BN;
            cumulativeLockFee: BN;
            lastUpdate: BN;
        };
        bump: number;
        tokenAccountBump: number;
        token22: boolean;
        uid: number;
        reservedAmount: BN;
        minReserveUsd: BN;
        limitPriceBufferBps: BN;
        padding: number[] | number[] | BN[] | number[] | BN[] | number[] | number[] | BN[] | BN[];
        owner: PublicKey;
        stakeStats: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardSnapshot: BN;
        unclaimedRewards: BN;
        feeShareBps: BN;
        isInitialized: number | boolean;
        targetCustody: PublicKey;
        collateralCustody: PublicKey;
        side: {
            none?: Record<string, never>;
            long?: Record<string, never>;
            short?: Record<string, never>;
        };
        correlation: boolean;
        maxPayoffBps: BN;
        openInterest: BN;
        collectivePosition: {
            openPositions: BN;
            updateTime: BN;
            averageEntryPrice: {
                price: BN;
                exponent: number;
            };
            sizeAmount: BN;
            sizeUsd: BN;
            lockedAmount: BN;
            lockedUsd: BN;
            collateralAmount: BN;
            collateralUsd: BN;
            unsettledFeeUsd: BN;
            cumulativeLockFeeSnapshot: BN;
            sizeDecimals: number;
            lockedDecimals: number;
            collateralDecimals: number;
        };
        targetCustodyUid: number;
        collateralCustodyUid: number;
        padding2: number[] | BN[] | BN[];
        numSigners: number;
        numSigned: number;
        minSignatures: number;
        instructionAccountsLen: number;
        instructionDataLen: number;
        instructionHash: BN;
        signers: PublicKey[];
        signed: number[];
        price: BN;
        expo: number;
        conf: BN;
        ema: BN;
        publishTime: BN;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        pools: PublicKey[];
        collections: PublicKey[];
        voltageMultiplier: {
            volume: BN;
            rewards: BN;
            rebates: BN;
        };
        tradingDiscount: BN[];
        referralRebate: BN[];
        defaultRebate: BN;
        inceptionTime: BN;
        transferAuthorityBump: number;
        perpetualsBump: number;
        tradeLimit: number;
        rebateLimitUsd: number;
        name: string;
        lpMint: PublicKey;
        oracleAuthority: PublicKey;
        stakedLpVault: PublicKey;
        rewardCustody: PublicKey;
        custodies: PublicKey[];
        ratios: {
            target: BN;
            min: BN;
            max: BN;
        }[];
        markets: PublicKey[];
        maxAumUsd: BN;
        aumUsd: BN;
        totalStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        stakingFeeShareBps: BN;
        lpMintBump: number;
        stakedLpVaultBump: number;
        vpVolumeFactor: number;
        uniqueCustodyCount: number;
        stakingFeeBoostBps: BN[];
        compoundingMint: PublicKey;
        compoundingLpVault: PublicKey;
        compoundingStats: {
            activeAmount: BN;
            totalSupply: BN;
            rewardSnapshot: BN;
            feeShareBps: BN;
            lastCompoundTime: BN;
        };
        compoundingMintBump: number;
        compoundingLpVaultBump: number;
        minLpPriceUsd: BN;
        maxLpPriceUsd: BN;
        lpPrice: BN;
        compoundingLpPrice: BN;
        lastUpdatedTimestamp: BN;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        key: PublicKey;
        feeAmount: BN;
        refererTokenStakeAccount: PublicKey;
        refererBoosterAccount: PublicKey;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: unknown;
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        tokenMint: PublicKey;
        tokenVaultTokenAccount: PublicKey;
        tokenPermissions: {
            allowDeposits: boolean;
            allowWithdrawal: boolean;
            allowRewardWithdrawal: boolean;
        };
        withdrawTimeLimit: BN;
        withdrawInstantFee: BN;
        withdrawInstantFeeEarned: BN;
        stakeLevel: BN[];
        tokensStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardTokensToDistribute: BN;
        rewardTokensPaid: BN;
        tokensToDistribute: BN;
        tokensDistributed: BN;
        rewardTokensDistributed: BN;
        revenueTokenAccountBump: number;
        revenuePerFafStaked: BN;
        revenueAccrued: BN;
        revenueDistributed: BN;
        revenuePaid: BN;
        nftMint: PublicKey;
        voltagePoints: BN;
        stats: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        snapshot: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        timestamp: BN;
        counter: BN;
        tokenStakeAccount: PublicKey;
        burnt: boolean;
    }>;
    getPositionData: (position: PositionAccount, poolConfig: PoolConfig) => Promise<any>;
    getOrderAccount: (orderAccountKey: PublicKey) => Promise<{
        pool: PublicKey;
        mint: PublicKey;
        tokenAccount: PublicKey;
        decimals: number;
        isStable: boolean;
        depegAdjustment: boolean;
        isVirtual: boolean;
        distributeRewards: boolean;
        oracle: {
            intOracleAccount: PublicKey;
            extOracleAccount: PublicKey;
            oracleType: {
                none?: Record<string, never>;
                custom?: Record<string, never>;
                pyth?: Record<string, never>;
            };
            maxDivergenceBps: BN;
            maxConfBps: BN;
            maxPriceAgeSec: number;
            maxBackupAgeSec: number;
        };
        pricing: {
            tradeSpreadMin: BN;
            tradeSpreadMax: BN;
            swapSpread: BN;
            minInitialLeverage: BN;
            maxInitialLeverage: BN;
            maxLeverage: BN;
            minCollateralUsd: BN;
            delaySeconds: BN;
            maxUtilization: BN;
            maxPositionLockedUsd: BN;
            maxExposureUsd: BN;
        };
        permissions: {
            allowSwap: boolean;
            allowAddLiquidity: boolean;
            allowRemoveLiquidity: boolean;
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
            allowLiquidation: boolean;
            allowLpStaking: boolean;
            allowFeeDistribution: boolean;
            allowUngatedTrading: boolean;
            allowFeeDiscounts: boolean;
            allowReferralRebates: boolean;
        } | {
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
        };
        fees: {
            mode: {
                fixed?: Record<string, never>;
                linear?: Record<string, never>;
            };
            swapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            swapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            addLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            removeLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            openPosition: BN;
            closePosition: BN;
            volatility: BN;
        };
        borrowRate: {
            baseRate: BN;
            slope1: BN;
            slope2: BN;
            optimalUtilization: BN;
        };
        rewardThreshold: BN;
        assets: {
            collateral: BN;
            owned: BN;
            locked: BN;
        };
        feesStats: {
            accrued: BN;
            distributed: BN;
            paid: BN;
            rewardPerLpStaked: BN;
            protocolFee: BN;
        };
        borrowRateState: {
            currentRate: BN;
            cumulativeLockFee: BN;
            lastUpdate: BN;
        };
        bump: number;
        tokenAccountBump: number;
        token22: boolean;
        uid: number;
        reservedAmount: BN;
        minReserveUsd: BN;
        limitPriceBufferBps: BN;
        padding: number[] | number[] | BN[] | number[] | BN[] | number[] | number[] | BN[] | BN[];
        owner: PublicKey;
        stakeStats: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardSnapshot: BN;
        unclaimedRewards: BN;
        feeShareBps: BN;
        isInitialized: number | boolean;
        targetCustody: PublicKey;
        collateralCustody: PublicKey;
        side: {
            none?: Record<string, never>;
            long?: Record<string, never>;
            short?: Record<string, never>;
        };
        correlation: boolean;
        maxPayoffBps: BN;
        openInterest: BN;
        collectivePosition: {
            openPositions: BN;
            updateTime: BN;
            averageEntryPrice: {
                price: BN;
                exponent: number;
            };
            sizeAmount: BN;
            sizeUsd: BN;
            lockedAmount: BN;
            lockedUsd: BN;
            collateralAmount: BN;
            collateralUsd: BN;
            unsettledFeeUsd: BN;
            cumulativeLockFeeSnapshot: BN;
            sizeDecimals: number;
            lockedDecimals: number;
            collateralDecimals: number;
        };
        targetCustodyUid: number;
        collateralCustodyUid: number;
        padding2: number[] | BN[] | BN[];
        numSigners: number;
        numSigned: number;
        minSignatures: number;
        instructionAccountsLen: number;
        instructionDataLen: number;
        instructionHash: BN;
        signers: PublicKey[];
        signed: number[];
        price: BN;
        expo: number;
        conf: BN;
        ema: BN;
        publishTime: BN;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        pools: PublicKey[];
        collections: PublicKey[];
        voltageMultiplier: {
            volume: BN;
            rewards: BN;
            rebates: BN;
        };
        tradingDiscount: BN[];
        referralRebate: BN[];
        defaultRebate: BN;
        inceptionTime: BN;
        transferAuthorityBump: number;
        perpetualsBump: number;
        tradeLimit: number;
        rebateLimitUsd: number;
        name: string;
        lpMint: PublicKey;
        oracleAuthority: PublicKey;
        stakedLpVault: PublicKey;
        rewardCustody: PublicKey;
        custodies: PublicKey[];
        ratios: {
            target: BN;
            min: BN;
            max: BN;
        }[];
        markets: PublicKey[];
        maxAumUsd: BN;
        aumUsd: BN;
        totalStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        stakingFeeShareBps: BN;
        lpMintBump: number;
        stakedLpVaultBump: number;
        vpVolumeFactor: number;
        uniqueCustodyCount: number;
        stakingFeeBoostBps: BN[];
        compoundingMint: PublicKey;
        compoundingLpVault: PublicKey;
        compoundingStats: {
            activeAmount: BN;
            totalSupply: BN;
            rewardSnapshot: BN;
            feeShareBps: BN;
            lastCompoundTime: BN;
        };
        compoundingMintBump: number;
        compoundingLpVaultBump: number;
        minLpPriceUsd: BN;
        maxLpPriceUsd: BN;
        lpPrice: BN;
        compoundingLpPrice: BN;
        lastUpdatedTimestamp: BN;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        key: PublicKey;
        feeAmount: BN;
        refererTokenStakeAccount: PublicKey;
        refererBoosterAccount: PublicKey;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: unknown;
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        tokenMint: PublicKey;
        tokenVaultTokenAccount: PublicKey;
        tokenPermissions: {
            allowDeposits: boolean;
            allowWithdrawal: boolean;
            allowRewardWithdrawal: boolean;
        };
        withdrawTimeLimit: BN;
        withdrawInstantFee: BN;
        withdrawInstantFeeEarned: BN;
        stakeLevel: BN[];
        tokensStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardTokensToDistribute: BN;
        rewardTokensPaid: BN;
        tokensToDistribute: BN;
        tokensDistributed: BN;
        rewardTokensDistributed: BN;
        revenueTokenAccountBump: number;
        revenuePerFafStaked: BN;
        revenueAccrued: BN;
        revenueDistributed: BN;
        revenuePaid: BN;
        nftMint: PublicKey;
        voltagePoints: BN;
        stats: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        snapshot: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        timestamp: BN;
        counter: BN;
        tokenStakeAccount: PublicKey;
        burnt: boolean;
    }>;
    getUserPosition: (owner: PublicKey, targetCustody: PublicKey, collateralCustody: PublicKey, side: Side) => Promise<{
        pool: PublicKey;
        mint: PublicKey;
        tokenAccount: PublicKey;
        decimals: number;
        isStable: boolean;
        depegAdjustment: boolean;
        isVirtual: boolean;
        distributeRewards: boolean;
        oracle: {
            intOracleAccount: PublicKey;
            extOracleAccount: PublicKey;
            oracleType: {
                none?: Record<string, never>;
                custom?: Record<string, never>;
                pyth?: Record<string, never>;
            };
            maxDivergenceBps: BN;
            maxConfBps: BN;
            maxPriceAgeSec: number;
            maxBackupAgeSec: number;
        };
        pricing: {
            tradeSpreadMin: BN;
            tradeSpreadMax: BN;
            swapSpread: BN;
            minInitialLeverage: BN;
            maxInitialLeverage: BN;
            maxLeverage: BN;
            minCollateralUsd: BN;
            delaySeconds: BN;
            maxUtilization: BN;
            maxPositionLockedUsd: BN;
            maxExposureUsd: BN;
        };
        permissions: {
            allowSwap: boolean;
            allowAddLiquidity: boolean;
            allowRemoveLiquidity: boolean;
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
            allowLiquidation: boolean;
            allowLpStaking: boolean;
            allowFeeDistribution: boolean;
            allowUngatedTrading: boolean;
            allowFeeDiscounts: boolean;
            allowReferralRebates: boolean;
        } | {
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
        };
        fees: {
            mode: {
                fixed?: Record<string, never>;
                linear?: Record<string, never>;
            };
            swapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            swapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            addLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            removeLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            openPosition: BN;
            closePosition: BN;
            volatility: BN;
        };
        borrowRate: {
            baseRate: BN;
            slope1: BN;
            slope2: BN;
            optimalUtilization: BN;
        };
        rewardThreshold: BN;
        assets: {
            collateral: BN;
            owned: BN;
            locked: BN;
        };
        feesStats: {
            accrued: BN;
            distributed: BN;
            paid: BN;
            rewardPerLpStaked: BN;
            protocolFee: BN;
        };
        borrowRateState: {
            currentRate: BN;
            cumulativeLockFee: BN;
            lastUpdate: BN;
        };
        bump: number;
        tokenAccountBump: number;
        token22: boolean;
        uid: number;
        reservedAmount: BN;
        minReserveUsd: BN;
        limitPriceBufferBps: BN;
        padding: number[] | number[] | BN[] | number[] | BN[] | number[] | number[] | BN[] | BN[];
        owner: PublicKey;
        stakeStats: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardSnapshot: BN;
        unclaimedRewards: BN;
        feeShareBps: BN;
        isInitialized: number | boolean;
        targetCustody: PublicKey;
        collateralCustody: PublicKey;
        side: {
            none?: Record<string, never>;
            long?: Record<string, never>;
            short?: Record<string, never>;
        };
        correlation: boolean;
        maxPayoffBps: BN;
        openInterest: BN;
        collectivePosition: {
            openPositions: BN;
            updateTime: BN;
            averageEntryPrice: {
                price: BN;
                exponent: number;
            };
            sizeAmount: BN;
            sizeUsd: BN;
            lockedAmount: BN;
            lockedUsd: BN;
            collateralAmount: BN;
            collateralUsd: BN;
            unsettledFeeUsd: BN;
            cumulativeLockFeeSnapshot: BN;
            sizeDecimals: number;
            lockedDecimals: number;
            collateralDecimals: number;
        };
        targetCustodyUid: number;
        collateralCustodyUid: number;
        padding2: number[] | BN[] | BN[];
        numSigners: number;
        numSigned: number;
        minSignatures: number;
        instructionAccountsLen: number;
        instructionDataLen: number;
        instructionHash: BN;
        signers: PublicKey[];
        signed: number[];
        price: BN;
        expo: number;
        conf: BN;
        ema: BN;
        publishTime: BN;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        pools: PublicKey[];
        collections: PublicKey[];
        voltageMultiplier: {
            volume: BN;
            rewards: BN;
            rebates: BN;
        };
        tradingDiscount: BN[];
        referralRebate: BN[];
        defaultRebate: BN;
        inceptionTime: BN;
        transferAuthorityBump: number;
        perpetualsBump: number;
        tradeLimit: number;
        rebateLimitUsd: number;
        name: string;
        lpMint: PublicKey;
        oracleAuthority: PublicKey;
        stakedLpVault: PublicKey;
        rewardCustody: PublicKey;
        custodies: PublicKey[];
        ratios: {
            target: BN;
            min: BN;
            max: BN;
        }[];
        markets: PublicKey[];
        maxAumUsd: BN;
        aumUsd: BN;
        totalStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        stakingFeeShareBps: BN;
        lpMintBump: number;
        stakedLpVaultBump: number;
        vpVolumeFactor: number;
        uniqueCustodyCount: number;
        stakingFeeBoostBps: BN[];
        compoundingMint: PublicKey;
        compoundingLpVault: PublicKey;
        compoundingStats: {
            activeAmount: BN;
            totalSupply: BN;
            rewardSnapshot: BN;
            feeShareBps: BN;
            lastCompoundTime: BN;
        };
        compoundingMintBump: number;
        compoundingLpVaultBump: number;
        minLpPriceUsd: BN;
        maxLpPriceUsd: BN;
        lpPrice: BN;
        compoundingLpPrice: BN;
        lastUpdatedTimestamp: BN;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        key: PublicKey;
        feeAmount: BN;
        refererTokenStakeAccount: PublicKey;
        refererBoosterAccount: PublicKey;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: unknown;
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        tokenMint: PublicKey;
        tokenVaultTokenAccount: PublicKey;
        tokenPermissions: {
            allowDeposits: boolean;
            allowWithdrawal: boolean;
            allowRewardWithdrawal: boolean;
        };
        withdrawTimeLimit: BN;
        withdrawInstantFee: BN;
        withdrawInstantFeeEarned: BN;
        stakeLevel: BN[];
        tokensStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardTokensToDistribute: BN;
        rewardTokensPaid: BN;
        tokensToDistribute: BN;
        tokensDistributed: BN;
        rewardTokensDistributed: BN;
        revenueTokenAccountBump: number;
        revenuePerFafStaked: BN;
        revenueAccrued: BN;
        revenueDistributed: BN;
        revenuePaid: BN;
        nftMint: PublicKey;
        voltagePoints: BN;
        stats: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        snapshot: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        timestamp: BN;
        counter: BN;
        tokenStakeAccount: PublicKey;
        burnt: boolean;
    }>;
    getUserOrderAccount: (owner: PublicKey, targetCustody: PublicKey, collateralCustody: PublicKey, side: Side) => Promise<{
        pool: PublicKey;
        mint: PublicKey;
        tokenAccount: PublicKey;
        decimals: number;
        isStable: boolean;
        depegAdjustment: boolean;
        isVirtual: boolean;
        distributeRewards: boolean;
        oracle: {
            intOracleAccount: PublicKey;
            extOracleAccount: PublicKey;
            oracleType: {
                none?: Record<string, never>;
                custom?: Record<string, never>;
                pyth?: Record<string, never>;
            };
            maxDivergenceBps: BN;
            maxConfBps: BN;
            maxPriceAgeSec: number;
            maxBackupAgeSec: number;
        };
        pricing: {
            tradeSpreadMin: BN;
            tradeSpreadMax: BN;
            swapSpread: BN;
            minInitialLeverage: BN;
            maxInitialLeverage: BN;
            maxLeverage: BN;
            minCollateralUsd: BN;
            delaySeconds: BN;
            maxUtilization: BN;
            maxPositionLockedUsd: BN;
            maxExposureUsd: BN;
        };
        permissions: {
            allowSwap: boolean;
            allowAddLiquidity: boolean;
            allowRemoveLiquidity: boolean;
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
            allowLiquidation: boolean;
            allowLpStaking: boolean;
            allowFeeDistribution: boolean;
            allowUngatedTrading: boolean;
            allowFeeDiscounts: boolean;
            allowReferralRebates: boolean;
        } | {
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
        };
        fees: {
            mode: {
                fixed?: Record<string, never>;
                linear?: Record<string, never>;
            };
            swapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            swapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            addLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            removeLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            openPosition: BN;
            closePosition: BN;
            volatility: BN;
        };
        borrowRate: {
            baseRate: BN;
            slope1: BN;
            slope2: BN;
            optimalUtilization: BN;
        };
        rewardThreshold: BN;
        assets: {
            collateral: BN;
            owned: BN;
            locked: BN;
        };
        feesStats: {
            accrued: BN;
            distributed: BN;
            paid: BN;
            rewardPerLpStaked: BN;
            protocolFee: BN;
        };
        borrowRateState: {
            currentRate: BN;
            cumulativeLockFee: BN;
            lastUpdate: BN;
        };
        bump: number;
        tokenAccountBump: number;
        token22: boolean;
        uid: number;
        reservedAmount: BN;
        minReserveUsd: BN;
        limitPriceBufferBps: BN;
        padding: number[] | number[] | BN[] | number[] | BN[] | number[] | number[] | BN[] | BN[];
        owner: PublicKey;
        stakeStats: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardSnapshot: BN;
        unclaimedRewards: BN;
        feeShareBps: BN;
        isInitialized: number | boolean;
        targetCustody: PublicKey;
        collateralCustody: PublicKey;
        side: {
            none?: Record<string, never>;
            long?: Record<string, never>;
            short?: Record<string, never>;
        };
        correlation: boolean;
        maxPayoffBps: BN;
        openInterest: BN;
        collectivePosition: {
            openPositions: BN;
            updateTime: BN;
            averageEntryPrice: {
                price: BN;
                exponent: number;
            };
            sizeAmount: BN;
            sizeUsd: BN;
            lockedAmount: BN;
            lockedUsd: BN;
            collateralAmount: BN;
            collateralUsd: BN;
            unsettledFeeUsd: BN;
            cumulativeLockFeeSnapshot: BN;
            sizeDecimals: number;
            lockedDecimals: number;
            collateralDecimals: number;
        };
        targetCustodyUid: number;
        collateralCustodyUid: number;
        padding2: number[] | BN[] | BN[];
        numSigners: number;
        numSigned: number;
        minSignatures: number;
        instructionAccountsLen: number;
        instructionDataLen: number;
        instructionHash: BN;
        signers: PublicKey[];
        signed: number[];
        price: BN;
        expo: number;
        conf: BN;
        ema: BN;
        publishTime: BN;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        pools: PublicKey[];
        collections: PublicKey[];
        voltageMultiplier: {
            volume: BN;
            rewards: BN;
            rebates: BN;
        };
        tradingDiscount: BN[];
        referralRebate: BN[];
        defaultRebate: BN;
        inceptionTime: BN;
        transferAuthorityBump: number;
        perpetualsBump: number;
        tradeLimit: number;
        rebateLimitUsd: number;
        name: string;
        lpMint: PublicKey;
        oracleAuthority: PublicKey;
        stakedLpVault: PublicKey;
        rewardCustody: PublicKey;
        custodies: PublicKey[];
        ratios: {
            target: BN;
            min: BN;
            max: BN;
        }[];
        markets: PublicKey[];
        maxAumUsd: BN;
        aumUsd: BN;
        totalStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        stakingFeeShareBps: BN;
        lpMintBump: number;
        stakedLpVaultBump: number;
        vpVolumeFactor: number;
        uniqueCustodyCount: number;
        stakingFeeBoostBps: BN[];
        compoundingMint: PublicKey;
        compoundingLpVault: PublicKey;
        compoundingStats: {
            activeAmount: BN;
            totalSupply: BN;
            rewardSnapshot: BN;
            feeShareBps: BN;
            lastCompoundTime: BN;
        };
        compoundingMintBump: number;
        compoundingLpVaultBump: number;
        minLpPriceUsd: BN;
        maxLpPriceUsd: BN;
        lpPrice: BN;
        compoundingLpPrice: BN;
        lastUpdatedTimestamp: BN;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        key: PublicKey;
        feeAmount: BN;
        refererTokenStakeAccount: PublicKey;
        refererBoosterAccount: PublicKey;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: unknown;
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        tokenMint: PublicKey;
        tokenVaultTokenAccount: PublicKey;
        tokenPermissions: {
            allowDeposits: boolean;
            allowWithdrawal: boolean;
            allowRewardWithdrawal: boolean;
        };
        withdrawTimeLimit: BN;
        withdrawInstantFee: BN;
        withdrawInstantFeeEarned: BN;
        stakeLevel: BN[];
        tokensStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardTokensToDistribute: BN;
        rewardTokensPaid: BN;
        tokensToDistribute: BN;
        tokensDistributed: BN;
        rewardTokensDistributed: BN;
        revenueTokenAccountBump: number;
        revenuePerFafStaked: BN;
        revenueAccrued: BN;
        revenueDistributed: BN;
        revenuePaid: BN;
        nftMint: PublicKey;
        voltagePoints: BN;
        stats: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        snapshot: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        timestamp: BN;
        counter: BN;
        tokenStakeAccount: PublicKey;
        burnt: boolean;
    }>;
    getUserPositions: (wallet: PublicKey, poolConfig: PoolConfig) => Promise<{
        owner: PublicKey;
        market: PublicKey;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        bump: number;
        pubkey: PublicKey;
    }[]>;
    getUserOrderAccounts: (wallet: PublicKey, poolConfig: PoolConfig) => Promise<{
        owner: PublicKey;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        bump: number;
        padding: BN[];
        pubkey: PublicKey;
    }[]>;
    getAllPositions: () => Promise<import("@coral-xyz/anchor").ProgramAccount<{
        pool: PublicKey;
        mint: PublicKey;
        tokenAccount: PublicKey;
        decimals: number;
        isStable: boolean;
        depegAdjustment: boolean;
        isVirtual: boolean;
        distributeRewards: boolean;
        oracle: {
            intOracleAccount: PublicKey;
            extOracleAccount: PublicKey;
            oracleType: {
                none?: Record<string, never>;
                custom?: Record<string, never>;
                pyth?: Record<string, never>;
            };
            maxDivergenceBps: BN;
            maxConfBps: BN;
            maxPriceAgeSec: number;
            maxBackupAgeSec: number;
        };
        pricing: {
            tradeSpreadMin: BN;
            tradeSpreadMax: BN;
            swapSpread: BN;
            minInitialLeverage: BN;
            maxInitialLeverage: BN;
            maxLeverage: BN;
            minCollateralUsd: BN;
            delaySeconds: BN;
            maxUtilization: BN;
            maxPositionLockedUsd: BN;
            maxExposureUsd: BN;
        };
        permissions: {
            allowSwap: boolean;
            allowAddLiquidity: boolean;
            allowRemoveLiquidity: boolean;
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
            allowLiquidation: boolean;
            allowLpStaking: boolean;
            allowFeeDistribution: boolean;
            allowUngatedTrading: boolean;
            allowFeeDiscounts: boolean;
            allowReferralRebates: boolean;
        } | {
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
        };
        fees: {
            mode: {
                fixed?: Record<string, never>;
                linear?: Record<string, never>;
            };
            swapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            swapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            addLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            removeLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            openPosition: BN;
            closePosition: BN;
            volatility: BN;
        };
        borrowRate: {
            baseRate: BN;
            slope1: BN;
            slope2: BN;
            optimalUtilization: BN;
        };
        rewardThreshold: BN;
        assets: {
            collateral: BN;
            owned: BN;
            locked: BN;
        };
        feesStats: {
            accrued: BN;
            distributed: BN;
            paid: BN;
            rewardPerLpStaked: BN;
            protocolFee: BN;
        };
        borrowRateState: {
            currentRate: BN;
            cumulativeLockFee: BN;
            lastUpdate: BN;
        };
        bump: number;
        tokenAccountBump: number;
        token22: boolean;
        uid: number;
        reservedAmount: BN;
        minReserveUsd: BN;
        limitPriceBufferBps: BN;
        padding: number[] | number[] | BN[] | number[] | BN[] | number[] | number[] | BN[] | BN[];
        owner: PublicKey;
        stakeStats: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardSnapshot: BN;
        unclaimedRewards: BN;
        feeShareBps: BN;
        isInitialized: number | boolean;
        targetCustody: PublicKey;
        collateralCustody: PublicKey;
        side: {
            none?: Record<string, never>;
            long?: Record<string, never>;
            short?: Record<string, never>;
        };
        correlation: boolean;
        maxPayoffBps: BN;
        openInterest: BN;
        collectivePosition: {
            openPositions: BN;
            updateTime: BN;
            averageEntryPrice: {
                price: BN;
                exponent: number;
            };
            sizeAmount: BN;
            sizeUsd: BN;
            lockedAmount: BN;
            lockedUsd: BN;
            collateralAmount: BN;
            collateralUsd: BN;
            unsettledFeeUsd: BN;
            cumulativeLockFeeSnapshot: BN;
            sizeDecimals: number;
            lockedDecimals: number;
            collateralDecimals: number;
        };
        targetCustodyUid: number;
        collateralCustodyUid: number;
        padding2: number[] | BN[] | BN[];
        numSigners: number;
        numSigned: number;
        minSignatures: number;
        instructionAccountsLen: number;
        instructionDataLen: number;
        instructionHash: BN;
        signers: PublicKey[];
        signed: number[];
        price: BN;
        expo: number;
        conf: BN;
        ema: BN;
        publishTime: BN;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        pools: PublicKey[];
        collections: PublicKey[];
        voltageMultiplier: {
            volume: BN;
            rewards: BN;
            rebates: BN;
        };
        tradingDiscount: BN[];
        referralRebate: BN[];
        defaultRebate: BN;
        inceptionTime: BN;
        transferAuthorityBump: number;
        perpetualsBump: number;
        tradeLimit: number;
        rebateLimitUsd: number;
        name: string;
        lpMint: PublicKey;
        oracleAuthority: PublicKey;
        stakedLpVault: PublicKey;
        rewardCustody: PublicKey;
        custodies: PublicKey[];
        ratios: {
            target: BN;
            min: BN;
            max: BN;
        }[];
        markets: PublicKey[];
        maxAumUsd: BN;
        aumUsd: BN;
        totalStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        stakingFeeShareBps: BN;
        lpMintBump: number;
        stakedLpVaultBump: number;
        vpVolumeFactor: number;
        uniqueCustodyCount: number;
        stakingFeeBoostBps: BN[];
        compoundingMint: PublicKey;
        compoundingLpVault: PublicKey;
        compoundingStats: {
            activeAmount: BN;
            totalSupply: BN;
            rewardSnapshot: BN;
            feeShareBps: BN;
            lastCompoundTime: BN;
        };
        compoundingMintBump: number;
        compoundingLpVaultBump: number;
        minLpPriceUsd: BN;
        maxLpPriceUsd: BN;
        lpPrice: BN;
        compoundingLpPrice: BN;
        lastUpdatedTimestamp: BN;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        key: PublicKey;
        feeAmount: BN;
        refererTokenStakeAccount: PublicKey;
        refererBoosterAccount: PublicKey;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: unknown;
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        tokenMint: PublicKey;
        tokenVaultTokenAccount: PublicKey;
        tokenPermissions: {
            allowDeposits: boolean;
            allowWithdrawal: boolean;
            allowRewardWithdrawal: boolean;
        };
        withdrawTimeLimit: BN;
        withdrawInstantFee: BN;
        withdrawInstantFeeEarned: BN;
        stakeLevel: BN[];
        tokensStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardTokensToDistribute: BN;
        rewardTokensPaid: BN;
        tokensToDistribute: BN;
        tokensDistributed: BN;
        rewardTokensDistributed: BN;
        revenueTokenAccountBump: number;
        revenuePerFafStaked: BN;
        revenueAccrued: BN;
        revenueDistributed: BN;
        revenuePaid: BN;
        nftMint: PublicKey;
        voltagePoints: BN;
        stats: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        snapshot: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        timestamp: BN;
        counter: BN;
        tokenStakeAccount: PublicKey;
        burnt: boolean;
    }>[]>;
    getAllActivePositions: () => Promise<import("@coral-xyz/anchor").ProgramAccount<{
        pool: PublicKey;
        mint: PublicKey;
        tokenAccount: PublicKey;
        decimals: number;
        isStable: boolean;
        depegAdjustment: boolean;
        isVirtual: boolean;
        distributeRewards: boolean;
        oracle: {
            intOracleAccount: PublicKey;
            extOracleAccount: PublicKey;
            oracleType: {
                none?: Record<string, never>;
                custom?: Record<string, never>;
                pyth?: Record<string, never>;
            };
            maxDivergenceBps: BN;
            maxConfBps: BN;
            maxPriceAgeSec: number;
            maxBackupAgeSec: number;
        };
        pricing: {
            tradeSpreadMin: BN;
            tradeSpreadMax: BN;
            swapSpread: BN;
            minInitialLeverage: BN;
            maxInitialLeverage: BN;
            maxLeverage: BN;
            minCollateralUsd: BN;
            delaySeconds: BN;
            maxUtilization: BN;
            maxPositionLockedUsd: BN;
            maxExposureUsd: BN;
        };
        permissions: {
            allowSwap: boolean;
            allowAddLiquidity: boolean;
            allowRemoveLiquidity: boolean;
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
            allowLiquidation: boolean;
            allowLpStaking: boolean;
            allowFeeDistribution: boolean;
            allowUngatedTrading: boolean;
            allowFeeDiscounts: boolean;
            allowReferralRebates: boolean;
        } | {
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
        };
        fees: {
            mode: {
                fixed?: Record<string, never>;
                linear?: Record<string, never>;
            };
            swapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            swapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            addLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            removeLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            openPosition: BN;
            closePosition: BN;
            volatility: BN;
        };
        borrowRate: {
            baseRate: BN;
            slope1: BN;
            slope2: BN;
            optimalUtilization: BN;
        };
        rewardThreshold: BN;
        assets: {
            collateral: BN;
            owned: BN;
            locked: BN;
        };
        feesStats: {
            accrued: BN;
            distributed: BN;
            paid: BN;
            rewardPerLpStaked: BN;
            protocolFee: BN;
        };
        borrowRateState: {
            currentRate: BN;
            cumulativeLockFee: BN;
            lastUpdate: BN;
        };
        bump: number;
        tokenAccountBump: number;
        token22: boolean;
        uid: number;
        reservedAmount: BN;
        minReserveUsd: BN;
        limitPriceBufferBps: BN;
        padding: number[] | number[] | BN[] | number[] | BN[] | number[] | number[] | BN[] | BN[];
        owner: PublicKey;
        stakeStats: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardSnapshot: BN;
        unclaimedRewards: BN;
        feeShareBps: BN;
        isInitialized: number | boolean;
        targetCustody: PublicKey;
        collateralCustody: PublicKey;
        side: {
            none?: Record<string, never>;
            long?: Record<string, never>;
            short?: Record<string, never>;
        };
        correlation: boolean;
        maxPayoffBps: BN;
        openInterest: BN;
        collectivePosition: {
            openPositions: BN;
            updateTime: BN;
            averageEntryPrice: {
                price: BN;
                exponent: number;
            };
            sizeAmount: BN;
            sizeUsd: BN;
            lockedAmount: BN;
            lockedUsd: BN;
            collateralAmount: BN;
            collateralUsd: BN;
            unsettledFeeUsd: BN;
            cumulativeLockFeeSnapshot: BN;
            sizeDecimals: number;
            lockedDecimals: number;
            collateralDecimals: number;
        };
        targetCustodyUid: number;
        collateralCustodyUid: number;
        padding2: number[] | BN[] | BN[];
        numSigners: number;
        numSigned: number;
        minSignatures: number;
        instructionAccountsLen: number;
        instructionDataLen: number;
        instructionHash: BN;
        signers: PublicKey[];
        signed: number[];
        price: BN;
        expo: number;
        conf: BN;
        ema: BN;
        publishTime: BN;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        pools: PublicKey[];
        collections: PublicKey[];
        voltageMultiplier: {
            volume: BN;
            rewards: BN;
            rebates: BN;
        };
        tradingDiscount: BN[];
        referralRebate: BN[];
        defaultRebate: BN;
        inceptionTime: BN;
        transferAuthorityBump: number;
        perpetualsBump: number;
        tradeLimit: number;
        rebateLimitUsd: number;
        name: string;
        lpMint: PublicKey;
        oracleAuthority: PublicKey;
        stakedLpVault: PublicKey;
        rewardCustody: PublicKey;
        custodies: PublicKey[];
        ratios: {
            target: BN;
            min: BN;
            max: BN;
        }[];
        markets: PublicKey[];
        maxAumUsd: BN;
        aumUsd: BN;
        totalStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        stakingFeeShareBps: BN;
        lpMintBump: number;
        stakedLpVaultBump: number;
        vpVolumeFactor: number;
        uniqueCustodyCount: number;
        stakingFeeBoostBps: BN[];
        compoundingMint: PublicKey;
        compoundingLpVault: PublicKey;
        compoundingStats: {
            activeAmount: BN;
            totalSupply: BN;
            rewardSnapshot: BN;
            feeShareBps: BN;
            lastCompoundTime: BN;
        };
        compoundingMintBump: number;
        compoundingLpVaultBump: number;
        minLpPriceUsd: BN;
        maxLpPriceUsd: BN;
        lpPrice: BN;
        compoundingLpPrice: BN;
        lastUpdatedTimestamp: BN;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        key: PublicKey;
        feeAmount: BN;
        refererTokenStakeAccount: PublicKey;
        refererBoosterAccount: PublicKey;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: unknown;
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        tokenMint: PublicKey;
        tokenVaultTokenAccount: PublicKey;
        tokenPermissions: {
            allowDeposits: boolean;
            allowWithdrawal: boolean;
            allowRewardWithdrawal: boolean;
        };
        withdrawTimeLimit: BN;
        withdrawInstantFee: BN;
        withdrawInstantFeeEarned: BN;
        stakeLevel: BN[];
        tokensStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardTokensToDistribute: BN;
        rewardTokensPaid: BN;
        tokensToDistribute: BN;
        tokensDistributed: BN;
        rewardTokensDistributed: BN;
        revenueTokenAccountBump: number;
        revenuePerFafStaked: BN;
        revenueAccrued: BN;
        revenueDistributed: BN;
        revenuePaid: BN;
        nftMint: PublicKey;
        voltagePoints: BN;
        stats: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        snapshot: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        timestamp: BN;
        counter: BN;
        tokenStakeAccount: PublicKey;
        burnt: boolean;
    }>[]>;
    getAllPositionsByMarket: (marketKey: PublicKey) => Promise<import("@coral-xyz/anchor").ProgramAccount<{
        pool: PublicKey;
        mint: PublicKey;
        tokenAccount: PublicKey;
        decimals: number;
        isStable: boolean;
        depegAdjustment: boolean;
        isVirtual: boolean;
        distributeRewards: boolean;
        oracle: {
            intOracleAccount: PublicKey;
            extOracleAccount: PublicKey;
            oracleType: {
                none?: Record<string, never>;
                custom?: Record<string, never>;
                pyth?: Record<string, never>;
            };
            maxDivergenceBps: BN;
            maxConfBps: BN;
            maxPriceAgeSec: number;
            maxBackupAgeSec: number;
        };
        pricing: {
            tradeSpreadMin: BN;
            tradeSpreadMax: BN;
            swapSpread: BN;
            minInitialLeverage: BN;
            maxInitialLeverage: BN;
            maxLeverage: BN;
            minCollateralUsd: BN;
            delaySeconds: BN;
            maxUtilization: BN;
            maxPositionLockedUsd: BN;
            maxExposureUsd: BN;
        };
        permissions: {
            allowSwap: boolean;
            allowAddLiquidity: boolean;
            allowRemoveLiquidity: boolean;
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
            allowLiquidation: boolean;
            allowLpStaking: boolean;
            allowFeeDistribution: boolean;
            allowUngatedTrading: boolean;
            allowFeeDiscounts: boolean;
            allowReferralRebates: boolean;
        } | {
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
        };
        fees: {
            mode: {
                fixed?: Record<string, never>;
                linear?: Record<string, never>;
            };
            swapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            swapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            addLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            removeLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            openPosition: BN;
            closePosition: BN;
            volatility: BN;
        };
        borrowRate: {
            baseRate: BN;
            slope1: BN;
            slope2: BN;
            optimalUtilization: BN;
        };
        rewardThreshold: BN;
        assets: {
            collateral: BN;
            owned: BN;
            locked: BN;
        };
        feesStats: {
            accrued: BN;
            distributed: BN;
            paid: BN;
            rewardPerLpStaked: BN;
            protocolFee: BN;
        };
        borrowRateState: {
            currentRate: BN;
            cumulativeLockFee: BN;
            lastUpdate: BN;
        };
        bump: number;
        tokenAccountBump: number;
        token22: boolean;
        uid: number;
        reservedAmount: BN;
        minReserveUsd: BN;
        limitPriceBufferBps: BN;
        padding: number[] | number[] | BN[] | number[] | BN[] | number[] | number[] | BN[] | BN[];
        owner: PublicKey;
        stakeStats: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardSnapshot: BN;
        unclaimedRewards: BN;
        feeShareBps: BN;
        isInitialized: number | boolean;
        targetCustody: PublicKey;
        collateralCustody: PublicKey;
        side: {
            none?: Record<string, never>;
            long?: Record<string, never>;
            short?: Record<string, never>;
        };
        correlation: boolean;
        maxPayoffBps: BN;
        openInterest: BN;
        collectivePosition: {
            openPositions: BN;
            updateTime: BN;
            averageEntryPrice: {
                price: BN;
                exponent: number;
            };
            sizeAmount: BN;
            sizeUsd: BN;
            lockedAmount: BN;
            lockedUsd: BN;
            collateralAmount: BN;
            collateralUsd: BN;
            unsettledFeeUsd: BN;
            cumulativeLockFeeSnapshot: BN;
            sizeDecimals: number;
            lockedDecimals: number;
            collateralDecimals: number;
        };
        targetCustodyUid: number;
        collateralCustodyUid: number;
        padding2: number[] | BN[] | BN[];
        numSigners: number;
        numSigned: number;
        minSignatures: number;
        instructionAccountsLen: number;
        instructionDataLen: number;
        instructionHash: BN;
        signers: PublicKey[];
        signed: number[];
        price: BN;
        expo: number;
        conf: BN;
        ema: BN;
        publishTime: BN;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        pools: PublicKey[];
        collections: PublicKey[];
        voltageMultiplier: {
            volume: BN;
            rewards: BN;
            rebates: BN;
        };
        tradingDiscount: BN[];
        referralRebate: BN[];
        defaultRebate: BN;
        inceptionTime: BN;
        transferAuthorityBump: number;
        perpetualsBump: number;
        tradeLimit: number;
        rebateLimitUsd: number;
        name: string;
        lpMint: PublicKey;
        oracleAuthority: PublicKey;
        stakedLpVault: PublicKey;
        rewardCustody: PublicKey;
        custodies: PublicKey[];
        ratios: {
            target: BN;
            min: BN;
            max: BN;
        }[];
        markets: PublicKey[];
        maxAumUsd: BN;
        aumUsd: BN;
        totalStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        stakingFeeShareBps: BN;
        lpMintBump: number;
        stakedLpVaultBump: number;
        vpVolumeFactor: number;
        uniqueCustodyCount: number;
        stakingFeeBoostBps: BN[];
        compoundingMint: PublicKey;
        compoundingLpVault: PublicKey;
        compoundingStats: {
            activeAmount: BN;
            totalSupply: BN;
            rewardSnapshot: BN;
            feeShareBps: BN;
            lastCompoundTime: BN;
        };
        compoundingMintBump: number;
        compoundingLpVaultBump: number;
        minLpPriceUsd: BN;
        maxLpPriceUsd: BN;
        lpPrice: BN;
        compoundingLpPrice: BN;
        lastUpdatedTimestamp: BN;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        key: PublicKey;
        feeAmount: BN;
        refererTokenStakeAccount: PublicKey;
        refererBoosterAccount: PublicKey;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: unknown;
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        tokenMint: PublicKey;
        tokenVaultTokenAccount: PublicKey;
        tokenPermissions: {
            allowDeposits: boolean;
            allowWithdrawal: boolean;
            allowRewardWithdrawal: boolean;
        };
        withdrawTimeLimit: BN;
        withdrawInstantFee: BN;
        withdrawInstantFeeEarned: BN;
        stakeLevel: BN[];
        tokensStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardTokensToDistribute: BN;
        rewardTokensPaid: BN;
        tokensToDistribute: BN;
        tokensDistributed: BN;
        rewardTokensDistributed: BN;
        revenueTokenAccountBump: number;
        revenuePerFafStaked: BN;
        revenueAccrued: BN;
        revenueDistributed: BN;
        revenuePaid: BN;
        nftMint: PublicKey;
        voltagePoints: BN;
        stats: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        snapshot: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        timestamp: BN;
        counter: BN;
        tokenStakeAccount: PublicKey;
        burnt: boolean;
    }>[]>;
    getAllActivePositionsByMarket: (marketKey: PublicKey) => Promise<import("@coral-xyz/anchor").ProgramAccount<{
        pool: PublicKey;
        mint: PublicKey;
        tokenAccount: PublicKey;
        decimals: number;
        isStable: boolean;
        depegAdjustment: boolean;
        isVirtual: boolean;
        distributeRewards: boolean;
        oracle: {
            intOracleAccount: PublicKey;
            extOracleAccount: PublicKey;
            oracleType: {
                none?: Record<string, never>;
                custom?: Record<string, never>;
                pyth?: Record<string, never>;
            };
            maxDivergenceBps: BN;
            maxConfBps: BN;
            maxPriceAgeSec: number;
            maxBackupAgeSec: number;
        };
        pricing: {
            tradeSpreadMin: BN;
            tradeSpreadMax: BN;
            swapSpread: BN;
            minInitialLeverage: BN;
            maxInitialLeverage: BN;
            maxLeverage: BN;
            minCollateralUsd: BN;
            delaySeconds: BN;
            maxUtilization: BN;
            maxPositionLockedUsd: BN;
            maxExposureUsd: BN;
        };
        permissions: {
            allowSwap: boolean;
            allowAddLiquidity: boolean;
            allowRemoveLiquidity: boolean;
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
            allowLiquidation: boolean;
            allowLpStaking: boolean;
            allowFeeDistribution: boolean;
            allowUngatedTrading: boolean;
            allowFeeDiscounts: boolean;
            allowReferralRebates: boolean;
        } | {
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
        };
        fees: {
            mode: {
                fixed?: Record<string, never>;
                linear?: Record<string, never>;
            };
            swapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            swapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            addLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            removeLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            openPosition: BN;
            closePosition: BN;
            volatility: BN;
        };
        borrowRate: {
            baseRate: BN;
            slope1: BN;
            slope2: BN;
            optimalUtilization: BN;
        };
        rewardThreshold: BN;
        assets: {
            collateral: BN;
            owned: BN;
            locked: BN;
        };
        feesStats: {
            accrued: BN;
            distributed: BN;
            paid: BN;
            rewardPerLpStaked: BN;
            protocolFee: BN;
        };
        borrowRateState: {
            currentRate: BN;
            cumulativeLockFee: BN;
            lastUpdate: BN;
        };
        bump: number;
        tokenAccountBump: number;
        token22: boolean;
        uid: number;
        reservedAmount: BN;
        minReserveUsd: BN;
        limitPriceBufferBps: BN;
        padding: number[] | number[] | BN[] | number[] | BN[] | number[] | number[] | BN[] | BN[];
        owner: PublicKey;
        stakeStats: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardSnapshot: BN;
        unclaimedRewards: BN;
        feeShareBps: BN;
        isInitialized: number | boolean;
        targetCustody: PublicKey;
        collateralCustody: PublicKey;
        side: {
            none?: Record<string, never>;
            long?: Record<string, never>;
            short?: Record<string, never>;
        };
        correlation: boolean;
        maxPayoffBps: BN;
        openInterest: BN;
        collectivePosition: {
            openPositions: BN;
            updateTime: BN;
            averageEntryPrice: {
                price: BN;
                exponent: number;
            };
            sizeAmount: BN;
            sizeUsd: BN;
            lockedAmount: BN;
            lockedUsd: BN;
            collateralAmount: BN;
            collateralUsd: BN;
            unsettledFeeUsd: BN;
            cumulativeLockFeeSnapshot: BN;
            sizeDecimals: number;
            lockedDecimals: number;
            collateralDecimals: number;
        };
        targetCustodyUid: number;
        collateralCustodyUid: number;
        padding2: number[] | BN[] | BN[];
        numSigners: number;
        numSigned: number;
        minSignatures: number;
        instructionAccountsLen: number;
        instructionDataLen: number;
        instructionHash: BN;
        signers: PublicKey[];
        signed: number[];
        price: BN;
        expo: number;
        conf: BN;
        ema: BN;
        publishTime: BN;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        pools: PublicKey[];
        collections: PublicKey[];
        voltageMultiplier: {
            volume: BN;
            rewards: BN;
            rebates: BN;
        };
        tradingDiscount: BN[];
        referralRebate: BN[];
        defaultRebate: BN;
        inceptionTime: BN;
        transferAuthorityBump: number;
        perpetualsBump: number;
        tradeLimit: number;
        rebateLimitUsd: number;
        name: string;
        lpMint: PublicKey;
        oracleAuthority: PublicKey;
        stakedLpVault: PublicKey;
        rewardCustody: PublicKey;
        custodies: PublicKey[];
        ratios: {
            target: BN;
            min: BN;
            max: BN;
        }[];
        markets: PublicKey[];
        maxAumUsd: BN;
        aumUsd: BN;
        totalStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        stakingFeeShareBps: BN;
        lpMintBump: number;
        stakedLpVaultBump: number;
        vpVolumeFactor: number;
        uniqueCustodyCount: number;
        stakingFeeBoostBps: BN[];
        compoundingMint: PublicKey;
        compoundingLpVault: PublicKey;
        compoundingStats: {
            activeAmount: BN;
            totalSupply: BN;
            rewardSnapshot: BN;
            feeShareBps: BN;
            lastCompoundTime: BN;
        };
        compoundingMintBump: number;
        compoundingLpVaultBump: number;
        minLpPriceUsd: BN;
        maxLpPriceUsd: BN;
        lpPrice: BN;
        compoundingLpPrice: BN;
        lastUpdatedTimestamp: BN;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        key: PublicKey;
        feeAmount: BN;
        refererTokenStakeAccount: PublicKey;
        refererBoosterAccount: PublicKey;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: unknown;
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        tokenMint: PublicKey;
        tokenVaultTokenAccount: PublicKey;
        tokenPermissions: {
            allowDeposits: boolean;
            allowWithdrawal: boolean;
            allowRewardWithdrawal: boolean;
        };
        withdrawTimeLimit: BN;
        withdrawInstantFee: BN;
        withdrawInstantFeeEarned: BN;
        stakeLevel: BN[];
        tokensStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardTokensToDistribute: BN;
        rewardTokensPaid: BN;
        tokensToDistribute: BN;
        tokensDistributed: BN;
        rewardTokensDistributed: BN;
        revenueTokenAccountBump: number;
        revenuePerFafStaked: BN;
        revenueAccrued: BN;
        revenueDistributed: BN;
        revenuePaid: BN;
        nftMint: PublicKey;
        voltagePoints: BN;
        stats: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        snapshot: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        timestamp: BN;
        counter: BN;
        tokenStakeAccount: PublicKey;
        burnt: boolean;
    }>[]>;
    getAllOrderAccounts: () => Promise<import("@coral-xyz/anchor").ProgramAccount<{
        pool: PublicKey;
        mint: PublicKey;
        tokenAccount: PublicKey;
        decimals: number;
        isStable: boolean;
        depegAdjustment: boolean;
        isVirtual: boolean;
        distributeRewards: boolean;
        oracle: {
            intOracleAccount: PublicKey;
            extOracleAccount: PublicKey;
            oracleType: {
                none?: Record<string, never>;
                custom?: Record<string, never>;
                pyth?: Record<string, never>;
            };
            maxDivergenceBps: BN;
            maxConfBps: BN;
            maxPriceAgeSec: number;
            maxBackupAgeSec: number;
        };
        pricing: {
            tradeSpreadMin: BN;
            tradeSpreadMax: BN;
            swapSpread: BN;
            minInitialLeverage: BN;
            maxInitialLeverage: BN;
            maxLeverage: BN;
            minCollateralUsd: BN;
            delaySeconds: BN;
            maxUtilization: BN;
            maxPositionLockedUsd: BN;
            maxExposureUsd: BN;
        };
        permissions: {
            allowSwap: boolean;
            allowAddLiquidity: boolean;
            allowRemoveLiquidity: boolean;
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
            allowLiquidation: boolean;
            allowLpStaking: boolean;
            allowFeeDistribution: boolean;
            allowUngatedTrading: boolean;
            allowFeeDiscounts: boolean;
            allowReferralRebates: boolean;
        } | {
            allowOpenPosition: boolean;
            allowClosePosition: boolean;
            allowCollateralWithdrawal: boolean;
            allowSizeChange: boolean;
        };
        fees: {
            mode: {
                fixed?: Record<string, never>;
                linear?: Record<string, never>;
            };
            swapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            swapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapIn: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            stableSwapOut: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            addLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            removeLiquidity: {
                minFee: BN;
                targetFee: BN;
                maxFee: BN;
            };
            openPosition: BN;
            closePosition: BN;
            volatility: BN;
        };
        borrowRate: {
            baseRate: BN;
            slope1: BN;
            slope2: BN;
            optimalUtilization: BN;
        };
        rewardThreshold: BN;
        assets: {
            collateral: BN;
            owned: BN;
            locked: BN;
        };
        feesStats: {
            accrued: BN;
            distributed: BN;
            paid: BN;
            rewardPerLpStaked: BN;
            protocolFee: BN;
        };
        borrowRateState: {
            currentRate: BN;
            cumulativeLockFee: BN;
            lastUpdate: BN;
        };
        bump: number;
        tokenAccountBump: number;
        token22: boolean;
        uid: number;
        reservedAmount: BN;
        minReserveUsd: BN;
        limitPriceBufferBps: BN;
        padding: number[] | number[] | BN[] | number[] | BN[] | number[] | number[] | BN[] | BN[];
        owner: PublicKey;
        stakeStats: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardSnapshot: BN;
        unclaimedRewards: BN;
        feeShareBps: BN;
        isInitialized: number | boolean;
        targetCustody: PublicKey;
        collateralCustody: PublicKey;
        side: {
            none?: Record<string, never>;
            long?: Record<string, never>;
            short?: Record<string, never>;
        };
        correlation: boolean;
        maxPayoffBps: BN;
        openInterest: BN;
        collectivePosition: {
            openPositions: BN;
            updateTime: BN;
            averageEntryPrice: {
                price: BN;
                exponent: number;
            };
            sizeAmount: BN;
            sizeUsd: BN;
            lockedAmount: BN;
            lockedUsd: BN;
            collateralAmount: BN;
            collateralUsd: BN;
            unsettledFeeUsd: BN;
            cumulativeLockFeeSnapshot: BN;
            sizeDecimals: number;
            lockedDecimals: number;
            collateralDecimals: number;
        };
        targetCustodyUid: number;
        collateralCustodyUid: number;
        padding2: number[] | BN[] | BN[];
        numSigners: number;
        numSigned: number;
        minSignatures: number;
        instructionAccountsLen: number;
        instructionDataLen: number;
        instructionHash: BN;
        signers: PublicKey[];
        signed: number[];
        price: BN;
        expo: number;
        conf: BN;
        ema: BN;
        publishTime: BN;
        market: PublicKey;
        limitOrders: unknown;
        takeProfitOrders: unknown;
        stopLossOrders: unknown;
        isInitialised: boolean;
        openOrders: number;
        openSl: number;
        openTp: number;
        inactiveSl: number;
        inactiveTp: number;
        activeOrders: number;
        pools: PublicKey[];
        collections: PublicKey[];
        voltageMultiplier: {
            volume: BN;
            rewards: BN;
            rebates: BN;
        };
        tradingDiscount: BN[];
        referralRebate: BN[];
        defaultRebate: BN;
        inceptionTime: BN;
        transferAuthorityBump: number;
        perpetualsBump: number;
        tradeLimit: number;
        rebateLimitUsd: number;
        name: string;
        lpMint: PublicKey;
        oracleAuthority: PublicKey;
        stakedLpVault: PublicKey;
        rewardCustody: PublicKey;
        custodies: PublicKey[];
        ratios: {
            target: BN;
            min: BN;
            max: BN;
        }[];
        markets: PublicKey[];
        maxAumUsd: BN;
        aumUsd: BN;
        totalStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        stakingFeeShareBps: BN;
        lpMintBump: number;
        stakedLpVaultBump: number;
        vpVolumeFactor: number;
        uniqueCustodyCount: number;
        stakingFeeBoostBps: BN[];
        compoundingMint: PublicKey;
        compoundingLpVault: PublicKey;
        compoundingStats: {
            activeAmount: BN;
            totalSupply: BN;
            rewardSnapshot: BN;
            feeShareBps: BN;
            lastCompoundTime: BN;
        };
        compoundingMintBump: number;
        compoundingLpVaultBump: number;
        minLpPriceUsd: BN;
        maxLpPriceUsd: BN;
        lpPrice: BN;
        compoundingLpPrice: BN;
        lastUpdatedTimestamp: BN;
        delegate: PublicKey;
        openTime: BN;
        updateTime: BN;
        entryPrice: {
            price: BN;
            exponent: number;
        };
        sizeAmount: BN;
        sizeUsd: BN;
        lockedAmount: BN;
        lockedUsd: BN;
        collateralAmount: BN;
        collateralUsd: BN;
        unsettledAmount: BN;
        unsettledFeesUsd: BN;
        cumulativeLockFeeSnapshot: BN;
        takeProfitPrice: {
            price: BN;
            exponent: number;
        };
        stopLossPrice: {
            price: BN;
            exponent: number;
        };
        sizeDecimals: number;
        lockedDecimals: number;
        collateralDecimals: number;
        key: PublicKey;
        feeAmount: BN;
        refererTokenStakeAccount: PublicKey;
        refererBoosterAccount: PublicKey;
        level: number;
        withdrawRequestCount: number;
        withdrawRequest: unknown;
        activeStakeAmount: BN;
        updateTimestamp: BN;
        tradeTimestamp: BN;
        tradeCounter: number;
        lastRewardEpochCount: number;
        rewardTokens: BN;
        unclaimedRevenueAmount: BN;
        revenueSnapshot: BN;
        tokenMint: PublicKey;
        tokenVaultTokenAccount: PublicKey;
        tokenPermissions: {
            allowDeposits: boolean;
            allowWithdrawal: boolean;
            allowRewardWithdrawal: boolean;
        };
        withdrawTimeLimit: BN;
        withdrawInstantFee: BN;
        withdrawInstantFeeEarned: BN;
        stakeLevel: BN[];
        tokensStaked: {
            pendingActivation: BN;
            activeAmount: BN;
            pendingDeactivation: BN;
            deactivatedAmount: BN;
        };
        rewardTokensToDistribute: BN;
        rewardTokensPaid: BN;
        tokensToDistribute: BN;
        tokensDistributed: BN;
        rewardTokensDistributed: BN;
        revenueTokenAccountBump: number;
        revenuePerFafStaked: BN;
        revenueAccrued: BN;
        revenueDistributed: BN;
        revenuePaid: BN;
        nftMint: PublicKey;
        voltagePoints: BN;
        stats: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        snapshot: {
            volumeUsd: BN;
            lpRewardsUsd: BN;
            referralRebateUsd: BN;
        };
        timestamp: BN;
        counter: BN;
        tokenStakeAccount: PublicKey;
        burnt: boolean;
    }>[]>;
    getAccountDiscriminator: (name: string) => Buffer;
    log: (...message: string[]) => void;
    prettyPrint: (object: object) => void;
    liquidate: (positionAccount: PublicKey, poolConfig: PoolConfig, tokenMint: PublicKey, collateralMint: PublicKey, marketPk: PublicKey) => Promise<TransactionInstruction>;
    getApyPercentageUi: (rewardCustodyAccount: CustodyAccount, previousSnapShotRewardPerLpStaked: BN, lpTokenUsdPrice: BN) => string;
    getAddLiquidityAmountAndFeeSync: (amountIn: BN, poolAccount: PoolAccount, inputTokenPrice: OraclePrice, inputTokenEmaPrice: OraclePrice, inputTokenCustodyAccount: CustodyAccount, lpTokenSupplyAmount: BN, poolAumUsdMax: BN, poolConfig: PoolConfig) => AddLiquidityAmountAndFee;
    getRemoveLiquidityAmountAndFeeSync: (lpAmountIn: BN, poolAccount: PoolAccount, outputTokenPrice: OraclePrice, outputTokenEmaPrice: OraclePrice, outputTokenCustodyAccount: CustodyAccount, lpTokenSupply: BN, poolAumUsdMax: BN, poolConfig: PoolConfig) => RemoveLiquidityAmountAndFee;
    private getNewRatioHelper;
    getFeeHelper: (action: FeesAction, amountAdd: BN, amountRemove: BN, inputTokenCustodyAccount: CustodyAccount, maxOraclePrice: OraclePrice, poolAumUsdMax: BN, poolAccount: PoolAccount, poolConfig: PoolConfig) => {
        feeBps: BN;
        feeAmount: BN;
    };
    getMinAndMaxOraclePriceSync: (price: OraclePrice, emaPrice: OraclePrice, custodyAccount: CustodyAccount) => {
        min: OraclePrice;
        max: OraclePrice;
    };
    getMinAndMaxPriceSync: (price: OraclePrice, emaPrice: OraclePrice, custodyAccount: CustodyAccount) => MinAndMaxPrice;
    checkIfPriceStaleOrCustom: (price: OraclePrice, emaPrice: OraclePrice, custodyAccount: CustodyAccount, timestampInSeconds: BN) => boolean;
    getAveragePriceSync: (price1: BN, size1: BN, price2: BN, size2: BN) => BN;
    getLeverageSync: (sizeUsd: BN, collateralAmount: BN, collateralMinOraclePrice: OraclePrice, collateralTokenDecimals: number, pnlUsd: BN) => BN;
    getLeverageAtAmountEntryWithSwapSync: (positionAccount: PositionAccount | null, inputDeltaAmount: BN, sizeDeltaAmount: BN, side: Side, poolAccount: PoolAccount, inputTokenPrice: OraclePrice, inputTokenEmaPrice: OraclePrice, inputTokenCustodyAccount: CustodyAccount, swapOutTokenPrice: OraclePrice, swapOutTokenEmaPrice: OraclePrice, swapOutTokenCustodyAccount: CustodyAccount, collateralTokenPrice: OraclePrice, collateralTokenEmaPrice: OraclePrice, collateralTokenCustodyAccount: CustodyAccount, targetTokenPrice: OraclePrice, targetTokenEmaPrice: OraclePrice, targetTokenCustodyAccount: CustodyAccount, swapPoolAumUsdMax: BN, poolConfigPosition: PoolConfig, poolConfigSwap: PoolConfig, pnlUsd: BN) => BN;
    getEntryPriceAndFeeSync: (positionAccount: PositionAccount | null, marketCorrelation: boolean, collateralDeltaAmount: BN, sizeDeltaAmount: BN, side: Side, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, collateralCustodyAccount: CustodyAccount, currentTimestamp: BN, discountBps?: BN) => EntryPriceAndFee;
    getEntryPriceAndFeeSyncV2: (positionAccount: PositionAccount | null, marketCorrelation: boolean, collateralDeltaAmount: BN, sizeDeltaAmount: BN, side: Side, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, collateralCustodyAccount: CustodyAccount, currentTimestamp: BN, discountBps?: BN, enableLogs?: boolean) => EntryPriceAndFeeV2;
    getEntryPriceUsdSync: (side: Side, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, lockedUsd: BN) => OraclePrice;
    getPriceAfterSlippage(isEntry: boolean, slippageBps: BN, targetPrice: OraclePrice, side: Side): ContractOraclePrice;
    getExitFeeSync: (positionAccount: PositionAccount, targetCustody: CustodyAccount, collateralCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, discountBps?: BN) => {
        exitFeeAmount: BN;
        exitFeeUsd: BN;
    };
    getExitPriceAndFeeSync: (positionAccount: PositionAccount, marketCorrelation: boolean, collateralDeltaAmount: BN, sizeDeltaAmount: BN, side: Side, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, collateralCustodyAccount: CustodyAccount, currentTimestamp: BN, discountBps?: BN) => ExitPriceAndFee;
    getTradeSpread: (targetCustodyAccount: CustodyAccount, lockedUsd: BN) => BN;
    getExitOraclePriceSync: (side: Side, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, lockedUsd: BN) => OraclePrice;
    getExitOraclePriceWithoutSpreadSync: (side: Side, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount) => OraclePrice;
    getSizeAmountFromLeverageAndCollateral: (collateralAmtWithFee: BN, leverage: string, marketToken: Token, collateralToken: Token, side: Side, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, collateralCustodyAccount: CustodyAccount, discountBps?: BN) => BN;
    getSizeAmountWithSwapSync: (amountIn: BN, leverage: string, side: Side, poolAccount: PoolAccount, inputTokenPrice: OraclePrice, inputTokenEmaPrice: OraclePrice, inputTokenCustodyAccount: CustodyAccount, collateralTokenPrice: OraclePrice, collateralTokenEmaPrice: OraclePrice, collateralTokenCustodyAccount: CustodyAccount, swapOutTokenPrice: OraclePrice, swapOutTokenEmaPrice: OraclePrice, swapOutTokenCustodyAccount: CustodyAccount, targetTokenPrice: OraclePrice, targetTokenEmaPrice: OraclePrice, targetTokenCustodyAccount: CustodyAccount, swapPoolAumUsdMax: BN, poolConfigSwap: PoolConfig, discountBps?: BN) => BN;
    getCollateralAmountWithFeeFromLeverageAndSize: (sizeAmount: BN, leverage: string, marketToken: Token, collateralToken: Token, side: Side, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, collateralCustodyAccount: CustodyAccount, discountBps?: BN) => BN;
    getCollateralAmountWithSwapSync: (sizeAmount: BN, leverage: string, side: Side, poolAccount: PoolAccount, inputTokenPrice: OraclePrice, inputTokenEmaPrice: OraclePrice, inputTokenCustodyAccount: CustodyAccount, swapOutTokenPrice: OraclePrice, swapOutTokenEmaPrice: OraclePrice, swapOutTokenCustodyAccount: CustodyAccount, collateralTokenPrice: OraclePrice, collateralTokenEmaPrice: OraclePrice, collateralTokenCustodyAccount: CustodyAccount, targetTokenPrice: OraclePrice, targetTokenEmaPrice: OraclePrice, targetTokenCustodyAccount: CustodyAccount, swapPoolAumUsdMax: BN, poolConfigPosition: PoolConfig, poolConfigSwap: PoolConfig) => BN;
    getDecreaseSizeCollateralAndFeeSync: (positionAccount: PositionAccount, marketCorrelation: boolean, sizeDeltaUsd: BN, keepLevSame: boolean, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, marketConfig: MarketConfig, targetCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, collateralCustodyAccount: CustodyAccount, currentTimestamp: BN, side: Side, poolConfig: PoolConfig, discountBps?: BN, debugLogs?: boolean) => RemoveCollateralData;
    getMaxWithdrawableAmountSyncInternal: (positionAccount: PositionAccount, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, collateralCustodyAccount: CustodyAccount, currentTimestamp: BN, poolConfig: PoolConfig, closeAmount?: BN, errorBandwidthPercentageUi?: number) => BN;
    getFinalCloseAmountSync: (positionAccount: PositionAccount, marketCorrelation: boolean, side: Side, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, collateralCustodyAccount: CustodyAccount, currentTimestamp: BN, poolConfig: PoolConfig) => {
        closeAmount: BN;
        feesAmount: BN;
    };
    getMaxWithdrawableAmountSync: (positionAccount: PositionAccount, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, collateralCustodyAccount: CustodyAccount, currentTimestamp: BN, poolConfig: PoolConfig, errorBandwidthPercentageUi?: number) => BN;
    getCumulativeLockFeeSync: (custodyAccount: CustodyAccount, currentTimestamp: BN) => BN;
    getBorrowRateSync: (custodyAccount: CustodyAccount, currentUtilization: BN) => BN;
    getLockFeeAndUnsettledUsdForPosition: (position: PositionAccount, collateralCustodyAccount: CustodyAccount, currentTimestamp: BN) => BN;
    getLockedUsd: (sideUsd: BN, side: Side, marketCorrelation: boolean, maxPayOffBps: BN) => BN;
    getLiquidationPriceSync: (collateralAmount: BN, sizeAmount: BN, entryOraclePrice: OraclePrice, lockAndUnsettledFeeUsd: BN, marketCorrelation: boolean, side: Side, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, collateralCustodyAccount: CustodyAccount, positionAccount: PositionAccount) => OraclePrice;
    getLiquidationPriceWithOrder: (collateralAmount: BN, collateralUsd: BN, sizeAmount: BN, sizeUsd: BN, sizeDecimals: number, limitOraclePrice: OraclePrice, marketCorrelation: boolean, side: Side, targetPrice: OraclePrice, targetEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, collateralCustodyAccount: CustodyAccount) => OraclePrice;
    getMaxProfitPriceSync: (entryPrice: OraclePrice, marketCorrelation: boolean, side: Side, positionAccount: PositionAccount) => OraclePrice;
    getEstimateProfitLossforTpSlEntry: (positionAccount: PositionAccount | null, isTakeProfit: boolean, userEntrytpSlOraclePrice: OraclePrice, collateralDeltaAmount: BN, sizeDeltaAmount: BN, side: Side, marketAccountPk: PublicKey, targetTokenPrice: OraclePrice, targetTokenEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, collateralCustodyAccount: CustodyAccount, poolConfig: PoolConfig) => {
        pnlUsd: BN;
        pnlPercentage: BN;
    };
    getTriggerPriceFromPnlSync: (pnlUsd: BN, exitFeeUsd: BN, positionSize: BN, sizeDecimals: number, entryPrice: OraclePrice, side: Side) => OraclePrice;
    getTriggerPriceFromRoiSync: (roi: BN, collateralUsd: BN, exitFeeUsd: BN, positionSize: BN, sizeDecimals: number, entryPrice: OraclePrice, side: Side) => OraclePrice;
    getPnlSync: (positionAccount: PositionAccount, targetTokenPrice: OraclePrice, targetTokenEmaPrice: OraclePrice, targetCustodyAccount: CustodyAccount, collateralPrice: OraclePrice, collateralEmaPrice: OraclePrice, collateralCustodyAccount: CustodyAccount, currentTimestamp: BN, delay: BN, poolConfig: PoolConfig) => {
        profitUsd: BN;
        lossUsd: BN;
    };
    getSwapAmountAndFeesSync: (amountIn: BN, amountOut: BN, poolAccount: PoolAccount, inputTokenPrice: OraclePrice, inputTokenEmaPrice: OraclePrice, inputTokenCustodyAccount: CustodyAccount, outputTokenPrice: OraclePrice, outputTokenEmaPrice: OraclePrice, outputTokenCustodyAccount: CustodyAccount, poolAumUsdMax: BN, poolConfig: PoolConfig) => {
        minAmountOut: BN;
        minAmountIn: BN;
        feeIn: BN;
        feeOut: BN;
    };
    getAssetsUnderManagementUsdSync: (poolAccount: PoolAccount, tokenPrices: OraclePrice[], tokenEmaPrices: OraclePrice[], custodies: CustodyAccount[], markets: MarketAccount[], aumCalcMode: "includePnl" | "excludePnl", currentTime: BN, poolConfig: PoolConfig) => {
        poolAmountUsd: BN;
        poolEquityUsd: BN;
    };
    getNftFinalDiscount: (perpetualsAccount: PerpetualsAccount, nftTradingAccount: Trading, currentTime: BN) => {
        discountBn: BN;
    };
    getFeeDiscount: (perpetualsAccount: PerpetualsAccount, tokenStakeAccount: TokenStake, currentTime: BN) => {
        discountBn: BN;
    };
    getIndexPriceAtParticularTime: (poolConfig: PoolConfig, targetPricesAtT1Ui: Number[], targetPricesAtT2Ui: Number[], tokenRatiosAtT2BN: BN[]) => string;
    getUserClaimableRevenueAmount: (POOL_CONFIG: PoolConfig, userPublicKey: PublicKey, enableDebuglogs?: boolean) => Promise<BN>;
    getStakedLpTokenPrice: (poolKey: PublicKey, POOL_CONFIG: PoolConfig) => Promise<string>;
    getAssetsUnderManagement: (poolKey: PublicKey, POOL_CONFIG: PoolConfig) => Promise<string>;
    getAddLiquidityAmountAndFeeView: (amount: BN, poolKey: PublicKey, depositCustodyKey: PublicKey, POOL_CONFIG: PoolConfig, userPublicKey?: PublicKey | undefined) => Promise<{
        amount: BN;
        fee: BN;
    }>;
    getRemoveLiquidityAmountAndFeeView: (amount: BN, poolKey: PublicKey, removeTokenCustodyKey: PublicKey, POOL_CONFIG: PoolConfig, userPublicKey?: PublicKey | undefined) => Promise<{
        amount: BN;
        fee: BN;
    }>;
    getCompoundingLPTokenPrice: (poolKey: PublicKey, POOL_CONFIG: PoolConfig) => Promise<string>;
    getAddCompoundingLiquidityAmountAndFeeView: (amount: BN, poolKey: PublicKey, depositCustodyKey: PublicKey, POOL_CONFIG: PoolConfig, userPublicKey?: PublicKey | undefined) => Promise<{
        amount: BN;
        fee: BN;
    }>;
    getRemoveCompoundingLiquidityAmountAndFeeView: (amount: BN, poolKey: PublicKey, removeTokenCustodyKey: PublicKey, POOL_CONFIG: PoolConfig, userPublicKey?: PublicKey | undefined) => Promise<{
        amount: BN;
        fee: BN;
    }>;
    getLiquidationPriceView: (positionAccountKey: PublicKey, poolConfig: PoolConfig) => Promise<any>;
    getLiquidationStateView: (positionAccount: PublicKey, poolName: string, tokenMint: PublicKey, collateralMint: PublicKey, poolConfig: PoolConfig) => Promise<any>;
    getCompoundingTokenDataView: (poolConfig: PoolConfig) => Promise<any>;
    getLpTokenPriceView: (poolConfig: PoolConfig) => Promise<any>;
    openPosition: (targetSymbol: string, collateralSymbol: string, priceWithSlippage: ContractOraclePrice, collateralWithfee: BN, size: BN, side: Side, poolConfig: PoolConfig, privilege: Privilege, tokenStakeAccount?: PublicKey, userReferralAccount?: PublicKey, rebateTokenAccount?: PublicKey, skipBalanceChecks?: boolean, ephemeralSignerPubkey?: any) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    closePosition: (marketSymbol: string, collateralSymbol: string, priceWithSlippage: ContractOraclePrice, side: Side, poolConfig: PoolConfig, privilege: Privilege, tokenStakeAccount?: PublicKey, userReferralAccount?: PublicKey, rebateTokenAccount?: PublicKey, createUserATA?: boolean, closeUsersWSOLATA?: boolean, ephemeralSignerPubkey?: any) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    swapAndOpen: (targetTokenSymbol: string, collateralTokenSymbol: string, userInputTokenSymbol: string, amountIn: BN, minCollateralAmountOut: BN, priceWithSlippage: ContractOraclePrice, sizeAmount: BN, side: Side, poolConfig: PoolConfig, privilege: Privilege, tokenStakeAccount?: PublicKey, userReferralAccount?: PublicKey, rebateTokenAccount?: PublicKey, skipBalanceChecks?: boolean, ephemeralSignerPubkey?: any) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    closeAndSwap: (targetTokenSymbol: string, userOutputTokenSymbol: string, collateralTokenSymbol: string, minSwapAmountOut: BN, priceWithSlippage: ContractOraclePrice, side: Side, poolConfig: PoolConfig, privilege: Privilege, tokenStakeAccount?: PublicKey, userReferralAccount?: PublicKey, rebateTokenAccount?: PublicKey, ephemeralSignerPubkey?: any) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    addCollateral: (collateralWithFee: BN, targetSymbol: string, collateralSymbol: string, side: Side, positionPubKey: PublicKey, poolConfig: PoolConfig, skipBalanceChecks?: boolean, ephemeralSignerPubkey?: any) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    swapAndAddCollateral: (targetSymbol: string, inputSymbol: string, collateralSymbol: string, amountIn: BN, minCollateralAmountOut: BN, side: Side, positionPubKey: PublicKey, poolConfig: PoolConfig, skipBalanceChecks?: boolean, ephemeralSignerPubkey?: any) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    removeCollateral: (collateralWithFee: BN, marketSymbol: string, collateralSymbol: string, side: Side, positionPubKey: PublicKey, poolConfig: PoolConfig, createUserATA?: boolean, closeUsersWSOLATA?: boolean, ephemeralSignerPubkey?: any) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    removeCollateralAndSwap: (targetSymbol: string, collateralSymbol: string, outputSymbol: string, minSwapAmountOut: BN, collateralDelta: BN, side: Side, poolConfig: PoolConfig, ephemeralSignerPubkey?: any) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    increaseSize: (targetSymbol: string, collateralSymbol: string, positionPubKey: PublicKey, side: Side, poolConfig: PoolConfig, priceWithSlippage: ContractOraclePrice, sizeDelta: BN, privilege: Privilege, tokenStakeAccount?: PublicKey, userReferralAccount?: PublicKey, rebateTokenAccount?: PublicKey) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    decreaseSize: (targetSymbol: string, collateralSymbol: string, side: Side, positionPubKey: PublicKey, poolConfig: PoolConfig, priceWithSlippage: ContractOraclePrice, sizeDelta: BN, privilege: Privilege, tokenStakeAccount?: PublicKey, userReferralAccount?: PublicKey, rebateTokenAccount?: PublicKey) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    addLiquidity: (payTokenSymbol: string, tokenAmountIn: BN, minLpAmountOut: BN, poolConfig: PoolConfig, skipBalanceChecks?: boolean, ephemeralSignerPubkey?: any) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    addLiquidityAndStake: (inputSymbol: string, amountIn: BN, minLpAmountOut: BN, poolConfig: PoolConfig, skipBalanceChecks?: boolean, ephemeralSignerPubkey?: any, userPublicKey?: PublicKey | undefined) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    removeLiquidity: (recieveTokenSymbol: string, liquidityAmountIn: BN, minTokenAmountOut: BN, poolConfig: PoolConfig, closeLpATA?: boolean, createUserATA?: boolean, closeUsersWSOLATA?: boolean, ephemeralSignerPubkey?: any, userPublicKey?: PublicKey | undefined) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    addReferral: (tokenStakeAccount: PublicKey, nftReferralAccount: PublicKey) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    updateNftAccount: (nftMint: PublicKey, updateReferer: boolean, updateBooster: boolean, flpStakeAccounts: PublicKey[]) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    levelUp: (poolConfig: PoolConfig, nftMint: PublicKey, authorizationRulesAccount: PublicKey) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    depositStake: (owner: PublicKey, feePayer: PublicKey, depositAmount: BN, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    refreshStakeWithAllFlpStakeAccounts: (rewardSymbol: string, poolConfig: PoolConfig, flpStakeAccountPks: PublicKey[]) => Promise<TransactionInstruction>;
    refreshStakeWithTokenStake: (rewardSymbol: string, poolConfig: PoolConfig, flpStakeAccountPk: PublicKey, userPublicKey?: PublicKey | undefined) => Promise<TransactionInstruction>;
    unstakeInstant: (rewardSymbol: string, unstakeAmount: BN, poolConfig: PoolConfig, userPublicKey?: PublicKey | undefined) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    setFeeShareBps: (poolConfig: PoolConfig, flpStakeAccountPks: PublicKey[]) => Promise<TransactionInstruction>;
    unstakeRequest: (unstakeAmount: BN, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    withdrawStake: (poolConfig: PoolConfig, pendingActivation?: boolean, deactivated?: boolean, createUserLPTA?: boolean, userPublicKey?: PublicKey | undefined) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    collectStakeFees: (rewardSymbol: string, poolConfig: PoolConfig, tokenStakeAccount?: PublicKey, createUserATA?: boolean) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    addCompoundingLiquidity: (amountIn: BN, minCompoundingAmountOut: BN, inTokenSymbol: string, rewardTokenMint: PublicKey, poolConfig: PoolConfig, skipBalanceChecks?: boolean, ephemeralSignerPubkey?: any, userPublicKey?: PublicKey | undefined) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    removeCompoundingLiquidity: (compoundingAmountIn: BN, minAmountOut: BN, outTokenSymbol: string, rewardTokenMint: PublicKey, poolConfig: PoolConfig, createUserATA?: boolean, ephemeralSignerPubkey?: any, userPublicKey?: PublicKey | undefined) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    migrateStake: (amount: BN, rewardTokenMint: PublicKey, poolConfig: PoolConfig, createUserATA?: boolean) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    migrateFlp: (amount: BN, rewardTokenMint: PublicKey, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    compoundingFee: (poolConfig: PoolConfig, rewardTokenSymbol?: string) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    burnAndClaim: (owner: PublicKey, nftMint: PublicKey, poolConfig: PoolConfig, createAta: boolean) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    burnAndStake: (owner: PublicKey, feePayer: PublicKey, nftMint: PublicKey, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    depositTokenStake: (owner: PublicKey, feePayer: PublicKey, depositAmount: BN, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    unstakeTokenRequest: (owner: PublicKey, unstakeAmount: BN, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    unstakeTokenInstant: (owner: PublicKey, unstakeAmount: BN, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    withdrawToken: (owner: PublicKey, withdrawRequestId: number, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    cancelUnstakeRequest: (owner: PublicKey, withdrawRequestId: number, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    collectTokenReward: (owner: PublicKey, poolConfig: PoolConfig, createUserATA?: boolean) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    collectRevenue: (owner: PublicKey, rewardSymbol: string, poolConfig: PoolConfig, createUserATA?: boolean) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    initRewardVault: (nftCount: BN, rewardSymbol: string, collectionMint: PublicKey, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    distributeReward: (rewardAmount: BN, rewardSymbol: string, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    collectNftReward: (rewardSymbol: string, poolConfig: PoolConfig, nftMint: PublicKey, createUserATA?: boolean) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    collectAndDistributeFee: (rewardSymbol: string, poolConfig: PoolConfig, createUserATA?: boolean, nftTradingAccount?: PublicKey) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    setTriggerPrice: (targetSymbol: string, collateralSymbol: string, side: Side, triggerPrice: ContractOraclePrice, isStopLoss: boolean, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    forceClosePosition: (positionAccount: PositionAccount, targetSymbol: string, collateralSymbol: string, side: Side, isStopLoss: boolean, poolConfig: PoolConfig, createUserATA?: boolean, closeUsersWSOLATA?: boolean, ephemeralSignerPubkey?: any) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    placeLimitOrder: (targetSymbol: string, collateralSymbol: string, reserveSymbol: string, receiveSymbol: string, side: Side, limitPrice: ContractOraclePrice, reserveAmount: BN, sizeAmount: BN, stopLossPrice: ContractOraclePrice, takeProfitPrice: ContractOraclePrice, poolConfig: PoolConfig, skipBalanceChecks?: boolean, ephemeralSignerPubkey?: any) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    editLimitOrder: (targetSymbol: string, collateralSymbol: string, reserveSymbol: string, receiveSymbol: string, side: Side, orderId: number, limitPrice: ContractOraclePrice, sizeAmount: BN, stopLossPrice: ContractOraclePrice, takeProfitPrice: ContractOraclePrice, poolConfig: PoolConfig, createUserATA?: boolean, ephemeralSignerPubkey?: any) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    executeLimitOrder: (userPubkey: PublicKey, targetSymbol: string, collateralSymbol: string, side: Side, orderId: number, poolConfig: PoolConfig, privilege: Privilege, tokenStakeAccount?: PublicKey, userReferralAccount?: PublicKey, rebateTokenAccount?: PublicKey) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    executeLimitWithSwap: (userPubkey: PublicKey, targetSymbol: string, collateralSymbol: string, reserveSymbol: string, side: Side, orderId: number, poolConfig: PoolConfig, privilege: Privilege, tokenStakeAccount?: PublicKey, userReferralAccount?: PublicKey, rebateTokenAccount?: PublicKey) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    placeTriggerOrder: (targetSymbol: string, collateralSymbol: string, receiveSymbol: string, side: Side, triggerPrice: ContractOraclePrice, deltaSizeAmount: BN, isStopLoss: boolean, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    editTriggerOrder: (targetSymbol: string, collateralSymbol: string, receiveSymbol: string, side: Side, orderId: number, triggerPrice: ContractOraclePrice, deltaSizeAmount: BN, isStopLoss: boolean, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    cancelTriggerOrder: (targetSymbol: string, collateralSymbol: string, side: Side, orderId: number, isStopLoss: boolean, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    cancelAllTriggerOrders: (targetSymbol: string, collateralSymbol: string, side: Side, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    executeTriggerWithSwap: (owner: PublicKey, targetSymbol: string, collateralSymbol: string, receivingSymbol: string, side: Side, orderId: number, isStopLoss: boolean, privilege: Privilege, poolConfig: PoolConfig, createUserATA?: boolean, ephemeralSignerPubkey?: any, tokenStakeAccount?: PublicKey, userReferralAccount?: PublicKey, rebateTokenAccount?: PublicKey) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    executeTriggerOrder: (owner: PublicKey, targetSymbol: string, collateralSymbol: string, side: Side, orderId: number, isStopLoss: boolean, privilege: Privilege, poolConfig: PoolConfig, createUserATA?: boolean, ephemeralSignerPubkey?: any, tokenStakeAccount?: PublicKey, userReferralAccount?: PublicKey, rebateTokenAccount?: PublicKey) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    migrateTriggerOrder: (owner: PublicKey, marketAccount: PublicKey, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    sendTransaction(ixs: TransactionInstruction[], opts?: SendTransactionOpts): Promise<string>;
    sendTransactionV3(ixs: TransactionInstruction[], opts?: SendTransactionOpts): Promise<{
        signature: string;
        versionedTransaction: VersionedTransaction;
    }>;
    swap: (userInputTokenSymbol: string, userOutputTokenSymbol: string, amountIn: BN, minAmountOut: BN, poolConfig: PoolConfig, useFeesPool?: boolean, createUserATA?: boolean, unWrapSol?: boolean, skipBalanceChecks?: boolean, ephemeralSignerPubkey?: any) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    swapFeeInternal: (rewardTokenSymbol: string, swapTokenSymbol: string, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    init: (admins: PublicKey[], config: any) => Promise<void>;
    setAdminSigners: (admins: PublicKey[], minSignatures: number) => Promise<void>;
    addPool: (name: string, maxAumUsd: BN, permissions: Permissions, metadataSymbol: string, metadataTitle: string, metadataUri: string, stakingFeeShareBps: BN, vpVolumeFactor: number) => Promise<void>;
    removePool: (name: string) => Promise<void>;
    addCustody: (poolName: string, tokenMint: PublicKey, isToken222: boolean, isStable: boolean, isVirtual: boolean, oracle: OracleParams, pricing: PricingParams, permissions: Permissions, fees: Fees, borrowRate: BorrowRateParams, ratios: TokenRatios[], depegAdjustment: boolean) => Promise<void>;
    editCustody: (poolName: string, tokenMint: PublicKey, isStable: boolean, oracle: OracleParams, pricing: PricingParams, permissions: Permissions, fees: Fees, borrowRate: BorrowRateParams, ratios: TokenRatios[]) => Promise<void>;
    removeCustody: (poolName: string, tokenMint: PublicKey, ratios: TokenRatios[], poolConfig: PoolConfig) => Promise<void>;
    protocolWithdrawFees: (rewardSymbol: string, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    moveProtocolFees: (rewardSymbol: string, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    setProtocolFeeShareBps: (feeShareBps: BN, poolConfig: PoolConfig) => Promise<TransactionInstruction>;
    setPermissions: (permissions: Permissions) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    reimburse: (tokenMint: PublicKey, amountIn: BN, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    setInternalOraclePrice: (tokenMint: PublicKey, price: BN, expo: number, conf: BN, ema: BN, publishTime: BN, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    setInternalOraclePriceBatch: (tokenMintList: PublicKey[], tokenInternalPrices: InternalPrice[], POOL_CONFIGS: PoolConfig[]) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    setInternalOracleEmaPriceBatch: (tokenMintList: PublicKey[], tokenInternalEmaPrices: InternalEmaPrice[], POOL_CONFIGS: PoolConfig[]) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    renameFlp: (flag: BN, lpTokenName: string, lpTokenSymbol: string, lpTokenUri: string, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    initStake: (stakingFeeShareBps: BN, rewardSymbol: string, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    initCompounding: (feeShareBps: BN, metadataTitle: string, metadataSymbol: string, metadataUri: string, rewardSymbol: string, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    initTokenVault: (token_permissions: TokenPermissions, tokens_to_distribute: BN, withdrawTimeLimit: BN, withdrawInstantFee: BN, stakeLevel: BN[], poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    setTokenVaultConfig: (token_permissions: TokenPermissions, withdrawTimeLimit: BN, withdrawInstantFee: BN, stakeLevel: BN[], poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    withdrawInstantFee: (poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    initRevenueTokenAccount: (feeShareBps: BN, rewardSymbol: string, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    distributeTokenReward: (amount: BN, epochCount: number, rewardSymbol: string, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    setTokenStakeLevel: (owner: PublicKey, stakeLevel: number) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
    setTokenReward: (owner: PublicKey, amount: BN, epochCount: number, poolConfig: PoolConfig) => Promise<{
        instructions: TransactionInstruction[];
        additionalSigners: Signer[];
    }>;
}
