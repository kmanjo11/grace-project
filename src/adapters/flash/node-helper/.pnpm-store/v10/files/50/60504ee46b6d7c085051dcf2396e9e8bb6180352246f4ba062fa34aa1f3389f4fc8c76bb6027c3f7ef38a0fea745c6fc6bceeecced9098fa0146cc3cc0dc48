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
exports.PositionAccount = void 0;
var PositionAccount = (function () {
    function PositionAccount(publicKey, parseData) {
        this.publicKey = publicKey;
        Object.assign(this, parseData);
    }
    PositionAccount.from = function (publicKey, parseData) {
        return new PositionAccount(publicKey, parseData);
    };
    PositionAccount.prototype.clone = function () {
        return __assign({}, this);
    };
    PositionAccount.prototype.updatePositionData = function (position) {
        Object.assign(this, __assign({}, position));
    };
    return PositionAccount;
}());
exports.PositionAccount = PositionAccount;
