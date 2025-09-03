"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OraclePrice = void 0;
var anchor_1 = require("@coral-xyz/anchor");
var constants_1 = require("./constants");
var utils_1 = require("./utils");
var OraclePrice = (function () {
    function OraclePrice(parseData) {
        Object.assign(this, parseData);
    }
    OraclePrice.from = function (parseData) {
        return new OraclePrice(parseData);
    };
    OraclePrice.prototype.toContractOraclePrice = function () {
        return {
            price: this.price,
            exponent: this.exponent.toNumber()
        };
    };
    OraclePrice.prototype.cmp = function (other) {
        var lhs, rhs;
        if (this.exponent.eq(other.exponent)) {
            lhs = this.price;
            rhs = other.price;
        }
        else if (this.exponent.lt(other.exponent)) {
            var scaled_price = other.scale_to_exponent(this.exponent);
            lhs = this.price;
            rhs = scaled_price.price;
        }
        else {
            var scaled_price = this.scale_to_exponent(other.exponent);
            lhs = scaled_price.price;
            rhs = other.price;
        }
        ;
        return lhs.cmp(rhs);
    };
    OraclePrice.prototype.getDivergenceFactor = function (other) {
        var thisPrice, reference;
        if (this.exponent.lte(other.exponent)) {
            thisPrice = this;
            reference = other.scale_to_exponent(this.exponent);
        }
        else {
            thisPrice = this.scale_to_exponent(other.exponent);
            reference = other;
        }
        if (!thisPrice.exponent.eq(reference.exponent)) {
            throw "Exponents mistmatch ".concat(thisPrice.exponent.toNumber(), " != ").concat(reference.exponent.toNumber());
        }
        var factor;
        if (thisPrice.price.gt(reference.price)) {
            factor = OraclePrice.from({ price: (thisPrice.price.sub(reference.price).div(reference.price)), exponent: thisPrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
        }
        else {
            if (!reference.price.isZero()) {
                factor = OraclePrice.from({ price: (reference.price.sub(thisPrice.price).div(reference.price)), exponent: thisPrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
            }
            else {
                factor = OraclePrice.from({ price: constants_1.BN_ZERO, exponent: thisPrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
            }
        }
        return (factor.scale_to_exponent(new anchor_1.BN(-1 * constants_1.BPS_DECIMALS)).price);
    };
    OraclePrice.prototype.scale_to_exponent = function (target_exponent) {
        if (!target_exponent.isNeg()) {
            throw new Error("Target exponent must be negative");
        }
        if (target_exponent.eq(this.exponent)) {
            return this;
        }
        var delta = target_exponent.sub(this.exponent);
        if (delta.gt(constants_1.BN_ZERO)) {
            return new OraclePrice({
                price: this.price.div(new anchor_1.BN(10).pow(delta)),
                confidence: this.confidence.div(new anchor_1.BN(10).pow(delta)),
                exponent: target_exponent
            });
        }
        else {
            return new OraclePrice({
                price: this.price.mul(new anchor_1.BN(10).pow(delta.neg())),
                confidence: this.confidence.mul(new anchor_1.BN(10).pow(delta.neg())),
                exponent: target_exponent
            });
        }
    };
    OraclePrice.prototype.getTokenAmount = function (asset_amount_usd, token_decimals) {
        if (asset_amount_usd.isZero() || this.price.isZero()) {
            return constants_1.BN_ZERO;
        }
        return (0, utils_1.checkedDecimalDiv)(asset_amount_usd, new anchor_1.BN(-1 * constants_1.USD_DECIMALS), this.price, this.exponent, new anchor_1.BN(-1 * token_decimals));
    };
    OraclePrice.prototype.getAssetAmountUsd = function (token_amount, token_decimals) {
        if (token_amount.isZero() || this.price.isZero()) {
            return constants_1.BN_ZERO;
        }
        return (0, utils_1.checkedDecimalMul)(token_amount, new anchor_1.BN(-1 * token_decimals), this.price, this.exponent, new anchor_1.BN(-1 * constants_1.USD_DECIMALS));
    };
    OraclePrice.prototype.toUiPrice = function (precision) {
        return (0, utils_1.nativeToUiDecimals)(this.price, this.exponent.toNumber() * -1, precision);
    };
    return OraclePrice;
}());
exports.OraclePrice = OraclePrice;
