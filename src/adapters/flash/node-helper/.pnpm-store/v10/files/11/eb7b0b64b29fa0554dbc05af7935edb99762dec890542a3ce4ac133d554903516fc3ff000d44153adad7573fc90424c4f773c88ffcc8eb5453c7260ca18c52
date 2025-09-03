import { BN } from "@coral-xyz/anchor";
import { PublicKey } from "@solana/web3.js";
import { LimitOrder, Order, TriggerOrder } from "./types";
export declare class OrderAccount implements Order {
    publicKey: PublicKey;
    owner: PublicKey;
    market: PublicKey;
    limitOrders: LimitOrder[];
    takeProfitOrders: TriggerOrder[];
    stopLossOrders: TriggerOrder[];
    isInitialised: boolean;
    openOrders: number;
    openSl: number;
    openTp: number;
    inactiveSl: number;
    inactiveTp: number;
    activeOrders: number;
    bump: number;
    padding: BN[];
    constructor(publicKey: PublicKey, parseData: Order);
    static from(publicKey: PublicKey, parseData: Order): OrderAccount;
    clone(): OrderAccount;
    updateOrderAccountData(order: Order): void;
}
