import { AnchorProvider } from '@coral-xyz/anchor';
import { AddressLookupTableAccount, BlockhashWithExpiryBlockHeight, Commitment, Signer, TransactionInstruction, VersionedTransaction } from '@solana/web3.js';
export interface SendTransactionOpts {
    postSendTxCallback?: ({ txid }: {
        txid: any;
    }) => void;
    latestBlockhash?: BlockhashWithExpiryBlockHeight;
    preflightCommitment?: Commitment;
    prioritizationFee?: number;
    additionalSigners?: Signer[];
    alts?: AddressLookupTableAccount[];
}
export declare function sendTransaction(provider: AnchorProvider, ixs: TransactionInstruction[], opts?: SendTransactionOpts): Promise<string>;
export declare function confirmTransaction(provider: AnchorProvider, signature: string, opts?: any): Promise<string>;
export declare function sendTransactionV2(provider: AnchorProvider, ixs: TransactionInstruction[], opts?: SendTransactionOpts): Promise<{
    signature: string;
    versionedTransaction: VersionedTransaction;
}>;
export declare function confirmTransactionV2(provider: AnchorProvider, versionedTransaction: VersionedTransaction, signature: string, opts?: any): Promise<string>;
export declare function sendTransactionV3(provider: AnchorProvider, ixs: TransactionInstruction[], opts?: SendTransactionOpts): Promise<{
    signature: string;
    versionedTransaction: VersionedTransaction;
}>;
export declare function confirmTransactionV3(provider: AnchorProvider, versionedTransaction: VersionedTransaction, signature: string, opts?: any): Promise<string>;
export declare const createComputeBudgetIx: (microLamports: number) => TransactionInstruction;
export declare class TransactionFailError extends Error {
    message: string;
    txid: string;
    constructor({ txid, message }: {
        txid: any;
        message: any;
    });
}
