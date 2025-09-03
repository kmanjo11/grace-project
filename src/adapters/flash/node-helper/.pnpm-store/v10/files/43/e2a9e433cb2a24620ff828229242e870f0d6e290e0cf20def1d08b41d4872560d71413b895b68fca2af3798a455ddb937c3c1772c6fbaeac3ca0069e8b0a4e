"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.checkedDecimalDiv = exports.checkedDecimalMul = exports.checkedDecimalCeilMul = exports.checkedCeilDiv = exports.scaleToExponent = exports.validateNumberString = exports.uiDecimalsToNative = exports.getUnixTs = void 0;
exports.toUiDecimalsOldSDK = toUiDecimalsOldSDK;
exports.nativeToUiDecimals = nativeToUiDecimals;
exports.checkIfAccountExists = checkIfAccountExists;
var bn_js_1 = __importDefault(require("bn.js"));
var constants_1 = require("../constants");
var bignumber_js_1 = __importDefault(require("bignumber.js"));
var getUnixTs = function () {
    return new Date().getTime() / 1000;
};
exports.getUnixTs = getUnixTs;
function toUiDecimalsOldSDK(nativeAmount, decimals, precision, commaSeperated) {
    if (precision === void 0) { precision = 3; }
    if (commaSeperated === void 0) { commaSeperated = false; }
    if (precision > decimals) {
        throw 'not allowed precision> decimals';
    }
    var r = '';
    if (nativeAmount instanceof bn_js_1.default) {
        var nativeAmountString = nativeAmount.toString();
        var d = nativeAmountString.slice(decimals * -1);
        var p = d.slice(0, precision);
        var nativeAmountWithoutDecimalsStr = nativeAmount.div(new bn_js_1.default(Math.pow(10, decimals))).toString();
        r = nativeAmountWithoutDecimalsStr + '.' + p;
    }
    else if (typeof nativeAmount === 'string') {
        if (isNaN(Number(nativeAmount))) {
            throw 'String No valid ';
        }
        if (nativeAmount.length < decimals) {
            nativeAmount = nativeAmount.padStart(decimals, '0');
        }
        var d = nativeAmount.slice(decimals * -1);
        var p = d.slice(0, precision);
        var nativeAmountWithoutDecimalsStr = new bn_js_1.default(nativeAmount).div(new bn_js_1.default(Math.pow(10, decimals))).toString();
        r = nativeAmountWithoutDecimalsStr + '.' + p;
    }
    else if (typeof nativeAmount === 'number') {
        var d = nativeAmount.toString().slice(decimals * -1);
        var p = d.slice(0, precision);
        var nativeAmountWithoutDecimalsStr = new bn_js_1.default(nativeAmount).div(new bn_js_1.default(Math.pow(10, decimals))).toString();
        r = nativeAmountWithoutDecimalsStr + '.' + p;
    }
    else {
        return 'type unknown';
    }
    if (commaSeperated) {
        return Number(r).toLocaleString();
    }
    else {
        return r;
    }
}
var uiDecimalsToNative = function (amountUi, decimals) {
    var valueBigNumber = (new bignumber_js_1.default(amountUi)).multipliedBy(new bignumber_js_1.default(Math.pow(10, decimals)));
    return new bn_js_1.default(valueBigNumber.toFixed(0, bignumber_js_1.default.ROUND_DOWN));
};
exports.uiDecimalsToNative = uiDecimalsToNative;
var validateNumberString = function (str) {
    if (typeof str === 'undefined') {
        return false;
    }
    if (str.trim() === '') {
        return false;
    }
    if (isNaN(Number(str))) {
        return false;
    }
    return true;
};
exports.validateNumberString = validateNumberString;
function nativeToUiDecimals(nativeAmount, decimals, precision, commaSeperated) {
    if (!precision)
        precision = decimals;
    if (!(0, exports.validateNumberString)(nativeAmount.toString())) {
        console.log("error - nativeAmount:", nativeAmount);
        throw "nativeToUiDecimals error: ".concat(nativeAmount, " Not valid ");
    }
    if (nativeAmount instanceof bignumber_js_1.default) {
    }
    else if (nativeAmount instanceof bn_js_1.default) {
    }
    else if (typeof nativeAmount === 'string') {
        if (isNaN(Number(nativeAmount))) {
            throw new Error("nativeToUiDecimals error: String Not valid ::: ".concat(nativeAmount));
        }
    }
    else if (typeof nativeAmount === 'number') {
    }
    else {
    }
    var denominator = (new bignumber_js_1.default(10)).pow(decimals);
    var r = (new bignumber_js_1.default(nativeAmount.toString())).div(denominator).toFixed(precision, bignumber_js_1.default.ROUND_DOWN);
    if (commaSeperated) {
        return Number(r).toLocaleString('en-US', { maximumFractionDigits: 2, minimumFractionDigits: 2 });
    }
    else {
        return r;
    }
}
function checkIfAccountExists(account, connection) {
    return __awaiter(this, void 0, void 0, function () {
        var bal;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4, connection.getBalance(account)];
                case 1:
                    bal = _a.sent();
                    if (bal > 0) {
                        return [2, true];
                    }
                    else {
                        return [2, false];
                    }
                    return [2];
            }
        });
    });
}
var scaleToExponent = function (arg, exponent, target_exponent) {
    if (target_exponent.eq(exponent)) {
        return arg;
    }
    var delta = target_exponent.sub(exponent);
    if (delta.gt(constants_1.BN_ZERO)) {
        return arg.div(new bn_js_1.default(10).pow(delta));
    }
    else {
        return arg.mul(new bn_js_1.default(10).pow(delta.muln(-1)));
    }
};
exports.scaleToExponent = scaleToExponent;
var checkedCeilDiv = function (arg1, arg2) {
    if (arg1.gt(constants_1.BN_ZERO)) {
        if (arg1.eq(arg2) && !arg2.isZero()) {
            return constants_1.BN_ONE;
        }
        var res = (arg1.sub(constants_1.BN_ONE)).div(arg2);
        if (!res) {
            throw Error("error :: MathOverflow");
        }
        return res.add(constants_1.BN_ONE);
    }
    else {
        var res = (arg1).div(arg2);
        if (!res) {
            throw Error("error :: MathOverflow");
        }
        return res;
    }
};
exports.checkedCeilDiv = checkedCeilDiv;
var checkedDecimalCeilMul = function (coefficient1, exponent1, coefficient2, exponent2, target_exponent) {
    if (coefficient1.isZero() || coefficient2.isZero()) {
        return constants_1.BN_ZERO;
    }
    var target_power = (exponent1.add(exponent2)).sub(target_exponent);
    if (target_power.gt(constants_1.BN_ZERO)) {
        return (coefficient1.mul(coefficient2)).mul(new bn_js_1.default(10).pow(target_power));
    }
    else {
        var a = (coefficient1.mul(coefficient2));
        var b = (new bn_js_1.default(10).pow(target_power.muln(-1)));
        return (0, exports.checkedCeilDiv)(a, b);
    }
};
exports.checkedDecimalCeilMul = checkedDecimalCeilMul;
var checkedDecimalMul = function (coefficient1, exponent1, coefficient2, exponent2, target_exponent) {
    if (coefficient1.isZero() || coefficient2.isZero()) {
        return constants_1.BN_ZERO;
    }
    var target_power = (exponent1.add(exponent2)).sub(target_exponent);
    if (target_power.gt(constants_1.BN_ZERO)) {
        return (coefficient1.mul(coefficient2)).mul(new bn_js_1.default(10).pow(target_power));
    }
    else {
        return (coefficient1.mul(coefficient2))
            .div(new bn_js_1.default(10).pow(target_power.muln(-1)));
    }
};
exports.checkedDecimalMul = checkedDecimalMul;
var checkedDecimalDiv = function (coefficient1, exponent1, coefficient2, exponent2, target_exponent) {
    if (coefficient2.isZero()) {
        throw Error("\"Error: Overflow in ".concat(coefficient1, " / ").concat(coefficient2));
    }
    if (coefficient1.isZero()) {
        return constants_1.BN_ZERO;
    }
    var scale_factor = constants_1.BN_ZERO;
    var target_power = (exponent1.sub(exponent2)).sub(target_exponent);
    if (exponent1.gt(constants_1.BN_ZERO)) {
        scale_factor = scale_factor.add(exponent1);
    }
    if (exponent2.lt(constants_1.BN_ZERO)) {
        scale_factor = scale_factor.sub(exponent2);
        target_power = target_power.add(exponent2);
    }
    if (target_exponent.lt(constants_1.BN_ZERO)) {
        scale_factor = scale_factor.sub(target_exponent);
        target_power = target_power.add(target_exponent);
    }
    var scaled_coeff1 = constants_1.BN_ZERO;
    if (scale_factor.gt(constants_1.BN_ZERO)) {
        scaled_coeff1 = coefficient1.mul(new bn_js_1.default(10).pow(scale_factor));
    }
    else {
        scaled_coeff1 = coefficient1;
    }
    ;
    if (target_power.gte(constants_1.BN_ZERO)) {
        return (scaled_coeff1.div(coefficient2))
            .mul(new bn_js_1.default(10).pow(target_power));
    }
    else {
        return (scaled_coeff1.div(coefficient2))
            .div(new bn_js_1.default(10).pow(target_power.muln(-1)));
    }
};
exports.checkedDecimalDiv = checkedDecimalDiv;
