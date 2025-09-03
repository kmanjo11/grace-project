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
exports.CustodyAccount = void 0;
var CustodyAccount = (function () {
    function CustodyAccount(publicKey, parseData) {
        this.publicKey = publicKey;
        Object.assign(this, parseData);
    }
    CustodyAccount.from = function (publicKey, parseData) {
        return new CustodyAccount(publicKey, parseData);
    };
    CustodyAccount.prototype.updateCustodyData = function (custody) {
        Object.assign(this, __assign({}, custody));
    };
    return CustodyAccount;
}());
exports.CustodyAccount = CustodyAccount;
