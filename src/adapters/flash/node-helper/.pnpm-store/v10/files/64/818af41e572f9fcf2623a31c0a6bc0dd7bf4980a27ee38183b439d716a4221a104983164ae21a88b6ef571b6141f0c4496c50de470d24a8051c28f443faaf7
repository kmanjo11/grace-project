"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TransactionFailError = exports.createComputeBudgetIx = void 0;
exports.sendTransaction = sendTransaction;
exports.confirmTransaction = confirmTransaction;
exports.sendTransactionV2 = sendTransactionV2;
exports.confirmTransactionV2 = confirmTransactionV2;
exports.sendTransactionV3 = sendTransactionV3;
exports.confirmTransactionV3 = confirmTransactionV3;
var nodewallet_1 = __importDefault(require("@coral-xyz/anchor/dist/cjs/nodewallet"));
var bytes_1 = require("@coral-xyz/anchor/dist/cjs/utils/bytes");
var web3_js_1 = require("@solana/web3.js");
function sendTransaction(provider_1, ixs_1) {
    return __awaiter(this, arguments, void 0, function (provider, ixs, opts) {
        var connection, latestBlockhash, _a, payer, message, vtx, signature;
        var _b, _c, _d, _e;
        if (opts === void 0) { opts = {}; }
        return __generator(this, function (_f) {
            switch (_f.label) {
                case 0:
                    connection = provider.connection;
                    if (!((_b = opts.latestBlockhash) !== null && _b !== void 0)) return [3, 1];
                    _a = _b;
                    return [3, 3];
                case 1: return [4, connection.getLatestBlockhash((_d = (_c = opts.preflightCommitment) !== null && _c !== void 0 ? _c : provider.opts.preflightCommitment) !== null && _d !== void 0 ? _d : 'finalized')];
                case 2:
                    _a = (_f.sent());
                    _f.label = 3;
                case 3:
                    latestBlockhash = _a;
                    payer = provider.wallet;
                    if (opts.prioritizationFee) {
                        ixs = __spreadArray(__spreadArray([], ixs, true), [(0, exports.createComputeBudgetIx)(opts.prioritizationFee)], false);
                    }
                    message = web3_js_1.MessageV0.compile({
                        payerKey: provider.wallet.publicKey,
                        instructions: ixs,
                        recentBlockhash: latestBlockhash.blockhash,
                        addressLookupTableAccounts: opts.alts,
                    });
                    vtx = new web3_js_1.VersionedTransaction(message);
                    if ((_e = opts === null || opts === void 0 ? void 0 : opts.additionalSigners) === null || _e === void 0 ? void 0 : _e.length) {
                        vtx.sign(__spreadArray([], opts === null || opts === void 0 ? void 0 : opts.additionalSigners, true));
                    }
                    if (!(typeof payer.signTransaction === 'function' &&
                        !(payer instanceof nodewallet_1.default || payer.constructor.name == 'NodeWallet'))) return [3, 5];
                    return [4, payer.signTransaction(vtx)];
                case 4:
                    vtx = (_f.sent());
                    return [3, 6];
                case 5:
                    vtx.sign([payer.payer]);
                    _f.label = 6;
                case 6: return [4, connection.sendTransaction(vtx, {
                        skipPreflight: true,
                    })];
                case 7:
                    signature = _f.sent();
                    return [2, signature];
            }
        });
    });
}
function confirmTransaction(provider_1, signature_1) {
    return __awaiter(this, arguments, void 0, function (provider, signature, opts) {
        var connection, latestBlockhash, _a, txConfirmationCommitment, status;
        var _b, _c, _d, _e;
        if (opts === void 0) { opts = {}; }
        return __generator(this, function (_f) {
            switch (_f.label) {
                case 0:
                    connection = provider.connection;
                    if (!((_b = opts.latestBlockhash) !== null && _b !== void 0)) return [3, 1];
                    _a = _b;
                    return [3, 3];
                case 1: return [4, connection.getLatestBlockhash((_d = (_c = opts.preflightCommitment) !== null && _c !== void 0 ? _c : provider.opts.preflightCommitment) !== null && _d !== void 0 ? _d : 'finalized')];
                case 2:
                    _a = (_f.sent());
                    _f.label = 3;
                case 3:
                    latestBlockhash = _a;
                    txConfirmationCommitment = (_e = opts.txConfirmationCommitment) !== null && _e !== void 0 ? _e : 'processed';
                    if (!(latestBlockhash.blockhash != null &&
                        latestBlockhash.lastValidBlockHeight != null)) return [3, 5];
                    return [4, connection.confirmTransaction({
                            signature: signature,
                            blockhash: latestBlockhash.blockhash,
                            lastValidBlockHeight: latestBlockhash.lastValidBlockHeight,
                        }, txConfirmationCommitment)];
                case 4:
                    status = (_f.sent()).value;
                    return [3, 7];
                case 5: return [4, connection.confirmTransaction(signature, txConfirmationCommitment)];
                case 6:
                    status = (_f.sent()).value;
                    _f.label = 7;
                case 7:
                    if (status.err) {
                        console.warn('Tx status: ', status);
                        throw new TransactionFailError({
                            txid: signature,
                            message: "".concat(JSON.stringify(status)),
                        });
                    }
                    return [2, signature];
            }
        });
    });
}
function sendTransactionV2(provider_1, ixs_1) {
    return __awaiter(this, arguments, void 0, function (provider, ixs, opts) {
        var connection, latestBlockhash, _a, payer, message, vtx, signature;
        var _b, _c, _d, _e;
        if (opts === void 0) { opts = {}; }
        return __generator(this, function (_f) {
            switch (_f.label) {
                case 0:
                    connection = provider.connection;
                    if (!((_b = opts.latestBlockhash) !== null && _b !== void 0)) return [3, 1];
                    _a = _b;
                    return [3, 3];
                case 1: return [4, connection.getLatestBlockhash((_d = (_c = opts.preflightCommitment) !== null && _c !== void 0 ? _c : provider.opts.preflightCommitment) !== null && _d !== void 0 ? _d : 'finalized')];
                case 2:
                    _a = (_f.sent());
                    _f.label = 3;
                case 3:
                    latestBlockhash = _a;
                    payer = provider.wallet;
                    if (opts.prioritizationFee) {
                        ixs = __spreadArray(__spreadArray([], ixs, true), [(0, exports.createComputeBudgetIx)(opts.prioritizationFee)], false);
                    }
                    message = web3_js_1.MessageV0.compile({
                        payerKey: provider.wallet.publicKey,
                        instructions: ixs,
                        recentBlockhash: latestBlockhash.blockhash,
                        addressLookupTableAccounts: opts.alts,
                    });
                    vtx = new web3_js_1.VersionedTransaction(message);
                    if ((_e = opts === null || opts === void 0 ? void 0 : opts.additionalSigners) === null || _e === void 0 ? void 0 : _e.length) {
                        vtx.sign(__spreadArray([], opts === null || opts === void 0 ? void 0 : opts.additionalSigners, true));
                    }
                    if (!(typeof payer.signTransaction === 'function' &&
                        !(payer instanceof nodewallet_1.default || payer.constructor.name == 'NodeWallet'))) return [3, 5];
                    return [4, payer.signTransaction(vtx)];
                case 4:
                    vtx = (_f.sent());
                    return [3, 6];
                case 5:
                    vtx.sign([payer.payer]);
                    _f.label = 6;
                case 6: return [4, connection.sendTransaction(vtx, {
                        skipPreflight: true,
                    })];
                case 7:
                    signature = _f.sent();
                    return [2, { signature: signature, versionedTransaction: vtx }];
            }
        });
    });
}
var sleep = function (ms) { return new Promise(function (r) { return setTimeout(r, ms); }); };
function confirmTransactionV2(provider_1, versionedTransaction_1, signature_1) {
    return __awaiter(this, arguments, void 0, function (provider, versionedTransaction, signature, opts) {
        var connection, status, done, blockhashResponse, lastValidBlockHeight, blockheight, signatureStatuses, result, x;
        if (opts === void 0) { opts = {}; }
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    connection = provider.connection;
                    done = false;
                    return [4, connection.getLatestBlockhashAndContext()];
                case 1:
                    blockhashResponse = _a.sent();
                    lastValidBlockHeight = blockhashResponse.context.slot + 150;
                    return [4, connection.getBlockHeight()];
                case 2:
                    blockheight = _a.sent();
                    _a.label = 3;
                case 3:
                    if (!(blockheight < lastValidBlockHeight && !done)) return [3, 8];
                    return [4, connection.getSignatureStatuses([signature])];
                case 4:
                    signatureStatuses = _a.sent();
                    result = signatureStatuses && signatureStatuses.value[0];
                    if (!result) {
                    }
                    else if (result.err) {
                        done = true;
                        status = (result.err);
                    }
                    else if (!(['processed', 'confirmed', 'finalized'].includes(result.confirmationStatus))) {
                    }
                    else {
                        done = true;
                        status = (result);
                    }
                    return [4, connection.sendTransaction(versionedTransaction, {
                            skipPreflight: true,
                        })];
                case 5:
                    x = _a.sent();
                    return [4, sleep(1000)];
                case 6:
                    _a.sent();
                    return [4, connection.getBlockHeight()];
                case 7:
                    blockheight = _a.sent();
                    return [3, 3];
                case 8:
                    if (status.err) {
                        console.warn('Tx status: ', status);
                        throw new TransactionFailError({
                            txid: signature,
                            message: "".concat(JSON.stringify(status)),
                        });
                    }
                    return [2, signature];
            }
        });
    });
}
function sendTransactionV3(provider_1, ixs_1) {
    return __awaiter(this, arguments, void 0, function (provider, ixs, opts) {
        var connection, latestBlockhash, _a, payer, message, vtx, tx, signature;
        var _b, _c, _d, _e;
        if (opts === void 0) { opts = {}; }
        return __generator(this, function (_f) {
            switch (_f.label) {
                case 0:
                    connection = provider.connection;
                    if (!((_b = opts.latestBlockhash) !== null && _b !== void 0)) return [3, 1];
                    _a = _b;
                    return [3, 3];
                case 1: return [4, connection.getLatestBlockhash((_d = (_c = opts.preflightCommitment) !== null && _c !== void 0 ? _c : provider.opts.preflightCommitment) !== null && _d !== void 0 ? _d : 'finalized')];
                case 2:
                    _a = (_f.sent());
                    _f.label = 3;
                case 3:
                    latestBlockhash = _a;
                    payer = provider.wallet;
                    message = web3_js_1.MessageV0.compile({
                        payerKey: provider.wallet.publicKey,
                        instructions: ixs,
                        recentBlockhash: latestBlockhash.blockhash,
                        addressLookupTableAccounts: opts.alts,
                    });
                    vtx = new web3_js_1.VersionedTransaction(message);
                    if ((_e = opts === null || opts === void 0 ? void 0 : opts.additionalSigners) === null || _e === void 0 ? void 0 : _e.length) {
                        vtx.sign(__spreadArray([], opts === null || opts === void 0 ? void 0 : opts.additionalSigners, true));
                    }
                    if (!(typeof payer.signTransaction === 'function' &&
                        !(payer instanceof nodewallet_1.default || payer.constructor.name == 'NodeWallet'))) return [3, 5];
                    return [4, payer.signTransaction(vtx)];
                case 4:
                    vtx = (_f.sent());
                    return [3, 6];
                case 5:
                    vtx.sign([payer.payer]);
                    _f.label = 6;
                case 6:
                    bytes_1.bs58.encode(vtx.serialize());
                    tx = bytes_1.bs58.encode(vtx.serialize());
                    return [4, connection.sendTransaction(vtx, {
                            skipPreflight: true,
                            maxRetries: 0,
                        })];
                case 7:
                    signature = _f.sent();
                    return [2, { signature: signature, versionedTransaction: vtx }];
            }
        });
    });
}
function confirmTransactionV3(provider_1, versionedTransaction_1, signature_1) {
    return __awaiter(this, arguments, void 0, function (provider, versionedTransaction, signature, opts) {
        var connection, status, blockhashResponse, lastValidBlockHeight, blockheight, signatureStatuses, result, x;
        if (opts === void 0) { opts = {}; }
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    connection = provider.connection;
                    return [4, connection.getLatestBlockhashAndContext()];
                case 1:
                    blockhashResponse = _a.sent();
                    lastValidBlockHeight = blockhashResponse.context.slot + 150;
                    return [4, connection.getBlockHeight()];
                case 2:
                    blockheight = _a.sent();
                    _a.label = 3;
                case 3:
                    if (!(blockheight < lastValidBlockHeight)) return [3, 8];
                    console.log('inside while :', signature, blockheight, lastValidBlockHeight);
                    return [4, connection.getSignatureStatuses([signature])];
                case 4:
                    signatureStatuses = _a.sent();
                    result = signatureStatuses && signatureStatuses.value[0];
                    console.log('result:', result, signatureStatuses.value[0]);
                    if (!result) {
                    }
                    else if (result.err) {
                        status = result;
                        console.log('breakinng with err', result.err);
                        return [3, 8];
                    }
                    else if (!['processed', 'confirmed', 'finalized'].includes(result.confirmationStatus)) {
                    }
                    else {
                        status = result;
                        console.log('breakinng with susccess', result);
                        return [3, 8];
                    }
                    console.log('status:', status);
                    return [4, connection.sendTransaction(versionedTransaction, {
                            skipPreflight: true,
                            maxRetries: 0,
                        })];
                case 5:
                    x = _a.sent();
                    console.log('retyr send :', x);
                    return [4, sleep(2000)];
                case 6:
                    _a.sent();
                    return [4, connection.getBlockHeight()];
                case 7:
                    blockheight = _a.sent();
                    return [3, 3];
                case 8:
                    if (status.err) {
                        console.warn('Tx status: ', status);
                        throw new TransactionFailError({
                            txid: signature,
                            message: "".concat(JSON.stringify(status)),
                        });
                    }
                    return [2, signature];
            }
        });
    });
}
var createComputeBudgetIx = function (microLamports) {
    var computeBudgetIx = web3_js_1.ComputeBudgetProgram.setComputeUnitPrice({
        microLamports: microLamports,
    });
    return computeBudgetIx;
};
exports.createComputeBudgetIx = createComputeBudgetIx;
var TransactionFailError = (function (_super) {
    __extends(TransactionFailError, _super);
    function TransactionFailError(_a) {
        var txid = _a.txid, message = _a.message;
        var _this = _super.call(this) || this;
        _this.message = message;
        _this.txid = txid;
        return _this;
    }
    return TransactionFailError;
}(Error));
exports.TransactionFailError = TransactionFailError;
