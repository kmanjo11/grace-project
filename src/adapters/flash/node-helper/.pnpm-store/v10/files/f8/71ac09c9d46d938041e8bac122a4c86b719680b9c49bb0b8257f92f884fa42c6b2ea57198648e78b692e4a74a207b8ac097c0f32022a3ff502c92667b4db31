"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.MarketAccount = void 0;
var web3_js_1 = require("@solana/web3.js");
var types_1 = require("./types");
var PositionAccount_1 = require("./PositionAccount");
var constants_1 = require("./constants");
var MarketAccount = (function () {
    function MarketAccount(publicKey, parseData) {
        this.publicKey = publicKey;
        Object.assign(this, parseData);
    }
    MarketAccount.from = function (publicKey, parseData) {
        return new MarketAccount(publicKey, parseData);
    };
    MarketAccount.prototype.updateMarketData = function (market) {
        Object.assign(this, __assign({}, market));
    };
    MarketAccount.prototype.getCollectivePosition = function () {
        if (this.collectivePosition.openPositions.gt(constants_1.BN_ZERO)) {
            var obj = __assign({ entryPrice: this.collectivePosition.averageEntryPrice, sizeAmount: this.collectivePosition.sizeAmount, sizeUsd: this.collectivePosition.sizeUsd, collateralAmount: this.collectivePosition.collateralAmount, collateralUsd: this.collectivePosition.collateralUsd, lockedAmount: this.collectivePosition.lockedAmount, lockedUsd: this.collectivePosition.lockedUsd, unsettledFeesUsd: this.collectivePosition.unsettledFeeUsd, cumulativeLockFeeSnapshot: this.collectivePosition.cumulativeLockFeeSnapshot }, types_1.DEFAULT_POSITION);
            return new PositionAccount_1.PositionAccount(web3_js_1.PublicKey.default, obj);
        }
        else {
            return new PositionAccount_1.PositionAccount(web3_js_1.PublicKey.default, types_1.DEFAULT_POSITION);
        }
    };
    return MarketAccount;
}());
exports.MarketAccount = MarketAccount;
