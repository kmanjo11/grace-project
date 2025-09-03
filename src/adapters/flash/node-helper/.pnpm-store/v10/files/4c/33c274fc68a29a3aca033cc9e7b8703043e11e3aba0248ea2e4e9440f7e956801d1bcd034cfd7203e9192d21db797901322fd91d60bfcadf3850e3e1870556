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
var _a;
Object.defineProperty(exports, "__esModule", { value: true });
exports.getBackupOracleInstruction = exports.getPythnetOraclePrices = exports.pythPriceServiceConnection = exports.API_ENDPOINT = void 0;
exports.createBackupOracleInstruction = createBackupOracleInstruction;
var price_service_client_1 = require("@pythnetwork/price-service-client");
var web3_js_1 = require("@solana/web3.js");
var bn_js_1 = __importDefault(require("bn.js"));
var bs58_1 = __importDefault(require("bs58"));
var tweetnacl_1 = __importDefault(require("tweetnacl"));
exports.API_ENDPOINT = (_a = process.env.NEXT_PUBLIC_API_ENDPOINT) !== null && _a !== void 0 ? _a : 'https://api.prod.flash.trade';
exports.pythPriceServiceConnection = new price_service_client_1.PriceServiceConnection('https://hermes.pyth.network', {
    priceFeedRequestConfig: {},
});
var getPythnetOraclePrices = function (program, poolConfig, backupOracleSecretKey) { return __awaiter(void 0, void 0, void 0, function () {
    var custodyMintKeys, pythPriceIds, _loop_1, _i, custodyMintKeys_1, custodyMintKey, currentPrices, backupOracleAccount, caches_1, permissionlessPythCache, message, signature, preInstruction;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                custodyMintKeys = poolConfig.custodies.map(function (f) { return f.mintKey; });
                pythPriceIds = [];
                _loop_1 = function (custodyMintKey) {
                    var t = poolConfig.tokens.find(function (f) { return f.mintKey.equals(custodyMintKey); });
                    if (t) {
                        pythPriceIds.push(t.pythPriceId);
                    }
                };
                for (_i = 0, custodyMintKeys_1 = custodyMintKeys; _i < custodyMintKeys_1.length; _i++) {
                    custodyMintKey = custodyMintKeys_1[_i];
                    _loop_1(custodyMintKey);
                }
                return [4, exports.pythPriceServiceConnection.getLatestPriceFeeds(pythPriceIds)];
            case 1:
                currentPrices = _a.sent();
                if (!currentPrices)
                    return [2];
                backupOracleAccount = web3_js_1.Keypair.fromSecretKey(bs58_1.default.decode(backupOracleSecretKey));
                if (pythPriceIds.length === currentPrices.length) {
                    caches_1 = currentPrices.map(function (price) {
                        var uncheckedPrice = price.getPriceUnchecked();
                        var uncheckedEmaPrice = price.getEmaPriceUnchecked();
                        return {
                            price: new bn_js_1.default(uncheckedPrice.price),
                            expo: uncheckedPrice.expo,
                            conf: new bn_js_1.default(uncheckedPrice.conf),
                            emaPrice: new bn_js_1.default(uncheckedEmaPrice.price),
                            publishTime: new bn_js_1.default(uncheckedPrice.publishTime)
                        };
                    });
                    permissionlessPythCache = {
                        backupCache: caches_1
                    };
                    message = program._coder.types.encode('PermissionlessPythCache', permissionlessPythCache);
                    signature = tweetnacl_1.default.sign.detached(message, backupOracleAccount.secretKey);
                    preInstruction = web3_js_1.Ed25519Program.createInstructionWithPublicKey({
                        publicKey: backupOracleAccount.publicKey.toBytes(),
                        message: message,
                        signature: signature,
                    });
                    return [2, preInstruction];
                }
                return [2];
        }
    });
}); };
exports.getPythnetOraclePrices = getPythnetOraclePrices;
var getBackupOracleInstruction = function (program, poolConfig, backupOracleSecretKey, backupCaches) {
    var custodiesLength = poolConfig.custodies.length;
    if (!backupCaches.length) {
        console.error("incorrect prices passed ,", custodiesLength, backupCaches.length);
        throw new Error("incorrect prices passed : custodiesLength: ".concat(custodiesLength, " , backupCaches.length: ").concat(backupCaches.length));
    }
    ;
    var backupOracleAccount = web3_js_1.Keypair.fromSecretKey(bs58_1.default.decode(backupOracleSecretKey));
    if (custodiesLength === backupCaches.length) {
        var permissionlessPythCache = {
            backupCache: backupCaches
        };
        var message = program._coder.types.encode('PermissionlessPythCache', permissionlessPythCache);
        var signature = tweetnacl_1.default.sign.detached(message, backupOracleAccount.secretKey);
        var preInstruction = web3_js_1.Ed25519Program.createInstructionWithPublicKey({
            publicKey: backupOracleAccount.publicKey.toBytes(),
            message: message,
            signature: signature,
        });
        return preInstruction;
    }
    else {
        console.error("incorrect prices passed ,", custodiesLength, backupCaches.length);
        throw new Error("incorrect prices passed : custodiesLength: ".concat(custodiesLength, " , currentPrices.length: ").concat(backupCaches.length));
    }
};
exports.getBackupOracleInstruction = getBackupOracleInstruction;
function createBackupOracleInstruction(poolAddress_1) {
    return __awaiter(this, arguments, void 0, function (poolAddress, overrideCheck) {
        var backupOracleData, backUpOracleInstruction, error_1;
        if (overrideCheck === void 0) { overrideCheck = false; }
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 3, , 4]);
                    return [4, fetch("".concat(exports.API_ENDPOINT, "/backup-oracle/prices?poolAddress=").concat(poolAddress))];
                case 1: return [4, (_a.sent()).json()];
                case 2:
                    backupOracleData = _a.sent();
                    backUpOracleInstruction = new web3_js_1.TransactionInstruction({
                        keys: backupOracleData.keys,
                        programId: new web3_js_1.PublicKey(backupOracleData.programId),
                        data: Buffer.from(backupOracleData.data),
                    });
                    return [2, [backUpOracleInstruction]];
                case 3:
                    error_1 = _a.sent();
                    console.error('Error creating backup oracle instruction:', error_1);
                    return [3, 4];
                case 4: return [2, []];
            }
        });
    });
}
