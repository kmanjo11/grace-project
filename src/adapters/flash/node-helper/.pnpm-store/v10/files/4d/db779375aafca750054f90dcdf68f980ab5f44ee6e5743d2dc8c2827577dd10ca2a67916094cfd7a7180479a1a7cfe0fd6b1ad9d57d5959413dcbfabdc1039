import { PublicKey, RpcResponseAndContext, SimulatedTransactionResponse, Transaction } from "@solana/web3.js";
import { PerpetualsClient } from "./PerpetualsClient";
export declare class ViewHelper {
    private perpetualsClient;
    constructor(client: PerpetualsClient);
    decodeLogs<T>(data: RpcResponseAndContext<SimulatedTransactionResponse>, instructionNumber: number, instructionName?: string): T | undefined;
    simulateTransaction(transaction: Transaction, userPublicKey?: PublicKey | undefined): Promise<RpcResponseAndContext<SimulatedTransactionResponse>>;
}
