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
exports.OrderAccount = void 0;
var OrderAccount = (function () {
    function OrderAccount(publicKey, parseData) {
        this.publicKey = publicKey;
        Object.assign(this, parseData);
    }
    OrderAccount.from = function (publicKey, parseData) {
        return new OrderAccount(publicKey, parseData);
    };
    OrderAccount.prototype.clone = function () {
        return __assign({}, this);
    };
    OrderAccount.prototype.updateOrderAccountData = function (order) {
        Object.assign(this, __assign({}, order));
    };
    return OrderAccount;
}());
exports.OrderAccount = OrderAccount;
