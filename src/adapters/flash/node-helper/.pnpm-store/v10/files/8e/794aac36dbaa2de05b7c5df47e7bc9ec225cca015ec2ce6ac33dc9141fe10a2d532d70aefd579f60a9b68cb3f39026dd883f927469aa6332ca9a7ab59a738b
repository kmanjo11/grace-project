"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.PoolDataClient = void 0;
var constants_1 = require("./constants");
var anchor_1 = require("@coral-xyz/anchor");
var utils_1 = require("./utils");
var bignumber_js_1 = __importDefault(require("bignumber.js"));
var PoolDataClient = (function () {
    function PoolDataClient(poolConfig, pool, lpTokenInfo, custodies) {
        this.poolConfig = poolConfig;
        this.pool = pool;
        this.lpTokenInfo = lpTokenInfo;
        this.custodies = custodies;
    }
    PoolDataClient.prototype.loadCustodies = function (custodies) {
        this.custodies = custodies;
    };
    PoolDataClient.prototype.loadPoolData = function (pool) {
        this.pool = pool;
    };
    PoolDataClient.prototype.loadLpData = function (lpTokenInfo) {
        this.lpTokenInfo = lpTokenInfo;
    };
    PoolDataClient.prototype.getLpStats = function (pricesMap) {
        var stableCoinAmountBni = new bignumber_js_1.default(0);
        var totalPoolValueUsdBnUi = new bignumber_js_1.default(0);
        var _loop_1 = function (custodyConfig) {
            if (custodyConfig.isVirtual)
                return "continue";
            var custodyAccount = this_1.custodies.find(function (t) { return t.mint.toBase58() === custodyConfig.mintKey.toBase58(); });
            if (custodyAccount) {
                var priceBnUi = new bignumber_js_1.default(pricesMap.get(custodyConfig.symbol).price.toUiPrice(8));
                var ownedBnUi = new bignumber_js_1.default(custodyAccount.assets.owned.toString()).dividedBy(Math.pow(10, custodyConfig.decimals));
                var ownedUsdBnUi = ownedBnUi.multipliedBy(priceBnUi);
                if (custodyAccount.isStable) {
                    stableCoinAmountBni = stableCoinAmountBni.plus(ownedBnUi);
                }
                totalPoolValueUsdBnUi = totalPoolValueUsdBnUi.plus(ownedUsdBnUi);
            }
        };
        var this_1 = this;
        for (var _i = 0, _a = this.poolConfig.custodies; _i < _a.length; _i++) {
            var custodyConfig = _a[_i];
            _loop_1(custodyConfig);
        }
        var lpTokenSupplyUi = new bignumber_js_1.default(this.lpTokenInfo.supply.toString()).dividedBy(Math.pow(10, constants_1.LP_DECIMALS));
        var lpTokenPriceUsdBnUi = this.lpTokenInfo.supply.toString() === '0' ?
            totalPoolValueUsdBnUi :
            totalPoolValueUsdBnUi.dividedBy(lpTokenSupplyUi);
        var stableCoinPercentageBnUi = stableCoinAmountBni.multipliedBy(100).dividedBy(totalPoolValueUsdBnUi);
        return {
            lpTokenSupply: new anchor_1.BN(this.lpTokenInfo.supply.toString()),
            decimals: this.poolConfig.lpDecimals,
            totalPoolValueUsd: (0, utils_1.uiDecimalsToNative)(totalPoolValueUsdBnUi.toString(), constants_1.USD_DECIMALS),
            totalPoolValueUsdUi: totalPoolValueUsdBnUi.toFixed(2, bignumber_js_1.default.ROUND_DOWN),
            price: ((0, utils_1.uiDecimalsToNative)(lpTokenPriceUsdBnUi.toString(), constants_1.USD_DECIMALS)),
            priceUi: lpTokenPriceUsdBnUi.toFixed(2, bignumber_js_1.default.ROUND_DOWN),
            stableCoinPercentage: stableCoinPercentageBnUi.toFixed(2, bignumber_js_1.default.ROUND_DOWN),
            marketCap: (0, utils_1.uiDecimalsToNative)(totalPoolValueUsdBnUi.toString(), constants_1.USD_DECIMALS),
        };
    };
    PoolDataClient.prototype.getCustodyStats = function (pricesMap) {
        var totalPoolValueUsd = this.getLpStats(pricesMap).totalPoolValueUsd;
        var totalPoolValueUsdUi = totalPoolValueUsd.isZero() ? '0' : (0, utils_1.nativeToUiDecimals)(totalPoolValueUsd, constants_1.USD_DECIMALS, constants_1.USD_DECIMALS);
        var custodyDetails = [];
        var _loop_2 = function (i) {
            var custodyConfig = this_2.poolConfig.custodies[i];
            if (custodyConfig.isVirtual)
                return "continue";
            var tokenRatio = this_2.pool.ratios[i];
            var custodyAccount = this_2.custodies.find(function (t) { return t.mint.toBase58() === custodyConfig.mintKey.toBase58(); });
            if (!custodyAccount)
                return "continue";
            var priceBnUi = new bignumber_js_1.default(pricesMap.get(custodyConfig.symbol).price.toUiPrice(8));
            var ownedBnUi = new bignumber_js_1.default(custodyAccount.assets.owned.toString()).dividedBy(Math.pow(10, custodyConfig.decimals));
            var ownedUsdBnUi = ownedBnUi.multipliedBy(priceBnUi);
            var lockedBnUi = new bignumber_js_1.default(custodyAccount.assets.locked.toString()).dividedBy(Math.pow(10, custodyConfig.decimals));
            var utilizationBnUi = (custodyAccount.assets.locked.isZero() || custodyAccount.assets.owned.isZero()) ? new bignumber_js_1.default(0) :
                lockedBnUi.dividedBy(ownedBnUi).multipliedBy(100);
            var currentRatioBnUi = totalPoolValueUsd.isZero() ? new bignumber_js_1.default(0) : ownedBnUi.multipliedBy(priceBnUi).dividedBy(totalPoolValueUsdUi).multipliedBy(100);
            var minRatioBnUi = tokenRatio.min.isZero() ? new bignumber_js_1.default(5) : new bignumber_js_1.default(tokenRatio.min.toString()).div(100);
            var maxRatioBnUi = tokenRatio.max.toString() === '10000' ? new bignumber_js_1.default(95) : new bignumber_js_1.default(tokenRatio.max.toString()).div(100);
            var availableToAddUsdBnUi = currentRatioBnUi.isGreaterThanOrEqualTo(maxRatioBnUi) ?
                new bignumber_js_1.default(0) :
                maxRatioBnUi.minus(currentRatioBnUi).multipliedBy(totalPoolValueUsdUi).div(100);
            var availableToAddAmountBnUi = availableToAddUsdBnUi.dividedBy(priceBnUi);
            var availableToRemoveUsdUi = minRatioBnUi.isGreaterThanOrEqualTo(currentRatioBnUi) ?
                new bignumber_js_1.default(0) :
                currentRatioBnUi.minus(minRatioBnUi).multipliedBy(totalPoolValueUsdUi).div(100);
            var availableToRemoveAmountBnUi = availableToRemoveUsdUi.dividedBy(priceBnUi);
            var minCapacityUsdBnUi = minRatioBnUi.multipliedBy(totalPoolValueUsdUi).div(100);
            var minCapacityAmountBnUi = minCapacityUsdBnUi.dividedBy(priceBnUi);
            var maxCapacityUsdBnUi = maxRatioBnUi.multipliedBy(totalPoolValueUsdUi).div(100);
            var maxCapacityAmountBnUi = maxCapacityUsdBnUi.dividedBy(priceBnUi);
            if (custodyAccount && tokenRatio) {
                custodyDetails.push({
                    symbol: custodyConfig.symbol,
                    priceUi: pricesMap.get(custodyConfig.symbol).price.toUiPrice(custodyConfig.usdPrecision),
                    minRatio: tokenRatio.min,
                    minRatioUi: (0, utils_1.nativeToUiDecimals)(tokenRatio.min, 2, 2),
                    maxRatio: tokenRatio.max,
                    maxRatioUi: (0, utils_1.nativeToUiDecimals)(tokenRatio.max, 2, 2),
                    targetRatio: tokenRatio.target,
                    targetRatioUi: (0, utils_1.nativeToUiDecimals)(tokenRatio.target, 2, 2),
                    currentRatio: (0, utils_1.uiDecimalsToNative)(currentRatioBnUi.toString(), 2),
                    currentRatioUi: currentRatioBnUi.toFixed(2, bignumber_js_1.default.ROUND_DOWN),
                    utilizationUi: utilizationBnUi.toFixed(2, bignumber_js_1.default.ROUND_DOWN),
                    lockedAmountUi: lockedBnUi.toFixed(4, bignumber_js_1.default.ROUND_DOWN),
                    assetsOwnedAmountUi: ownedBnUi.toFixed(4, bignumber_js_1.default.ROUND_DOWN),
                    totalUsdOwnedAmountUi: ownedUsdBnUi.toFixed(2, bignumber_js_1.default.ROUND_DOWN),
                    availableToAddAmountUi: availableToAddAmountBnUi.toFixed(4, bignumber_js_1.default.ROUND_DOWN),
                    availableToAddUsdUi: availableToAddUsdBnUi.toFixed(2, bignumber_js_1.default.ROUND_DOWN),
                    availableToRemoveAmountUi: availableToRemoveAmountBnUi.toFixed(4, bignumber_js_1.default.ROUND_DOWN),
                    availableToRemoveUsdUi: availableToRemoveUsdUi.toFixed(2, bignumber_js_1.default.ROUND_DOWN),
                    minCapacityAmountUi: minCapacityAmountBnUi.toFixed(custodyConfig.decimals),
                    maxCapacityAmountUi: maxCapacityAmountBnUi.toFixed(custodyConfig.decimals),
                });
            }
        };
        var this_2 = this;
        for (var i = 0; i < this.poolConfig.custodies.length; i++) {
            _loop_2(i);
        }
        return custodyDetails;
    };
    return PoolDataClient;
}());
exports.PoolDataClient = PoolDataClient;
