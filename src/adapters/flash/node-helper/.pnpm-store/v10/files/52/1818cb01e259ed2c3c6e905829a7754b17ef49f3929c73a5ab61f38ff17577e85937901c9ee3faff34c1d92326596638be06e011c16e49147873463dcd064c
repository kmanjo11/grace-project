"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TradingAccount = void 0;
var TradingAccount = (function () {
    function TradingAccount(publicKey, parseData) {
        this.publicKey = publicKey;
        Object.assign(this, parseData);
    }
    TradingAccount.from = function (publicKey, parseData) {
        return new TradingAccount(publicKey, parseData);
    };
    TradingAccount.prototype.updatePoolData = function (parseData) {
        Object.assign(this, parseData);
    };
    return TradingAccount;
}());
exports.TradingAccount = TradingAccount;
