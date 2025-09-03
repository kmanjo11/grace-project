import { Connection, PublicKey } from '@solana/web3.js';
export declare function createLookupTable(authority: PublicKey, payer: PublicKey, connection: Connection): Promise<{
    lookupTableInst: import("@solana/web3.js").TransactionInstruction;
    lookUpTableAddress: PublicKey;
}>;
export declare function addAddressesToTable(authority: PublicKey, payer: PublicKey, lookUpTableAddress: PublicKey, addressesToAdd: PublicKey[]): Promise<import("@solana/web3.js").TransactionInstruction>;
export declare function getAddressesInTable(connection: Connection, lookUpTableAddress: PublicKey): Promise<PublicKey[]>;
