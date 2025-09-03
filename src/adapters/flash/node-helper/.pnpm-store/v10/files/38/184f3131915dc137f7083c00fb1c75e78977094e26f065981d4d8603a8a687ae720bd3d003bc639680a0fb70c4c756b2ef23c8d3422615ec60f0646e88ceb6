"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TokenStakeAccount = void 0;
var anchor_1 = require("@coral-xyz/anchor");
var TokenStakeAccount = (function () {
    function TokenStakeAccount(data) {
        this.owner = data.owner;
        this.isInitialized = data.isInitialized;
        this.bump = data.bump;
        this.level = data.level;
        this.withdrawRequestCount = data.withdrawRequestCount;
        this.withdrawRequest = data.withdrawRequest;
        this.activeStakeAmount = data.activeStakeAmount;
        this.updateTimestamp = data.updateTimestamp;
        this.tradeTimestamp = data.tradeTimestamp;
        this.tradeCounter = data.tradeCounter;
        this.rewardTokens = data.rewardTokens;
        this.lastRewardEpochCount = data.lastRewardEpochCount;
        this.unclaimedRevenueAmount = data.unclaimedRevenueAmount;
        this.revenueSnapshot = data.revenueSnapshot;
        this.padding = data.padding;
    }
    TokenStakeAccount.from = function (decodedData) {
        return new TokenStakeAccount({
            owner: decodedData.owner,
            isInitialized: decodedData.isInitialized,
            bump: decodedData.bump,
            level: decodedData.level,
            withdrawRequestCount: decodedData.withdrawRequestCount,
            withdrawRequest: decodedData.withdrawRequest,
            activeStakeAmount: new anchor_1.BN(decodedData.activeStakeAmount),
            updateTimestamp: new anchor_1.BN(decodedData.updateTimestamp),
            tradeTimestamp: new anchor_1.BN(decodedData.tradeTimestamp),
            tradeCounter: decodedData.tradeCounter,
            rewardTokens: new anchor_1.BN(decodedData.rewardTokens),
            lastRewardEpochCount: decodedData.lastRewardEpochCount,
            unclaimedRevenueAmount: decodedData.unclaimedRevenueAmount,
            revenueSnapshot: decodedData.revenueSnapshot,
            padding: decodedData.padding.map(function (p) { return new anchor_1.BN(p); }),
        });
    };
    TokenStakeAccount.prototype.updateData = function (newData) {
        Object.assign(this, newData);
    };
    return TokenStakeAccount;
}());
exports.TokenStakeAccount = TokenStakeAccount;
