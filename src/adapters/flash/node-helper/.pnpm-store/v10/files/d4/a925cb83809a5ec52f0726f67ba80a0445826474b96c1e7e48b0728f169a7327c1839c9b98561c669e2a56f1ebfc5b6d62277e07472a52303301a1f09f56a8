"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DEFAULT_POSITION = exports.FeesAction = exports.FeesMode = exports.OracleType = exports.Side = exports.Privilege = void 0;
exports.isVariant = isVariant;
exports.isOneOfVariant = isOneOfVariant;
var web3_js_1 = require("@solana/web3.js");
var constants_1 = require("../constants");
function isVariant(object, type) {
    return object.hasOwnProperty(type);
}
function isOneOfVariant(object, types) {
    return types.reduce(function (result, type) {
        return result || object.hasOwnProperty(type);
    }, false);
}
var Privilege = (function () {
    function Privilege() {
    }
    Privilege.None = { none: {} };
    Privilege.Stake = { stake: {} };
    Privilege.Referral = { referral: {} };
    return Privilege;
}());
exports.Privilege = Privilege;
var Side = (function () {
    function Side() {
    }
    Side.None = { none: {} };
    Side.Long = { long: {} };
    Side.Short = { short: {} };
    return Side;
}());
exports.Side = Side;
var OracleType = (function () {
    function OracleType() {
    }
    OracleType.None = { none: {} };
    OracleType.Test = { test: {} };
    OracleType.Pyth = { pyth: {} };
    return OracleType;
}());
exports.OracleType = OracleType;
var FeesMode = (function () {
    function FeesMode() {
    }
    FeesMode.Fixed = { fixed: {} };
    FeesMode.Linear = { linear: {} };
    return FeesMode;
}());
exports.FeesMode = FeesMode;
var FeesAction = (function () {
    function FeesAction() {
    }
    FeesAction.AddLiquidity = { addLiquidity: {} };
    FeesAction.RemoveLiquidity = { removeLiquidity: {} };
    FeesAction.SwapIn = { swapIn: {} };
    FeesAction.SwapOut = { swapOut: {} };
    FeesAction.StableSwapIn = { stableSwapIn: {} };
    FeesAction.StableSwapOut = { stableSwapOut: {} };
    return FeesAction;
}());
exports.FeesAction = FeesAction;
exports.DEFAULT_POSITION = {
    owner: web3_js_1.PublicKey.default,
    delegate: web3_js_1.PublicKey.default,
    market: web3_js_1.PublicKey.default,
    openTime: constants_1.BN_ZERO,
    updateTime: constants_1.BN_ZERO,
    entryPrice: { price: constants_1.BN_ZERO, exponent: 0 },
    sizeAmount: constants_1.BN_ZERO,
    sizeUsd: constants_1.BN_ZERO,
    lockedAmount: constants_1.BN_ZERO,
    lockedUsd: constants_1.BN_ZERO,
    collateralAmount: constants_1.BN_ZERO,
    collateralUsd: constants_1.BN_ZERO,
    unsettledAmount: constants_1.BN_ZERO,
    unsettledFeesUsd: constants_1.BN_ZERO,
    cumulativeLockFeeSnapshot: constants_1.BN_ZERO,
    takeProfitPrice: { price: constants_1.BN_ZERO, exponent: 0 },
    stopLossPrice: { price: constants_1.BN_ZERO, exponent: 0 },
    sizeDecimals: 0,
    lockedDecimals: 0,
    collateralDecimals: 0,
    bump: 0
};
