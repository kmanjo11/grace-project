"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PoolAccount = void 0;
var PoolAccount = (function () {
    function PoolAccount(publicKey, parseData) {
        this.publicKey = publicKey;
        Object.assign(this, parseData);
    }
    PoolAccount.from = function (publicKey, parseData) {
        return new PoolAccount(publicKey, parseData);
    };
    PoolAccount.prototype.updatePoolData = function (parseData) {
        Object.assign(this, parseData);
    };
    PoolAccount.prototype.getCustodyId = function (custodyKey) {
        return this.custodies.findIndex(function (i) { return i.toBase58() == custodyKey.toBase58(); });
    };
    return PoolAccount;
}());
exports.PoolAccount = PoolAccount;
