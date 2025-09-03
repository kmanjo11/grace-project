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
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewHelper = void 0;
var web3_js_1 = require("@solana/web3.js");
var base64_1 = require("@coral-xyz/anchor/dist/cjs/utils/bytes/base64");
var perpetuals_1 = require("./idl/perpetuals");
var IdlCoder_1 = require("./utils/IdlCoder");
var ViewHelper = (function () {
    function ViewHelper(client) {
        this.perpetualsClient = client;
    }
    ViewHelper.prototype.decodeLogs = function (data, instructionNumber, instructionName) {
        var _a, _b, _c;
        if (instructionName === void 0) { instructionName = ''; }
        try {
            var returnPrefix_1 = "Program return: ".concat(this.perpetualsClient.programId, " ");
            if (data.value.logs && data.value.err === null) {
                var returnLog = data.value.logs.find(function (l) { return l.startsWith(returnPrefix_1); });
                if (!returnLog) {
                    throw new Error('View expected return log');
                }
                var returnData = (0, base64_1.decode)(returnLog.slice(returnPrefix_1.length));
                var returnType = perpetuals_1.IDL.instructions[instructionNumber].returns;
                if (!returnType) {
                    throw new Error('View expected return type');
                }
                var coder = IdlCoder_1.IdlCoder.fieldLayout({ type: returnType }, Array.from(__spreadArray(__spreadArray([], ((_a = perpetuals_1.IDL.accounts) !== null && _a !== void 0 ? _a : []), true), ((_b = perpetuals_1.IDL.types) !== null && _b !== void 0 ? _b : []), true)));
                return coder.decode(returnData);
            }
            else {
                console.error('No Logs Found : name : data:', instructionName, data);
                console.error('Logs err::', (_c = data.value.logs) === null || _c === void 0 ? void 0 : _c.toString());
                throw new Error("FLASH No Logs Found ".concat({ cause: data }));
            }
        }
        catch (error) {
            console.log("decode error::", error);
        }
    };
    ViewHelper.prototype.simulateTransaction = function (transaction_1) {
        return __awaiter(this, arguments, void 0, function (transaction, userPublicKey) {
            var latestBlockhash, messageV0, transaction2;
            if (userPublicKey === void 0) { userPublicKey = undefined; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        transaction.feePayer = userPublicKey !== null && userPublicKey !== void 0 ? userPublicKey : this.perpetualsClient.provider.publicKey;
                        return [4, this.perpetualsClient.provider.connection.getLatestBlockhash('confirmed')];
                    case 1:
                        latestBlockhash = _a.sent();
                        messageV0 = new web3_js_1.TransactionMessage({
                            payerKey: this.perpetualsClient.provider.publicKey,
                            recentBlockhash: latestBlockhash.blockhash,
                            instructions: transaction.instructions,
                        }).compileToV0Message(this.perpetualsClient.addressLookupTables);
                        transaction2 = new web3_js_1.VersionedTransaction(messageV0);
                        return [2, this.perpetualsClient.provider.connection.simulateTransaction(transaction2, { sigVerify: false, replaceRecentBlockhash: true })];
                }
            });
        });
    };
    return ViewHelper;
}());
exports.ViewHelper = ViewHelper;
