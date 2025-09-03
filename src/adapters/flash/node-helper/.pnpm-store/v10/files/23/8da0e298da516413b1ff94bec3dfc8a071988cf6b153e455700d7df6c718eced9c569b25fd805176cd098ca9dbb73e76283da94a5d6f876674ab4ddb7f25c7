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
exports.PerpetualsClient = void 0;
var anchor_1 = require("@coral-xyz/anchor");
var web3_js_1 = require("@solana/web3.js");
var spl_token_1 = require("@solana/spl-token");
var js_sha256_1 = require("js-sha256");
var bs58_1 = require("bs58");
var PositionAccount_1 = require("./PositionAccount");
var types_1 = require("./types");
var OraclePrice_1 = require("./OraclePrice");
var perpetuals_1 = require("./idl/perpetuals");
var perp_composability_1 = require("./idl/perp_composability");
var fbnft_rewards_1 = require("./idl/fbnft_rewards");
var reward_distribution_1 = require("./idl/reward_distribution");
var rpc_1 = require("./utils/rpc");
var utils_1 = require("./utils");
var constants_1 = require("./constants");
var bignumber_js_1 = __importDefault(require("bignumber.js"));
var backupOracle_1 = require("./backupOracle");
var getReferralAccounts_1 = require("./utils/getReferralAccounts");
var ViewHelper_1 = require("./ViewHelper");
var TokenStakeAccount_1 = require("./TokenStakeAccount");
var TokenVaultAccount_1 = require("./TokenVaultAccount");
var PerpetualsClient = (function () {
    function PerpetualsClient(provider, programId, composabilityProgramId, fbNftRewardProgramId, rewardDistributionProgramId, opts, useExtOracleAccount) {
        if (useExtOracleAccount === void 0) { useExtOracleAccount = false; }
        var _this = this;
        var _a;
        this.addressLookupTables = [];
        this.setPrioritizationFee = function (fee) {
            _this.prioritizationFee = fee;
        };
        this.loadAddressLookupTable = function (poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var addresses, _i, _a, address, addressLookupTable, accCreationLamports;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        addresses = [];
                        _i = 0, _a = poolConfig.addressLookupTableAddresses;
                        _b.label = 1;
                    case 1:
                        if (!(_i < _a.length)) return [3, 4];
                        address = _a[_i];
                        return [4, this.provider.connection.getAddressLookupTable(address)];
                    case 2:
                        addressLookupTable = (_b.sent()).value;
                        if (addressLookupTable) {
                            addresses.push(addressLookupTable);
                        }
                        _b.label = 3;
                    case 3:
                        _i++;
                        return [3, 1];
                    case 4:
                        this.addressLookupTables = addresses;
                        return [4, (0, spl_token_1.getMinimumBalanceForRentExemptAccount)(this.provider.connection)];
                    case 5:
                        accCreationLamports = (_b.sent());
                        if (accCreationLamports) {
                            this.minimumBalanceForRentExemptAccountLamports = accCreationLamports;
                        }
                        return [2];
                }
            });
        }); };
        this.findProgramAddress = function (label, extraSeeds) {
            if (extraSeeds === void 0) { extraSeeds = null; }
            var seeds = [Buffer.from(anchor_1.utils.bytes.utf8.encode(label))];
            if (extraSeeds) {
                for (var _i = 0, extraSeeds_1 = extraSeeds; _i < extraSeeds_1.length; _i++) {
                    var extraSeed = extraSeeds_1[_i];
                    if (typeof extraSeed === "string") {
                        seeds.push(Buffer.from(anchor_1.utils.bytes.utf8.encode(extraSeed)));
                    }
                    else if (Array.isArray(extraSeed)) {
                        seeds.push(Buffer.from(extraSeed));
                    }
                    else {
                        seeds.push(extraSeed.toBuffer());
                    }
                }
            }
            var res = web3_js_1.PublicKey.findProgramAddressSync(seeds, _this.program.programId);
            return { publicKey: res[0], bump: res[1] };
        };
        this.findProgramAddressFromProgramId = function (label, extraSeeds, programId) {
            if (extraSeeds === void 0) { extraSeeds = null; }
            if (programId === void 0) { programId = _this.program.programId; }
            var seeds = [Buffer.from(anchor_1.utils.bytes.utf8.encode(label))];
            if (extraSeeds) {
                for (var _i = 0, extraSeeds_2 = extraSeeds; _i < extraSeeds_2.length; _i++) {
                    var extraSeed = extraSeeds_2[_i];
                    if (typeof extraSeed === "string") {
                        seeds.push(Buffer.from(anchor_1.utils.bytes.utf8.encode(extraSeed)));
                    }
                    else if (Array.isArray(extraSeed)) {
                        seeds.push(Buffer.from(extraSeed));
                    }
                    else {
                        seeds.push(extraSeed.toBuffer());
                    }
                }
            }
            var res = web3_js_1.PublicKey.findProgramAddressSync(seeds, programId);
            return { publicKey: res[0], bump: res[1] };
        };
        this.adjustTokenRatios = function (ratios) {
            if (ratios.length == 0) {
                return ratios;
            }
            var target = Math.floor(10000 / ratios.length);
            for (var _i = 0, ratios_1 = ratios; _i < ratios_1.length; _i++) {
                var ratio = ratios_1[_i];
                ratio.target = new anchor_1.BN(target);
            }
            if (10000 % ratios.length !== 0) {
                ratios[ratios.length - 1].target = new anchor_1.BN(target + (10000 % ratios.length));
            }
            return ratios;
        };
        this.getPerpetuals = function () { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2, this.program.account.perpetuals.fetch(this.perpetuals.publicKey)];
            });
        }); };
        this.getPoolKey = function (name) {
            return _this.findProgramAddress("pool", name).publicKey;
        };
        this.getPool = function (name) { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2, this.program.account.pool.fetch(this.getPoolKey(name))];
            });
        }); };
        this.getPools = function () { return __awaiter(_this, void 0, void 0, function () {
            var perpetuals;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4, this.getPerpetuals()];
                    case 1:
                        perpetuals = _a.sent();
                        return [2, this.program.account.pool.fetchMultiple(perpetuals.pools)];
                }
            });
        }); };
        this.getPoolLpTokenKey = function (name) {
            return _this.findProgramAddress("lp_token_mint", [_this.getPoolKey(name)])
                .publicKey;
        };
        this.getPoolCompoundingTokenKey = function (name) {
            return _this.findProgramAddress("compounding_token_mint", [_this.getPoolKey(name)])
                .publicKey;
        };
        this.getCustodyKey = function (poolName, tokenMint) {
            return _this.findProgramAddress("custody", [
                _this.getPoolKey(poolName),
                tokenMint,
            ]).publicKey;
        };
        this.getCustodyTokenAccountKey = function (poolName, tokenMint) {
            return _this.findProgramAddress("custody_token_account", [
                _this.getPoolKey(poolName),
                tokenMint,
            ]).publicKey;
        };
        this.getTradingAccount = function (tradingAccount) { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2, this.program.account.trading.fetch(tradingAccount)];
            });
        }); };
        this.getPosition = function (postionKey) { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2, this.program.account.position.fetch(postionKey)];
            });
        }); };
        this.getPositionData = function (position, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var marketConfig, targetCustodyConfig, collateralCustodyConfig, getPositionData, err_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        marketConfig = poolConfig.markets.find(function (i) { return i.marketAccount.equals(position.market); });
                        targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.custodyAccount.equals(marketConfig.targetCustody); });
                        collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.custodyAccount.equals(marketConfig.collateralCustody); });
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4, this.program.methods
                                .getPositionData({})
                                .accounts({
                                perpetuals: this.perpetuals.publicKey,
                                pool: poolConfig.poolAddress,
                                position: position.publicKey,
                                market: marketConfig.marketAccount,
                                targetCustody: targetCustodyConfig.custodyAccount,
                                custodyOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                collateralCustody: collateralCustodyConfig.custodyAccount,
                                collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                            })
                                .view()];
                    case 2:
                        getPositionData = _a.sent();
                        console.log(getPositionData);
                        return [2, getPositionData];
                    case 3:
                        err_1 = _a.sent();
                        console.log("perpClient setPool error:: ", err_1);
                        throw err_1;
                    case 4: return [2];
                }
            });
        }); };
        this.getOrderAccount = function (orderAccountKey) { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2, this.program.account.order.fetch(orderAccountKey)];
            });
        }); };
        this.getUserPosition = function (owner, targetCustody, collateralCustody, side) { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2, this.program.account.position.fetch(this.getPositionKey(owner, targetCustody, collateralCustody, side))];
            });
        }); };
        this.getUserOrderAccount = function (owner, targetCustody, collateralCustody, side) { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2, this.program.account.position.fetch(this.getOrderAccountKey(owner, targetCustody, collateralCustody, side))];
            });
        }); };
        this.getUserPositions = function (wallet, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var marketAccountsPks, positionKeys, positionsDatas;
            var _this = this;
            var _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        marketAccountsPks = poolConfig.getAllMarketPks();
                        positionKeys = marketAccountsPks.map(function (f) { return _this.findProgramAddress("position", [
                            wallet,
                            f
                        ]); }).map(function (p) { return p.publicKey; });
                        return [4, this.provider.connection.getMultipleAccountsInfo(positionKeys)];
                    case 1:
                        positionsDatas = (_a = (_b.sent())) !== null && _a !== void 0 ? _a : [];
                        return [2, positionsDatas
                                .map(function (p, i) { return ({ pubkey: positionKeys[i], data: p }); })
                                .filter(function (f) { return f.data !== null; })
                                .map(function (k) { return (__assign({ pubkey: k.pubkey }, _this.program.account.position.coder.accounts.decode('position', k.data.data))); })];
                }
            });
        }); };
        this.getUserOrderAccounts = function (wallet, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var marketAccountsPks, orderAccountKeys, orderAccountsDatas;
            var _this = this;
            var _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        marketAccountsPks = poolConfig.getAllMarketPks();
                        orderAccountKeys = marketAccountsPks.map(function (f) { return _this.findProgramAddress("order", [
                            wallet,
                            f
                        ]); }).map(function (p) { return p.publicKey; });
                        return [4, this.provider.connection.getMultipleAccountsInfo(orderAccountKeys)];
                    case 1:
                        orderAccountsDatas = (_a = (_b.sent())) !== null && _a !== void 0 ? _a : [];
                        return [2, orderAccountsDatas
                                .map(function (p, i) { return ({ pubkey: orderAccountKeys[i], data: p }); })
                                .filter(function (f) { return f.data !== null; })
                                .map(function (k) { return (__assign({ pubkey: k.pubkey }, _this.program.account.position.coder.accounts.decode('order', k.data.data))); })];
                }
            });
        }); };
        this.getAllPositions = function () { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2, this.program.account.position.all()];
            });
        }); };
        this.getAllActivePositions = function () { return __awaiter(_this, void 0, void 0, function () {
            var allPositions, activePositions;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4, this.program.account.position.all()];
                    case 1:
                        allPositions = _a.sent();
                        activePositions = allPositions.filter(function (f) { return !f.account.sizeAmount.isZero(); });
                        return [2, activePositions];
                }
            });
        }); };
        this.getAllPositionsByMarket = function (marketKey) { return __awaiter(_this, void 0, void 0, function () {
            var data, allPositions;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        data = (0, bs58_1.encode)(Buffer.concat([marketKey.toBuffer()]));
                        return [4, this.program.account.position.all([
                                {
                                    memcmp: { bytes: data, offset: 40 }
                                }
                            ])];
                    case 1:
                        allPositions = _a.sent();
                        return [2, allPositions];
                }
            });
        }); };
        this.getAllActivePositionsByMarket = function (marketKey) { return __awaiter(_this, void 0, void 0, function () {
            var data, allPositions, activePositions;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        data = (0, bs58_1.encode)(Buffer.concat([marketKey.toBuffer()]));
                        return [4, this.program.account.position.all([
                                {
                                    memcmp: { bytes: data, offset: 40 }
                                }
                            ])];
                    case 1:
                        allPositions = _a.sent();
                        activePositions = allPositions.filter(function (f) { return !f.account.sizeAmount.isZero(); });
                        return [2, activePositions];
                }
            });
        }); };
        this.getAllOrderAccounts = function () { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2, this.program.account.order.all()];
            });
        }); };
        this.getAccountDiscriminator = function (name) {
            return Buffer.from(js_sha256_1.sha256.digest("account:".concat(name))).slice(0, 8);
        };
        this.log = function () {
            var message = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                message[_i] = arguments[_i];
            }
            var date = new Date();
            var date_str = date.toDateString();
            var time = date.toLocaleTimeString();
            console.log("[".concat(date_str, " ").concat(time, "] ").concat(message));
        };
        this.prettyPrint = function (object) {
            console.log(JSON.stringify(object, null, 2));
        };
        this.liquidate = function (positionAccount, poolConfig, tokenMint, collateralMint, marketPk) { return __awaiter(_this, void 0, void 0, function () {
            var targetCustodyConfig, collateralCustodyConfig;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        targetCustodyConfig = poolConfig.custodies.find(function (f) { return f.mintKey.equals(tokenMint); });
                        collateralCustodyConfig = poolConfig.custodies.find(function (f) { return f.mintKey.equals(collateralMint); });
                        return [4, this.program.methods
                                .liquidate({})
                                .accounts({
                                signer: this.provider.wallet.publicKey,
                                perpetuals: this.perpetuals.publicKey,
                                pool: poolConfig.poolAddress,
                                position: positionAccount,
                                market: marketPk,
                                targetCustody: targetCustodyConfig.custodyAccount,
                                targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                collateralCustody: collateralCustodyConfig.custodyAccount,
                                collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.program.programId,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                            })
                                .instruction()];
                    case 1: return [2, _a.sent()];
                }
            });
        }); };
        this.getApyPercentageUi = function (rewardCustodyAccount, previousSnapShotRewardPerLpStaked, lpTokenUsdPrice) {
            var currentRewardPerLpStaked = rewardCustodyAccount.feesStats.rewardPerLpStaked;
            var difference = currentRewardPerLpStaked.sub(previousSnapShotRewardPerLpStaked);
            var anualizedRewardUi = new bignumber_js_1.default(difference.toString()).multipliedBy(365).dividedBy(lpTokenUsdPrice.toString());
            var percentage = anualizedRewardUi.multipliedBy(100);
            return percentage.toString();
        };
        this.getAddLiquidityAmountAndFeeSync = function (amountIn, poolAccount, inputTokenPrice, inputTokenEmaPrice, inputTokenCustodyAccount, lpTokenSupplyAmount, poolAumUsdMax, poolConfig) {
            if (inputTokenCustodyAccount.isVirtual) {
                throw new Error("Virtual custody, cannot add liquidity");
            }
            if (!inputTokenPrice.exponent.eq(inputTokenEmaPrice.exponent)) {
                throw new Error("exponent mistach");
            }
            var minMaxPrice = _this.getMinAndMaxOraclePriceSync(inputTokenPrice, inputTokenEmaPrice, inputTokenCustodyAccount);
            var fee = _this.getFeeHelper(types_1.FeesAction.AddLiquidity, amountIn, constants_1.BN_ZERO, inputTokenCustodyAccount, minMaxPrice.max, poolAumUsdMax, poolAccount, poolConfig).feeAmount;
            var tokenAmountUsd = minMaxPrice.min.getAssetAmountUsd((amountIn.sub(fee)), inputTokenCustodyAccount.decimals);
            var lpTokenOut;
            if (poolAumUsdMax.isZero()) {
                lpTokenOut = tokenAmountUsd;
            }
            else {
                lpTokenOut = (tokenAmountUsd.mul(lpTokenSupplyAmount)).div(poolAumUsdMax);
            }
            return {
                lpAmountOut: lpTokenOut,
                fee: fee
            };
        };
        this.getRemoveLiquidityAmountAndFeeSync = function (lpAmountIn, poolAccount, outputTokenPrice, outputTokenEmaPrice, outputTokenCustodyAccount, lpTokenSupply, poolAumUsdMax, poolConfig) {
            if (!outputTokenPrice.exponent.eq(outputTokenEmaPrice.exponent)) {
                throw new Error("exponent mistach");
            }
            var minMaxPrice = _this.getMinAndMaxOraclePriceSync(outputTokenPrice, outputTokenEmaPrice, outputTokenCustodyAccount);
            var removeAmountUsd = (poolAumUsdMax.mul(lpAmountIn)).div(lpTokenSupply);
            var removeAmount;
            var oneOracle = OraclePrice_1.OraclePrice.from({ price: new anchor_1.BN(Math.pow(10, 8)), exponent: new anchor_1.BN(-8), confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
            if (outputTokenCustodyAccount.isStable && minMaxPrice.min != minMaxPrice.max && minMaxPrice.max.price.lt(oneOracle.price)) {
                removeAmount = oneOracle.getTokenAmount(removeAmountUsd, outputTokenCustodyAccount.decimals);
            }
            else {
                removeAmount = minMaxPrice.max.getTokenAmount(removeAmountUsd, outputTokenCustodyAccount.decimals);
            }
            var fee = _this.getFeeHelper(types_1.FeesAction.RemoveLiquidity, constants_1.BN_ZERO, removeAmount, outputTokenCustodyAccount, minMaxPrice.max, poolAumUsdMax, poolAccount, poolConfig).feeAmount;
            return {
                tokenAmountOut: removeAmount.sub(fee),
                fee: fee,
            };
        };
        this.getFeeHelper = function (action, amountAdd, amountRemove, inputTokenCustodyAccount, maxOraclePrice, poolAumUsdMax, poolAccount, poolConfig) {
            var fees;
            switch (action) {
                case types_1.FeesAction.AddLiquidity:
                    fees = inputTokenCustodyAccount.fees.addLiquidity;
                    break;
                case types_1.FeesAction.RemoveLiquidity:
                    fees = inputTokenCustodyAccount.fees.removeLiquidity;
                    break;
                case types_1.FeesAction.SwapIn:
                    fees = inputTokenCustodyAccount.fees.swapIn;
                    break;
                case types_1.FeesAction.SwapOut:
                    fees = inputTokenCustodyAccount.fees.swapOut;
                    break;
            }
            if (inputTokenCustodyAccount.fees.mode == types_1.FeesMode.Fixed) {
                return { feeBps: fees.minFee, feeAmount: anchor_1.BN.max(amountAdd, amountRemove).mul(fees.minFee).div(new anchor_1.BN(constants_1.RATE_POWER)) };
            }
            var newRatio = _this.getNewRatioHelper(amountAdd, amountRemove, inputTokenCustodyAccount, maxOraclePrice, poolAumUsdMax);
            var index = poolAccount.custodies.findIndex(function (c) { return c.equals(inputTokenCustodyAccount.publicKey); });
            var ratios = poolAccount.ratios[index];
            var fee = constants_1.BN_ZERO;
            if (action == types_1.FeesAction.AddLiquidity || action == types_1.FeesAction.SwapIn || action == types_1.FeesAction.StableSwapIn) {
                if (newRatio.lte(ratios.min)) {
                    fee = fees.minFee;
                }
                else if (newRatio.lte(ratios.target) && ratios.target.gt(ratios.min)) {
                    fee = fees.minFee.add((newRatio.sub(ratios.min)).mul(fees.targetFee.sub(fees.minFee)).div(ratios.target.sub(ratios.min)));
                }
                else if (newRatio.lte(ratios.max) && ratios.max.gt(ratios.target)) {
                    fee = fees.targetFee.add((newRatio.sub(ratios.target)).mul(fees.maxFee.sub(fees.targetFee)).div(ratios.max.sub(ratios.target)));
                }
                else {
                    fee = fees.maxFee;
                }
            }
            else {
                if (newRatio.gte(ratios.max)) {
                    fee = fees.minFee;
                }
                else if (newRatio.gte(ratios.target) && ratios.max.gt(ratios.target)) {
                    fee = fees.minFee.add((ratios.max.sub(newRatio)).mul(fees.targetFee.sub(fees.minFee)).div(ratios.max.sub(ratios.target)));
                }
                else if (newRatio.gte(ratios.min) && ratios.target.gt(ratios.min)) {
                    fee = fees.targetFee.add((ratios.target.sub(newRatio)).mul(fees.maxFee.sub(fees.targetFee)).div(ratios.target.sub(ratios.min)));
                }
                else {
                    fee = fees.maxFee;
                }
            }
            var feeAmount = anchor_1.BN.max(amountAdd, amountRemove).mul(fee).div(new anchor_1.BN(constants_1.RATE_POWER));
            return { feeBps: fee, feeAmount: feeAmount };
        };
        this.getMinAndMaxOraclePriceSync = function (price, emaPrice, custodyAccount) {
            var maxPrice = price;
            var minPrice = price;
            var divergenceBps;
            if (custodyAccount.isStable) {
                var oneUsdPrice = OraclePrice_1.OraclePrice.from({
                    price: new anchor_1.BN(10).pow(maxPrice.exponent.abs()),
                    exponent: maxPrice.exponent,
                    confidence: maxPrice.confidence,
                    timestamp: maxPrice.timestamp
                });
                divergenceBps = maxPrice.getDivergenceFactor(oneUsdPrice);
            }
            else {
                divergenceBps = maxPrice.getDivergenceFactor(emaPrice);
            }
            if (divergenceBps.gte(custodyAccount.oracle.maxDivergenceBps)) {
                var confBps = (maxPrice.confidence.muln(constants_1.BPS_POWER)).div(maxPrice.price);
                if (confBps.lt(custodyAccount.oracle.maxConfBps)) {
                    minPrice.price = maxPrice.price.sub(maxPrice.confidence);
                    maxPrice.price = maxPrice.price.add(maxPrice.confidence);
                    return {
                        min: minPrice,
                        max: maxPrice
                    };
                }
                else {
                    minPrice.price = maxPrice.price.sub(maxPrice.confidence);
                    return {
                        min: minPrice,
                        max: maxPrice
                    };
                }
            }
            else {
                return {
                    min: maxPrice,
                    max: maxPrice
                };
            }
        };
        this.getMinAndMaxPriceSync = function (price, emaPrice, custodyAccount) {
            var minPrice = price;
            var divergenceBps;
            if (custodyAccount.isStable) {
                divergenceBps = price.getDivergenceFactor(OraclePrice_1.OraclePrice.from({ price: new anchor_1.BN(10).pow(price.exponent.abs()), exponent: price.exponent, confidence: price.confidence, timestamp: price.timestamp }));
            }
            else {
                divergenceBps = price.getDivergenceFactor(emaPrice);
            }
            if (divergenceBps.gte(custodyAccount.oracle.maxDivergenceBps)) {
                var factorBps = custodyAccount.oracle.maxDivergenceBps.isZero ? constants_1.BN_ZERO : (divergenceBps.mul(new anchor_1.BN(constants_1.BPS_POWER))).div(custodyAccount.oracle.maxDivergenceBps);
                var confBps = (price.confidence.muln(constants_1.BPS_POWER)).div(price.price);
                if (confBps.lt(custodyAccount.oracle.maxConfBps)) {
                    var confFactor = anchor_1.BN.min(factorBps, new anchor_1.BN(50000));
                    var confScale = (price.confidence.mul(confFactor)).div(new anchor_1.BN(constants_1.BPS_POWER));
                    minPrice.price = price.price.sub(confScale);
                }
                else {
                    minPrice.price = price.price.sub(price.confidence);
                }
            }
            else {
                return {
                    min: price.scale_to_exponent(new anchor_1.BN(constants_1.USD_DECIMALS).neg()).price,
                    max: price.scale_to_exponent(new anchor_1.BN(constants_1.USD_DECIMALS).neg()).price
                };
            }
            return {
                min: minPrice.scale_to_exponent(new anchor_1.BN(constants_1.USD_DECIMALS).neg()).price,
                max: price.scale_to_exponent(new anchor_1.BN(constants_1.USD_DECIMALS).neg()).price
            };
        };
        this.checkIfPriceStaleOrCustom = function (price, emaPrice, custodyAccount, timestampInSeconds) {
            if (timestampInSeconds.lt(price.timestamp)) {
                throw new Error("current time cannot be timepassed");
            }
            if (timestampInSeconds.sub(price.timestamp).gt(new anchor_1.BN(custodyAccount.oracle.maxPriceAgeSec))) {
                return true;
            }
            var deviation;
            if (custodyAccount.isStable) {
                deviation = price.getDivergenceFactor(OraclePrice_1.OraclePrice.from({ price: new anchor_1.BN(10).pow(price.exponent.abs()), exponent: price.exponent, confidence: price.confidence, timestamp: price.timestamp }));
            }
            else {
                deviation = price.getDivergenceFactor(emaPrice);
            }
            if (deviation.gte(custodyAccount.oracle.maxDivergenceBps)) {
                var confFactor = (price.confidence.muln(constants_1.BPS_POWER)).div(price.price);
                if (confFactor.lt(custodyAccount.oracle.maxConfBps)) {
                    return false;
                }
                else {
                    return true;
                }
            }
            return false;
        };
        this.getAveragePriceSync = function (price1, size1, price2, size2) {
            var initialValue = size1.mul(price1);
            var addedValue = size2.mul(price2);
            var totalValue = initialValue.add(addedValue);
            var totalSize = size1.add(size2);
            var averageEntryPrice = totalValue.div(totalSize);
            return averageEntryPrice;
        };
        this.getLeverageSync = function (sizeUsd, collateralAmount, collateralMinOraclePrice, collateralTokenDecimals, pnlUsd) {
            var currentCollateralUsd = collateralMinOraclePrice.getAssetAmountUsd(collateralAmount, collateralTokenDecimals);
            var currentCollateralUsdIncludingPnl = currentCollateralUsd.add(pnlUsd);
            if (currentCollateralUsdIncludingPnl.gt(constants_1.BN_ZERO)) {
                return sizeUsd.mul(new anchor_1.BN(constants_1.BPS_POWER)).div(currentCollateralUsdIncludingPnl);
            }
            else {
                return new anchor_1.BN(Number.MAX_SAFE_INTEGER);
            }
        };
        this.getLeverageAtAmountEntryWithSwapSync = function (positionAccount, inputDeltaAmount, sizeDeltaAmount, side, poolAccount, inputTokenPrice, inputTokenEmaPrice, inputTokenCustodyAccount, swapOutTokenPrice, swapOutTokenEmaPrice, swapOutTokenCustodyAccount, collateralTokenPrice, collateralTokenEmaPrice, collateralTokenCustodyAccount, targetTokenPrice, targetTokenEmaPrice, targetTokenCustodyAccount, swapPoolAumUsdMax, poolConfigPosition, poolConfigSwap, pnlUsd) {
            var finalCollateralAmount = constants_1.BN_ZERO;
            if (!inputDeltaAmount.isZero()) {
                if (inputTokenCustodyAccount.publicKey.equals(collateralTokenCustodyAccount.publicKey)) {
                    finalCollateralAmount = inputDeltaAmount;
                }
                else {
                    var swapAmountOut = _this.getSwapAmountAndFeesSync(inputDeltaAmount, constants_1.BN_ZERO, poolAccount, inputTokenPrice, inputTokenEmaPrice, inputTokenCustodyAccount, swapOutTokenPrice, swapOutTokenEmaPrice, swapOutTokenCustodyAccount, swapPoolAumUsdMax, poolConfigSwap).minAmountOut;
                    finalCollateralAmount = swapAmountOut;
                }
            }
            var lockedUsd = targetTokenPrice.getAssetAmountUsd(sizeDeltaAmount, targetTokenCustodyAccount.decimals);
            var entryOraclePrice = _this.getEntryPriceUsdSync(side, targetTokenPrice, targetTokenEmaPrice, targetTokenCustodyAccount, lockedUsd);
            var openFeeUsd = constants_1.BN_ZERO;
            if (sizeDeltaAmount != constants_1.BN_ZERO) {
                var sizeDeltaUsd = entryOraclePrice.getAssetAmountUsd(sizeDeltaAmount, targetTokenCustodyAccount.decimals);
                openFeeUsd = sizeDeltaUsd.mul(targetTokenCustodyAccount.fees.openPosition).div(new anchor_1.BN(constants_1.RATE_POWER));
            }
            if (positionAccount === null) {
                var data = __assign({}, types_1.DEFAULT_POSITION);
                positionAccount = PositionAccount_1.PositionAccount.from(web3_js_1.PublicKey.default, data);
            }
            else {
                positionAccount = positionAccount.clone();
                var positionEntryPrice = OraclePrice_1.OraclePrice.from({
                    price: positionAccount.entryPrice.price,
                    exponent: new anchor_1.BN(positionAccount.entryPrice.exponent),
                    confidence: constants_1.BN_ZERO,
                    timestamp: constants_1.BN_ZERO
                });
                entryOraclePrice.price = _this.getAveragePriceSync(positionEntryPrice.price, positionAccount.sizeAmount, entryOraclePrice.price, sizeDeltaAmount);
            }
            var collateralMinOraclePrice = _this.getMinAndMaxOraclePriceSync(collateralTokenPrice, collateralTokenEmaPrice, collateralTokenCustodyAccount).min;
            var collateralAmount = positionAccount.collateralAmount.add(finalCollateralAmount);
            var currentCollateralUsd = collateralMinOraclePrice.getAssetAmountUsd(collateralAmount, collateralTokenCustodyAccount.decimals);
            var currentCollateralUsdIncludingPnl = currentCollateralUsd.add(pnlUsd).sub(openFeeUsd);
            var sizeAmount = positionAccount.sizeAmount.add(sizeDeltaAmount);
            var sizeAmountUsd = entryOraclePrice.getAssetAmountUsd(sizeAmount, targetTokenCustodyAccount.decimals);
            if (currentCollateralUsdIncludingPnl.gt(constants_1.BN_ZERO)) {
                return sizeAmountUsd.mul(new anchor_1.BN(constants_1.BPS_POWER)).div(currentCollateralUsdIncludingPnl);
            }
            else {
                return new anchor_1.BN(Number.MAX_SAFE_INTEGER);
            }
        };
        this.getEntryPriceAndFeeSync = function (positionAccount, marketCorrelation, collateralDeltaAmount, sizeDeltaAmount, side, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, discountBps) {
            if (discountBps === void 0) { discountBps = constants_1.BN_ZERO; }
            if (collateralDeltaAmount.isNeg() || sizeDeltaAmount.isNeg()) {
                throw new Error("Delta Amounts cannot be negative.");
            }
            var lockedUsd = targetPrice.getAssetAmountUsd(sizeDeltaAmount, targetCustodyAccount.decimals);
            var entryOraclePrice = _this.getEntryPriceUsdSync(side, targetPrice, targetEmaPrice, targetCustodyAccount, lockedUsd);
            if (positionAccount === null) {
                var data = __assign({}, types_1.DEFAULT_POSITION);
                positionAccount = PositionAccount_1.PositionAccount.from(web3_js_1.PublicKey.default, data);
                var sizeUsd = entryOraclePrice.getAssetAmountUsd(sizeDeltaAmount, targetCustodyAccount.decimals);
                positionAccount.sizeUsd = sizeUsd;
                positionAccount.sizeDecimals = targetCustodyAccount.decimals;
                positionAccount.collateralDecimals = collateralCustodyAccount.decimals;
                positionAccount.lockedDecimals = collateralCustodyAccount.decimals;
            }
            else {
                positionAccount = positionAccount.clone();
                var positionEntryPrice = OraclePrice_1.OraclePrice.from({
                    price: positionAccount.entryPrice.price,
                    exponent: new anchor_1.BN(positionAccount.entryPrice.exponent),
                    confidence: constants_1.BN_ZERO,
                    timestamp: constants_1.BN_ZERO
                });
                entryOraclePrice.price = _this.getAveragePriceSync(positionEntryPrice.price, positionAccount.sizeAmount, entryOraclePrice.price, sizeDeltaAmount);
                var sizeDeltaUsd = entryOraclePrice.getAssetAmountUsd(sizeDeltaAmount, targetCustodyAccount.decimals);
                positionAccount.sizeUsd = positionAccount.sizeUsd.add(sizeDeltaUsd);
            }
            positionAccount.collateralAmount = positionAccount.collateralAmount.add(collateralDeltaAmount);
            positionAccount.sizeAmount = positionAccount.sizeAmount.add(sizeDeltaAmount);
            var lockFeeUsd = _this.getLockFeeAndUnsettledUsdForPosition(positionAccount, collateralCustodyAccount, currentTimestamp);
            var liquidationPrice = _this.getLiquidationPriceSync(positionAccount.collateralAmount, positionAccount.sizeAmount, entryOraclePrice, lockFeeUsd, marketCorrelation, side, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, positionAccount);
            var sizeAmountUsd = entryOraclePrice.getAssetAmountUsd(sizeDeltaAmount, targetCustodyAccount.decimals);
            var collateralTokenMinOraclePrice = _this.getMinAndMaxOraclePriceSync(collateralPrice, collateralEmaPrice, collateralCustodyAccount).min;
            var feeUsd = constants_1.BN_ZERO;
            var feeAmount = constants_1.BN_ZERO;
            var feeUsdAfterDiscount = constants_1.BN_ZERO;
            var feeAmountAfterDiscount = constants_1.BN_ZERO;
            if (positionAccount !== null && sizeDeltaAmount.isZero()) {
            }
            else {
                feeUsd = sizeAmountUsd.mul(targetCustodyAccount.fees.openPosition).div(new anchor_1.BN(constants_1.RATE_POWER));
                feeAmount = feeUsd.mul(new anchor_1.BN(Math.pow(10, collateralCustodyAccount.decimals))).div(collateralTokenMinOraclePrice.price);
                if (discountBps.gt(constants_1.BN_ZERO)) {
                    feeUsdAfterDiscount = feeUsd.mul(discountBps).div(new anchor_1.BN(constants_1.BPS_POWER));
                    feeUsdAfterDiscount = feeUsd.sub(feeUsdAfterDiscount);
                    feeAmountAfterDiscount = feeUsdAfterDiscount.mul(new anchor_1.BN(Math.pow(10, collateralCustodyAccount.decimals))).div(collateralTokenMinOraclePrice.price);
                }
                else {
                    feeUsdAfterDiscount = feeUsd;
                    feeAmountAfterDiscount = feeAmount;
                }
            }
            return {
                entryOraclePrice: entryOraclePrice,
                feeUsd: feeUsd,
                feeAmount: feeAmount,
                feeUsdAfterDiscount: feeUsdAfterDiscount,
                feeAmountAfterDiscount: feeAmountAfterDiscount,
                liquidationPrice: liquidationPrice
            };
        };
        this.getEntryPriceAndFeeSyncV2 = function (positionAccount, marketCorrelation, collateralDeltaAmount, sizeDeltaAmount, side, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, discountBps, enableLogs) {
            if (discountBps === void 0) { discountBps = constants_1.BN_ZERO; }
            if (enableLogs === void 0) { enableLogs = false; }
            if (collateralDeltaAmount.isNeg() || sizeDeltaAmount.isNeg()) {
                throw new Error("Delta Amounts cannot be negative.");
            }
            var lockedUsd = targetPrice.getAssetAmountUsd(sizeDeltaAmount, targetCustodyAccount.decimals);
            var entryOraclePrice = _this.getEntryPriceUsdSync(side, targetPrice, targetEmaPrice, targetCustodyAccount, lockedUsd);
            if (positionAccount === null) {
                var data = __assign({}, types_1.DEFAULT_POSITION);
                positionAccount = PositionAccount_1.PositionAccount.from(web3_js_1.PublicKey.default, data);
                var sizeUsd = entryOraclePrice.getAssetAmountUsd(sizeDeltaAmount, targetCustodyAccount.decimals);
                positionAccount.sizeUsd = sizeUsd;
                positionAccount.sizeDecimals = targetCustodyAccount.decimals;
                positionAccount.collateralDecimals = collateralCustodyAccount.decimals;
                positionAccount.lockedDecimals = collateralCustodyAccount.decimals;
            }
            else {
                positionAccount = positionAccount.clone();
                var positionEntryPrice = OraclePrice_1.OraclePrice.from({
                    price: positionAccount.entryPrice.price,
                    exponent: new anchor_1.BN(positionAccount.entryPrice.exponent),
                    confidence: constants_1.BN_ZERO,
                    timestamp: constants_1.BN_ZERO
                });
                entryOraclePrice.price = _this.getAveragePriceSync(positionEntryPrice.price, positionAccount.sizeAmount, entryOraclePrice.price, sizeDeltaAmount);
                var sizeDeltaUsd = entryOraclePrice.getAssetAmountUsd(sizeDeltaAmount, targetCustodyAccount.decimals);
                positionAccount.sizeUsd = positionAccount.sizeUsd.add(sizeDeltaUsd);
            }
            positionAccount.collateralAmount = positionAccount.collateralAmount.add(collateralDeltaAmount);
            positionAccount.sizeAmount = positionAccount.sizeAmount.add(sizeDeltaAmount);
            var lockFeeUsd = _this.getLockFeeAndUnsettledUsdForPosition(positionAccount, collateralCustodyAccount, currentTimestamp);
            var liquidationPrice = _this.getLiquidationPriceSync(positionAccount.collateralAmount, positionAccount.sizeAmount, entryOraclePrice, lockFeeUsd, marketCorrelation, side, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, positionAccount);
            var sizeAmountUsd = entryOraclePrice.getAssetAmountUsd(sizeDeltaAmount, targetCustodyAccount.decimals);
            var collateralTokenMinOraclePrice = _this.getMinAndMaxOraclePriceSync(collateralPrice, collateralEmaPrice, collateralCustodyAccount).min;
            var feeUsd = constants_1.BN_ZERO;
            var feeAmount = constants_1.BN_ZERO;
            var feeUsdAfterDiscount = constants_1.BN_ZERO;
            var feeAmountAfterDiscount = constants_1.BN_ZERO;
            if (positionAccount !== null && sizeDeltaAmount.isZero()) {
            }
            else {
                feeUsd = sizeAmountUsd.mul(targetCustodyAccount.fees.openPosition).div(new anchor_1.BN(constants_1.RATE_POWER));
                feeAmount = feeUsd.mul(new anchor_1.BN(Math.pow(10, collateralCustodyAccount.decimals))).div(collateralTokenMinOraclePrice.price);
                if (discountBps.gt(constants_1.BN_ZERO)) {
                    feeUsdAfterDiscount = feeUsd.mul(discountBps).div(new anchor_1.BN(constants_1.BPS_POWER));
                    feeUsdAfterDiscount = feeUsd.sub(feeUsdAfterDiscount);
                    feeAmountAfterDiscount = feeUsdAfterDiscount.mul(new anchor_1.BN(Math.pow(10, collateralCustodyAccount.decimals))).div(collateralTokenMinOraclePrice.price);
                }
                else {
                    feeUsdAfterDiscount = feeUsd;
                    feeAmountAfterDiscount = feeAmount;
                }
            }
            var divergenceBps;
            divergenceBps = targetPrice.getDivergenceFactor(targetEmaPrice);
            var vbFeeUsd = constants_1.BN_ZERO;
            if (divergenceBps.gte(targetCustodyAccount.oracle.maxDivergenceBps)) {
                if (enableLogs)
                    console.log("volitlity fee added:", "divergenceBps", divergenceBps.toString(), "maxDivergenceBps", targetCustodyAccount.oracle.maxDivergenceBps.toString());
                vbFeeUsd = sizeAmountUsd.mul(targetCustodyAccount.fees.volatility).div(new anchor_1.BN(constants_1.RATE_POWER));
            }
            else {
                if (enableLogs)
                    console.log("volitlity fee zero:", "divergenceBps", divergenceBps.toString(), "maxDivergenceBps", targetCustodyAccount.oracle.maxDivergenceBps.toString());
            }
            return {
                entryOraclePrice: entryOraclePrice,
                feeUsd: feeUsd,
                feeAmount: feeAmount,
                vbFeeUsd: vbFeeUsd,
                feeUsdAfterDiscount: feeUsdAfterDiscount,
                feeAmountAfterDiscount: feeAmountAfterDiscount,
                liquidationPrice: liquidationPrice
            };
        };
        this.getEntryPriceUsdSync = function (side, targetPrice, targetEmaPrice, targetCustodyAccount, lockedUsd) {
            var _a = _this.getMinAndMaxOraclePriceSync(targetPrice, targetEmaPrice, targetCustodyAccount), minPrice = _a.min, maxPrice = _a.max;
            var spread = _this.getTradeSpread(targetCustodyAccount, lockedUsd);
            var USD_POWER = (new anchor_1.BN(10)).pow(new anchor_1.BN(constants_1.USD_DECIMALS));
            var entryPriceBN = (0, types_1.isVariant)(side, 'long') ?
                maxPrice.price.add(maxPrice.price.mul(spread).div(USD_POWER)) :
                minPrice.price.sub(minPrice.price.mul(spread).div(USD_POWER));
            var entryOraclePrice = OraclePrice_1.OraclePrice.from({ price: entryPriceBN, exponent: maxPrice.exponent, confidence: maxPrice.confidence, timestamp: maxPrice.timestamp });
            return entryOraclePrice;
        };
        this.getExitFeeSync = function (positionAccount, targetCustody, collateralCustodyAccount, collateralPrice, collateralEmaPrice, discountBps) {
            if (discountBps === void 0) { discountBps = constants_1.BN_ZERO; }
            var closePositionFeeRate = targetCustody.fees.closePosition;
            if (!discountBps.isZero()) {
                closePositionFeeRate = closePositionFeeRate.mul(constants_1.BN_ONE.sub(discountBps));
            }
            var exitFeeUsd = positionAccount.sizeUsd.mul(closePositionFeeRate).div(new anchor_1.BN(constants_1.RATE_POWER));
            var collateralTokenMinOraclePrice = _this.getMinAndMaxOraclePriceSync(collateralPrice, collateralEmaPrice, collateralCustodyAccount).min;
            var exitFeeAmount = collateralTokenMinOraclePrice.getTokenAmount(exitFeeUsd, collateralCustodyAccount.decimals);
            return {
                exitFeeAmount: exitFeeAmount,
                exitFeeUsd: exitFeeUsd
            };
        };
        this.getExitPriceAndFeeSync = function (positionAccount, marketCorrelation, collateralDeltaAmount, sizeDeltaAmount, side, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, discountBps) {
            if (discountBps === void 0) { discountBps = constants_1.BN_ZERO; }
            var resultingPositionAccount = positionAccount.clone();
            if (collateralDeltaAmount.isNeg() || sizeDeltaAmount.isNeg()) {
                throw new Error("Delta Amounts cannot be negative ");
            }
            resultingPositionAccount.collateralAmount = resultingPositionAccount.collateralAmount.sub(collateralDeltaAmount);
            resultingPositionAccount.sizeAmount = resultingPositionAccount.sizeAmount.sub(sizeDeltaAmount);
            if (resultingPositionAccount.collateralAmount.isNeg() || resultingPositionAccount.sizeAmount.isNeg()) {
                throw new Error("cannot remove/close more than collateral/Size");
            }
            var lockedUsd = targetPrice.getAssetAmountUsd(sizeDeltaAmount, targetCustodyAccount.decimals);
            var exitOraclePrice = _this.getExitOraclePriceSync(side, targetPrice, targetEmaPrice, targetCustodyAccount, lockedUsd);
            var _a = _this.getMinAndMaxOraclePriceSync(collateralPrice, collateralEmaPrice, collateralCustodyAccount), collateralTokenMinOraclePrice = _a.min, collateralTokenMaxOraclePrice = _a.max;
            var lockAndUnsettledFeeUsd = _this.getLockFeeAndUnsettledUsdForPosition(resultingPositionAccount, collateralCustodyAccount, currentTimestamp);
            var lockAndUnsettledFee = collateralTokenMinOraclePrice.getTokenAmount(lockAndUnsettledFeeUsd, collateralCustodyAccount.decimals);
            var sizeAmountUsd = exitOraclePrice.getAssetAmountUsd(sizeDeltaAmount, targetCustodyAccount.decimals);
            var exitFeeUsd = sizeAmountUsd.mul(targetCustodyAccount.fees.closePosition).div(new anchor_1.BN(constants_1.RATE_POWER));
            var exitFeeAmount = collateralTokenMaxOraclePrice.getTokenAmount(exitFeeUsd, collateralCustodyAccount.decimals);
            var exitFeeUsdAfterDiscount = constants_1.BN_ZERO;
            var exitFeeAmountAfterDiscount = constants_1.BN_ZERO;
            if (discountBps.gt(constants_1.BN_ZERO)) {
                exitFeeUsdAfterDiscount = exitFeeUsd.mul(discountBps).div(new anchor_1.BN(constants_1.BPS_POWER));
                exitFeeUsdAfterDiscount = exitFeeUsd.sub(exitFeeUsdAfterDiscount);
                exitFeeAmountAfterDiscount = collateralTokenMaxOraclePrice.getTokenAmount(exitFeeUsdAfterDiscount, collateralCustodyAccount.decimals);
            }
            else {
                exitFeeUsdAfterDiscount = exitFeeUsd;
                exitFeeAmountAfterDiscount = exitFeeAmount;
            }
            var positionEntryOraclePrice = new OraclePrice_1.OraclePrice({
                price: positionAccount.entryPrice.price, exponent: new anchor_1.BN(positionAccount.entryPrice.exponent), confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO
            });
            resultingPositionAccount.sizeUsd = positionEntryOraclePrice.getAssetAmountUsd(resultingPositionAccount.sizeAmount, targetCustodyAccount.decimals);
            var liquidationPrice = _this.getLiquidationPriceSync(resultingPositionAccount.collateralAmount, resultingPositionAccount.sizeAmount, positionEntryOraclePrice, lockAndUnsettledFeeUsd, marketCorrelation, side, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, positionAccount);
            return {
                exitOraclePrice: exitOraclePrice,
                borrowFeeUsd: lockAndUnsettledFeeUsd,
                borrowFeeAmount: lockAndUnsettledFee,
                exitFeeUsd: exitFeeUsd,
                exitFeeAmount: exitFeeAmount,
                exitFeeUsdAfterDiscount: exitFeeUsdAfterDiscount,
                exitFeeAmountAfterDiscount: exitFeeAmountAfterDiscount,
                liquidationPrice: liquidationPrice
            };
        };
        this.getTradeSpread = function (targetCustodyAccount, lockedUsd) {
            if (targetCustodyAccount.pricing.tradeSpreadMax.sub(targetCustodyAccount.pricing.tradeSpreadMin).isZero()
                ||
                    lockedUsd.isZero()) {
                return constants_1.BN_ZERO;
            }
            var slope = ((targetCustodyAccount.pricing.tradeSpreadMax.sub(targetCustodyAccount.pricing.tradeSpreadMin)).mul(new anchor_1.BN(Math.pow(10, (constants_1.RATE_DECIMALS + constants_1.BPS_DECIMALS)))))
                .div(targetCustodyAccount.pricing.maxPositionLockedUsd);
            var variable = (slope.mul(lockedUsd)).div(new anchor_1.BN(Math.pow(10, (constants_1.RATE_DECIMALS + constants_1.BPS_DECIMALS))));
            var finalSpread = targetCustodyAccount.pricing.tradeSpreadMin.add(variable);
            return finalSpread;
        };
        this.getExitOraclePriceSync = function (side, targetPrice, targetEmaPrice, targetCustodyAccount, lockedUsd) {
            var _a = _this.getMinAndMaxOraclePriceSync(targetPrice, targetEmaPrice, targetCustodyAccount), minPrice = _a.min, maxPrice = _a.max;
            var spread = _this.getTradeSpread(targetCustodyAccount, lockedUsd);
            var USD_POWER = (new anchor_1.BN(10)).pow(new anchor_1.BN(constants_1.USD_DECIMALS));
            var exitPriceBN = (0, types_1.isVariant)(side, 'long') ?
                maxPrice.price.sub(maxPrice.price.mul(spread).div(USD_POWER)) :
                minPrice.price.add(minPrice.price.mul(spread).div(USD_POWER));
            var exitOraclePrice = OraclePrice_1.OraclePrice.from({ price: exitPriceBN, exponent: maxPrice.exponent, confidence: maxPrice.confidence, timestamp: maxPrice.timestamp });
            return exitOraclePrice;
        };
        this.getExitOraclePriceWithoutSpreadSync = function (side, targetPrice, targetEmaPrice, targetCustodyAccount) {
            var _a = _this.getMinAndMaxOraclePriceSync(targetPrice, targetEmaPrice, targetCustodyAccount), minPrice = _a.min, maxPrice = _a.max;
            if ((0, types_1.isVariant)(side, 'long')) {
                return minPrice;
            }
            else {
                return maxPrice;
            }
        };
        this.getSizeAmountFromLeverageAndCollateral = function (collateralAmtWithFee, leverage, marketToken, collateralToken, side, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, discountBps) {
            if (discountBps === void 0) { discountBps = constants_1.BN_ZERO; }
            var collateralTokenMinPrice = _this.getMinAndMaxPriceSync(collateralPrice, collateralEmaPrice, collateralCustodyAccount).min;
            var collateralTokenMinPriceUi = new bignumber_js_1.default(collateralTokenMinPrice.toString()).dividedBy(Math.pow(10, constants_1.USD_DECIMALS));
            var collateralAmtMinUsdUi = new bignumber_js_1.default(collateralAmtWithFee.toString()).dividedBy(Math.pow(10, collateralToken.decimals))
                .multipliedBy(collateralTokenMinPriceUi);
            var openPosFeeRateUi = new bignumber_js_1.default(targetCustodyAccount.fees.openPosition.toString()).dividedBy(Math.pow(10, constants_1.RATE_DECIMALS));
            if (!discountBps.isZero()) {
                var discountBpsUi = new bignumber_js_1.default(discountBps.toString()).dividedBy(Math.pow(10, constants_1.BPS_DECIMALS));
                openPosFeeRateUi = openPosFeeRateUi.multipliedBy(new bignumber_js_1.default(1).minus(discountBpsUi));
            }
            var sizeUsdUi = collateralAmtMinUsdUi.multipliedBy(leverage)
                .dividedBy(new bignumber_js_1.default(1).plus(openPosFeeRateUi.multipliedBy(leverage)));
            var lockedUsd = (0, utils_1.uiDecimalsToNative)(sizeUsdUi.toString(), constants_1.USD_DECIMALS);
            var entryOraclePrice = _this.getEntryPriceUsdSync(side, targetPrice, targetEmaPrice, targetCustodyAccount, lockedUsd);
            var entryPriceUsdUi = new bignumber_js_1.default(entryOraclePrice.toUiPrice(constants_1.ORACLE_EXPONENT));
            var sizeAmountUi = sizeUsdUi.dividedBy(entryPriceUsdUi);
            return (0, utils_1.uiDecimalsToNative)(sizeAmountUi.toFixed(marketToken.decimals, bignumber_js_1.default.ROUND_DOWN), marketToken.decimals);
        };
        this.getSizeAmountWithSwapSync = function (amountIn, leverage, side, poolAccount, inputTokenPrice, inputTokenEmaPrice, inputTokenCustodyAccount, collateralTokenPrice, collateralTokenEmaPrice, collateralTokenCustodyAccount, swapOutTokenPrice, swapOutTokenEmaPrice, swapOutTokenCustodyAccount, targetTokenPrice, targetTokenEmaPrice, targetTokenCustodyAccount, swapPoolAumUsdMax, poolConfigSwap, discountBps) {
            if (discountBps === void 0) { discountBps = constants_1.BN_ZERO; }
            var finalCollateralAmount = constants_1.BN_ZERO;
            if (inputTokenCustodyAccount.publicKey.equals(collateralTokenCustodyAccount.publicKey)) {
                finalCollateralAmount = amountIn;
            }
            else {
                var swapAmountOut = _this.getSwapAmountAndFeesSync(amountIn, constants_1.BN_ZERO, poolAccount, inputTokenPrice, inputTokenEmaPrice, inputTokenCustodyAccount, swapOutTokenPrice, swapOutTokenEmaPrice, swapOutTokenCustodyAccount, swapPoolAumUsdMax, poolConfigSwap).minAmountOut;
                finalCollateralAmount = swapAmountOut;
            }
            var collateralTokenMinPrice = _this.getMinAndMaxPriceSync(collateralTokenPrice, collateralTokenEmaPrice, collateralTokenCustodyAccount).min;
            var collateralTokenMinPriceUi = new bignumber_js_1.default(collateralTokenMinPrice.toString()).dividedBy(Math.pow(10, constants_1.USD_DECIMALS));
            var collateralAmtMinUsdUi = new bignumber_js_1.default(finalCollateralAmount.toString()).dividedBy(Math.pow(10, collateralTokenCustodyAccount.decimals))
                .multipliedBy(collateralTokenMinPriceUi);
            var openPosFeeRateUi = new bignumber_js_1.default(targetTokenCustodyAccount.fees.openPosition.toString()).dividedBy(Math.pow(10, constants_1.RATE_DECIMALS));
            if (!discountBps.isZero()) {
                var discountBpsUi = new bignumber_js_1.default(discountBps.toString()).dividedBy(Math.pow(10, constants_1.BPS_DECIMALS));
                openPosFeeRateUi = openPosFeeRateUi.multipliedBy(new bignumber_js_1.default(1).minus(discountBpsUi));
            }
            var sizeUsdUi = collateralAmtMinUsdUi.multipliedBy(leverage)
                .dividedBy(new bignumber_js_1.default(1).plus(openPosFeeRateUi.multipliedBy(leverage)));
            var lockedUsd = (0, utils_1.uiDecimalsToNative)(sizeUsdUi.toFixed(constants_1.USD_DECIMALS), constants_1.USD_DECIMALS);
            var entryOraclePrice = _this.getEntryPriceUsdSync(side, targetTokenPrice, targetTokenEmaPrice, targetTokenCustodyAccount, lockedUsd);
            var entryPriceUsdUi = new bignumber_js_1.default(entryOraclePrice.toUiPrice(constants_1.ORACLE_EXPONENT));
            var sizeAmountUi = sizeUsdUi.dividedBy(entryPriceUsdUi);
            return (0, utils_1.uiDecimalsToNative)(sizeAmountUi.toFixed(targetTokenCustodyAccount.decimals, bignumber_js_1.default.ROUND_DOWN), targetTokenCustodyAccount.decimals);
        };
        this.getCollateralAmountWithFeeFromLeverageAndSize = function (sizeAmount, leverage, marketToken, collateralToken, side, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, discountBps) {
            if (discountBps === void 0) { discountBps = constants_1.BN_ZERO; }
            var collateralTokenMinPrice = _this.getMinAndMaxPriceSync(collateralPrice, collateralEmaPrice, collateralCustodyAccount).min;
            var collateralTokenMinPriceUi = new bignumber_js_1.default(collateralTokenMinPrice.toString()).dividedBy(Math.pow(10, constants_1.USD_DECIMALS));
            var lockedUsd = targetPrice.getAssetAmountUsd(sizeAmount, targetCustodyAccount.decimals);
            var entryOraclePrice = _this.getEntryPriceUsdSync(side, targetPrice, targetEmaPrice, targetCustodyAccount, lockedUsd);
            var entryPriceUsdUi = new bignumber_js_1.default(entryOraclePrice.toUiPrice(constants_1.ORACLE_EXPONENT));
            var openPosFeeRateUi = new bignumber_js_1.default(targetCustodyAccount.fees.openPosition.toString()).dividedBy(Math.pow(10, constants_1.RATE_DECIMALS));
            if (!discountBps.isZero()) {
                var discountBpsUi = new bignumber_js_1.default(discountBps.toString()).dividedBy(Math.pow(10, constants_1.BPS_DECIMALS));
                openPosFeeRateUi = openPosFeeRateUi.multipliedBy(new bignumber_js_1.default(1).minus(discountBpsUi));
            }
            var sizeAmountUi = new bignumber_js_1.default(sizeAmount.toString()).dividedBy(Math.pow(10, marketToken.decimals));
            var sizeUsdUi = entryPriceUsdUi.multipliedBy(sizeAmountUi);
            var collateralWithFeeUsdUi = sizeUsdUi.multipliedBy(new bignumber_js_1.default(1).plus(openPosFeeRateUi.multipliedBy(leverage))).dividedBy(leverage);
            var collateralAmtWithFeeUi = collateralWithFeeUsdUi.dividedBy(collateralTokenMinPriceUi);
            return (0, utils_1.uiDecimalsToNative)(collateralAmtWithFeeUi.toFixed(collateralToken.decimals, bignumber_js_1.default.ROUND_DOWN), collateralToken.decimals);
        };
        this.getCollateralAmountWithSwapSync = function (sizeAmount, leverage, side, poolAccount, inputTokenPrice, inputTokenEmaPrice, inputTokenCustodyAccount, swapOutTokenPrice, swapOutTokenEmaPrice, swapOutTokenCustodyAccount, collateralTokenPrice, collateralTokenEmaPrice, collateralTokenCustodyAccount, targetTokenPrice, targetTokenEmaPrice, targetTokenCustodyAccount, swapPoolAumUsdMax, poolConfigPosition, poolConfigSwap) {
            var collateralTokenMinPrice = _this.getMinAndMaxPriceSync(collateralTokenPrice, collateralTokenEmaPrice, collateralTokenCustodyAccount).min;
            var collateralTokenMinPriceUi = new bignumber_js_1.default(collateralTokenMinPrice.toString()).dividedBy(Math.pow(10, constants_1.USD_DECIMALS));
            var lockedUsd = targetTokenPrice.getAssetAmountUsd(sizeAmount, targetTokenCustodyAccount.decimals);
            var entryOraclePrice = _this.getEntryPriceUsdSync(side, targetTokenPrice, targetTokenEmaPrice, targetTokenCustodyAccount, lockedUsd);
            var entryPriceUsdUi = new bignumber_js_1.default(entryOraclePrice.toUiPrice(constants_1.ORACLE_EXPONENT));
            var openPosFeeRateUi = new bignumber_js_1.default(targetTokenCustodyAccount.fees.openPosition.toString()).dividedBy(Math.pow(10, constants_1.RATE_DECIMALS));
            var sizeAmountUi = new bignumber_js_1.default(sizeAmount.toString()).dividedBy(Math.pow(10, targetTokenCustodyAccount.decimals));
            var sizeUsdUi = entryPriceUsdUi.multipliedBy(sizeAmountUi);
            var collateralWithFeeUsdUi = sizeUsdUi.multipliedBy(new bignumber_js_1.default(1).plus(openPosFeeRateUi.multipliedBy(leverage))).dividedBy(leverage);
            var collateralAmtWithFeeUi = collateralWithFeeUsdUi.dividedBy(collateralTokenMinPriceUi);
            var collateralAmountWithFee = (0, utils_1.uiDecimalsToNative)(collateralAmtWithFeeUi.toFixed(collateralTokenCustodyAccount.decimals, bignumber_js_1.default.ROUND_DOWN), collateralTokenCustodyAccount.decimals);
            var collateralInInputToken;
            if (inputTokenCustodyAccount.publicKey.equals(collateralTokenCustodyAccount.publicKey)) {
                collateralInInputToken = collateralAmountWithFee;
            }
            else {
                collateralInInputToken = _this.getSwapAmountAndFeesSync(constants_1.BN_ZERO, collateralAmountWithFee, poolAccount, inputTokenPrice, inputTokenEmaPrice, inputTokenCustodyAccount, swapOutTokenPrice, swapOutTokenEmaPrice, swapOutTokenCustodyAccount, swapPoolAumUsdMax, poolConfigSwap).minAmountIn;
            }
            return collateralInInputToken;
        };
        this.getDecreaseSizeCollateralAndFeeSync = function (positionAccount, marketCorrelation, sizeDeltaUsd, keepLevSame, targetPrice, targetEmaPrice, marketConfig, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, side, poolConfig, discountBps, debugLogs) {
            if (discountBps === void 0) { discountBps = constants_1.BN_ZERO; }
            if (debugLogs === void 0) { debugLogs = false; }
            if (!marketConfig.marketAccount.equals(positionAccount.market)) {
                throw new Error("marketCustodyAccount mismatch");
            }
            if (!targetCustodyAccount.publicKey.equals(marketConfig.targetCustody)) {
                throw new Error("marketCustodyAccount mismatch");
            }
            if (!collateralCustodyAccount.publicKey.equals(marketConfig.collateralCustody)) {
                throw new Error("collateralCustodyAccount mismatch");
            }
            var collateralMinMaxPrice = _this.getMinAndMaxOraclePriceSync(collateralPrice, collateralEmaPrice, collateralCustodyAccount);
            var positionDelta = PositionAccount_1.PositionAccount.from(positionAccount.publicKey, __assign({}, positionAccount));
            var positionEntryOraclePrice = new OraclePrice_1.OraclePrice({
                price: positionAccount.entryPrice.price, exponent: new anchor_1.BN(positionAccount.entryPrice.exponent), confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO
            });
            var sizeDeltaAmount = positionEntryOraclePrice.getTokenAmount(sizeDeltaUsd, targetCustodyAccount.decimals);
            positionDelta.sizeAmount = sizeDeltaAmount;
            var decimalPower = new anchor_1.BN(Math.pow(10, targetCustodyAccount.decimals));
            var closeRatio = (positionDelta.sizeAmount.mul(decimalPower)).div(positionAccount.sizeAmount);
            positionDelta.sizeUsd = (positionAccount.sizeUsd.mul(closeRatio)).div(decimalPower);
            positionDelta.unsettledFeesUsd = (positionAccount.unsettledFeesUsd.mul(closeRatio)).div(decimalPower);
            positionDelta.lockedAmount = (positionAccount.lockedAmount.mul(closeRatio)).div(decimalPower);
            positionDelta.lockedUsd = (positionAccount.lockedUsd.mul(closeRatio)).div(decimalPower);
            positionDelta.collateralAmount = (positionAccount.collateralAmount.mul(closeRatio)).div(decimalPower);
            var newPnl = _this.getPnlSync(positionDelta, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, targetCustodyAccount.pricing.delaySeconds, poolConfig);
            var exitFeeUsd = positionDelta.sizeUsd.mul(targetCustodyAccount.fees.closePosition).div(new anchor_1.BN(constants_1.RATE_POWER));
            if (discountBps.gt(constants_1.BN_ZERO)) {
                var discount = exitFeeUsd.mul(discountBps).div(new anchor_1.BN(constants_1.BPS_POWER));
                exitFeeUsd = exitFeeUsd.sub(discount);
            }
            var lockAndUnsettledFeeUsd = _this.getLockFeeAndUnsettledUsdForPosition(positionDelta, collateralCustodyAccount, currentTimestamp);
            var totalFeesUsd = (exitFeeUsd.add(lockAndUnsettledFeeUsd));
            var currentCollateralUsd = collateralMinMaxPrice.min.getAssetAmountUsd(positionDelta.collateralAmount, collateralCustodyAccount.decimals);
            var liabilityUsd = newPnl.lossUsd.add(totalFeesUsd);
            var assetsUsd = newPnl.profitUsd.add(currentCollateralUsd);
            var closeAmount, feesAmount;
            if (debugLogs) {
                console.log("assetsUsd.sub(liabilityUsd):", collateralCustodyAccount.decimals, assetsUsd.toString(), liabilityUsd.toString(), assetsUsd.sub(liabilityUsd).toString());
            }
            if (assetsUsd.gte(liabilityUsd)) {
                closeAmount = collateralMinMaxPrice.max.getTokenAmount(assetsUsd.sub(liabilityUsd), collateralCustodyAccount.decimals);
                feesAmount = collateralMinMaxPrice.min.getTokenAmount(totalFeesUsd, collateralCustodyAccount.decimals);
            }
            else {
                closeAmount = constants_1.BN_ZERO;
                feesAmount = collateralMinMaxPrice.min.getTokenAmount(assetsUsd.sub(newPnl.lossUsd), collateralCustodyAccount.decimals);
            }
            var newPosition = PositionAccount_1.PositionAccount.from(positionAccount.publicKey, __assign({}, positionAccount));
            newPosition.sizeAmount = positionAccount.sizeAmount.sub(positionDelta.sizeAmount);
            newPosition.sizeUsd = positionAccount.sizeUsd.sub(positionDelta.sizeUsd);
            newPosition.lockedUsd = positionAccount.lockedUsd.sub(positionDelta.lockedUsd);
            newPosition.lockedAmount = positionAccount.lockedAmount.sub(positionDelta.lockedAmount);
            newPosition.collateralAmount = positionAccount.collateralAmount.sub(positionDelta.collateralAmount);
            newPosition.unsettledFeesUsd = positionAccount.unsettledFeesUsd.sub(positionDelta.unsettledFeesUsd);
            newPosition.collateralUsd = collateralMinMaxPrice.min.getAssetAmountUsd(newPosition.collateralAmount, collateralCustodyAccount.decimals);
            var feeUsdWithDiscount = constants_1.BN_ZERO;
            var feeUsd = sizeDeltaUsd.mul(targetCustodyAccount.fees.closePosition).div(new anchor_1.BN(constants_1.RATE_POWER));
            if (discountBps.gt(constants_1.BN_ZERO)) {
                feeUsdWithDiscount = feeUsd.mul(discountBps).div(new anchor_1.BN(constants_1.BPS_POWER));
                feeUsdWithDiscount = exitFeeUsd.sub(feeUsdWithDiscount);
            }
            else {
                feeUsdWithDiscount = feeUsd;
            }
            feeUsd = feeUsd.add(lockAndUnsettledFeeUsd);
            feeUsdWithDiscount = feeUsdWithDiscount.add(lockAndUnsettledFeeUsd);
            if (keepLevSame) {
                var collateralAmountReceived = closeAmount;
                var collateralAmountRecievedUsd = collateralMinMaxPrice.min.getAssetAmountUsd(collateralAmountReceived, collateralCustodyAccount.decimals);
                var maxWithdrawableAmount = _this.getMaxWithdrawableAmountSyncInternal(newPosition, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, poolConfig, closeAmount);
                if (debugLogs) {
                    console.log("maxWithdrawableAmount ", maxWithdrawableAmount.toString(), keepLevSame);
                    console.log("collateralAmountReceived ", collateralAmountReceived.toString(), keepLevSame);
                }
                if (collateralAmountReceived.lt(constants_1.BN_ZERO)) {
                    collateralAmountReceived = constants_1.BN_ZERO;
                    collateralAmountRecievedUsd = constants_1.BN_ZERO;
                }
                else if (collateralAmountReceived.gt(maxWithdrawableAmount)) {
                    if (debugLogs) {
                        console.log("exceeding to redicing maxWithdrawableAmount ", maxWithdrawableAmount.toString(), collateralAmountReceived.toString());
                    }
                    collateralAmountReceived = maxWithdrawableAmount;
                    collateralAmountRecievedUsd = collateralMinMaxPrice.min.getAssetAmountUsd(maxWithdrawableAmount, collateralCustodyAccount.decimals);
                }
                var entryPrice = OraclePrice_1.OraclePrice.from({ price: newPosition.entryPrice.price, exponent: new anchor_1.BN(newPosition.entryPrice.exponent), confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
                var finalInterestUsd = _this.getLockFeeAndUnsettledUsdForPosition(newPosition, collateralCustodyAccount, currentTimestamp);
                var finalLiquidationPrice = _this.getLiquidationPriceSync(newPosition.collateralAmount, newPosition.sizeAmount, entryPrice, finalInterestUsd, marketCorrelation, side, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, newPosition);
                var finalPnl = _this.getPnlSync(newPosition, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, targetCustodyAccount.pricing.delaySeconds, poolConfig);
                var finalPnlUsd = finalPnl.profitUsd.sub(finalPnl.lossUsd);
                var newLev = _this.getLeverageSync(newPosition.sizeUsd, newPosition.collateralAmount, collateralMinMaxPrice.min, collateralCustodyAccount.decimals, constants_1.BN_ZERO);
                return {
                    newSizeUsd: newPosition.sizeUsd,
                    feeUsd: feeUsd,
                    feeUsdWithDiscount: feeUsdWithDiscount,
                    lockAndUnsettledFeeUsd: lockAndUnsettledFeeUsd,
                    newLev: newLev,
                    liquidationPrice: finalLiquidationPrice,
                    collateralAmountRecieved: collateralAmountReceived,
                    newCollateralAmount: newPosition.collateralAmount,
                    newPnl: finalPnlUsd
                };
            }
            else {
                throw "only same leverage is supported for now";
            }
        };
        this.getMaxWithdrawableAmountSyncInternal = function (positionAccount, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, poolConfig, closeAmount, errorBandwidthPercentageUi) {
            if (closeAmount === void 0) { closeAmount = constants_1.BN_ZERO; }
            if (errorBandwidthPercentageUi === void 0) { errorBandwidthPercentageUi = 5; }
            if (errorBandwidthPercentageUi > 100 || errorBandwidthPercentageUi < 0) {
                throw new Error("errorBandwidthPercentageUi cannot be >100 or <0");
            }
            var MAX_INIT_LEVERAGE = targetCustodyAccount.pricing.maxInitialLeverage.mul(new anchor_1.BN(100 - errorBandwidthPercentageUi)).div(new anchor_1.BN(100));
            var profitLoss = _this.getPnlSync(positionAccount, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, targetCustodyAccount.pricing.delaySeconds, poolConfig);
            var _a = _this.getMinAndMaxOraclePriceSync(collateralPrice, collateralEmaPrice, collateralCustodyAccount), collateralMinPrice = _a.min, collateralMaxPrice = _a.max;
            var currentCollateralUsd = collateralMinPrice.getAssetAmountUsd(positionAccount.collateralAmount.add(closeAmount), collateralCustodyAccount.decimals);
            var availableInitMarginUsd = constants_1.BN_ZERO;
            if (profitLoss.lossUsd.lt(currentCollateralUsd)) {
                availableInitMarginUsd = currentCollateralUsd.sub(profitLoss.lossUsd);
            }
            else {
                console.log("profitLoss.lossUsd > coll :: should have been liquidated");
                return constants_1.BN_ZERO;
            }
            var maxRemovableCollateralUsd = availableInitMarginUsd.sub(positionAccount.sizeUsd.muln(constants_1.BPS_POWER).div(MAX_INIT_LEVERAGE));
            if (maxRemovableCollateralUsd.isNeg()) {
                return constants_1.BN_ZERO;
            }
            var maxWithdrawableAmount;
            var remainingCollateralUsd = availableInitMarginUsd.sub(maxRemovableCollateralUsd);
            if (remainingCollateralUsd < targetCustodyAccount.pricing.minCollateralUsd) {
                var diff = targetCustodyAccount.pricing.minCollateralUsd.sub(remainingCollateralUsd);
                var updatedMaxRemovableCollateralUsd = maxRemovableCollateralUsd.sub(diff);
                if (updatedMaxRemovableCollateralUsd.isNeg()) {
                    return constants_1.BN_ZERO;
                }
                else {
                    maxWithdrawableAmount = collateralMaxPrice.getTokenAmount(updatedMaxRemovableCollateralUsd, collateralCustodyAccount.decimals);
                }
            }
            else {
                maxWithdrawableAmount = collateralMaxPrice.getTokenAmount(maxRemovableCollateralUsd, collateralCustodyAccount.decimals);
            }
            return maxWithdrawableAmount;
        };
        this.getFinalCloseAmountSync = function (positionAccount, marketCorrelation, side, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, poolConfig) {
            var position = PositionAccount_1.PositionAccount.from(positionAccount.publicKey, __assign({}, positionAccount));
            var collateralMinMaxPrice = _this.getMinAndMaxOraclePriceSync(collateralPrice, collateralEmaPrice, collateralCustodyAccount);
            var collateralUsd = collateralMinMaxPrice.min.getAssetAmountUsd(position.collateralAmount, collateralCustodyAccount.decimals);
            var newPnl = _this.getPnlSync(position, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, targetCustodyAccount.pricing.delaySeconds, poolConfig);
            var exitPriceAndFee = _this.getExitPriceAndFeeSync(positionAccount, marketCorrelation, positionAccount.collateralAmount, positionAccount.sizeAmount, side, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp);
            var totalFeesUsd = (exitPriceAndFee.exitFeeUsd.add(exitPriceAndFee.borrowFeeUsd));
            var liabilityUsd = newPnl.lossUsd.add(totalFeesUsd);
            var assetsUsd = newPnl.profitUsd.add(collateralMinMaxPrice.min.getAssetAmountUsd(positionAccount.collateralAmount, positionAccount.collateralDecimals));
            var closeAmount, feesAmount;
            if (assetsUsd.gt(liabilityUsd)) {
                closeAmount = collateralMinMaxPrice.max.getTokenAmount(assetsUsd.sub(liabilityUsd), position.collateralDecimals);
                feesAmount = collateralMinMaxPrice.min.getTokenAmount(totalFeesUsd, positionAccount.collateralDecimals);
            }
            else {
                closeAmount = constants_1.BN_ZERO;
                feesAmount = collateralMinMaxPrice.min.getTokenAmount(assetsUsd.sub(newPnl.lossUsd), positionAccount.collateralDecimals);
            }
            return { closeAmount: closeAmount, feesAmount: feesAmount };
        };
        this.getMaxWithdrawableAmountSync = function (positionAccount, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, poolConfig, errorBandwidthPercentageUi) {
            if (errorBandwidthPercentageUi === void 0) { errorBandwidthPercentageUi = 5; }
            if (errorBandwidthPercentageUi > 100 || errorBandwidthPercentageUi < 0) {
                throw new Error("errorBandwidthPercentageUi cannot be >100 or <0");
            }
            var MAX_INIT_LEVERAGE = targetCustodyAccount.pricing.maxInitialLeverage.mul(new anchor_1.BN(100 - errorBandwidthPercentageUi)).div(new anchor_1.BN(100));
            var maxRemoveableCollateralUsdAfterMinRequired = positionAccount.collateralUsd.sub(targetCustodyAccount.pricing.minCollateralUsd.mul(new anchor_1.BN(100 + errorBandwidthPercentageUi)).div(new anchor_1.BN(100)));
            if (maxRemoveableCollateralUsdAfterMinRequired.isNeg()) {
                console.log("THIS cannot happen but still");
                return constants_1.BN_ZERO;
            }
            var profitLoss = _this.getPnlSync(positionAccount, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, targetCustodyAccount.pricing.delaySeconds, poolConfig);
            var _a = _this.getMinAndMaxOraclePriceSync(collateralPrice, collateralEmaPrice, collateralCustodyAccount), collateralMinPrice = _a.min, collateralMaxPrice = _a.max;
            var currentCollateralUsd = collateralMinPrice.getAssetAmountUsd(positionAccount.collateralAmount, collateralCustodyAccount.decimals);
            var availableInitMarginUsd = constants_1.BN_ZERO;
            if (profitLoss.lossUsd.lt(currentCollateralUsd)) {
                availableInitMarginUsd = currentCollateralUsd.sub(profitLoss.lossUsd);
            }
            else {
                console.log("profitLoss.lossUsd > coll :: should have been liquidated");
                return constants_1.BN_ZERO;
            }
            var maxRemovableCollateralUsd = availableInitMarginUsd.sub(positionAccount.sizeUsd.muln(constants_1.BPS_POWER).div(MAX_INIT_LEVERAGE));
            if (maxRemovableCollateralUsd.isNeg()) {
                return constants_1.BN_ZERO;
            }
            var maxWithdrawableAmount;
            if (maxRemoveableCollateralUsdAfterMinRequired.lt(maxRemovableCollateralUsd)) {
                maxWithdrawableAmount = collateralMaxPrice.getTokenAmount(maxRemoveableCollateralUsdAfterMinRequired, collateralCustodyAccount.decimals);
            }
            else {
                maxWithdrawableAmount = collateralMaxPrice.getTokenAmount(maxRemovableCollateralUsd, collateralCustodyAccount.decimals);
            }
            return maxWithdrawableAmount;
        };
        this.getCumulativeLockFeeSync = function (custodyAccount, currentTimestamp) {
            var cumulativeLockFee = constants_1.BN_ZERO;
            if (currentTimestamp.gt(custodyAccount.borrowRateState.lastUpdate)) {
                cumulativeLockFee = (currentTimestamp
                    .sub(custodyAccount.borrowRateState.lastUpdate))
                    .mul(custodyAccount.borrowRateState.currentRate)
                    .div(new anchor_1.BN(3600))
                    .add(custodyAccount.borrowRateState.cumulativeLockFee);
            }
            else {
                cumulativeLockFee = custodyAccount.borrowRateState.cumulativeLockFee;
            }
            return cumulativeLockFee;
        };
        this.getBorrowRateSync = function (custodyAccount, currentUtilization) {
            var borrowRate = constants_1.BN_ZERO;
            if (currentUtilization.lt(custodyAccount.borrowRate.optimalUtilization)
                || (custodyAccount.borrowRate.optimalUtilization.gte(new anchor_1.BN(constants_1.RATE_POWER)))) {
                borrowRate = (currentUtilization.mul(custodyAccount.borrowRate.slope1))
                    .div(custodyAccount.borrowRate.optimalUtilization);
            }
            else if (currentUtilization.lt(custodyAccount.pricing.maxUtilization)) {
                borrowRate = custodyAccount.borrowRate.slope1
                    .add(currentUtilization.sub(custodyAccount.borrowRate.optimalUtilization)
                    .mul(custodyAccount.borrowRate.slope2)
                    .div(custodyAccount.pricing.maxUtilization.sub(custodyAccount.borrowRate.optimalUtilization)));
            }
            else {
                borrowRate = custodyAccount.borrowRate.slope1.add(custodyAccount.borrowRate.slope2);
            }
            return borrowRate;
        };
        this.getLockFeeAndUnsettledUsdForPosition = function (position, collateralCustodyAccount, currentTimestamp) {
            var cumulativeLockFee = _this.getCumulativeLockFeeSync(collateralCustodyAccount, currentTimestamp);
            var lockFeeUsd = constants_1.BN_ZERO;
            if (cumulativeLockFee.gt(position.cumulativeLockFeeSnapshot)) {
                lockFeeUsd = cumulativeLockFee.sub(position.cumulativeLockFeeSnapshot).mul(position.lockedUsd).div(new anchor_1.BN(constants_1.RATE_POWER));
            }
            lockFeeUsd = lockFeeUsd.add(position.unsettledFeesUsd);
            return lockFeeUsd;
        };
        this.getLockedUsd = function (sideUsd, side, marketCorrelation, maxPayOffBps) {
            var maxPayOffBpsNew = constants_1.BN_ZERO;
            if (marketCorrelation || (0, types_1.isVariant)(side, 'short')) {
                maxPayOffBpsNew = anchor_1.BN.min(new anchor_1.BN(constants_1.BPS_POWER), maxPayOffBps);
            }
            else {
                maxPayOffBpsNew = maxPayOffBps;
            }
            var lockedUsd = (sideUsd.mul(maxPayOffBpsNew)).div(new anchor_1.BN(constants_1.BPS_POWER));
            return lockedUsd;
        };
        this.getLiquidationPriceSync = function (collateralAmount, sizeAmount, entryOraclePrice, lockAndUnsettledFeeUsd, marketCorrelation, side, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, positionAccount) {
            var zeroOraclePrice = OraclePrice_1.OraclePrice.from({
                price: constants_1.BN_ZERO,
                exponent: constants_1.BN_ZERO,
                confidence: constants_1.BN_ZERO,
                timestamp: constants_1.BN_ZERO
            });
            if (collateralAmount.isZero() || sizeAmount.isZero()) {
                return zeroOraclePrice;
            }
            if (positionAccount.entryPrice.exponent && !entryOraclePrice.exponent.eq(new anchor_1.BN(positionAccount.entryPrice.exponent))) {
                throw new Error("Exponent mismatch : ".concat(positionAccount.entryPrice.exponent, " & ").concat(entryOraclePrice.exponent.toString(), " ").concat(entryOraclePrice === null || entryOraclePrice === void 0 ? void 0 : entryOraclePrice.toUiPrice(8)));
            }
            var exitFeeUsd = positionAccount.sizeUsd.mul(targetCustodyAccount.fees.closePosition).div(new anchor_1.BN(constants_1.RATE_POWER));
            var unsettledLossUsd = exitFeeUsd.add(lockAndUnsettledFeeUsd);
            var liablitiesUsd = positionAccount.sizeUsd.mul(new anchor_1.BN(constants_1.BPS_POWER)).div(targetCustodyAccount.pricing.maxLeverage).add(unsettledLossUsd);
            var targetMinMaxPriceOracle = _this.getMinAndMaxOraclePriceSync(targetPrice, targetEmaPrice, targetCustodyAccount);
            var collateralMinMaxPriceOracle = _this.getMinAndMaxOraclePriceSync(collateralPrice, collateralEmaPrice, collateralCustodyAccount);
            var liquidationPrice;
            if (marketCorrelation && (0, types_1.isVariant)(side, 'long')) {
                var newCollateralAmount = void 0;
                if (targetCustodyAccount.mint == collateralCustodyAccount.mint) {
                    newCollateralAmount = collateralAmount;
                }
                else {
                    var pairPrice = collateralMinMaxPriceOracle.min.price.mul(new anchor_1.BN(10).pow(collateralMinMaxPriceOracle.min.exponent)).div(targetMinMaxPriceOracle.max.price);
                    var swapPrice = pairPrice.sub(pairPrice.mul(collateralCustodyAccount.pricing.swapSpread).div(new anchor_1.BN(constants_1.BPS_POWER)));
                    newCollateralAmount = (0, utils_1.checkedDecimalMul)(collateralAmount, new anchor_1.BN(-1 * collateralCustodyAccount.decimals), swapPrice, collateralMinMaxPriceOracle.min.exponent, new anchor_1.BN(-1 * targetCustodyAccount.decimals));
                }
                var lp = OraclePrice_1.OraclePrice.from({
                    price: (positionAccount.sizeUsd.add(liablitiesUsd)).mul(new anchor_1.BN(Math.pow(10, (positionAccount.sizeDecimals + 3))))
                        .div(sizeAmount.add(newCollateralAmount)),
                    exponent: new anchor_1.BN(-1 * constants_1.RATE_DECIMALS),
                    confidence: constants_1.BN_ZERO,
                    timestamp: constants_1.BN_ZERO
                });
                liquidationPrice = lp.scale_to_exponent(new anchor_1.BN(entryOraclePrice.exponent));
            }
            else {
                var assetsUsd = collateralMinMaxPriceOracle.min.getAssetAmountUsd(collateralAmount, collateralCustodyAccount.decimals);
                if (assetsUsd.gte(liablitiesUsd)) {
                    var priceDiffLossOracle = OraclePrice_1.OraclePrice.from({
                        price: (assetsUsd.sub(liablitiesUsd)).mul(new anchor_1.BN(Math.pow(10, (positionAccount.sizeDecimals + 3))))
                            .div(positionAccount.sizeAmount),
                        exponent: new anchor_1.BN(-1 * constants_1.RATE_DECIMALS),
                        confidence: constants_1.BN_ZERO,
                        timestamp: constants_1.BN_ZERO
                    }).scale_to_exponent(new anchor_1.BN(entryOraclePrice.exponent));
                    if ((0, types_1.isVariant)(side, 'long')) {
                        liquidationPrice = OraclePrice_1.OraclePrice.from({
                            price: entryOraclePrice.price.sub(priceDiffLossOracle.price),
                            exponent: new anchor_1.BN(entryOraclePrice.exponent),
                            confidence: constants_1.BN_ZERO,
                            timestamp: constants_1.BN_ZERO
                        });
                    }
                    else {
                        liquidationPrice = OraclePrice_1.OraclePrice.from({
                            price: entryOraclePrice.price.add(priceDiffLossOracle.price),
                            exponent: new anchor_1.BN(entryOraclePrice.exponent),
                            confidence: constants_1.BN_ZERO,
                            timestamp: constants_1.BN_ZERO
                        });
                    }
                }
                else {
                    var priceDiffProfitOracle = OraclePrice_1.OraclePrice.from({
                        price: (liablitiesUsd.sub(assetsUsd)).mul(new anchor_1.BN(Math.pow(10, (positionAccount.sizeDecimals + 3))))
                            .div(positionAccount.sizeAmount),
                        exponent: new anchor_1.BN(-1 * constants_1.RATE_DECIMALS),
                        confidence: constants_1.BN_ZERO,
                        timestamp: constants_1.BN_ZERO
                    }).scale_to_exponent(new anchor_1.BN(entryOraclePrice.exponent));
                    if ((0, types_1.isVariant)(side, 'long')) {
                        liquidationPrice = OraclePrice_1.OraclePrice.from({
                            price: entryOraclePrice.price.add(priceDiffProfitOracle.price),
                            exponent: new anchor_1.BN(entryOraclePrice.exponent),
                            confidence: constants_1.BN_ZERO,
                            timestamp: constants_1.BN_ZERO
                        });
                    }
                    else {
                        liquidationPrice = OraclePrice_1.OraclePrice.from({
                            price: entryOraclePrice.price.sub(priceDiffProfitOracle.price),
                            exponent: new anchor_1.BN(entryOraclePrice.exponent),
                            confidence: constants_1.BN_ZERO,
                            timestamp: constants_1.BN_ZERO
                        });
                    }
                }
            }
            return liquidationPrice.price.isNeg() ? zeroOraclePrice : liquidationPrice;
        };
        this.getLiquidationPriceWithOrder = function (collateralAmount, collateralUsd, sizeAmount, sizeUsd, sizeDecimals, limitOraclePrice, marketCorrelation, side, targetPrice, targetEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount) {
            var zeroOraclePrice = OraclePrice_1.OraclePrice.from({
                price: constants_1.BN_ZERO,
                exponent: constants_1.BN_ZERO,
                confidence: constants_1.BN_ZERO,
                timestamp: constants_1.BN_ZERO
            });
            if (collateralAmount.isZero() || sizeAmount.isZero()) {
                return zeroOraclePrice;
            }
            var exitFeeUsd = sizeUsd.mul(targetCustodyAccount.fees.closePosition).div(new anchor_1.BN(constants_1.RATE_POWER));
            var unsettledLossUsd = exitFeeUsd;
            var liablitiesUsd = sizeUsd.mul(new anchor_1.BN(constants_1.BPS_POWER)).div(targetCustodyAccount.pricing.maxLeverage).add(unsettledLossUsd);
            var targetMinMaxPriceOracle = _this.getMinAndMaxOraclePriceSync(targetPrice, targetEmaPrice, targetCustodyAccount);
            var collateralMinMaxPriceOracle = _this.getMinAndMaxOraclePriceSync(collateralPrice, collateralEmaPrice, collateralCustodyAccount);
            var liquidationPrice;
            if (marketCorrelation && (0, types_1.isVariant)(side, 'long')) {
                var newCollateralAmount = void 0;
                if (targetCustodyAccount.mint == collateralCustodyAccount.mint) {
                    newCollateralAmount = collateralAmount;
                }
                else {
                    var pairPrice = collateralMinMaxPriceOracle.min.price.mul(new anchor_1.BN(10).pow(collateralMinMaxPriceOracle.min.exponent)).div(targetMinMaxPriceOracle.max.price);
                    var swapPrice = pairPrice.sub(pairPrice.mul(collateralCustodyAccount.pricing.swapSpread).div(new anchor_1.BN(constants_1.BPS_POWER)));
                    newCollateralAmount = (0, utils_1.checkedDecimalMul)(collateralAmount, new anchor_1.BN(-1 * collateralCustodyAccount.decimals), swapPrice, collateralMinMaxPriceOracle.min.exponent, new anchor_1.BN(-1 * targetCustodyAccount.decimals));
                }
                var lp = OraclePrice_1.OraclePrice.from({
                    price: (sizeUsd.add(liablitiesUsd)).mul(new anchor_1.BN(Math.pow(10, (sizeDecimals + 3))))
                        .div(sizeAmount.add(newCollateralAmount)),
                    exponent: new anchor_1.BN(-1 * constants_1.RATE_DECIMALS),
                    confidence: constants_1.BN_ZERO,
                    timestamp: constants_1.BN_ZERO
                });
                liquidationPrice = lp.scale_to_exponent(new anchor_1.BN(limitOraclePrice.exponent));
            }
            else {
                var assetsUsd = collateralUsd;
                if (assetsUsd.gte(liablitiesUsd)) {
                    var priceDiffLossOracle = OraclePrice_1.OraclePrice.from({
                        price: (assetsUsd.sub(liablitiesUsd)).mul(new anchor_1.BN(Math.pow(10, (sizeDecimals + 3))))
                            .div(sizeAmount),
                        exponent: new anchor_1.BN(-1 * constants_1.RATE_DECIMALS),
                        confidence: constants_1.BN_ZERO,
                        timestamp: constants_1.BN_ZERO
                    }).scale_to_exponent(new anchor_1.BN(limitOraclePrice.exponent));
                    if ((0, types_1.isVariant)(side, 'long')) {
                        liquidationPrice = OraclePrice_1.OraclePrice.from({
                            price: limitOraclePrice.price.sub(priceDiffLossOracle.price),
                            exponent: new anchor_1.BN(limitOraclePrice.exponent),
                            confidence: constants_1.BN_ZERO,
                            timestamp: constants_1.BN_ZERO
                        });
                    }
                    else {
                        liquidationPrice = OraclePrice_1.OraclePrice.from({
                            price: limitOraclePrice.price.add(priceDiffLossOracle.price),
                            exponent: new anchor_1.BN(limitOraclePrice.exponent),
                            confidence: constants_1.BN_ZERO,
                            timestamp: constants_1.BN_ZERO
                        });
                    }
                }
                else {
                    var priceDiffProfitOracle = OraclePrice_1.OraclePrice.from({
                        price: (liablitiesUsd.sub(assetsUsd)).mul(new anchor_1.BN(Math.pow(10, (sizeDecimals + 3))))
                            .div(sizeAmount),
                        exponent: new anchor_1.BN(-1 * constants_1.RATE_DECIMALS),
                        confidence: constants_1.BN_ZERO,
                        timestamp: constants_1.BN_ZERO
                    }).scale_to_exponent(new anchor_1.BN(limitOraclePrice.exponent));
                    if ((0, types_1.isVariant)(side, 'long')) {
                        liquidationPrice = OraclePrice_1.OraclePrice.from({
                            price: limitOraclePrice.price.add(priceDiffProfitOracle.price),
                            exponent: new anchor_1.BN(limitOraclePrice.exponent),
                            confidence: constants_1.BN_ZERO,
                            timestamp: constants_1.BN_ZERO
                        });
                    }
                    else {
                        liquidationPrice = OraclePrice_1.OraclePrice.from({
                            price: limitOraclePrice.price.sub(priceDiffProfitOracle.price),
                            exponent: new anchor_1.BN(limitOraclePrice.exponent),
                            confidence: constants_1.BN_ZERO,
                            timestamp: constants_1.BN_ZERO
                        });
                    }
                }
            }
            return liquidationPrice.price.isNeg() ? zeroOraclePrice : liquidationPrice;
        };
        this.getMaxProfitPriceSync = function (entryPrice, marketCorrelation, side, positionAccount) {
            var zeroOraclePrice = OraclePrice_1.OraclePrice.from({
                price: constants_1.BN_ZERO,
                exponent: constants_1.BN_ZERO,
                confidence: constants_1.BN_ZERO,
                timestamp: constants_1.BN_ZERO
            });
            if (positionAccount.sizeAmount.isZero()) {
                return zeroOraclePrice;
            }
            var priceDiffProfit = OraclePrice_1.OraclePrice.from({
                price: positionAccount.lockedUsd.mul(new anchor_1.BN(10).pow(new anchor_1.BN(positionAccount.sizeDecimals + 3)))
                    .div(positionAccount.sizeAmount),
                exponent: new anchor_1.BN(-1 * constants_1.RATE_DECIMALS),
                confidence: constants_1.BN_ZERO,
                timestamp: constants_1.BN_ZERO
            }).scale_to_exponent(entryPrice.exponent);
            var maxProfitPrice;
            if ((0, types_1.isVariant)(side, 'long')) {
                if (marketCorrelation) {
                    return zeroOraclePrice;
                }
                maxProfitPrice = OraclePrice_1.OraclePrice.from({
                    price: entryPrice.price.add(priceDiffProfit.price),
                    exponent: entryPrice.exponent,
                    confidence: constants_1.BN_ZERO,
                    timestamp: constants_1.BN_ZERO
                });
            }
            else {
                maxProfitPrice = OraclePrice_1.OraclePrice.from({
                    price: entryPrice.price.sub(priceDiffProfit.price),
                    exponent: entryPrice.exponent,
                    confidence: constants_1.BN_ZERO,
                    timestamp: constants_1.BN_ZERO
                });
            }
            return maxProfitPrice.price.isNeg() ? zeroOraclePrice : maxProfitPrice;
        };
        this.getEstimateProfitLossforTpSlEntry = function (positionAccount, isTakeProfit, userEntrytpSlOraclePrice, collateralDeltaAmount, sizeDeltaAmount, side, marketAccountPk, targetTokenPrice, targetTokenEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, poolConfig) {
            if (collateralDeltaAmount.isNeg() || sizeDeltaAmount.isNeg()) {
                throw new Error("Delta Amounts cannot be negative.");
            }
            var lockedUsd = targetTokenEmaPrice.getAssetAmountUsd(sizeDeltaAmount, targetCustodyAccount.decimals);
            var entryOraclePrice = _this.getEntryPriceUsdSync(side, targetTokenPrice, targetTokenEmaPrice, targetCustodyAccount, lockedUsd);
            if (positionAccount === null) {
                var data = __assign({}, types_1.DEFAULT_POSITION);
                positionAccount = PositionAccount_1.PositionAccount.from(web3_js_1.PublicKey.default, data);
                positionAccount.sizeDecimals = targetCustodyAccount.decimals;
                positionAccount.collateralDecimals = collateralCustodyAccount.decimals;
                positionAccount.lockedDecimals = collateralCustodyAccount.decimals;
                positionAccount.entryPrice.price = entryOraclePrice.price;
                positionAccount.entryPrice.exponent = entryOraclePrice.exponent.toNumber();
            }
            else {
                positionAccount = positionAccount.clone();
                var positionEntryPrice = OraclePrice_1.OraclePrice.from({
                    price: positionAccount.entryPrice.price,
                    exponent: new anchor_1.BN(positionAccount.entryPrice.exponent),
                    confidence: constants_1.BN_ZERO,
                    timestamp: constants_1.BN_ZERO
                });
                entryOraclePrice.price = _this.getAveragePriceSync(positionEntryPrice.price, positionAccount.sizeAmount, entryOraclePrice.price, sizeDeltaAmount);
                positionAccount.entryPrice.price = entryOraclePrice.price;
            }
            var sizeDeltaUsd = entryOraclePrice.getAssetAmountUsd(sizeDeltaAmount, targetCustodyAccount.decimals);
            positionAccount.sizeUsd = positionAccount.sizeUsd.add(sizeDeltaUsd);
            positionAccount.sizeAmount = positionAccount.sizeAmount.add(sizeDeltaAmount);
            positionAccount.market = marketAccountPk;
            positionAccount.lockedUsd = targetTokenPrice.getAssetAmountUsd(positionAccount.sizeAmount, targetCustodyAccount.decimals);
            positionAccount.lockedAmount = collateralPrice.getTokenAmount(positionAccount.lockedUsd, collateralCustodyAccount.decimals);
            positionAccount.collateralAmount = positionAccount.collateralAmount.add(collateralDeltaAmount);
            positionAccount.collateralUsd = collateralPrice.getAssetAmountUsd(positionAccount.collateralAmount, collateralCustodyAccount.decimals);
            var currentTime = new anchor_1.BN((0, utils_1.getUnixTs)());
            var pnl = _this.getPnlSync(positionAccount, userEntrytpSlOraclePrice, userEntrytpSlOraclePrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTime, targetCustodyAccount.pricing.delaySeconds, poolConfig);
            var pnlUsd = pnl.profitUsd.sub(pnl.lossUsd);
            var pnlPercentage = pnlUsd.mul(new anchor_1.BN(constants_1.BPS_POWER)).div(positionAccount.collateralUsd);
            if (isTakeProfit) {
                return {
                    pnlUsd: pnl.profitUsd,
                    pnlPercentage: pnlPercentage
                };
            }
            else {
                return {
                    pnlUsd: pnl.lossUsd,
                    pnlPercentage: pnlPercentage
                };
            }
        };
        this.getTriggerPriceFromPnlSync = function (pnlUsd, exitFeeUsd, positionSize, sizeDecimals, entryPrice, side) {
            var usdDecimals = 6;
            var scaledSizeAmount;
            if (sizeDecimals > usdDecimals) {
                scaledSizeAmount = positionSize.div(new anchor_1.BN(10).pow(new anchor_1.BN(sizeDecimals - usdDecimals)));
            }
            else {
                scaledSizeAmount = positionSize.mul(new anchor_1.BN(10).pow(new anchor_1.BN(usdDecimals - sizeDecimals)));
            }
            if (scaledSizeAmount.isZero()) {
                throw new Error("Position size cannot be zero");
            }
            var exitPrice;
            if ((0, types_1.isVariant)(side, 'long')) {
                exitPrice = entryPrice.price.add((pnlUsd.add(exitFeeUsd)).mul(new anchor_1.BN(Math.pow(10, entryPrice.exponent.abs().toNumber()))).div(scaledSizeAmount));
            }
            else {
                exitPrice = entryPrice.price.sub((pnlUsd.add(exitFeeUsd)).mul(new anchor_1.BN(Math.pow(10, entryPrice.exponent.abs().toNumber()))).div(scaledSizeAmount));
            }
            return new OraclePrice_1.OraclePrice({
                price: exitPrice,
                exponent: entryPrice.exponent,
                confidence: entryPrice.confidence,
                timestamp: constants_1.BN_ZERO,
            });
        };
        this.getTriggerPriceFromRoiSync = function (roi, collateralUsd, exitFeeUsd, positionSize, sizeDecimals, entryPrice, side) {
            var usdDecimals = 6;
            var scaledSizeAmount;
            if (sizeDecimals > usdDecimals) {
                scaledSizeAmount = positionSize.div(new anchor_1.BN(10).pow(new anchor_1.BN(sizeDecimals - usdDecimals)));
            }
            else {
                scaledSizeAmount = positionSize.mul(new anchor_1.BN(10).pow(new anchor_1.BN(usdDecimals - sizeDecimals)));
            }
            if (scaledSizeAmount.isZero()) {
                throw new Error("Position size cannot be zero");
            }
            var pnlUsd = roi.mul(collateralUsd).div(new anchor_1.BN(100));
            var exitPrice;
            if ((0, types_1.isVariant)(side, 'long')) {
                exitPrice = entryPrice.price.add((pnlUsd.add(exitFeeUsd)).mul(new anchor_1.BN(Math.pow(10, entryPrice.exponent.abs().toNumber()))).div(scaledSizeAmount));
            }
            else {
                exitPrice = entryPrice.price.sub((pnlUsd.add(exitFeeUsd)).mul(new anchor_1.BN(Math.pow(10, entryPrice.exponent.abs().toNumber()))).div(scaledSizeAmount));
            }
            return new OraclePrice_1.OraclePrice({
                price: exitPrice,
                exponent: entryPrice.exponent,
                confidence: entryPrice.confidence,
                timestamp: constants_1.BN_ZERO,
            });
        };
        this.getPnlSync = function (positionAccount, targetTokenPrice, targetTokenEmaPrice, targetCustodyAccount, collateralPrice, collateralEmaPrice, collateralCustodyAccount, currentTimestamp, delay, poolConfig) {
            if (positionAccount.sizeUsd.isZero() || positionAccount.entryPrice.price.isZero()) {
                return {
                    profitUsd: constants_1.BN_ZERO,
                    lossUsd: constants_1.BN_ZERO,
                };
            }
            var side = poolConfig.getMarketConfigByPk(positionAccount.market).side;
            var lockedUsd = targetTokenPrice.getAssetAmountUsd(positionAccount.sizeAmount, targetCustodyAccount.decimals);
            var exitOraclePrice = _this.getExitOraclePriceSync(side, targetTokenPrice, targetTokenEmaPrice, targetCustodyAccount, lockedUsd);
            var collateralMinPrice = _this.getMinAndMaxOraclePriceSync(collateralPrice, collateralEmaPrice, collateralCustodyAccount).min;
            var priceDiffProfit, priceDiffLoss;
            var positionEntryPrice = OraclePrice_1.OraclePrice.from({
                price: positionAccount.entryPrice.price,
                exponent: new anchor_1.BN(positionAccount.entryPrice.exponent),
                confidence: constants_1.BN_ZERO,
                timestamp: constants_1.BN_ZERO
            });
            if (!exitOraclePrice.exponent.eq(positionEntryPrice.exponent)) {
                throw new Error("exponent mistach");
            }
            if ((0, types_1.isVariant)(side, 'long')) {
                if (exitOraclePrice.price.gt(positionEntryPrice.price)) {
                    if (currentTimestamp.gt(positionAccount.updateTime.add(delay))) {
                        priceDiffProfit = new OraclePrice_1.OraclePrice({ price: exitOraclePrice.price.sub(positionEntryPrice.price), exponent: exitOraclePrice.exponent, confidence: exitOraclePrice.confidence, timestamp: constants_1.BN_ZERO });
                        priceDiffLoss = new OraclePrice_1.OraclePrice({ price: constants_1.BN_ZERO, exponent: exitOraclePrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
                    }
                    else {
                        priceDiffProfit = new OraclePrice_1.OraclePrice({ price: constants_1.BN_ZERO, exponent: exitOraclePrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
                        priceDiffLoss = new OraclePrice_1.OraclePrice({ price: constants_1.BN_ZERO, exponent: exitOraclePrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
                    }
                }
                else {
                    priceDiffProfit = new OraclePrice_1.OraclePrice({ price: constants_1.BN_ZERO, exponent: exitOraclePrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
                    priceDiffLoss = new OraclePrice_1.OraclePrice({ price: positionEntryPrice.price.sub(exitOraclePrice.price), exponent: exitOraclePrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
                }
            }
            else {
                if (exitOraclePrice.price.lt(positionEntryPrice.price)) {
                    if (currentTimestamp.gt(positionAccount.updateTime.add(delay))) {
                        priceDiffProfit = new OraclePrice_1.OraclePrice({ price: positionEntryPrice.price.sub(exitOraclePrice.price), exponent: exitOraclePrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
                        priceDiffLoss = new OraclePrice_1.OraclePrice({ price: constants_1.BN_ZERO, exponent: exitOraclePrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
                    }
                    else {
                        priceDiffProfit = new OraclePrice_1.OraclePrice({ price: constants_1.BN_ZERO, exponent: exitOraclePrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
                        priceDiffLoss = new OraclePrice_1.OraclePrice({ price: constants_1.BN_ZERO, exponent: exitOraclePrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
                    }
                }
                else {
                    priceDiffProfit = new OraclePrice_1.OraclePrice({ price: constants_1.BN_ZERO, exponent: exitOraclePrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
                    priceDiffLoss = new OraclePrice_1.OraclePrice({ price: exitOraclePrice.price.sub(positionEntryPrice.price), exponent: exitOraclePrice.exponent, confidence: constants_1.BN_ZERO, timestamp: constants_1.BN_ZERO });
                }
            }
            ;
            if (!priceDiffProfit.exponent.eq(priceDiffLoss.exponent)) {
                throw new Error("exponent mistach");
            }
            if (priceDiffProfit.price.gt(constants_1.BN_ZERO)) {
                return {
                    profitUsd: anchor_1.BN.min(priceDiffProfit.getAssetAmountUsd(positionAccount.sizeAmount, positionAccount.sizeDecimals), collateralMinPrice.getAssetAmountUsd(positionAccount.lockedAmount, positionAccount.lockedDecimals)),
                    lossUsd: constants_1.BN_ZERO,
                };
            }
            else {
                return {
                    profitUsd: constants_1.BN_ZERO,
                    lossUsd: priceDiffLoss.getAssetAmountUsd(positionAccount.sizeAmount, positionAccount.sizeDecimals),
                };
            }
        };
        this.getSwapAmountAndFeesSync = function (amountIn, amountOut, poolAccount, inputTokenPrice, inputTokenEmaPrice, inputTokenCustodyAccount, outputTokenPrice, outputTokenEmaPrice, outputTokenCustodyAccount, poolAumUsdMax, poolConfig) {
            if (!amountIn.isZero() && !amountOut.isZero()) {
                throw new Error("both amountIn and amountOut cannot be non-zero");
            }
            if (amountIn.isZero() && amountOut.isZero()) {
                return {
                    minAmountIn: constants_1.BN_ZERO,
                    minAmountOut: constants_1.BN_ZERO,
                    feeIn: constants_1.BN_ZERO,
                    feeOut: constants_1.BN_ZERO,
                };
            }
            var newInputTokenPrice, newInputTokenEmaPrice;
            var newOutputTokenPrice, newOutputTokenEmaPrice;
            if (inputTokenPrice.exponent.lte(outputTokenPrice.exponent)) {
                newInputTokenPrice = inputTokenPrice;
                newInputTokenEmaPrice = inputTokenEmaPrice;
                newOutputTokenPrice = outputTokenPrice.scale_to_exponent(inputTokenPrice.exponent);
                newOutputTokenEmaPrice = outputTokenEmaPrice.scale_to_exponent(inputTokenPrice.exponent);
            }
            else {
                newInputTokenPrice = inputTokenPrice.scale_to_exponent(outputTokenPrice.exponent);
                newInputTokenEmaPrice = inputTokenEmaPrice.scale_to_exponent(outputTokenPrice.exponent);
                newOutputTokenPrice = outputTokenPrice;
                newOutputTokenEmaPrice = outputTokenEmaPrice;
            }
            if (!newInputTokenPrice.exponent.eq(newOutputTokenPrice.exponent)) {
                throw "Exponents mistmatch ".concat(newInputTokenPrice.exponent.toNumber(), " != ").concat(newOutputTokenPrice.exponent.toNumber());
            }
            var inputMinMaxPrice = _this.getMinAndMaxOraclePriceSync(newInputTokenPrice, newInputTokenEmaPrice, inputTokenCustodyAccount);
            var outputMinMaxPrice = _this.getMinAndMaxOraclePriceSync(newOutputTokenPrice, newOutputTokenEmaPrice, outputTokenCustodyAccount);
            var pairPrice;
            var inputTokenAmount;
            var outputTokenAmount;
            var feeIn;
            var feeOut;
            if (amountIn.isZero()) {
                if (inputTokenCustodyAccount.isStable &&
                    inputMinMaxPrice.min != inputMinMaxPrice.max &&
                    inputTokenCustodyAccount.depegAdjustment) {
                    pairPrice = outputMinMaxPrice.min.price;
                }
                else {
                    pairPrice = outputMinMaxPrice.min.price.mul(new anchor_1.BN(10).pow(outputMinMaxPrice.min.exponent)).div(inputMinMaxPrice.max.price);
                }
                var swapPrice = pairPrice.sub(pairPrice.mul(outputTokenCustodyAccount.pricing.swapSpread).div(new anchor_1.BN(constants_1.BPS_POWER)));
                inputTokenAmount = (0, utils_1.checkedDecimalMul)(amountOut, new anchor_1.BN(-1 * outputTokenCustodyAccount.decimals), swapPrice, inputMinMaxPrice.min.exponent, new anchor_1.BN(-1 * inputTokenCustodyAccount.decimals));
                feeIn = _this.getFeeHelper(types_1.FeesAction.SwapIn, inputTokenAmount, constants_1.BN_ZERO, inputTokenCustodyAccount, inputMinMaxPrice.max, poolAumUsdMax, poolAccount, poolConfig).feeAmount;
                feeOut = _this.getFeeHelper(types_1.FeesAction.SwapOut, constants_1.BN_ZERO, amountOut, outputTokenCustodyAccount, outputMinMaxPrice.max, poolAumUsdMax, poolAccount, poolConfig).feeAmount;
                var swapAmount = (0, utils_1.checkedDecimalMul)(amountOut.add(feeOut), new anchor_1.BN(-1 * outputTokenCustodyAccount.decimals), swapPrice, inputMinMaxPrice.min.exponent, new anchor_1.BN(-1 * inputTokenCustodyAccount.decimals)).add(feeIn);
                return {
                    minAmountIn: swapAmount,
                    minAmountOut: constants_1.BN_ZERO,
                    feeIn: feeIn,
                    feeOut: feeOut,
                };
            }
            else {
                if (outputTokenCustodyAccount.isStable &&
                    outputMinMaxPrice.min != outputMinMaxPrice.max &&
                    outputTokenCustodyAccount.depegAdjustment) {
                    pairPrice = inputMinMaxPrice.min.price;
                }
                else {
                    pairPrice = inputMinMaxPrice.min.price.mul(new anchor_1.BN(10).pow(inputMinMaxPrice.min.exponent)).div(outputMinMaxPrice.max.price);
                }
                var swapPrice = pairPrice.sub(pairPrice.mul(inputTokenCustodyAccount.pricing.swapSpread).div(new anchor_1.BN(constants_1.BPS_POWER)));
                outputTokenAmount = (0, utils_1.checkedDecimalMul)(amountIn, new anchor_1.BN(-1 * inputTokenCustodyAccount.decimals), swapPrice, inputMinMaxPrice.min.exponent, new anchor_1.BN(-1 * outputTokenCustodyAccount.decimals));
                feeIn = _this.getFeeHelper(types_1.FeesAction.SwapIn, amountIn, constants_1.BN_ZERO, inputTokenCustodyAccount, inputMinMaxPrice.max, poolAumUsdMax, poolAccount, poolConfig).feeAmount;
                feeOut = _this.getFeeHelper(types_1.FeesAction.SwapOut, constants_1.BN_ZERO, outputTokenAmount, outputTokenCustodyAccount, outputMinMaxPrice.max, poolAumUsdMax, poolAccount, poolConfig).feeAmount;
                var swapAmount = (0, utils_1.checkedDecimalMul)(amountIn.sub(feeIn), new anchor_1.BN(-1 * inputTokenCustodyAccount.decimals), swapPrice, inputMinMaxPrice.min.exponent, new anchor_1.BN(-1 * outputTokenCustodyAccount.decimals)).sub(feeOut);
                return {
                    minAmountIn: constants_1.BN_ZERO,
                    minAmountOut: swapAmount,
                    feeIn: feeIn,
                    feeOut: feeOut,
                };
            }
        };
        this.getAssetsUnderManagementUsdSync = function (poolAccount, tokenPrices, tokenEmaPrices, custodies, markets, aumCalcMode, currentTime, poolConfig) {
            var poolAmountUsd = constants_1.BN_ZERO;
            for (var index = 0; index < custodies.length; index++) {
                if (custodies.length != poolAccount.custodies.length || !custodies[index].publicKey.equals(poolAccount.custodies[index])) {
                    throw Error("incorrect custodies");
                }
                if (tokenPrices.length != custodies.length || tokenPrices.length != tokenEmaPrices.length) {
                    throw Error("token prices length incorrect");
                }
                var tokenMinMaxPrice = _this.getMinAndMaxOraclePriceSync(tokenPrices[index], tokenEmaPrices[index], custodies[index]);
                var token_amount_usd = tokenMinMaxPrice.max.getAssetAmountUsd(custodies[index].assets.owned, custodies[index].decimals);
                poolAmountUsd = poolAmountUsd.add(token_amount_usd);
            }
            if (aumCalcMode === "includePnl") {
                var poolEquityUsd = poolAmountUsd;
                for (var index = 0; index < markets.length; index++) {
                    if (markets.length != poolAccount.markets.length || !markets[index].publicKey.equals(poolAccount.markets[index])) {
                        throw Error("incorrect markets");
                    }
                    var targetCustodyId = poolAccount.getCustodyId(markets[index].targetCustody);
                    var collateralCustodyId = poolAccount.getCustodyId(markets[index].collateralCustody);
                    var position = markets[index].getCollectivePosition();
                    var collectivePnl = _this.getPnlSync(position, tokenPrices[targetCustodyId], tokenEmaPrices[targetCustodyId], custodies[targetCustodyId], tokenPrices[collateralCustodyId], tokenEmaPrices[collateralCustodyId], custodies[collateralCustodyId], currentTime, custodies[targetCustodyId].pricing.delaySeconds, poolConfig);
                    var collateralMinMaxPrice = _this.getMinAndMaxOraclePriceSync(tokenPrices[collateralCustodyId], tokenEmaPrices[collateralCustodyId], custodies[collateralCustodyId]);
                    var collectiveCollateralUsd = collateralMinMaxPrice.min.getAssetAmountUsd(position.collateralAmount, position.collateralDecimals);
                    var collectiveLossUsd = anchor_1.BN.min(collectivePnl.lossUsd, collectiveCollateralUsd);
                    poolEquityUsd = (poolEquityUsd.add(collectiveLossUsd)).sub(collectivePnl.profitUsd);
                }
                return { poolAmountUsd: poolAmountUsd, poolEquityUsd: poolEquityUsd };
            }
            else {
                return { poolAmountUsd: poolAmountUsd, poolEquityUsd: constants_1.BN_ZERO };
            }
        };
        this.getNftFinalDiscount = function (perpetualsAccount, nftTradingAccount, currentTime) {
            if (currentTime.sub(nftTradingAccount.timestamp).lt(constants_1.DAY_SECONDS) && nftTradingAccount.counter.gt(new anchor_1.BN(perpetualsAccount.tradeLimit))) {
                return { discountBn: constants_1.BN_ZERO };
            }
            else {
                return { discountBn: perpetualsAccount.tradingDiscount[nftTradingAccount.level - 1] };
            }
        };
        this.getFeeDiscount = function (perpetualsAccount, tokenStakeAccount, currentTime) {
            if (tokenStakeAccount.level === 0) {
                return { discountBn: constants_1.BN_ZERO };
            }
            else if (currentTime.sub(tokenStakeAccount.tradeTimestamp).lt(constants_1.DAY_SECONDS) && (new anchor_1.BN(tokenStakeAccount.tradeCounter)).gt(new anchor_1.BN(perpetualsAccount.tradeLimit))) {
                return { discountBn: constants_1.BN_ZERO };
            }
            else {
                return { discountBn: perpetualsAccount.tradingDiscount[tokenStakeAccount.level - 1] };
            }
        };
        this.getIndexPriceAtParticularTime = function (poolConfig, targetPricesAtT1Ui, targetPricesAtT2Ui, tokenRatiosAtT2BN) {
            var custodyTokens = poolConfig.custodies;
            var finalIndexPriceAtT1 = new bignumber_js_1.default(0);
            if (!(targetPricesAtT1Ui.length === custodyTokens.length && targetPricesAtT2Ui.length === custodyTokens.length)) {
                throw new Error("targetPrices length mismatch custodyTokens.length : ".concat(custodyTokens.length, " ,  targetPricesAtT1.length : ").concat(targetPricesAtT1Ui.length, " , targetPricesAtT2.length : ").concat(targetPricesAtT2Ui.length));
            }
            for (var index = 0; index < custodyTokens.length; index++) {
                var tokenCustody = custodyTokens[index];
                var tokenPriceAtT1 = new bignumber_js_1.default(targetPricesAtT1Ui[index].toString());
                var tokenPriceAtT2 = new bignumber_js_1.default(targetPricesAtT2Ui[index].toString());
                var ratioUi = (0, utils_1.nativeToUiDecimals)(tokenRatiosAtT2BN[index], 4, 4);
                var ratioOfTokenAtT2 = new bignumber_js_1.default(ratioUi);
                finalIndexPriceAtT1 = (tokenPriceAtT1.minus(tokenPriceAtT2).dividedBy(tokenPriceAtT2)).multipliedBy(ratioOfTokenAtT2);
            }
            return finalIndexPriceAtT1.toString();
        };
        this.getUserClaimableRevenueAmount = function (POOL_CONFIG_1, userPublicKey_1) {
            var args_1 = [];
            for (var _i = 2; _i < arguments.length; _i++) {
                args_1[_i - 2] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([POOL_CONFIG_1, userPublicKey_1], args_1, true), void 0, function (POOL_CONFIG, userPublicKey, enableDebuglogs) {
                var fafTokenVaultPk, fafTokenVaultAccountInfo, fafTokenVaultAccount, fafTokenVault, tokenStakeAccount, accountInfo, fafStakeData, tokenStakeFafAccount, activeStakeAmount, revenuePerFafStaked, revenueWatermark, revenueSnapshot, unclaimedRevenue, revenueAmount;
                var _a, _b, _c, _d;
                if (enableDebuglogs === void 0) { enableDebuglogs = false; }
                return __generator(this, function (_e) {
                    switch (_e.label) {
                        case 0:
                            fafTokenVaultPk = POOL_CONFIG.tokenVault;
                            return [4, this.provider.connection.getAccountInfo(fafTokenVaultPk)];
                        case 1:
                            fafTokenVaultAccountInfo = _e.sent();
                            fafTokenVaultAccount = null;
                            if (fafTokenVaultAccountInfo) {
                                fafTokenVault = this.program.coder.accounts.decode('tokenVault', fafTokenVaultAccountInfo.data);
                                fafTokenVaultAccount = TokenVaultAccount_1.TokenVaultAccount.from(fafTokenVaultPk, fafTokenVault);
                            }
                            else {
                                console.log('No account info found for fafTokenVaultPk:', fafTokenVaultPk.toBase58());
                                throw new Error('No account info found for fafTokenVaultPk');
                            }
                            if (!fafTokenVaultAccount) {
                                return [2, constants_1.BN_ZERO];
                            }
                            tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from('token_stake'), userPublicKey.toBuffer()], POOL_CONFIG.programId)[0];
                            return [4, this.provider.connection.getAccountInfo(tokenStakeAccount)];
                        case 2:
                            accountInfo = _e.sent();
                            if (accountInfo) {
                                fafStakeData = this.program.coder.accounts.decode('tokenStake', accountInfo.data);
                                tokenStakeFafAccount = TokenStakeAccount_1.TokenStakeAccount.from(fafStakeData);
                                activeStakeAmount = (_a = tokenStakeFafAccount === null || tokenStakeFafAccount === void 0 ? void 0 : tokenStakeFafAccount.activeStakeAmount) !== null && _a !== void 0 ? _a : constants_1.BN_ZERO;
                                revenuePerFafStaked = (_b = fafTokenVaultAccount === null || fafTokenVaultAccount === void 0 ? void 0 : fafTokenVaultAccount.revenuePerFafStaked) !== null && _b !== void 0 ? _b : constants_1.BN_ZERO;
                                revenueWatermark = activeStakeAmount
                                    .mul(revenuePerFafStaked)
                                    .div(new anchor_1.BN(10).pow(new anchor_1.BN(constants_1.FAF_DECIMALS)));
                                revenueSnapshot = (_c = tokenStakeFafAccount === null || tokenStakeFafAccount === void 0 ? void 0 : tokenStakeFafAccount.revenueSnapshot) !== null && _c !== void 0 ? _c : constants_1.BN_ZERO;
                                unclaimedRevenue = (_d = tokenStakeFafAccount === null || tokenStakeFafAccount === void 0 ? void 0 : tokenStakeFafAccount.unclaimedRevenueAmount) !== null && _d !== void 0 ? _d : constants_1.BN_ZERO;
                                revenueAmount = revenueWatermark.sub(revenueSnapshot).add(unclaimedRevenue);
                                if (revenueAmount.lt(constants_1.BN_ZERO)) {
                                    revenueAmount = constants_1.BN_ZERO;
                                }
                                return [2, revenueAmount];
                            }
                            else {
                                return [2, constants_1.BN_ZERO];
                            }
                            return [2];
                    }
                });
            });
        };
        this.getStakedLpTokenPrice = function (poolKey, POOL_CONFIG) { return __awaiter(_this, void 0, void 0, function () {
            var backUpOracleInstructionPromise, custodies, custodyMetas, marketMetas, _i, custodies_1, token, _a, custodies_2, custody, _b, _c, market, transaction, backUpOracleInstruction, result, index, res;
            var _d;
            return __generator(this, function (_e) {
                switch (_e.label) {
                    case 0:
                        backUpOracleInstructionPromise = (0, backupOracle_1.createBackupOracleInstruction)(POOL_CONFIG.poolAddress.toBase58(), true);
                        custodies = POOL_CONFIG.custodies;
                        custodyMetas = [];
                        marketMetas = [];
                        for (_i = 0, custodies_1 = custodies; _i < custodies_1.length; _i++) {
                            token = custodies_1[_i];
                            custodyMetas.push({
                                isSigner: false,
                                isWritable: false,
                                pubkey: token.custodyAccount,
                            });
                        }
                        for (_a = 0, custodies_2 = custodies; _a < custodies_2.length; _a++) {
                            custody = custodies_2[_a];
                            custodyMetas.push({
                                isSigner: false,
                                isWritable: false,
                                pubkey: custody.intOracleAccount,
                            });
                        }
                        for (_b = 0, _c = POOL_CONFIG.markets; _b < _c.length; _b++) {
                            market = _c[_b];
                            marketMetas.push({
                                pubkey: market.marketAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        return [4, this.program.methods
                                .getLpTokenPrice({})
                                .accounts({
                                perpetuals: POOL_CONFIG.perpetuals,
                                pool: poolKey,
                                lpTokenMint: POOL_CONFIG.stakedLpTokenMint,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                            })
                                .remainingAccounts(__spreadArray(__spreadArray([], custodyMetas, true), marketMetas, true))
                                .transaction()];
                    case 1:
                        transaction = _e.sent();
                        return [4, backUpOracleInstructionPromise];
                    case 2:
                        backUpOracleInstruction = _e.sent();
                        (_d = transaction.instructions).unshift.apply(_d, backUpOracleInstruction);
                        return [4, this.viewHelper.simulateTransaction(transaction)];
                    case 3:
                        result = _e.sent();
                        index = perpetuals_1.IDL.instructions.findIndex(function (f) { return f.name === 'getLpTokenPrice'; });
                        res = this.viewHelper.decodeLogs(result, index, 'getLpTokenPrice');
                        return [2, res.toString()];
                }
            });
        }); };
        this.getAssetsUnderManagement = function (poolKey, POOL_CONFIG) { return __awaiter(_this, void 0, void 0, function () {
            var backUpOracleInstructionPromise, custodies, custodyMetas, marketMetas, _i, custodies_3, token, _a, custodies_4, custody, _b, _c, market;
            return __generator(this, function (_d) {
                switch (_d.label) {
                    case 0:
                        backUpOracleInstructionPromise = (0, backupOracle_1.createBackupOracleInstruction)(POOL_CONFIG.poolAddress.toBase58(), true);
                        custodies = POOL_CONFIG.custodies;
                        custodyMetas = [];
                        marketMetas = [];
                        for (_i = 0, custodies_3 = custodies; _i < custodies_3.length; _i++) {
                            token = custodies_3[_i];
                            custodyMetas.push({
                                isSigner: false,
                                isWritable: false,
                                pubkey: token.custodyAccount,
                            });
                        }
                        for (_a = 0, custodies_4 = custodies; _a < custodies_4.length; _a++) {
                            custody = custodies_4[_a];
                            custodyMetas.push({
                                isSigner: false,
                                isWritable: false,
                                pubkey: custody.intOracleAccount,
                            });
                        }
                        for (_b = 0, _c = POOL_CONFIG.markets; _b < _c.length; _b++) {
                            market = _c[_b];
                            marketMetas.push({
                                pubkey: market.marketAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        return [4, this.program.methods
                                .getAssetsUnderManagement({})
                                .accounts({
                                perpetuals: POOL_CONFIG.perpetuals,
                                pool: poolKey,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                            })
                                .remainingAccounts(__spreadArray(__spreadArray([], custodyMetas, true), marketMetas, true))
                                .view()
                                .catch(function (err) {
                                console.error(err);
                                throw err;
                            })];
                    case 1: return [2, _d.sent()];
                }
            });
        }); };
        this.getAddLiquidityAmountAndFeeView = function (amount_1, poolKey_1, depositCustodyKey_1, POOL_CONFIG_1) {
            var args_1 = [];
            for (var _i = 4; _i < arguments.length; _i++) {
                args_1[_i - 4] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([amount_1, poolKey_1, depositCustodyKey_1, POOL_CONFIG_1], args_1, true), void 0, function (amount, poolKey, depositCustodyKey, POOL_CONFIG, userPublicKey) {
                var custodies, custodyMetas, marketMetas, _a, custodies_5, token, _b, custodies_6, custody, _c, _d, market, depositCustodyConfig, transaction, result, index, res;
                if (userPublicKey === void 0) { userPublicKey = undefined; }
                return __generator(this, function (_e) {
                    switch (_e.label) {
                        case 0:
                            custodies = POOL_CONFIG.custodies;
                            custodyMetas = [];
                            marketMetas = [];
                            for (_a = 0, custodies_5 = custodies; _a < custodies_5.length; _a++) {
                                token = custodies_5[_a];
                                custodyMetas.push({
                                    isSigner: false,
                                    isWritable: false,
                                    pubkey: token.custodyAccount,
                                });
                            }
                            for (_b = 0, custodies_6 = custodies; _b < custodies_6.length; _b++) {
                                custody = custodies_6[_b];
                                custodyMetas.push({
                                    isSigner: false,
                                    isWritable: false,
                                    pubkey: custody.intOracleAccount,
                                });
                            }
                            for (_c = 0, _d = POOL_CONFIG.markets; _c < _d.length; _c++) {
                                market = _d[_c];
                                marketMetas.push({
                                    pubkey: market.marketAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            depositCustodyConfig = custodies.find(function (i) { return i.custodyAccount.equals(depositCustodyKey); });
                            return [4, this.program.methods
                                    .getAddLiquidityAmountAndFee({
                                    amountIn: amount,
                                })
                                    .accounts({
                                    perpetuals: POOL_CONFIG.perpetuals,
                                    pool: poolKey,
                                    custody: depositCustodyKey,
                                    custodyOracleAccount: depositCustodyConfig.intOracleAccount,
                                    lpTokenMint: POOL_CONFIG.stakedLpTokenMint,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                })
                                    .remainingAccounts(__spreadArray(__spreadArray([], custodyMetas, true), marketMetas, true))
                                    .transaction()];
                        case 1:
                            transaction = _e.sent();
                            return [4, this.viewHelper.simulateTransaction(transaction, userPublicKey)];
                        case 2:
                            result = _e.sent();
                            index = perpetuals_1.IDL.instructions.findIndex(function (f) { return f.name === 'getAddLiquidityAmountAndFee'; });
                            res = this.viewHelper.decodeLogs(result, index, 'getAddLiquidityAmountAndFee');
                            return [2, {
                                    amount: res.amount,
                                    fee: res.fee,
                                }];
                    }
                });
            });
        };
        this.getRemoveLiquidityAmountAndFeeView = function (amount_1, poolKey_1, removeTokenCustodyKey_1, POOL_CONFIG_1) {
            var args_1 = [];
            for (var _i = 4; _i < arguments.length; _i++) {
                args_1[_i - 4] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([amount_1, poolKey_1, removeTokenCustodyKey_1, POOL_CONFIG_1], args_1, true), void 0, function (amount, poolKey, removeTokenCustodyKey, POOL_CONFIG, userPublicKey) {
                var custodies, custodyMetas, marketMetas, _a, custodies_7, token, _b, custodies_8, custody, _c, _d, market, removeCustodyConfig, transaction, result, index, res;
                if (userPublicKey === void 0) { userPublicKey = undefined; }
                return __generator(this, function (_e) {
                    switch (_e.label) {
                        case 0:
                            custodies = POOL_CONFIG.custodies;
                            custodyMetas = [];
                            marketMetas = [];
                            for (_a = 0, custodies_7 = custodies; _a < custodies_7.length; _a++) {
                                token = custodies_7[_a];
                                custodyMetas.push({
                                    isSigner: false,
                                    isWritable: false,
                                    pubkey: token.custodyAccount,
                                });
                            }
                            for (_b = 0, custodies_8 = custodies; _b < custodies_8.length; _b++) {
                                custody = custodies_8[_b];
                                custodyMetas.push({
                                    isSigner: false,
                                    isWritable: false,
                                    pubkey: custody.intOracleAccount,
                                });
                            }
                            for (_c = 0, _d = POOL_CONFIG.markets; _c < _d.length; _c++) {
                                market = _d[_c];
                                marketMetas.push({
                                    pubkey: market.marketAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            removeCustodyConfig = custodies.find(function (i) { return i.custodyAccount.equals(removeTokenCustodyKey); });
                            return [4, this.program.methods
                                    .getRemoveLiquidityAmountAndFee({
                                    lpAmountIn: amount,
                                })
                                    .accounts({
                                    perpetuals: POOL_CONFIG.perpetuals,
                                    pool: poolKey,
                                    custody: removeTokenCustodyKey,
                                    custodyOracleAccount: removeCustodyConfig.intOracleAccount,
                                    lpTokenMint: POOL_CONFIG.stakedLpTokenMint,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                })
                                    .remainingAccounts(__spreadArray(__spreadArray([], custodyMetas, true), marketMetas, true))
                                    .transaction()];
                        case 1:
                            transaction = _e.sent();
                            return [4, this.viewHelper.simulateTransaction(transaction, userPublicKey)];
                        case 2:
                            result = _e.sent();
                            index = perpetuals_1.IDL.instructions.findIndex(function (f) { return f.name === 'getRemoveLiquidityAmountAndFee'; });
                            if (result.value.err) {
                                return [2, {
                                        amount: new anchor_1.BN(0),
                                        fee: new anchor_1.BN(0),
                                    }];
                            }
                            res = this.viewHelper.decodeLogs(result, index, 'getRemoveLiquidityAmountAndFee');
                            return [2, {
                                    amount: res.amount,
                                    fee: res.fee,
                                }];
                    }
                });
            });
        };
        this.getCompoundingLPTokenPrice = function (poolKey, POOL_CONFIG) { return __awaiter(_this, void 0, void 0, function () {
            var backUpOracleInstructionPromise, custodies, custodyMetas, marketMetas, _i, custodies_9, token, _a, custodies_10, custody, _b, _c, market, backUpOracleInstruction, transaction, result, index, res;
            var _d;
            return __generator(this, function (_e) {
                switch (_e.label) {
                    case 0:
                        backUpOracleInstructionPromise = (0, backupOracle_1.createBackupOracleInstruction)(POOL_CONFIG.poolAddress.toBase58(), true);
                        custodies = POOL_CONFIG.custodies;
                        custodyMetas = [];
                        marketMetas = [];
                        for (_i = 0, custodies_9 = custodies; _i < custodies_9.length; _i++) {
                            token = custodies_9[_i];
                            custodyMetas.push({
                                isSigner: false,
                                isWritable: false,
                                pubkey: token.custodyAccount,
                            });
                        }
                        for (_a = 0, custodies_10 = custodies; _a < custodies_10.length; _a++) {
                            custody = custodies_10[_a];
                            custodyMetas.push({
                                isSigner: false,
                                isWritable: false,
                                pubkey: custody.intOracleAccount,
                            });
                        }
                        for (_b = 0, _c = POOL_CONFIG.markets; _b < _c.length; _b++) {
                            market = _c[_b];
                            marketMetas.push({
                                pubkey: market.marketAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        return [4, backUpOracleInstructionPromise];
                    case 1:
                        backUpOracleInstruction = _e.sent();
                        return [4, this.program.methods
                                .getCompoundingTokenPrice({})
                                .accounts({
                                perpetuals: POOL_CONFIG.perpetuals,
                                pool: poolKey,
                                lpTokenMint: POOL_CONFIG.stakedLpTokenMint,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                            })
                                .remainingAccounts(__spreadArray(__spreadArray([], custodyMetas, true), marketMetas, true))
                                .transaction()];
                    case 2:
                        transaction = _e.sent();
                        (_d = transaction.instructions).unshift.apply(_d, backUpOracleInstruction);
                        return [4, this.viewHelper.simulateTransaction(transaction)];
                    case 3:
                        result = _e.sent();
                        index = perpetuals_1.IDL.instructions.findIndex(function (f) { return f.name === 'getCompoundingTokenPrice'; });
                        res = this.viewHelper.decodeLogs(result, index, 'getCompoundingTokenPrice');
                        return [2, res.toString()];
                }
            });
        }); };
        this.getAddCompoundingLiquidityAmountAndFeeView = function (amount_1, poolKey_1, depositCustodyKey_1, POOL_CONFIG_1) {
            var args_1 = [];
            for (var _i = 4; _i < arguments.length; _i++) {
                args_1[_i - 4] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([amount_1, poolKey_1, depositCustodyKey_1, POOL_CONFIG_1], args_1, true), void 0, function (amount, poolKey, depositCustodyKey, POOL_CONFIG, userPublicKey) {
                var custodies, custodyMetas, marketMetas, _a, custodies_11, token, _b, custodies_12, custody, _c, _d, market, depositCustodyConfig, rewardCustody, transaction, result, index, res;
                if (userPublicKey === void 0) { userPublicKey = undefined; }
                return __generator(this, function (_e) {
                    switch (_e.label) {
                        case 0:
                            custodies = POOL_CONFIG.custodies;
                            custodyMetas = [];
                            marketMetas = [];
                            for (_a = 0, custodies_11 = custodies; _a < custodies_11.length; _a++) {
                                token = custodies_11[_a];
                                custodyMetas.push({
                                    isSigner: false,
                                    isWritable: false,
                                    pubkey: token.custodyAccount,
                                });
                            }
                            for (_b = 0, custodies_12 = custodies; _b < custodies_12.length; _b++) {
                                custody = custodies_12[_b];
                                custodyMetas.push({
                                    isSigner: false,
                                    isWritable: false,
                                    pubkey: custody.intOracleAccount,
                                });
                            }
                            for (_c = 0, _d = POOL_CONFIG.markets; _c < _d.length; _c++) {
                                market = _d[_c];
                                marketMetas.push({
                                    pubkey: market.marketAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            depositCustodyConfig = custodies.find(function (i) { return i.custodyAccount.equals(depositCustodyKey); });
                            rewardCustody = POOL_CONFIG.custodies.find(function (f) { return f.symbol == 'USDC'; });
                            return [4, this.program.methods
                                    .getAddCompoundingLiquidityAmountAndFee({
                                    amountIn: amount,
                                })
                                    .accounts({
                                    perpetuals: POOL_CONFIG.perpetuals,
                                    pool: poolKey,
                                    inCustody: depositCustodyKey,
                                    inCustodyOracleAccount: depositCustodyConfig.intOracleAccount,
                                    rewardCustody: rewardCustody.custodyAccount,
                                    rewardCustodyOracleAccount: rewardCustody.intOracleAccount,
                                    lpTokenMint: POOL_CONFIG.stakedLpTokenMint,
                                    compoundingTokenMint: POOL_CONFIG.compoundingTokenMint,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                })
                                    .remainingAccounts(__spreadArray(__spreadArray([], custodyMetas, true), marketMetas, true))
                                    .transaction()];
                        case 1:
                            transaction = _e.sent();
                            return [4, this.viewHelper.simulateTransaction(transaction, userPublicKey)];
                        case 2:
                            result = _e.sent();
                            index = perpetuals_1.IDL.instructions.findIndex(function (f) { return f.name === 'getAddCompoundingLiquidityAmountAndFee'; });
                            res = this.viewHelper.decodeLogs(result, index, 'getAddCompoundingLiquidityAmountAndFee');
                            return [2, {
                                    amount: res.amount,
                                    fee: res.fee,
                                }];
                    }
                });
            });
        };
        this.getRemoveCompoundingLiquidityAmountAndFeeView = function (amount_1, poolKey_1, removeTokenCustodyKey_1, POOL_CONFIG_1) {
            var args_1 = [];
            for (var _i = 4; _i < arguments.length; _i++) {
                args_1[_i - 4] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([amount_1, poolKey_1, removeTokenCustodyKey_1, POOL_CONFIG_1], args_1, true), void 0, function (amount, poolKey, removeTokenCustodyKey, POOL_CONFIG, userPublicKey) {
                var custodies, custodyMetas, marketMetas, _a, custodies_13, token, _b, custodies_14, custody, _c, _d, market, removeCustodyConfig, rewardCustody, transaction, result, index, res;
                if (userPublicKey === void 0) { userPublicKey = undefined; }
                return __generator(this, function (_e) {
                    switch (_e.label) {
                        case 0:
                            custodies = POOL_CONFIG.custodies;
                            custodyMetas = [];
                            marketMetas = [];
                            for (_a = 0, custodies_13 = custodies; _a < custodies_13.length; _a++) {
                                token = custodies_13[_a];
                                custodyMetas.push({
                                    isSigner: false,
                                    isWritable: false,
                                    pubkey: token.custodyAccount,
                                });
                            }
                            for (_b = 0, custodies_14 = custodies; _b < custodies_14.length; _b++) {
                                custody = custodies_14[_b];
                                custodyMetas.push({
                                    isSigner: false,
                                    isWritable: false,
                                    pubkey: custody.intOracleAccount,
                                });
                            }
                            for (_c = 0, _d = POOL_CONFIG.markets; _c < _d.length; _c++) {
                                market = _d[_c];
                                marketMetas.push({
                                    pubkey: market.marketAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            removeCustodyConfig = custodies.find(function (i) { return i.custodyAccount.equals(removeTokenCustodyKey); });
                            rewardCustody = POOL_CONFIG.custodies.find(function (f) { return f.symbol == 'USDC'; });
                            return [4, this.program.methods
                                    .getRemoveCompoundingLiquidityAmountAndFee({
                                    compoundingAmountIn: amount,
                                })
                                    .accounts({
                                    perpetuals: POOL_CONFIG.perpetuals,
                                    pool: poolKey,
                                    outCustody: removeTokenCustodyKey,
                                    outCustodyOracleAccount: removeCustodyConfig.intOracleAccount,
                                    rewardCustody: rewardCustody.custodyAccount,
                                    rewardCustodyOracleAccount: rewardCustody.intOracleAccount,
                                    compoundingTokenMint: POOL_CONFIG.compoundingTokenMint,
                                    lpTokenMint: POOL_CONFIG.stakedLpTokenMint,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                })
                                    .remainingAccounts(__spreadArray(__spreadArray([], custodyMetas, true), marketMetas, true))
                                    .transaction()];
                        case 1:
                            transaction = _e.sent();
                            return [4, this.viewHelper.simulateTransaction(transaction, userPublicKey)];
                        case 2:
                            result = _e.sent();
                            index = perpetuals_1.IDL.instructions.findIndex(function (f) { return f.name === 'getRemoveCompoundingLiquidityAmountAndFee'; });
                            if (result.value.err) {
                                return [2, {
                                        amount: new anchor_1.BN(0),
                                        fee: new anchor_1.BN(0),
                                    }];
                            }
                            res = this.viewHelper.decodeLogs(result, index, 'getRemoveCompoundingLiquidityAmountAndFee');
                            return [2, {
                                    amount: res.amount,
                                    fee: res.fee,
                                }];
                    }
                });
            });
        };
        this.getLiquidationPriceView = function (positionAccountKey, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var positionAccount_1, marketConfig_1, targetCustodyConfig, collateralCustodyConfig, err_2;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        _a.trys.push([0, 3, , 4]);
                        return [4, this.getPosition(positionAccountKey)];
                    case 1:
                        positionAccount_1 = _a.sent();
                        marketConfig_1 = poolConfig.markets.find(function (m) { return m.marketAccount.equals(positionAccount_1.market); });
                        if (!marketConfig_1) {
                            throw new Error("Market config not found for position account: ".concat(positionAccountKey.toBase58()));
                        }
                        targetCustodyConfig = poolConfig.custodies.find(function (f) { return f.custodyAccount.equals(marketConfig_1.targetCustody); });
                        collateralCustodyConfig = poolConfig.custodies.find(function (f) { return f.custodyAccount.equals(marketConfig_1.collateralCustody); });
                        return [4, this.program.methods
                                .getLiquidationPrice({})
                                .accounts({
                                perpetuals: this.perpetuals.publicKey,
                                pool: poolConfig.poolAddress,
                                position: positionAccountKey,
                                targetCustody: targetCustodyConfig.custodyAccount,
                                targetOracleAccount: targetCustodyConfig.intOracleAccount,
                                collateralCustody: collateralCustodyConfig.custodyAccount,
                                collateralOracleAccount: collateralCustodyConfig.intOracleAccount,
                                market: marketConfig_1.marketAccount,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                            })
                                .view()
                                .catch(function (err) {
                                console.error(err);
                                throw err;
                            })];
                    case 2: return [2, _a.sent()];
                    case 3:
                        err_2 = _a.sent();
                        console.error("Error in getLiquidationPriceView:", err_2);
                        throw err_2;
                    case 4: return [2];
                }
            });
        }); };
        this.getLiquidationStateView = function (positionAccount, poolName, tokenMint, collateralMint, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var targetCustodyConfig, collateralCustodyConfig;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        targetCustodyConfig = poolConfig.custodies.find(function (f) { return f.mintKey.equals(tokenMint); });
                        collateralCustodyConfig = poolConfig.custodies.find(function (f) { return f.mintKey.equals(collateralMint); });
                        return [4, this.program.methods
                                .getLiquidationState({})
                                .accounts({
                                perpetuals: this.perpetuals.publicKey,
                                pool: poolConfig.poolAddress,
                                position: positionAccount,
                                targetCustody: this.getCustodyKey(poolName, tokenMint),
                                targetOracleAccount: targetCustodyConfig.custodyAccount,
                                collateralCustody: this.getCustodyKey(poolName, collateralMint),
                                collateralOracleAccount: collateralCustodyConfig.custodyAccount,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                            })
                                .view()
                                .catch(function (err) {
                                console.error(err);
                                throw err;
                            })];
                    case 1: return [2, _a.sent()];
                }
            });
        }); };
        this.getCompoundingTokenDataView = function (poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var custodyAccountMetas, custodyOracleAccountMetas, markets, _i, _a, custody, _b, _c, market;
            return __generator(this, function (_d) {
                switch (_d.label) {
                    case 0:
                        custodyAccountMetas = [];
                        custodyOracleAccountMetas = [];
                        markets = [];
                        for (_i = 0, _a = poolConfig.custodies; _i < _a.length; _i++) {
                            custody = _a[_i];
                            custodyAccountMetas.push({
                                pubkey: custody.custodyAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                            custodyOracleAccountMetas.push({
                                pubkey: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        for (_b = 0, _c = poolConfig.markets; _b < _c.length; _b++) {
                            market = _c[_b];
                            markets.push({
                                pubkey: market.marketAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        return [4, this.program.methods
                                .getCompoundingTokenData({})
                                .accounts({
                                perpetuals: this.perpetuals.publicKey,
                                pool: poolConfig.poolAddress,
                                lpTokenMint: poolConfig.stakedLpTokenMint,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                            })
                                .remainingAccounts(__spreadArray(__spreadArray(__spreadArray([], custodyAccountMetas, true), custodyOracleAccountMetas, true), markets, true))
                                .view()
                                .catch(function (err) {
                                console.error(err);
                                throw err;
                            })];
                    case 1: return [2, _d.sent()];
                }
            });
        }); };
        this.getLpTokenPriceView = function (poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var custodyAccountMetas, custodyOracleAccountMetas, markets, _i, _a, custody, _b, _c, market;
            return __generator(this, function (_d) {
                switch (_d.label) {
                    case 0:
                        custodyAccountMetas = [];
                        custodyOracleAccountMetas = [];
                        markets = [];
                        for (_i = 0, _a = poolConfig.custodies; _i < _a.length; _i++) {
                            custody = _a[_i];
                            custodyAccountMetas.push({
                                pubkey: custody.custodyAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                            custodyOracleAccountMetas.push({
                                pubkey: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        for (_b = 0, _c = poolConfig.markets; _b < _c.length; _b++) {
                            market = _c[_b];
                            markets.push({
                                pubkey: market.marketAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        return [4, this.program.methods
                                .getLpTokenPrice({})
                                .accounts({
                                perpetuals: this.perpetuals.publicKey,
                                pool: poolConfig.poolAddress,
                                lpTokenMint: poolConfig.stakedLpTokenMint,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                            })
                                .remainingAccounts(__spreadArray(__spreadArray(__spreadArray([], custodyAccountMetas, true), custodyOracleAccountMetas, true), markets, true))
                                .view()
                                .catch(function (err) {
                                console.error(err);
                                throw err;
                            })];
                    case 1: return [2, _d.sent()];
                }
            });
        }); };
        this.openPosition = function (targetSymbol_1, collateralSymbol_1, priceWithSlippage_1, collateralWithfee_1, size_1, side_1, poolConfig_1, privilege_1) {
            var args_1 = [];
            for (var _i = 8; _i < arguments.length; _i++) {
                args_1[_i - 8] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([targetSymbol_1, collateralSymbol_1, priceWithSlippage_1, collateralWithfee_1, size_1, side_1, poolConfig_1, privilege_1], args_1, true), void 0, function (targetSymbol, collateralSymbol, priceWithSlippage, collateralWithfee, size, side, poolConfig, privilege, tokenStakeAccount, userReferralAccount, rebateTokenAccount, skipBalanceChecks, ephemeralSignerPubkey) {
                var publicKey, targetCustodyConfig, collateralCustodyConfig, collateralToken, marketAccount, userCollateralTokenAccount, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, lamports, unWrappedSolBalance, _a, tokenAccountBalance, _b, positionAccount, params, instruction;
                if (tokenStakeAccount === void 0) { tokenStakeAccount = web3_js_1.PublicKey.default; }
                if (userReferralAccount === void 0) { userReferralAccount = web3_js_1.PublicKey.default; }
                if (rebateTokenAccount === void 0) { rebateTokenAccount = web3_js_1.PublicKey.default; }
                if (skipBalanceChecks === void 0) { skipBalanceChecks = false; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                return __generator(this, function (_c) {
                    switch (_c.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                            collateralToken = poolConfig.getTokenFromSymbol(collateralSymbol);
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            userCollateralTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey, publicKey, true, collateralToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            if (!(collateralSymbol == 'SOL')) return [3, 3];
                            console.log("collateralSymbol === SOL", collateralSymbol);
                            lamports = collateralWithfee.add(new anchor_1.BN(this.minimumBalanceForRentExemptAccountLamports));
                            if (!!skipBalanceChecks) return [3, 2];
                            _a = anchor_1.BN.bind;
                            return [4, this.provider.connection.getBalance(publicKey)];
                        case 1:
                            unWrappedSolBalance = new (_a.apply(anchor_1.BN, [void 0, _c.sent()]))();
                            if (unWrappedSolBalance.lt(lamports)) {
                                throw "Insufficient SOL Funds";
                            }
                            _c.label = 2;
                        case 2:
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports.toNumber(),
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 6];
                        case 3:
                            if (!!skipBalanceChecks) return [3, 6];
                            return [4, (0, utils_1.checkIfAccountExists)(userCollateralTokenAccount, this.provider.connection)];
                        case 4:
                            if (!(_c.sent())) {
                                throw "Insufficient Funds , token Account doesn't exist";
                            }
                            _b = anchor_1.BN.bind;
                            return [4, this.provider.connection.getTokenAccountBalance(userCollateralTokenAccount)];
                        case 5:
                            tokenAccountBalance = new (_b.apply(anchor_1.BN, [void 0, (_c.sent()).value.amount]))();
                            if (tokenAccountBalance.lt(collateralWithfee)) {
                                throw "Insufficient Funds need more ".concat(collateralWithfee.sub(tokenAccountBalance), " tokens");
                            }
                            _c.label = 6;
                        case 6:
                            positionAccount = poolConfig.getPositionFromMarketPk(publicKey, marketAccount);
                            params = {
                                priceWithSlippage: priceWithSlippage,
                                collateralAmount: collateralWithfee,
                                sizeAmount: size,
                                privilege: privilege
                            };
                            return [4, this.program.methods
                                    .openPosition(params)
                                    .accounts({
                                    owner: publicKey,
                                    feePayer: publicKey,
                                    fundingAccount: collateralSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userCollateralTokenAccount,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    position: positionAccount,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    systemProgram: web3_js_1.SystemProgram.programId,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    transferAuthority: this.authority.publicKey,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    fundingMint: collateralCustodyConfig.mintKey
                                })
                                    .remainingAccounts(__spreadArray([], (0, getReferralAccounts_1.getReferralAccounts)(tokenStakeAccount, userReferralAccount, rebateTokenAccount, privilege), true))
                                    .instruction()];
                        case 7:
                            instruction = _c.sent();
                            instructions.push(instruction);
                            return [2, {
                                    instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                    additionalSigners: additionalSigners
                                }];
                    }
                });
            });
        };
        this.closePosition = function (marketSymbol_1, collateralSymbol_1, priceWithSlippage_1, side_1, poolConfig_1, privilege_1) {
            var args_1 = [];
            for (var _i = 6; _i < arguments.length; _i++) {
                args_1[_i - 6] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([marketSymbol_1, collateralSymbol_1, priceWithSlippage_1, side_1, poolConfig_1, privilege_1], args_1, true), void 0, function (marketSymbol, collateralSymbol, priceWithSlippage, side, poolConfig, privilege, tokenStakeAccount, userReferralAccount, rebateTokenAccount, createUserATA, closeUsersWSOLATA, ephemeralSignerPubkey) {
                var publicKey, userReceivingTokenAccount, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, lamports, _a, collateralCustodyConfig, targetCustodyConfig, marketAccount, positionAccount, instruction, closeWsolATAIns, error_1;
                if (tokenStakeAccount === void 0) { tokenStakeAccount = web3_js_1.PublicKey.default; }
                if (userReferralAccount === void 0) { userReferralAccount = web3_js_1.PublicKey.default; }
                if (rebateTokenAccount === void 0) { rebateTokenAccount = web3_js_1.PublicKey.default; }
                if (createUserATA === void 0) { createUserATA = true; }
                if (closeUsersWSOLATA === void 0) { closeUsersWSOLATA = false; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            console.log("close position :::", marketSymbol, poolConfig.getTokenFromSymbol(marketSymbol).mintKey.toBase58());
                            publicKey = this.provider.wallet.publicKey;
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _b.label = 1;
                        case 1:
                            _b.trys.push([1, 7, , 8]);
                            if (!(collateralSymbol == 'SOL')) return [3, 2];
                            lamports = (this.minimumBalanceForRentExemptAccountLamports);
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports,
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 5];
                        case 2:
                            userReceivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey, publicKey, true, poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            _a = createUserATA;
                            if (!_a) return [3, 4];
                            return [4, (0, utils_1.checkIfAccountExists)(userReceivingTokenAccount, this.provider.connection)];
                        case 3:
                            _a = !(_b.sent());
                            _b.label = 4;
                        case 4:
                            if (_a) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userReceivingTokenAccount, publicKey, poolConfig.getTokenFromSymbol(collateralSymbol).mintKey, poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            _b.label = 5;
                        case 5:
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(marketSymbol).mintKey); });
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            positionAccount = poolConfig.getPositionFromMarketPk(publicKey, marketAccount);
                            return [4, this.program.methods
                                    .closePosition({
                                    priceWithSlippage: priceWithSlippage,
                                    privilege: privilege
                                })
                                    .accounts({
                                    feePayer: publicKey,
                                    owner: publicKey,
                                    receivingAccount: collateralSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userReceivingTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    position: positionAccount,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    collateralMint: collateralCustodyConfig.mintKey,
                                    collateralTokenProgram: poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID
                                })
                                    .remainingAccounts(__spreadArray([], (0, getReferralAccounts_1.getReferralAccounts)(tokenStakeAccount, userReferralAccount, rebateTokenAccount, privilege), true))
                                    .instruction()];
                        case 6:
                            instruction = _b.sent();
                            instructions.push(instruction);
                            if (collateralSymbol == 'WSOL' && closeUsersWSOLATA) {
                                closeWsolATAIns = (0, spl_token_1.createCloseAccountInstruction)(userReceivingTokenAccount, publicKey, publicKey);
                                postInstructions.push(closeWsolATAIns);
                            }
                            return [3, 8];
                        case 7:
                            error_1 = _b.sent();
                            console.error("perpclient closePosition error:", error_1);
                            throw error_1;
                        case 8: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.swapAndOpen = function (targetTokenSymbol_1, collateralTokenSymbol_1, userInputTokenSymbol_1, amountIn_1, minCollateralAmountOut_1, priceWithSlippage_1, sizeAmount_1, side_1, poolConfig_1, privilege_1) {
            var args_1 = [];
            for (var _i = 10; _i < arguments.length; _i++) {
                args_1[_i - 10] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([targetTokenSymbol_1, collateralTokenSymbol_1, userInputTokenSymbol_1, amountIn_1, minCollateralAmountOut_1, priceWithSlippage_1, sizeAmount_1, side_1, poolConfig_1, privilege_1], args_1, true), void 0, function (targetTokenSymbol, collateralTokenSymbol, userInputTokenSymbol, amountIn, minCollateralAmountOut, priceWithSlippage, sizeAmount, side, poolConfig, privilege, tokenStakeAccount, userReferralAccount, rebateTokenAccount, skipBalanceChecks, ephemeralSignerPubkey) {
                var publicKey, userInputCustodyConfig, collateralCustodyConfig, targetCustodyConfig, marketAccount, positionAccount, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, targetToken, userInputTokenAccount, userInputToken, lamports, unWrappedSolBalance, _a, userOutputTokenAccount, tokenAccountBalance, _b, userOutputTokenAccount, rebateMintAccount, inx, err_3;
                if (tokenStakeAccount === void 0) { tokenStakeAccount = web3_js_1.PublicKey.default; }
                if (userReferralAccount === void 0) { userReferralAccount = web3_js_1.PublicKey.default; }
                if (rebateTokenAccount === void 0) { rebateTokenAccount = web3_js_1.PublicKey.default; }
                if (skipBalanceChecks === void 0) { skipBalanceChecks = false; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                return __generator(this, function (_c) {
                    switch (_c.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            userInputCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(userInputTokenSymbol).mintKey); });
                            if (!userInputCustodyConfig) {
                                throw "userInputCustodyConfig not found";
                            }
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralTokenSymbol).mintKey); });
                            if (!collateralCustodyConfig) {
                                throw "collateralCustodyConfig not found";
                            }
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetTokenSymbol).mintKey); });
                            if (!targetCustodyConfig) {
                                throw "targetCustodyConfig not found";
                            }
                            if (userInputCustodyConfig.mintKey.equals(collateralCustodyConfig.mintKey)) {
                                throw "Don't use Swap, just call Open position";
                            }
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            positionAccount = poolConfig.getPositionFromMarketPk(publicKey, marketAccount);
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            targetToken = poolConfig.getTokenFromSymbol(targetCustodyConfig.symbol);
                            userInputToken = poolConfig.getTokenFromSymbol(userInputTokenSymbol);
                            if (!(userInputTokenSymbol == 'SOL')) return [3, 5];
                            console.log("inputSymbol === SOL", userInputTokenSymbol);
                            lamports = amountIn.add(new anchor_1.BN(this.minimumBalanceForRentExemptAccountLamports));
                            if (!!skipBalanceChecks) return [3, 2];
                            _a = anchor_1.BN.bind;
                            return [4, this.provider.connection.getBalance(publicKey)];
                        case 1:
                            unWrappedSolBalance = new (_a.apply(anchor_1.BN, [void 0, _c.sent()]))();
                            if (unWrappedSolBalance.lt(lamports)) {
                                throw "Insufficient SOL Funds";
                            }
                            _c.label = 2;
                        case 2:
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports.toNumber(),
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            if (!!poolConfig.getTokenFromSymbol(targetCustodyConfig.symbol).mintKey.equals(spl_token_1.NATIVE_MINT)) return [3, 4];
                            userOutputTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(targetCustodyConfig.symbol).mintKey, publicKey, true, poolConfig.getTokenFromSymbol(targetCustodyConfig.symbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            return [4, (0, utils_1.checkIfAccountExists)(userOutputTokenAccount, this.provider.connection)];
                        case 3:
                            if (!(_c.sent())) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userOutputTokenAccount, publicKey, poolConfig.getTokenFromSymbol(targetCustodyConfig.symbol).mintKey));
                            }
                            _c.label = 4;
                        case 4: return [3, 10];
                        case 5:
                            userInputTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(userInputTokenSymbol).mintKey, publicKey, true, poolConfig.getTokenFromSymbol(userInputTokenSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            if (!!skipBalanceChecks) return [3, 8];
                            return [4, (0, utils_1.checkIfAccountExists)(userInputTokenAccount, this.provider.connection)];
                        case 6:
                            if (!(_c.sent())) {
                                throw "Insufficient Funds , Token Account doesn't exist";
                            }
                            _b = anchor_1.BN.bind;
                            return [4, this.provider.connection.getTokenAccountBalance(userInputTokenAccount)];
                        case 7:
                            tokenAccountBalance = new (_b.apply(anchor_1.BN, [void 0, (_c.sent()).value.amount]))();
                            if (tokenAccountBalance.lt(amountIn)) {
                                throw "Insufficient Funds need more ".concat(amountIn.sub(tokenAccountBalance), " tokens");
                            }
                            _c.label = 8;
                        case 8:
                            userOutputTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(targetCustodyConfig.symbol).mintKey, publicKey, true, poolConfig.getTokenFromSymbol(targetCustodyConfig.symbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            return [4, (0, utils_1.checkIfAccountExists)(userOutputTokenAccount, this.provider.connection)];
                        case 9:
                            if (!(_c.sent())) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userOutputTokenAccount, publicKey, poolConfig.getTokenFromSymbol(targetCustodyConfig.symbol).mintKey, poolConfig.getTokenFromSymbol(targetCustodyConfig.symbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            _c.label = 10;
                        case 10:
                            rebateMintAccount = {
                                pubkey: collateralCustodyConfig.mintKey,
                                isSigner: false,
                                isWritable: false
                            };
                            _c.label = 11;
                        case 11:
                            _c.trys.push([11, 13, , 14]);
                            return [4, this.program.methods
                                    .swapAndOpen({
                                    amountIn: amountIn,
                                    minCollateralAmountOut: minCollateralAmountOut,
                                    priceWithSlippage: priceWithSlippage,
                                    sizeAmount: sizeAmount,
                                    privilege: privilege
                                })
                                    .accounts({
                                    owner: publicKey,
                                    feePayer: publicKey,
                                    fundingAccount: userInputTokenSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userInputTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    receivingCustody: userInputCustodyConfig.custodyAccount,
                                    receivingCustodyOracleAccount: this.useExtOracleAccount ? userInputCustodyConfig.extOracleAccount : userInputCustodyConfig.intOracleAccount,
                                    receivingCustodyTokenAccount: userInputCustodyConfig.tokenAccount,
                                    position: positionAccount,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    systemProgram: web3_js_1.SystemProgram.programId,
                                    tokenProgram: poolConfig.getTokenFromSymbol(collateralTokenSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    fundingMint: userInputCustodyConfig.mintKey,
                                    fundingTokenProgram: poolConfig.getTokenFromSymbol(userInputTokenSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    collateralMint: collateralCustodyConfig.mintKey,
                                    collateralTokenProgram: poolConfig.getTokenFromSymbol(collateralTokenSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID
                                })
                                    .remainingAccounts(__spreadArray([], (0, getReferralAccounts_1.getReferralAccounts)(tokenStakeAccount, userReferralAccount, rebateTokenAccount, privilege), true))
                                    .instruction()];
                        case 12:
                            inx = _c.sent();
                            instructions.push(inx);
                            return [3, 14];
                        case 13:
                            err_3 = _c.sent();
                            console.error("perpClient SwapAndOpen error:: ", err_3);
                            throw err_3;
                        case 14: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.closeAndSwap = function (targetTokenSymbol_1, userOutputTokenSymbol_1, collateralTokenSymbol_1, minSwapAmountOut_1, priceWithSlippage_1, side_1, poolConfig_1, privilege_1) {
            var args_1 = [];
            for (var _i = 8; _i < arguments.length; _i++) {
                args_1[_i - 8] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([targetTokenSymbol_1, userOutputTokenSymbol_1, collateralTokenSymbol_1, minSwapAmountOut_1, priceWithSlippage_1, side_1, poolConfig_1, privilege_1], args_1, true), void 0, function (targetTokenSymbol, userOutputTokenSymbol, collateralTokenSymbol, minSwapAmountOut, priceWithSlippage, side, poolConfig, privilege, tokenStakeAccount, userReferralAccount, rebateTokenAccount, ephemeralSignerPubkey) {
                var publicKey, userOutputCustodyConfig, collateralCustodyConfig, targetCustodyConfig, marketAccount, positionAccount, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, userReceivingTokenAccount, collateralToken, userOutputToken, lamports, userCollateralTokenAccount, rebateMintAccount, inx, err_4;
                if (tokenStakeAccount === void 0) { tokenStakeAccount = web3_js_1.PublicKey.default; }
                if (userReferralAccount === void 0) { userReferralAccount = web3_js_1.PublicKey.default; }
                if (rebateTokenAccount === void 0) { rebateTokenAccount = web3_js_1.PublicKey.default; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            userOutputCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(userOutputTokenSymbol).mintKey); });
                            if (!userOutputCustodyConfig) {
                                throw "userOutputCustodyConfig not found";
                            }
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralTokenSymbol).mintKey); });
                            if (!collateralCustodyConfig) {
                                throw "collateralCustodyConfig not found";
                            }
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetTokenSymbol).mintKey); });
                            if (!targetCustodyConfig) {
                                throw "targetCustodyConfig not found";
                            }
                            if (userOutputCustodyConfig.mintKey.equals(collateralCustodyConfig.mintKey)) {
                                throw "Dont use swap, just call close position";
                            }
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            positionAccount = poolConfig.getPositionFromMarketPk(publicKey, marketAccount);
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            collateralToken = poolConfig.getTokenFromSymbol(collateralTokenSymbol);
                            userOutputToken = poolConfig.getTokenFromSymbol(userOutputTokenSymbol);
                            if (!(userOutputTokenSymbol == 'SOL')) return [3, 1];
                            console.log("outputSymbol === SOL", userOutputTokenSymbol);
                            lamports = (this.minimumBalanceForRentExemptAccountLamports);
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports,
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            additionalSigners.push(wrappedSolAccount);
                            return [3, 3];
                        case 1:
                            userReceivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(userOutputToken.mintKey, publicKey, true, userOutputToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            return [4, (0, utils_1.checkIfAccountExists)(userReceivingTokenAccount, this.provider.connection)];
                        case 2:
                            if (!(_a.sent())) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userReceivingTokenAccount, publicKey, userOutputToken.mintKey, userOutputToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            _a.label = 3;
                        case 3:
                            userCollateralTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(collateralToken.mintKey, publicKey, true, collateralToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            return [4, (0, utils_1.checkIfAccountExists)(userCollateralTokenAccount, this.provider.connection)];
                        case 4:
                            if (!(_a.sent())) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userCollateralTokenAccount, publicKey, collateralToken.mintKey, collateralToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            rebateMintAccount = {
                                pubkey: collateralCustodyConfig.mintKey,
                                isSigner: false,
                                isWritable: false
                            };
                            _a.label = 5;
                        case 5:
                            _a.trys.push([5, 7, , 8]);
                            return [4, this.program.methods
                                    .closeAndSwap({
                                    priceWithSlippage: priceWithSlippage,
                                    minSwapAmountOut: minSwapAmountOut,
                                    privilege: privilege
                                })
                                    .accounts({
                                    owner: publicKey,
                                    feePayer: publicKey,
                                    receivingAccount: userOutputTokenSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userReceivingTokenAccount,
                                    collateralAccount: userCollateralTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    position: positionAccount,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    dispensingCustody: userOutputCustodyConfig.custodyAccount,
                                    dispensingOracleAccount: this.useExtOracleAccount ? userOutputCustodyConfig.extOracleAccount : userOutputCustodyConfig.intOracleAccount,
                                    dispensingCustodyTokenAccount: userOutputCustodyConfig.tokenAccount,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    receivingMint: userOutputCustodyConfig.mintKey,
                                    receivingTokenProgram: userOutputToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    collateralMint: collateralCustodyConfig.mintKey,
                                    collateralTokenProgram: collateralToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID
                                })
                                    .remainingAccounts(__spreadArray([], (0, getReferralAccounts_1.getReferralAccounts)(tokenStakeAccount, userReferralAccount, rebateTokenAccount, privilege), true))
                                    .instruction()];
                        case 6:
                            inx = _a.sent();
                            instructions.push(inx);
                            return [3, 8];
                        case 7:
                            err_4 = _a.sent();
                            console.error("perpClient CloseAndSwap error:: ", err_4);
                            throw err_4;
                        case 8: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.addCollateral = function (collateralWithFee_1, targetSymbol_1, collateralSymbol_1, side_1, positionPubKey_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 6; _i < arguments.length; _i++) {
                args_1[_i - 6] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([collateralWithFee_1, targetSymbol_1, collateralSymbol_1, side_1, positionPubKey_1, poolConfig_1], args_1, true), void 0, function (collateralWithFee, targetSymbol, collateralSymbol, side, positionPubKey, poolConfig, skipBalanceChecks, ephemeralSignerPubkey) {
                var publicKey, collateralCustodyConfig, targetCustodyConfig, marketAccount, userPayingTokenAccount, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, lamports, unWrappedSolBalance, _a, tokenAccountBalance, _b, instruction;
                if (skipBalanceChecks === void 0) { skipBalanceChecks = false; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                return __generator(this, function (_c) {
                    switch (_c.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            if (!collateralCustodyConfig || !targetCustodyConfig) {
                                throw "payTokenCustody not found";
                            }
                            userPayingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(collateralCustodyConfig.mintKey, publicKey, true);
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            if (!(collateralSymbol == 'SOL')) return [3, 3];
                            console.log("collateralSymbol === SOL", collateralSymbol);
                            lamports = collateralWithFee.add(new anchor_1.BN(this.minimumBalanceForRentExemptAccountLamports));
                            console.log("lamports:", lamports.toNumber());
                            if (!!skipBalanceChecks) return [3, 2];
                            _a = anchor_1.BN.bind;
                            return [4, this.provider.connection.getBalance(publicKey)];
                        case 1:
                            unWrappedSolBalance = new (_a.apply(anchor_1.BN, [void 0, _c.sent()]))();
                            if (unWrappedSolBalance.lt(lamports)) {
                                throw "Insufficient SOL Funds";
                            }
                            _c.label = 2;
                        case 2:
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports.toNumber(),
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 6];
                        case 3:
                            if (!!skipBalanceChecks) return [3, 6];
                            return [4, (0, utils_1.checkIfAccountExists)(userPayingTokenAccount, this.provider.connection)];
                        case 4:
                            if (!(_c.sent())) {
                                throw "Insufficient Funds , token Account doesn't exist";
                            }
                            _b = anchor_1.BN.bind;
                            return [4, this.provider.connection.getTokenAccountBalance(userPayingTokenAccount)];
                        case 5:
                            tokenAccountBalance = new (_b.apply(anchor_1.BN, [void 0, (_c.sent()).value.amount]))();
                            if (tokenAccountBalance.lt(collateralWithFee)) {
                                throw "Insufficient Funds need more ".concat(collateralWithFee.sub(tokenAccountBalance), " tokens");
                            }
                            _c.label = 6;
                        case 6: return [4, this.program.methods.addCollateral({
                                collateralDelta: collateralWithFee
                            }).accounts({
                                owner: publicKey,
                                position: positionPubKey,
                                market: marketAccount,
                                fundingAccount: collateralSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userPayingTokenAccount,
                                perpetuals: poolConfig.perpetuals,
                                pool: poolConfig.poolAddress,
                                targetCustody: targetCustodyConfig.custodyAccount,
                                targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                collateralCustody: collateralCustodyConfig.custodyAccount,
                                collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                eventAuthority: this.eventAuthority.publicKey,
                                tokenProgram: poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                program: this.programId,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                fundingMint: collateralCustodyConfig.mintKey
                            })
                                .instruction()];
                        case 7:
                            instruction = _c.sent();
                            instructions.push(instruction);
                            return [2, {
                                    instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                    additionalSigners: additionalSigners
                                }];
                    }
                });
            });
        };
        this.swapAndAddCollateral = function (targetSymbol_1, inputSymbol_1, collateralSymbol_1, amountIn_1, minCollateralAmountOut_1, side_1, positionPubKey_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 8; _i < arguments.length; _i++) {
                args_1[_i - 8] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([targetSymbol_1, inputSymbol_1, collateralSymbol_1, amountIn_1, minCollateralAmountOut_1, side_1, positionPubKey_1, poolConfig_1], args_1, true), void 0, function (targetSymbol, inputSymbol, collateralSymbol, amountIn, minCollateralAmountOut, side, positionPubKey, poolConfig, skipBalanceChecks, ephemeralSignerPubkey) {
                var publicKey, collateralCustodyConfig, targetCustodyConfig, inputCustodyConfig, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, userInputTokenAccount, lamports, unWrappedSolBalance, _a, tokenAccountBalance, _b, userCollateralTokenAccount, marketAccount, instruction;
                if (skipBalanceChecks === void 0) { skipBalanceChecks = false; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                return __generator(this, function (_c) {
                    switch (_c.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                            inputCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(inputSymbol).mintKey); });
                            if (!collateralCustodyConfig || !targetCustodyConfig || !inputCustodyConfig) {
                                throw "payTokenCustody not found";
                            }
                            if (inputCustodyConfig.mintKey.equals(collateralCustodyConfig.mintKey)) {
                                throw "Use Simple Swap";
                            }
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            if (!(inputSymbol == 'SOL')) return [3, 3];
                            console.log("inputSymbol === SOL", inputSymbol);
                            lamports = amountIn.add(new anchor_1.BN(this.minimumBalanceForRentExemptAccountLamports));
                            console.log("lamports:", lamports.toNumber());
                            if (!!skipBalanceChecks) return [3, 2];
                            _a = anchor_1.BN.bind;
                            return [4, this.provider.connection.getBalance(publicKey)];
                        case 1:
                            unWrappedSolBalance = new (_a.apply(anchor_1.BN, [void 0, _c.sent()]))();
                            if (unWrappedSolBalance.lt(lamports)) {
                                throw "Insufficient SOL Funds";
                            }
                            _c.label = 2;
                        case 2:
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports.toNumber(),
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 6];
                        case 3:
                            userInputTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(inputCustodyConfig.mintKey, publicKey, true, poolConfig.getTokenFromSymbol(inputSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            if (!!skipBalanceChecks) return [3, 6];
                            return [4, (0, utils_1.checkIfAccountExists)(userInputTokenAccount, this.provider.connection)];
                        case 4:
                            if (!(_c.sent())) {
                                throw "Insufficient Funds , token Account doesn't exist";
                            }
                            _b = anchor_1.BN.bind;
                            return [4, this.provider.connection.getTokenAccountBalance(userInputTokenAccount)];
                        case 5:
                            tokenAccountBalance = new (_b.apply(anchor_1.BN, [void 0, (_c.sent()).value.amount]))();
                            if (tokenAccountBalance.lt(amountIn)) {
                                throw "Insufficient Funds need more ".concat(amountIn.sub(tokenAccountBalance), " tokens");
                            }
                            _c.label = 6;
                        case 6:
                            userCollateralTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(collateralCustodyConfig.mintKey, publicKey, true, poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            return [4, (0, utils_1.checkIfAccountExists)(userCollateralTokenAccount, this.provider.connection)];
                        case 7:
                            if (!(_c.sent())) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userCollateralTokenAccount, publicKey, collateralCustodyConfig.mintKey, poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            return [4, this.program.methods.swapAndAddCollateral({
                                    amountIn: amountIn,
                                    minCollateralAmountOut: minCollateralAmountOut,
                                }).accounts({
                                    owner: publicKey,
                                    feePayer: publicKey,
                                    fundingAccount: inputSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userInputTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    receivingCustody: inputCustodyConfig.custodyAccount,
                                    receivingCustodyOracleAccount: this.useExtOracleAccount ? inputCustodyConfig.extOracleAccount : inputCustodyConfig.intOracleAccount,
                                    receivingCustodyTokenAccount: inputCustodyConfig.tokenAccount,
                                    position: positionPubKey,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    fundingMint: collateralCustodyConfig.mintKey,
                                })
                                    .instruction()];
                        case 8:
                            instruction = _c.sent();
                            instructions.push(instruction);
                            return [2, {
                                    instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                    additionalSigners: additionalSigners
                                }];
                    }
                });
            });
        };
        this.removeCollateral = function (collateralWithFee_1, marketSymbol_1, collateralSymbol_1, side_1, positionPubKey_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 6; _i < arguments.length; _i++) {
                args_1[_i - 6] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([collateralWithFee_1, marketSymbol_1, collateralSymbol_1, side_1, positionPubKey_1, poolConfig_1], args_1, true), void 0, function (collateralWithFee, marketSymbol, collateralSymbol, side, positionPubKey, poolConfig, createUserATA, closeUsersWSOLATA, ephemeralSignerPubkey) {
                var publicKey, collateralCustodyConfig, targetCustodyConfig, userReceivingTokenAccount, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, lamports, _a, marketAccount, instruction, closeWsolATAIns, error_2;
                if (createUserATA === void 0) { createUserATA = true; }
                if (closeUsersWSOLATA === void 0) { closeUsersWSOLATA = false; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) {
                                return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey);
                            });
                            targetCustodyConfig = poolConfig.custodies.find(function (i) {
                                return i.mintKey.equals(poolConfig.getTokenFromSymbol(marketSymbol).mintKey);
                            });
                            if (!collateralCustodyConfig || !targetCustodyConfig) {
                                throw "collateralCustodyConfig/marketCustodyConfig  not found";
                            }
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _b.label = 1;
                        case 1:
                            _b.trys.push([1, 7, , 8]);
                            console.log("removeCollateral  -- collateralSymbol:", collateralSymbol);
                            if (!(collateralSymbol == 'SOL')) return [3, 2];
                            console.log("remove collateral in SOL ...create WSOL temp and close it ");
                            lamports = this.minimumBalanceForRentExemptAccountLamports;
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports,
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 5];
                        case 2:
                            userReceivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey, publicKey, true, poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            _a = createUserATA;
                            if (!_a) return [3, 4];
                            return [4, (0, utils_1.checkIfAccountExists)(userReceivingTokenAccount, this.provider.connection)];
                        case 3:
                            _a = !(_b.sent());
                            _b.label = 4;
                        case 4:
                            if (_a) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userReceivingTokenAccount, publicKey, poolConfig.getTokenFromSymbol(collateralSymbol).mintKey, poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            _b.label = 5;
                        case 5:
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            return [4, this.program.methods
                                    .removeCollateral({
                                    collateralDelta: collateralWithFee,
                                })
                                    .accounts({
                                    owner: publicKey,
                                    receivingAccount: collateralSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userReceivingTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    position: positionPubKey,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    tokenProgram: poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    receivingMint: collateralCustodyConfig.mintKey
                                })
                                    .instruction()];
                        case 6:
                            instruction = _b.sent();
                            instructions.push(instruction);
                            if (collateralSymbol == 'WSOL' && closeUsersWSOLATA) {
                                closeWsolATAIns = (0, spl_token_1.createCloseAccountInstruction)(userReceivingTokenAccount, publicKey, publicKey);
                                postInstructions.push(closeWsolATAIns);
                            }
                            return [3, 8];
                        case 7:
                            error_2 = _b.sent();
                            console.error("perpclient removeCollateral error:", error_2);
                            throw error_2;
                        case 8: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.removeCollateralAndSwap = function (targetSymbol_1, collateralSymbol_1, outputSymbol_1, minSwapAmountOut_1, collateralDelta_1, side_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 7; _i < arguments.length; _i++) {
                args_1[_i - 7] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([targetSymbol_1, collateralSymbol_1, outputSymbol_1, minSwapAmountOut_1, collateralDelta_1, side_1, poolConfig_1], args_1, true), void 0, function (targetSymbol, collateralSymbol, outputSymbol, minSwapAmountOut, collateralDelta, side, poolConfig, ephemeralSignerPubkey) {
                var publicKey, targetCustodyConfig, collateralCustodyConfig, outputCustodyConfig, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, userReceivingTokenAccount, lamports, userCollateralTokenAccount, marketAccount, positionAccount, instruction;
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                            outputCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(outputSymbol).mintKey); });
                            if (outputCustodyConfig.mintKey.equals(collateralCustodyConfig.mintKey)) {
                                throw "Dont use swap, just call remove collateral";
                            }
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            if (!(outputSymbol == 'SOL')) return [3, 1];
                            console.log("outputSymbol === SOL", outputSymbol);
                            lamports = this.minimumBalanceForRentExemptAccountLamports;
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports,
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 3];
                        case 1:
                            userReceivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(outputSymbol).mintKey, publicKey, true, poolConfig.getTokenFromSymbol(outputSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            return [4, (0, utils_1.checkIfAccountExists)(userReceivingTokenAccount, this.provider.connection)];
                        case 2:
                            if (!(_a.sent())) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userReceivingTokenAccount, publicKey, poolConfig.getTokenFromSymbol(outputSymbol).mintKey, poolConfig.getTokenFromSymbol(outputSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            _a.label = 3;
                        case 3:
                            userCollateralTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey, publicKey, true, poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            return [4, (0, utils_1.checkIfAccountExists)(userCollateralTokenAccount, this.provider.connection)];
                        case 4:
                            if (!(_a.sent())) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userCollateralTokenAccount, publicKey, poolConfig.getTokenFromSymbol(collateralSymbol).mintKey, poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            positionAccount = poolConfig.getPositionFromMarketPk(publicKey, marketAccount);
                            return [4, this.program.methods
                                    .removeCollateralAndSwap({
                                    collateralDelta: collateralDelta,
                                    minSwapAmountOut: minSwapAmountOut,
                                })
                                    .accounts({
                                    owner: publicKey,
                                    feePayer: publicKey,
                                    receivingAccount: outputSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userReceivingTokenAccount,
                                    collateralAccount: userCollateralTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    position: positionAccount,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    dispensingCustody: outputCustodyConfig.custodyAccount,
                                    dispensingOracleAccount: this.useExtOracleAccount ? outputCustodyConfig.extOracleAccount : outputCustodyConfig.intOracleAccount,
                                    dispensingCustodyTokenAccount: outputCustodyConfig.tokenAccount,
                                    tokenProgram: poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    receivingMint: outputCustodyConfig.mintKey,
                                    receivingTokenProgram: poolConfig.getTokenFromSymbol(outputSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    collateralMint: collateralCustodyConfig.mintKey,
                                    collateralTokenProgram: poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID
                                })
                                    .instruction()];
                        case 5:
                            instruction = _a.sent();
                            instructions.push(instruction);
                            return [2, {
                                    instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                    additionalSigners: additionalSigners
                                }];
                    }
                });
            });
        };
        this.increaseSize = function (targetSymbol_1, collateralSymbol_1, positionPubKey_1, side_1, poolConfig_1, priceWithSlippage_1, sizeDelta_1, privilege_1) {
            var args_1 = [];
            for (var _i = 8; _i < arguments.length; _i++) {
                args_1[_i - 8] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([targetSymbol_1, collateralSymbol_1, positionPubKey_1, side_1, poolConfig_1, priceWithSlippage_1, sizeDelta_1, privilege_1], args_1, true), void 0, function (targetSymbol, collateralSymbol, positionPubKey, side, poolConfig, priceWithSlippage, sizeDelta, privilege, tokenStakeAccount, userReferralAccount, rebateTokenAccount) {
                var publicKey, collateralCustodyConfig, targetCustodyConfig, marketAccount, preInstructions, instructions, postInstructions, additionalSigners, instruction;
                if (tokenStakeAccount === void 0) { tokenStakeAccount = web3_js_1.PublicKey.default; }
                if (userReferralAccount === void 0) { userReferralAccount = web3_js_1.PublicKey.default; }
                if (rebateTokenAccount === void 0) { rebateTokenAccount = web3_js_1.PublicKey.default; }
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) {
                                return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey);
                            });
                            targetCustodyConfig = poolConfig.custodies.find(function (i) {
                                return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey);
                            });
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            if (!collateralCustodyConfig || !targetCustodyConfig) {
                                throw "collateralCustodyConfig/marketCustodyConfig  not found";
                            }
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            return [4, this.program.methods
                                    .increaseSize({
                                    priceWithSlippage: priceWithSlippage,
                                    sizeDelta: sizeDelta,
                                    privilege: privilege
                                })
                                    .accounts({
                                    owner: publicKey,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    position: positionPubKey,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    tokenProgram: poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    collateralMint: collateralCustodyConfig.mintKey
                                })
                                    .remainingAccounts(__spreadArray([], (0, getReferralAccounts_1.getReferralAccounts)(tokenStakeAccount, userReferralAccount, rebateTokenAccount, privilege), true))
                                    .instruction()];
                        case 1:
                            instruction = _a.sent();
                            instructions.push(instruction);
                            return [2, {
                                    instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                    additionalSigners: additionalSigners
                                }];
                    }
                });
            });
        };
        this.decreaseSize = function (targetSymbol_1, collateralSymbol_1, side_1, positionPubKey_1, poolConfig_1, priceWithSlippage_1, sizeDelta_1, privilege_1) {
            var args_1 = [];
            for (var _i = 8; _i < arguments.length; _i++) {
                args_1[_i - 8] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([targetSymbol_1, collateralSymbol_1, side_1, positionPubKey_1, poolConfig_1, priceWithSlippage_1, sizeDelta_1, privilege_1], args_1, true), void 0, function (targetSymbol, collateralSymbol, side, positionPubKey, poolConfig, priceWithSlippage, sizeDelta, privilege, tokenStakeAccount, userReferralAccount, rebateTokenAccount) {
                var publicKey, collateralCustodyConfig, targetCustodyConfig, marketAccount, preInstructions, instructions, postInstructions, additionalSigners, instruction;
                if (tokenStakeAccount === void 0) { tokenStakeAccount = web3_js_1.PublicKey.default; }
                if (userReferralAccount === void 0) { userReferralAccount = web3_js_1.PublicKey.default; }
                if (rebateTokenAccount === void 0) { rebateTokenAccount = web3_js_1.PublicKey.default; }
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) {
                                return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey);
                            });
                            targetCustodyConfig = poolConfig.custodies.find(function (i) {
                                return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey);
                            });
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            if (!collateralCustodyConfig || !targetCustodyConfig) {
                                throw "collateralCustodyConfig/marketCustodyConfig  not found";
                            }
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            return [4, this.program.methods
                                    .decreaseSize({
                                    priceWithSlippage: priceWithSlippage,
                                    sizeDelta: sizeDelta,
                                    privilege: privilege
                                })
                                    .accounts({
                                    owner: publicKey,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    position: positionPubKey,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    tokenProgram: poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    collateralMint: collateralCustodyConfig.mintKey
                                })
                                    .remainingAccounts(__spreadArray([], (0, getReferralAccounts_1.getReferralAccounts)(tokenStakeAccount, userReferralAccount, rebateTokenAccount, privilege), true))
                                    .instruction()];
                        case 1:
                            instruction = _a.sent();
                            instructions.push(instruction);
                            return [2, {
                                    instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                    additionalSigners: additionalSigners
                                }];
                    }
                });
            });
        };
        this.addLiquidity = function (payTokenSymbol_1, tokenAmountIn_1, minLpAmountOut_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 4; _i < arguments.length; _i++) {
                args_1[_i - 4] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([payTokenSymbol_1, tokenAmountIn_1, minLpAmountOut_1, poolConfig_1], args_1, true), void 0, function (payTokenSymbol, tokenAmountIn, minLpAmountOut, poolConfig, skipBalanceChecks, ephemeralSignerPubkey) {
                var publicKey, payTokenCustodyConfig, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, payToken, userPayingTokenAccount, lpTokenAccount, custodyAccountMetas, custodyOracleAccountMetas, markets, _a, _b, custody, _c, _d, market, lamports, unWrappedSolBalance, _e, tokenAccountBalance, _f, instruction, err_5;
                if (skipBalanceChecks === void 0) { skipBalanceChecks = false; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                return __generator(this, function (_g) {
                    switch (_g.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            payTokenCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(payTokenSymbol).mintKey); });
                            if (!payTokenCustodyConfig) {
                                throw "payTokenCustodyConfig not found";
                            }
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            payToken = poolConfig.getTokenFromSymbol(payTokenSymbol);
                            _g.label = 1;
                        case 1:
                            _g.trys.push([1, 10, , 11]);
                            userPayingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(payTokenCustodyConfig.mintKey, publicKey, true, payToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            lpTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.stakedLpTokenMint, publicKey, true);
                            custodyAccountMetas = [];
                            custodyOracleAccountMetas = [];
                            markets = [];
                            for (_a = 0, _b = poolConfig.custodies; _a < _b.length; _a++) {
                                custody = _b[_a];
                                custodyAccountMetas.push({
                                    pubkey: custody.custodyAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                                custodyOracleAccountMetas.push({
                                    pubkey: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            for (_c = 0, _d = poolConfig.markets; _c < _d.length; _c++) {
                                market = _d[_c];
                                markets.push({
                                    pubkey: market.marketAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            return [4, (0, utils_1.checkIfAccountExists)(lpTokenAccount, this.provider.connection)];
                        case 2:
                            if (!(_g.sent())) {
                                instructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, lpTokenAccount, publicKey, poolConfig.stakedLpTokenMint));
                            }
                            if (!(payTokenSymbol == 'SOL')) return [3, 5];
                            console.log("payTokenSymbol === SOL", payTokenSymbol);
                            lamports = tokenAmountIn.add(new anchor_1.BN(this.minimumBalanceForRentExemptAccountLamports));
                            if (!!skipBalanceChecks) return [3, 4];
                            _e = anchor_1.BN.bind;
                            return [4, this.provider.connection.getBalance(publicKey)];
                        case 3:
                            unWrappedSolBalance = new (_e.apply(anchor_1.BN, [void 0, _g.sent()]))();
                            if (unWrappedSolBalance.lt(lamports)) {
                                throw "Insufficient SOL Funds";
                            }
                            _g.label = 4;
                        case 4:
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports.toNumber(),
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 8];
                        case 5:
                            if (!!skipBalanceChecks) return [3, 8];
                            return [4, (0, utils_1.checkIfAccountExists)(userPayingTokenAccount, this.provider.connection)];
                        case 6:
                            if (!(_g.sent())) {
                                throw "Insufficient Funds , token Account doesn't exist";
                            }
                            _f = anchor_1.BN.bind;
                            return [4, this.provider.connection.getTokenAccountBalance(userPayingTokenAccount)];
                        case 7:
                            tokenAccountBalance = new (_f.apply(anchor_1.BN, [void 0, (_g.sent()).value.amount]))();
                            if (tokenAccountBalance.lt(tokenAmountIn)) {
                                throw "Insufficient Funds need more ".concat(tokenAmountIn.sub(tokenAccountBalance), " tokens");
                            }
                            _g.label = 8;
                        case 8: return [4, this.program.methods
                                .addLiquidity({
                                amountIn: tokenAmountIn,
                                minLpAmountOut: minLpAmountOut
                            })
                                .accounts({
                                owner: publicKey,
                                fundingAccount: payTokenSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userPayingTokenAccount,
                                lpTokenAccount: lpTokenAccount,
                                transferAuthority: poolConfig.transferAuthority,
                                perpetuals: poolConfig.perpetuals,
                                pool: poolConfig.poolAddress,
                                custody: payTokenCustodyConfig.custodyAccount,
                                custodyOracleAccount: this.useExtOracleAccount ? payTokenCustodyConfig.extOracleAccount : payTokenCustodyConfig.intOracleAccount,
                                custodyTokenAccount: payTokenCustodyConfig.tokenAccount,
                                lpTokenMint: poolConfig.stakedLpTokenMint,
                                eventAuthority: this.eventAuthority.publicKey,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                program: this.programId,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                fundingMint: payTokenCustodyConfig.mintKey,
                                fundingTokenProgram: payToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID
                            })
                                .remainingAccounts(__spreadArray(__spreadArray(__spreadArray([], custodyAccountMetas, true), custodyOracleAccountMetas, true), markets, true))
                                .instruction()];
                        case 9:
                            instruction = _g.sent();
                            instructions.push(instruction);
                            return [3, 11];
                        case 10:
                            err_5 = _g.sent();
                            console.error("perpClient addLiquidity error:: ", err_5);
                            throw err_5;
                        case 11: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.addLiquidityAndStake = function (inputSymbol_1, amountIn_1, minLpAmountOut_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 4; _i < arguments.length; _i++) {
                args_1[_i - 4] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([inputSymbol_1, amountIn_1, minLpAmountOut_1, poolConfig_1], args_1, true), void 0, function (inputSymbol, amountIn, minLpAmountOut, poolConfig, skipBalanceChecks, ephemeralSignerPubkey, userPublicKey) {
                var publicKey, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, userInputTokenAccount, lpTokenMint, inputCustodyConfig, lpTokenAccount, inputToken, flpStakeAccount, poolStakedLpVault, lamports, unWrappedSolBalance, _a, tokenAccountBalance, _b, custodyAccountMetas, custodyOracleAccountMetas, markets, _c, _d, custody, _e, _f, market, instruction;
                if (skipBalanceChecks === void 0) { skipBalanceChecks = false; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                if (userPublicKey === void 0) { userPublicKey = undefined; }
                return __generator(this, function (_g) {
                    switch (_g.label) {
                        case 0:
                            publicKey = userPublicKey !== null && userPublicKey !== void 0 ? userPublicKey : this.provider.wallet.publicKey;
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            lpTokenMint = poolConfig.stakedLpTokenMint;
                            inputCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(inputSymbol).mintKey); });
                            lpTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(lpTokenMint, publicKey, true);
                            inputToken = poolConfig.getTokenFromSymbol(inputSymbol);
                            flpStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("stake"), publicKey.toBuffer(), poolConfig.poolAddress.toBuffer()], this.programId)[0];
                            poolStakedLpVault = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("staked_lp_token_account"), poolConfig.poolAddress.toBuffer(), lpTokenMint.toBuffer()], this.programId)[0];
                            if (!(inputSymbol == 'SOL')) return [3, 4];
                            console.log("inputSymbol === SOL", inputSymbol);
                            lamports = amountIn.add(new anchor_1.BN(this.minimumBalanceForRentExemptAccountLamports));
                            console.log("lamports:", lamports.toNumber());
                            if (!!skipBalanceChecks) return [3, 2];
                            _a = anchor_1.BN.bind;
                            return [4, this.provider.connection.getBalance(publicKey)];
                        case 1:
                            unWrappedSolBalance = new (_a.apply(anchor_1.BN, [void 0, _g.sent()]))();
                            if (unWrappedSolBalance.lt(lamports)) {
                                throw "Insufficient SOL Funds";
                            }
                            _g.label = 2;
                        case 2: return [4, (0, utils_1.checkIfAccountExists)(lpTokenAccount, this.provider.connection)];
                        case 3:
                            if (!(_g.sent())) {
                                instructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, lpTokenAccount, publicKey, poolConfig.stakedLpTokenMint));
                            }
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports.toNumber(),
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 7];
                        case 4:
                            userInputTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(inputCustodyConfig.mintKey, publicKey, true, inputToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            if (!!skipBalanceChecks) return [3, 7];
                            return [4, (0, utils_1.checkIfAccountExists)(userInputTokenAccount, this.provider.connection)];
                        case 5:
                            if (!(_g.sent())) {
                                throw "Insufficient Funds , token Account doesn't exist";
                            }
                            _b = anchor_1.BN.bind;
                            return [4, this.provider.connection.getTokenAccountBalance(userInputTokenAccount)];
                        case 6:
                            tokenAccountBalance = new (_b.apply(anchor_1.BN, [void 0, (_g.sent()).value.amount]))();
                            if (tokenAccountBalance.lt(amountIn)) {
                                throw "Insufficient Funds need more ".concat(amountIn.sub(tokenAccountBalance), " tokens");
                            }
                            _g.label = 7;
                        case 7:
                            custodyAccountMetas = [];
                            custodyOracleAccountMetas = [];
                            markets = [];
                            for (_c = 0, _d = poolConfig.custodies; _c < _d.length; _c++) {
                                custody = _d[_c];
                                custodyAccountMetas.push({
                                    pubkey: custody.custodyAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                                custodyOracleAccountMetas.push({
                                    pubkey: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            for (_e = 0, _f = poolConfig.markets; _e < _f.length; _e++) {
                                market = _f[_e];
                                markets.push({
                                    pubkey: market.marketAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            return [4, this.program.methods.addLiquidityAndStake({
                                    amountIn: amountIn,
                                    minLpAmountOut: minLpAmountOut,
                                }).accounts({
                                    owner: publicKey,
                                    feePayer: publicKey,
                                    fundingAccount: inputSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userInputTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    custody: inputCustodyConfig.custodyAccount,
                                    custodyOracleAccount: this.useExtOracleAccount ? inputCustodyConfig.extOracleAccount : inputCustodyConfig.intOracleAccount,
                                    custodyTokenAccount: inputCustodyConfig.tokenAccount,
                                    lpTokenMint: lpTokenMint,
                                    flpStakeAccount: flpStakeAccount,
                                    poolStakedLpVault: poolStakedLpVault,
                                    systemProgram: web3_js_1.SystemProgram.programId,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    fundingMint: inputCustodyConfig.mintKey,
                                    fundingTokenProgram: inputToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID
                                })
                                    .remainingAccounts(__spreadArray(__spreadArray(__spreadArray([], custodyAccountMetas, true), custodyOracleAccountMetas, true), markets, true))
                                    .instruction()];
                        case 8:
                            instruction = _g.sent();
                            instructions.push(instruction);
                            return [2, {
                                    instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                    additionalSigners: additionalSigners
                                }];
                    }
                });
            });
        };
        this.removeLiquidity = function (recieveTokenSymbol_1, liquidityAmountIn_1, minTokenAmountOut_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 4; _i < arguments.length; _i++) {
                args_1[_i - 4] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([recieveTokenSymbol_1, liquidityAmountIn_1, minTokenAmountOut_1, poolConfig_1], args_1, true), void 0, function (recieveTokenSymbol, liquidityAmountIn, minTokenAmountOut, poolConfig, closeLpATA, createUserATA, closeUsersWSOLATA, ephemeralSignerPubkey, userPublicKey) {
                var recieveTokenCustodyConfig, publicKey, userReceivingTokenAccount, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, recieveToken, stakedLpTokenAccount, custodyAccountMetas, custodyOracleAccountMetas, markets, _a, _b, custody, _c, _d, market, lamports, _e, removeLiquidityTx, closeInx, closeWsolATAIns, err_6;
                if (closeLpATA === void 0) { closeLpATA = false; }
                if (createUserATA === void 0) { createUserATA = true; }
                if (closeUsersWSOLATA === void 0) { closeUsersWSOLATA = false; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                if (userPublicKey === void 0) { userPublicKey = undefined; }
                return __generator(this, function (_f) {
                    switch (_f.label) {
                        case 0:
                            recieveTokenCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(recieveTokenSymbol).mintKey); });
                            if (!recieveTokenCustodyConfig) {
                                throw "recieveTokenCustody not found";
                            }
                            publicKey = userPublicKey !== null && userPublicKey !== void 0 ? userPublicKey : this.provider.wallet.publicKey;
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            recieveToken = poolConfig.getTokenFromSymbol(recieveTokenSymbol);
                            _f.label = 1;
                        case 1:
                            _f.trys.push([1, 7, , 8]);
                            stakedLpTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.stakedLpTokenMint, publicKey, true);
                            custodyAccountMetas = [];
                            custodyOracleAccountMetas = [];
                            markets = [];
                            for (_a = 0, _b = poolConfig.custodies; _a < _b.length; _a++) {
                                custody = _b[_a];
                                custodyAccountMetas.push({
                                    pubkey: custody.custodyAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                                custodyOracleAccountMetas.push({
                                    pubkey: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            for (_c = 0, _d = poolConfig.markets; _c < _d.length; _c++) {
                                market = _d[_c];
                                markets.push({
                                    pubkey: market.marketAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            if (!(recieveTokenSymbol == 'SOL')) return [3, 2];
                            lamports = this.minimumBalanceForRentExemptAccountLamports;
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports,
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 5];
                        case 2:
                            userReceivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(recieveToken.mintKey, publicKey, true, recieveToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            _e = createUserATA;
                            if (!_e) return [3, 4];
                            return [4, (0, utils_1.checkIfAccountExists)(userReceivingTokenAccount, this.provider.connection)];
                        case 3:
                            _e = !(_f.sent());
                            _f.label = 4;
                        case 4:
                            if (_e) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userReceivingTokenAccount, publicKey, recieveToken.mintKey, recieveToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            _f.label = 5;
                        case 5: return [4, this.program.methods
                                .removeLiquidity({
                                lpAmountIn: liquidityAmountIn,
                                minAmountOut: minTokenAmountOut
                            })
                                .accounts({
                                owner: publicKey,
                                receivingAccount: recieveTokenSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userReceivingTokenAccount,
                                lpTokenAccount: stakedLpTokenAccount,
                                transferAuthority: poolConfig.transferAuthority,
                                perpetuals: poolConfig.perpetuals,
                                pool: poolConfig.poolAddress,
                                custody: recieveTokenCustodyConfig.custodyAccount,
                                custodyOracleAccount: this.useExtOracleAccount ? recieveTokenCustodyConfig.extOracleAccount : recieveTokenCustodyConfig.intOracleAccount,
                                custodyTokenAccount: recieveTokenCustodyConfig.tokenAccount,
                                lpTokenMint: poolConfig.stakedLpTokenMint,
                                eventAuthority: this.eventAuthority.publicKey,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                program: this.programId,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                receivingMint: recieveTokenCustodyConfig.mintKey,
                                receivingTokenProgram: recieveToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID
                            })
                                .remainingAccounts(__spreadArray(__spreadArray(__spreadArray([], custodyAccountMetas, true), custodyOracleAccountMetas, true), markets, true))
                                .instruction()];
                        case 6:
                            removeLiquidityTx = _f.sent();
                            instructions.push(removeLiquidityTx);
                            if (closeLpATA) {
                                closeInx = (0, spl_token_1.createCloseAccountInstruction)(stakedLpTokenAccount, publicKey, publicKey);
                                instructions.push(closeInx);
                            }
                            if (recieveTokenSymbol == 'WSOL' && closeUsersWSOLATA) {
                                closeWsolATAIns = (0, spl_token_1.createCloseAccountInstruction)(userReceivingTokenAccount, publicKey, publicKey);
                                postInstructions.push(closeWsolATAIns);
                            }
                            return [3, 8];
                        case 7:
                            err_6 = _f.sent();
                            console.log("perpClient removeLiquidity error:: ", err_6);
                            throw err_6;
                        case 8: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.addReferral = function (tokenStakeAccount, nftReferralAccount) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, addReferralInstruction, err_7;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4, this.program.methods
                                .createReferral({})
                                .accounts({
                                owner: publicKey,
                                feePayer: publicKey,
                                referralAccount: nftReferralAccount,
                                tokenStakeAccount: tokenStakeAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                            })
                                .instruction()];
                    case 2:
                        addReferralInstruction = _a.sent();
                        instructions.push(addReferralInstruction);
                        return [3, 4];
                    case 3:
                        err_7 = _a.sent();
                        console.log("perpClient addReferral error:: ", err_7);
                        throw err_7;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.updateNftAccount = function (nftMint, updateReferer, updateBooster, flpStakeAccounts) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, nftTradingAccount, nftReferralAccount, nftTokenAccount, flpStakeAccountMetas, _i, flpStakeAccounts_1, flpStakeAccountPk, updateNftTradingAccountInstruction, err_8;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 4, , 5]);
                        nftTradingAccount = web3_js_1.PublicKey.findProgramAddressSync([
                            Buffer.from("trading"),
                            nftMint.toBuffer(),
                        ], this.programId)[0];
                        nftReferralAccount = web3_js_1.PublicKey.findProgramAddressSync([
                            Buffer.from("referral"),
                            publicKey.toBuffer(),
                        ], this.programId)[0];
                        return [4, (0, spl_token_1.getAssociatedTokenAddress)(nftMint, publicKey, true)];
                    case 2:
                        nftTokenAccount = _a.sent();
                        flpStakeAccountMetas = [];
                        for (_i = 0, flpStakeAccounts_1 = flpStakeAccounts; _i < flpStakeAccounts_1.length; _i++) {
                            flpStakeAccountPk = flpStakeAccounts_1[_i];
                            flpStakeAccountMetas.push({
                                pubkey: flpStakeAccountPk,
                                isSigner: false,
                                isWritable: true,
                            });
                        }
                        return [4, this.program.methods
                                .updateTradingAccount({
                                updateReferer: updateReferer,
                                updateBooster: updateBooster
                            })
                                .accounts({
                                owner: publicKey,
                                feePayer: publicKey,
                                nftTokenAccount: nftTokenAccount,
                                referralAccount: nftReferralAccount,
                                tradingAccount: nftTradingAccount
                            })
                                .instruction()];
                    case 3:
                        updateNftTradingAccountInstruction = _a.sent();
                        instructions.push(updateNftTradingAccountInstruction);
                        return [3, 5];
                    case 4:
                        err_8 = _a.sent();
                        console.log("perpClient updateNftAccount error:: ", err_8);
                        throw err_8;
                    case 5: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.levelUp = function (poolConfig, nftMint, authorizationRulesAccount) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, nftTradingAccount, metadataAccount, levelUpInstruction, err_9;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        nftTradingAccount = web3_js_1.PublicKey.findProgramAddressSync([
                            Buffer.from("trading"),
                            nftMint.toBuffer(),
                        ], this.programId)[0];
                        metadataAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("metadata"), constants_1.METAPLEX_PROGRAM_ID.toBuffer(), nftMint.toBuffer()], constants_1.METAPLEX_PROGRAM_ID)[0];
                        return [4, this.program.methods
                                .levelUp({})
                                .accounts({
                                owner: publicKey,
                                perpetuals: this.perpetuals.publicKey,
                                pool: poolConfig.poolAddress,
                                metadataAccount: metadataAccount,
                                nftMint: nftMint,
                                metadataProgram: constants_1.METAPLEX_PROGRAM_ID,
                                tradingAccount: nftTradingAccount,
                                transferAuthority: this.authority.publicKey,
                                authorizationRulesAccount: authorizationRulesAccount,
                                authorizationRulesProgram: new web3_js_1.PublicKey('auth9SigNpDKz4sJJ1DfCTuZrZNSAgh9sFD3rboVmgg'),
                                systemProgram: web3_js_1.SystemProgram.programId,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                            })
                                .instruction()];
                    case 2:
                        levelUpInstruction = _a.sent();
                        instructions.push(levelUpInstruction);
                        return [3, 4];
                    case 3:
                        err_9 = _a.sent();
                        console.log("perpClient levelUp error:: ", err_9);
                        throw err_9;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.depositStake = function (owner, feePayer, depositAmount, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var preInstructions, instructions, postInstructions, additionalSigners, lpTokenMint, poolStakedLpVault, flpStakeAccount, userLpTokenAccount, depositStakeInstruction, err_10;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 4, , 5]);
                        lpTokenMint = poolConfig.stakedLpTokenMint;
                        poolStakedLpVault = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("staked_lp_token_account"), poolConfig.poolAddress.toBuffer(), lpTokenMint.toBuffer()], this.programId)[0];
                        flpStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("stake"), owner.toBuffer(), poolConfig.poolAddress.toBuffer()], this.programId)[0];
                        return [4, (0, spl_token_1.getAssociatedTokenAddress)(poolConfig.stakedLpTokenMint, owner, true)];
                    case 2:
                        userLpTokenAccount = _a.sent();
                        return [4, this.program.methods
                                .depositStake({
                                depositAmount: depositAmount
                            })
                                .accounts({
                                owner: owner,
                                feePayer: feePayer,
                                fundingLpTokenAccount: userLpTokenAccount,
                                transferAuthority: poolConfig.transferAuthority,
                                perpetuals: this.perpetuals.publicKey,
                                pool: poolConfig.poolAddress,
                                flpStakeAccount: flpStakeAccount,
                                poolStakedLpVault: poolStakedLpVault,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId,
                                lpTokenMint: poolConfig.stakedLpTokenMint,
                            })
                                .instruction()];
                    case 3:
                        depositStakeInstruction = _a.sent();
                        instructions.push(depositStakeInstruction);
                        return [3, 5];
                    case 4:
                        err_10 = _a.sent();
                        console.log("perpClient depositStaking error:: ", err_10);
                        throw err_10;
                    case 5: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.refreshStakeWithAllFlpStakeAccounts = function (rewardSymbol, poolConfig, flpStakeAccountPks) { return __awaiter(_this, void 0, void 0, function () {
            var rewardCustodyMint, rewardCustodyConfig, pool, feeDistributionTokenAccount, custodyAccountMetas, _i, _a, custody, maxFlpStakeAccountPkLength, flpStakeAccountMetas, _b, flpStakeAccountPks_1, flpStakeAccountPk, refreshStakeInstruction, err_11;
            return __generator(this, function (_c) {
                switch (_c.label) {
                    case 0:
                        _c.trys.push([0, 2, , 3]);
                        rewardCustodyMint = poolConfig.getTokenFromSymbol(rewardSymbol).mintKey;
                        rewardCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(rewardSymbol).mintKey); });
                        pool = poolConfig.poolAddress;
                        feeDistributionTokenAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("custody_token_account"), pool.toBuffer(), rewardCustodyMint.toBuffer()], this.programId)[0];
                        custodyAccountMetas = [];
                        for (_i = 0, _a = poolConfig.custodies; _i < _a.length; _i++) {
                            custody = _a[_i];
                            custodyAccountMetas.push({
                                pubkey: custody.custodyAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        maxFlpStakeAccountPkLength = 32 - 4 + custodyAccountMetas.length;
                        if (flpStakeAccountPks.length > maxFlpStakeAccountPkLength) {
                            throw new Error("Max of ".concat(maxFlpStakeAccountPkLength, " flpStakeAccountPks can be updated at a time."));
                        }
                        flpStakeAccountMetas = [];
                        for (_b = 0, flpStakeAccountPks_1 = flpStakeAccountPks; _b < flpStakeAccountPks_1.length; _b++) {
                            flpStakeAccountPk = flpStakeAccountPks_1[_b];
                            flpStakeAccountMetas.push({
                                pubkey: flpStakeAccountPk,
                                isSigner: false,
                                isWritable: true,
                            });
                        }
                        return [4, this.program.methods
                                .refreshStake({})
                                .accounts({
                                perpetuals: this.perpetuals.publicKey,
                                pool: pool,
                                rewardCustody: rewardCustodyConfig.custodyAccount,
                                feeDistributionTokenAccount: feeDistributionTokenAccount,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.program.programId,
                            })
                                .remainingAccounts(__spreadArray(__spreadArray([], custodyAccountMetas, true), flpStakeAccountMetas, true))
                                .instruction()];
                    case 1:
                        refreshStakeInstruction = _c.sent();
                        return [2, refreshStakeInstruction];
                    case 2:
                        err_11 = _c.sent();
                        console.log("perpClient refreshStaking error:: ", err_11);
                        throw err_11;
                    case 3: return [2];
                }
            });
        }); };
        this.refreshStakeWithTokenStake = function (rewardSymbol_1, poolConfig_1, flpStakeAccountPk_1) {
            var args_1 = [];
            for (var _i = 3; _i < arguments.length; _i++) {
                args_1[_i - 3] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([rewardSymbol_1, poolConfig_1, flpStakeAccountPk_1], args_1, true), void 0, function (rewardSymbol, poolConfig, flpStakeAccountPk, userPublicKey) {
                var publicKey, rewardCustodyMint, rewardCustodyConfig, pool, feeDistributionTokenAccount, custodyAccountMetas, _a, _b, custody, stakeAccountMetas, tokenStakeAccount, refreshStakeInstruction, err_12;
                if (userPublicKey === void 0) { userPublicKey = undefined; }
                return __generator(this, function (_c) {
                    switch (_c.label) {
                        case 0:
                            _c.trys.push([0, 2, , 3]);
                            publicKey = userPublicKey !== null && userPublicKey !== void 0 ? userPublicKey : this.provider.wallet.publicKey;
                            rewardCustodyMint = poolConfig.getTokenFromSymbol(rewardSymbol).mintKey;
                            rewardCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(rewardSymbol).mintKey); });
                            pool = poolConfig.poolAddress;
                            feeDistributionTokenAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("custody_token_account"), pool.toBuffer(), rewardCustodyMint.toBuffer()], this.programId)[0];
                            custodyAccountMetas = [];
                            for (_a = 0, _b = poolConfig.custodies; _a < _b.length; _a++) {
                                custody = _b[_a];
                                custodyAccountMetas.push({
                                    pubkey: custody.custodyAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            stakeAccountMetas = [];
                            stakeAccountMetas.push({
                                pubkey: flpStakeAccountPk,
                                isSigner: false,
                                isWritable: true,
                            });
                            tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("token_stake"), publicKey.toBuffer()], this.programId)[0];
                            stakeAccountMetas.push({
                                pubkey: tokenStakeAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                            return [4, this.program.methods
                                    .refreshStake({})
                                    .accounts({
                                    perpetuals: this.perpetuals.publicKey,
                                    pool: pool,
                                    rewardCustody: rewardCustodyConfig.custodyAccount,
                                    feeDistributionTokenAccount: feeDistributionTokenAccount,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.program.programId,
                                })
                                    .remainingAccounts(__spreadArray(__spreadArray([], custodyAccountMetas, true), stakeAccountMetas, true))
                                    .instruction()];
                        case 1:
                            refreshStakeInstruction = _c.sent();
                            return [2, refreshStakeInstruction];
                        case 2:
                            err_12 = _c.sent();
                            console.log("perpClient refreshStaking error:: ", err_12);
                            throw err_12;
                        case 3: return [2];
                    }
                });
            });
        };
        this.unstakeInstant = function (rewardSymbol_1, unstakeAmount_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 3; _i < arguments.length; _i++) {
                args_1[_i - 3] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([rewardSymbol_1, unstakeAmount_1, poolConfig_1], args_1, true), void 0, function (rewardSymbol, unstakeAmount, poolConfig, userPublicKey) {
                var publicKey, preInstructions, instructions, postInstructions, additionalSigners, rewardCustodyConfig, pool, flpStakeAccount, tokenStakeAccount, tokenStakeAccounts, _a, unstakeInstantInstruction, err_13;
                if (userPublicKey === void 0) { userPublicKey = undefined; }
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            publicKey = userPublicKey !== null && userPublicKey !== void 0 ? userPublicKey : this.provider.wallet.publicKey;
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _b.label = 1;
                        case 1:
                            _b.trys.push([1, 5, , 6]);
                            rewardCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(rewardSymbol).mintKey); });
                            pool = poolConfig.poolAddress;
                            flpStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("stake"), publicKey.toBuffer(), pool.toBuffer()], this.programId)[0];
                            tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("token_stake"), publicKey.toBuffer()], this.programId)[0];
                            tokenStakeAccounts = [];
                            _a = tokenStakeAccount;
                            if (!_a) return [3, 3];
                            return [4, (0, utils_1.checkIfAccountExists)(tokenStakeAccount, this.provider.connection)];
                        case 2:
                            _a = (_b.sent());
                            _b.label = 3;
                        case 3:
                            if (_a) {
                                tokenStakeAccounts.push({
                                    pubkey: tokenStakeAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            return [4, this.program.methods
                                    .unstakeInstant({
                                    unstakeAmount: unstakeAmount
                                })
                                    .accounts({
                                    owner: publicKey,
                                    perpetuals: this.perpetuals.publicKey,
                                    pool: pool,
                                    flpStakeAccount: flpStakeAccount,
                                    rewardCustody: rewardCustodyConfig.custodyAccount,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.program.programId,
                                })
                                    .remainingAccounts(__spreadArray([], tokenStakeAccounts, true))
                                    .instruction()];
                        case 4:
                            unstakeInstantInstruction = _b.sent();
                            instructions.push(unstakeInstantInstruction);
                            return [3, 6];
                        case 5:
                            err_13 = _b.sent();
                            console.log("perpClient unstakeInstant error:: ", err_13);
                            throw err_13;
                        case 6: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.setFeeShareBps = function (poolConfig, flpStakeAccountPks) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, pool, custodyAccountMetas, _i, _a, custody, maxFlpStakeAccountPkLength, flpStakeAccountMetas, _b, flpStakeAccountPks_2, flpStakeAccountPk, refreshStakeInstruction, err_14;
            return __generator(this, function (_c) {
                switch (_c.label) {
                    case 0:
                        _c.trys.push([0, 2, , 3]);
                        publicKey = this.provider.wallet.publicKey;
                        pool = poolConfig.poolAddress;
                        custodyAccountMetas = [];
                        for (_i = 0, _a = poolConfig.custodies; _i < _a.length; _i++) {
                            custody = _a[_i];
                            custodyAccountMetas.push({
                                pubkey: custody.custodyAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        maxFlpStakeAccountPkLength = 32 - 4 + custodyAccountMetas.length;
                        if (flpStakeAccountPks.length > maxFlpStakeAccountPkLength) {
                            throw new Error("Max of ".concat(maxFlpStakeAccountPkLength, " flpStakeAccountPks can be updated at a time."));
                        }
                        flpStakeAccountMetas = [];
                        for (_b = 0, flpStakeAccountPks_2 = flpStakeAccountPks; _b < flpStakeAccountPks_2.length; _b++) {
                            flpStakeAccountPk = flpStakeAccountPks_2[_b];
                            flpStakeAccountMetas.push({
                                pubkey: flpStakeAccountPk,
                                isSigner: false,
                                isWritable: true,
                            });
                        }
                        return [4, this.program.methods
                                .setFeeShare({
                                feeShareBps: new anchor_1.BN(7000)
                            })
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                pool: pool,
                            })
                                .remainingAccounts(__spreadArray([], flpStakeAccountMetas, true))
                                .instruction()];
                    case 1:
                        refreshStakeInstruction = _c.sent();
                        return [2, refreshStakeInstruction];
                    case 2:
                        err_14 = _c.sent();
                        console.log("perpClient refreshStaking error:: ", err_14);
                        throw err_14;
                    case 3: return [2];
                }
            });
        }); };
        this.unstakeRequest = function (unstakeAmount, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, pool, flpStakeAccount, unstakeRequestInstruction, err_15;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        pool = poolConfig.poolAddress;
                        flpStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("stake"), publicKey.toBuffer(), pool.toBuffer()], this.programId)[0];
                        return [4, this.program.methods
                                .unstakeRequest({
                                unstakeAmount: unstakeAmount
                            })
                                .accounts({
                                owner: publicKey,
                                perpetuals: this.perpetuals.publicKey,
                                pool: pool,
                                flpStakeAccount: flpStakeAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId
                            })
                                .instruction()];
                    case 2:
                        unstakeRequestInstruction = _a.sent();
                        instructions.push(unstakeRequestInstruction);
                        return [3, 4];
                    case 3:
                        err_15 = _a.sent();
                        console.log("perpClient unstakeRequest error:: ", err_15);
                        throw err_15;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.withdrawStake = function (poolConfig_1) {
            var args_1 = [];
            for (var _i = 1; _i < arguments.length; _i++) {
                args_1[_i - 1] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([poolConfig_1], args_1, true), void 0, function (poolConfig, pendingActivation, deactivated, createUserLPTA, userPublicKey) {
                var publicKey, preInstructions, instructions, postInstructions, additionalSigners, lpTokenMint, pool, poolStakedLpVault, flpStakeAccount, userLpTokenAccount, _a, withdrawStakeInstruction, err_16;
                if (pendingActivation === void 0) { pendingActivation = true; }
                if (deactivated === void 0) { deactivated = true; }
                if (createUserLPTA === void 0) { createUserLPTA = true; }
                if (userPublicKey === void 0) { userPublicKey = undefined; }
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            publicKey = userPublicKey !== null && userPublicKey !== void 0 ? userPublicKey : this.provider.wallet.publicKey;
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _b.label = 1;
                        case 1:
                            _b.trys.push([1, 5, , 6]);
                            lpTokenMint = poolConfig.stakedLpTokenMint;
                            pool = poolConfig.poolAddress;
                            poolStakedLpVault = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("staked_lp_token_account"), pool.toBuffer(), lpTokenMint.toBuffer()], this.program.programId)[0];
                            flpStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("stake"), publicKey.toBuffer(), pool.toBuffer()], this.program.programId)[0];
                            userLpTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.stakedLpTokenMint, publicKey, true);
                            _a = createUserLPTA;
                            if (!_a) return [3, 3];
                            return [4, (0, utils_1.checkIfAccountExists)(userLpTokenAccount, this.provider.connection)];
                        case 2:
                            _a = !(_b.sent());
                            _b.label = 3;
                        case 3:
                            if (_a) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userLpTokenAccount, publicKey, poolConfig.stakedLpTokenMint));
                            }
                            return [4, this.program.methods
                                    .withdrawStake({
                                    pendingActivation: pendingActivation,
                                    deactivated: deactivated
                                })
                                    .accounts({
                                    owner: publicKey,
                                    receivingLpTokenAccount: userLpTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: this.perpetuals.publicKey,
                                    pool: pool,
                                    flpStakeAccount: flpStakeAccount,
                                    poolStakedLpVault: poolStakedLpVault,
                                    systemProgram: web3_js_1.SystemProgram.programId,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.program.programId,
                                    lpMint: poolConfig.stakedLpTokenMint,
                                })
                                    .instruction()];
                        case 4:
                            withdrawStakeInstruction = _b.sent();
                            instructions.push(withdrawStakeInstruction);
                            return [3, 6];
                        case 5:
                            err_16 = _b.sent();
                            console.log("perpClient withdrawStake error:: ", err_16);
                            throw err_16;
                        case 6: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.collectStakeFees = function (rewardSymbol_1, poolConfig_1, tokenStakeAccount_1) {
            var args_1 = [];
            for (var _i = 3; _i < arguments.length; _i++) {
                args_1[_i - 3] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([rewardSymbol_1, poolConfig_1, tokenStakeAccount_1], args_1, true), void 0, function (rewardSymbol, poolConfig, tokenStakeAccount, createUserATA) {
                var publicKey, rewardCustodyMint, rewardCustodyConfig, preInstructions, instructions, postInstructions, additionalSigners, pool, flpStakeAccount, receivingTokenAccount, _a, tokenStakeAccounts, withdrawStakeInstruction, err_17;
                if (createUserATA === void 0) { createUserATA = true; }
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            rewardCustodyMint = poolConfig.getTokenFromSymbol(rewardSymbol).mintKey;
                            rewardCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(rewardSymbol).mintKey); });
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _b.label = 1;
                        case 1:
                            _b.trys.push([1, 5, , 6]);
                            pool = poolConfig.poolAddress;
                            flpStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("stake"), publicKey.toBuffer(), pool.toBuffer()], this.program.programId)[0];
                            receivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(rewardCustodyMint, publicKey, true);
                            _a = createUserATA;
                            if (!_a) return [3, 3];
                            return [4, (0, utils_1.checkIfAccountExists)(receivingTokenAccount, this.provider.connection)];
                        case 2:
                            _a = !(_b.sent());
                            _b.label = 3;
                        case 3:
                            if (_a) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, receivingTokenAccount, publicKey, rewardCustodyMint));
                            }
                            tokenStakeAccounts = [];
                            if (tokenStakeAccount) {
                                tokenStakeAccounts.push({
                                    pubkey: tokenStakeAccount,
                                    isSigner: false,
                                    isWritable: true,
                                });
                            }
                            return [4, this.program.methods
                                    .collectStakeFees({})
                                    .accounts({
                                    owner: publicKey,
                                    receivingTokenAccount: receivingTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: this.perpetuals.publicKey,
                                    pool: pool,
                                    feeCustody: rewardCustodyConfig.custodyAccount,
                                    flpStakeAccount: flpStakeAccount,
                                    feeCustodyTokenAccount: rewardCustodyConfig.tokenAccount,
                                    program: this.program.programId,
                                    systemProgram: web3_js_1.SystemProgram.programId,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    receivingMint: rewardCustodyMint,
                                })
                                    .remainingAccounts(__spreadArray([], tokenStakeAccounts, true))
                                    .instruction()];
                        case 4:
                            withdrawStakeInstruction = _b.sent();
                            instructions.push(withdrawStakeInstruction);
                            return [3, 6];
                        case 5:
                            err_17 = _b.sent();
                            console.log("perpClient withdrawStake error:: ", err_17);
                            throw err_17;
                        case 6: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.addCompoundingLiquidity = function (amountIn_1, minCompoundingAmountOut_1, inTokenSymbol_1, rewardTokenMint_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 5; _i < arguments.length; _i++) {
                args_1[_i - 5] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([amountIn_1, minCompoundingAmountOut_1, inTokenSymbol_1, rewardTokenMint_1, poolConfig_1], args_1, true), void 0, function (amountIn, minCompoundingAmountOut, inTokenSymbol, rewardTokenMint, poolConfig, skipBalanceChecks, ephemeralSignerPubkey, userPublicKey) {
                var publicKey, preInstructions, instructions, additionalSigners, postInstructions, rewardCustody, inCustodyConfig, lpTokenMint, compoundingTokenMint, wrappedSolAccount, lpTokenAccount, compoundingTokenAccount, fundingAccount, custodyAccountMetas, custodyOracleAccountMetas, markets, _a, _b, custody, _c, _d, market, lamports, unWrappedSolBalance, _e, addCompoundingLiquidity, err_18;
                if (skipBalanceChecks === void 0) { skipBalanceChecks = false; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                if (userPublicKey === void 0) { userPublicKey = undefined; }
                return __generator(this, function (_f) {
                    switch (_f.label) {
                        case 0:
                            publicKey = userPublicKey !== null && userPublicKey !== void 0 ? userPublicKey : this.provider.wallet.publicKey;
                            preInstructions = [];
                            instructions = [];
                            additionalSigners = [];
                            postInstructions = [];
                            rewardCustody = poolConfig.custodies.find(function (f) { return f.symbol == 'USDC'; });
                            inCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(inTokenSymbol).mintKey); });
                            lpTokenMint = poolConfig.stakedLpTokenMint;
                            compoundingTokenMint = poolConfig.compoundingTokenMint;
                            lpTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.stakedLpTokenMint, publicKey, true);
                            compoundingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(compoundingTokenMint, publicKey, true);
                            fundingAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(inCustodyConfig.mintKey, publicKey, true, poolConfig.getTokenFromSymbol(inTokenSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            custodyAccountMetas = [];
                            custodyOracleAccountMetas = [];
                            markets = [];
                            for (_a = 0, _b = poolConfig.custodies; _a < _b.length; _a++) {
                                custody = _b[_a];
                                custodyAccountMetas.push({
                                    pubkey: custody.custodyAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                                custodyOracleAccountMetas.push({
                                    pubkey: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            for (_c = 0, _d = poolConfig.markets; _c < _d.length; _c++) {
                                market = _d[_c];
                                markets.push({
                                    pubkey: market.marketAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            return [4, (0, utils_1.checkIfAccountExists)(lpTokenAccount, this.provider.connection)];
                        case 1:
                            if (!(_f.sent())) {
                                instructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, lpTokenAccount, publicKey, poolConfig.stakedLpTokenMint));
                            }
                            return [4, (0, utils_1.checkIfAccountExists)(compoundingTokenAccount, this.provider.connection)];
                        case 2:
                            if (!(_f.sent())) {
                                instructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, compoundingTokenAccount, publicKey, poolConfig.compoundingTokenMint));
                            }
                            if (!(inTokenSymbol == 'SOL')) return [3, 5];
                            console.log("inTokenSymbol === SOL", inTokenSymbol);
                            lamports = amountIn.add(new anchor_1.BN(this.minimumBalanceForRentExemptAccountLamports));
                            if (!!skipBalanceChecks) return [3, 4];
                            _e = anchor_1.BN.bind;
                            return [4, this.provider.connection.getBalance(publicKey)];
                        case 3:
                            unWrappedSolBalance = new (_e.apply(anchor_1.BN, [void 0, _f.sent()]))();
                            if (unWrappedSolBalance.lt(lamports)) {
                                throw "Insufficient SOL Funds";
                            }
                            _f.label = 4;
                        case 4:
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports.toNumber(),
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 7];
                        case 5:
                            if (!!skipBalanceChecks) return [3, 7];
                            return [4, (0, utils_1.checkIfAccountExists)(fundingAccount, this.provider.connection)];
                        case 6:
                            if (!(_f.sent())) {
                                throw "Insufficient Funds , token Account doesn't exist";
                            }
                            _f.label = 7;
                        case 7:
                            _f.trys.push([7, 9, , 10]);
                            return [4, this.program.methods
                                    .addCompoundingLiquidity({
                                    amountIn: amountIn,
                                    minCompoundingAmountOut: minCompoundingAmountOut
                                })
                                    .accounts({
                                    owner: publicKey,
                                    fundingAccount: inTokenSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : fundingAccount,
                                    compoundingTokenAccount: compoundingTokenAccount,
                                    poolCompoundingLpVault: poolConfig.compoundingLpVault,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    inCustody: inCustodyConfig.custodyAccount,
                                    inCustodyOracleAccount: this.useExtOracleAccount ? inCustodyConfig.extOracleAccount : inCustodyConfig.intOracleAccount,
                                    inCustodyTokenAccount: inCustodyConfig.tokenAccount,
                                    rewardCustody: rewardCustody.custodyAccount,
                                    rewardCustodyOracleAccount: this.useExtOracleAccount ? rewardCustody.extOracleAccount : rewardCustody.intOracleAccount,
                                    lpTokenMint: lpTokenMint,
                                    compoundingTokenMint: compoundingTokenMint,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.program.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    fundingMint: inCustodyConfig.mintKey,
                                    fundingTokenProgram: poolConfig.getTokenFromSymbol(inTokenSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                })
                                    .remainingAccounts(__spreadArray(__spreadArray(__spreadArray([], custodyAccountMetas, true), custodyOracleAccountMetas, true), markets, true))
                                    .instruction()];
                        case 8:
                            addCompoundingLiquidity = _f.sent();
                            instructions.push(addCompoundingLiquidity);
                            return [3, 10];
                        case 9:
                            err_18 = _f.sent();
                            console.log("perpClient addCompoundingLiquidity error:: ", err_18);
                            return [3, 10];
                        case 10: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.removeCompoundingLiquidity = function (compoundingAmountIn_1, minAmountOut_1, outTokenSymbol_1, rewardTokenMint_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 5; _i < arguments.length; _i++) {
                args_1[_i - 5] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([compoundingAmountIn_1, minAmountOut_1, outTokenSymbol_1, rewardTokenMint_1, poolConfig_1], args_1, true), void 0, function (compoundingAmountIn, minAmountOut, outTokenSymbol, rewardTokenMint, poolConfig, createUserATA, ephemeralSignerPubkey, userPublicKey) {
                var publicKey, userReceivingTokenAccount, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, rewardCustody, outCustodyConfig, lpTokenMint, compoundingTokenMint, lamports, _a, custodyAccountMetas, custodyOracleAccountMetas, markets, _b, _c, custody, _d, _e, market, compoundingTokenAccount, removeCompoundingLiquidity, err_19;
                if (createUserATA === void 0) { createUserATA = true; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                if (userPublicKey === void 0) { userPublicKey = undefined; }
                return __generator(this, function (_f) {
                    switch (_f.label) {
                        case 0:
                            publicKey = userPublicKey !== null && userPublicKey !== void 0 ? userPublicKey : this.provider.wallet.publicKey;
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            rewardCustody = poolConfig.custodies.find(function (f) { return f.symbol == 'USDC'; });
                            outCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(outTokenSymbol).mintKey); });
                            lpTokenMint = poolConfig.stakedLpTokenMint;
                            compoundingTokenMint = poolConfig.compoundingTokenMint;
                            if (!(outCustodyConfig.symbol == 'SOL')) return [3, 1];
                            lamports = this.minimumBalanceForRentExemptAccountLamports;
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports,
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 4];
                        case 1:
                            userReceivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(outCustodyConfig.mintKey, publicKey, true, poolConfig.getTokenFromSymbol(outTokenSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            _a = createUserATA;
                            if (!_a) return [3, 3];
                            return [4, (0, utils_1.checkIfAccountExists)(userReceivingTokenAccount, this.provider.connection)];
                        case 2:
                            _a = !(_f.sent());
                            _f.label = 3;
                        case 3:
                            if (_a) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userReceivingTokenAccount, publicKey, outCustodyConfig.mintKey, poolConfig.getTokenFromSymbol(outTokenSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            _f.label = 4;
                        case 4:
                            custodyAccountMetas = [];
                            custodyOracleAccountMetas = [];
                            markets = [];
                            for (_b = 0, _c = poolConfig.custodies; _b < _c.length; _b++) {
                                custody = _c[_b];
                                custodyAccountMetas.push({
                                    pubkey: custody.custodyAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                                custodyOracleAccountMetas.push({
                                    pubkey: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            for (_d = 0, _e = poolConfig.markets; _d < _e.length; _d++) {
                                market = _e[_d];
                                markets.push({
                                    pubkey: market.marketAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            compoundingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(compoundingTokenMint, publicKey, true);
                            _f.label = 5;
                        case 5:
                            _f.trys.push([5, 7, , 8]);
                            return [4, this.program.methods
                                    .removeCompoundingLiquidity({
                                    compoundingAmountIn: compoundingAmountIn,
                                    minAmountOut: minAmountOut
                                })
                                    .accounts({
                                    owner: publicKey,
                                    receivingAccount: outCustodyConfig.symbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userReceivingTokenAccount,
                                    compoundingTokenAccount: compoundingTokenAccount,
                                    poolCompoundingLpVault: poolConfig.compoundingLpVault,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    outCustody: outCustodyConfig.custodyAccount,
                                    outCustodyOracleAccount: this.useExtOracleAccount ? outCustodyConfig.extOracleAccount : outCustodyConfig.intOracleAccount,
                                    outCustodyTokenAccount: outCustodyConfig.tokenAccount,
                                    rewardCustody: rewardCustody.custodyAccount,
                                    rewardCustodyOracleAccount: this.useExtOracleAccount ? rewardCustody.extOracleAccount : rewardCustody.intOracleAccount,
                                    lpTokenMint: lpTokenMint,
                                    compoundingTokenMint: compoundingTokenMint,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.program.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    receivingMint: outCustodyConfig.mintKey,
                                    receivingTokenProgram: poolConfig.getTokenFromSymbol(outTokenSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID
                                })
                                    .remainingAccounts(__spreadArray(__spreadArray(__spreadArray([], custodyAccountMetas, true), custodyOracleAccountMetas, true), markets, true))
                                    .instruction()];
                        case 6:
                            removeCompoundingLiquidity = _f.sent();
                            instructions.push(removeCompoundingLiquidity);
                            return [3, 8];
                        case 7:
                            err_19 = _f.sent();
                            console.log("perpClient removeCompoundingLiquidity error:: ", err_19);
                            return [3, 8];
                        case 8: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.migrateStake = function (amount_1, rewardTokenMint_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 3; _i < arguments.length; _i++) {
                args_1[_i - 3] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([amount_1, rewardTokenMint_1, poolConfig_1], args_1, true), void 0, function (amount, rewardTokenMint, poolConfig, createUserATA) {
                var publicKey, preInstructions, instructions, postInstructions, additionalSigners, rewardCustody, lpTokenMint, compoundingTokenMint, compoudingTokenAccount, _a, flpStakeAccount, tokenStakeAccount, tokenStakeAccounts, _b, poolStakedLpVault, custodyAccountMetas, custodyOracleAccountMetas, markets, _c, _d, custody, _e, _f, market, migrateStake, err_20;
                if (createUserATA === void 0) { createUserATA = true; }
                return __generator(this, function (_g) {
                    switch (_g.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            rewardCustody = poolConfig.custodies.find(function (f) { return f.symbol == 'USDC'; });
                            lpTokenMint = poolConfig.stakedLpTokenMint;
                            compoundingTokenMint = poolConfig.compoundingTokenMint;
                            compoudingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(compoundingTokenMint, publicKey, true);
                            _a = createUserATA;
                            if (!_a) return [3, 2];
                            return [4, (0, utils_1.checkIfAccountExists)(compoudingTokenAccount, this.provider.connection)];
                        case 1:
                            _a = !(_g.sent());
                            _g.label = 2;
                        case 2:
                            if (_a) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, compoudingTokenAccount, publicKey, compoundingTokenMint));
                            }
                            flpStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("stake"), publicKey.toBuffer(), poolConfig.poolAddress.toBuffer()], this.programId)[0];
                            tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("token_stake"), publicKey.toBuffer()], this.programId)[0];
                            tokenStakeAccounts = [];
                            _b = tokenStakeAccount;
                            if (!_b) return [3, 4];
                            return [4, (0, utils_1.checkIfAccountExists)(tokenStakeAccount, this.provider.connection)];
                        case 3:
                            _b = (_g.sent());
                            _g.label = 4;
                        case 4:
                            if (_b) {
                                tokenStakeAccounts.push({
                                    pubkey: tokenStakeAccount,
                                    isSigner: false,
                                    isWritable: true,
                                });
                            }
                            poolStakedLpVault = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("staked_lp_token_account"), poolConfig.poolAddress.toBuffer(), lpTokenMint.toBuffer()], this.programId)[0];
                            custodyAccountMetas = [];
                            custodyOracleAccountMetas = [];
                            markets = [];
                            for (_c = 0, _d = poolConfig.custodies; _c < _d.length; _c++) {
                                custody = _d[_c];
                                custodyAccountMetas.push({
                                    pubkey: custody.custodyAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                                custodyOracleAccountMetas.push({
                                    pubkey: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            for (_e = 0, _f = poolConfig.markets; _e < _f.length; _e++) {
                                market = _f[_e];
                                markets.push({
                                    pubkey: market.marketAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            _g.label = 5;
                        case 5:
                            _g.trys.push([5, 7, , 8]);
                            return [4, this.program.methods
                                    .migrateStake({
                                    amount: amount
                                })
                                    .accounts({
                                    owner: publicKey,
                                    compoundingTokenAccount: compoudingTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    flpStakeAccount: flpStakeAccount,
                                    rewardCustody: rewardCustody.custodyAccount,
                                    rewardCustodyOracleAccount: this.useExtOracleAccount ? rewardCustody.extOracleAccount : rewardCustody.intOracleAccount,
                                    poolStakedLpVault: poolStakedLpVault,
                                    poolCompoundingLpVault: poolConfig.compoundingLpVault,
                                    lpTokenMint: lpTokenMint,
                                    compoundingTokenMint: compoundingTokenMint,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.program.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                                })
                                    .remainingAccounts(__spreadArray(__spreadArray(__spreadArray(__spreadArray([], custodyAccountMetas, true), custodyOracleAccountMetas, true), markets, true), tokenStakeAccounts, true))
                                    .instruction()];
                        case 6:
                            migrateStake = _g.sent();
                            instructions.push(migrateStake);
                            return [3, 8];
                        case 7:
                            err_20 = _g.sent();
                            console.log("perpClient migrateStake error:: ", err_20);
                            return [3, 8];
                        case 8: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.migrateFlp = function (amount, rewardTokenMint, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, rewardCustody, lpTokenMint, compoundingTokenMint, compoudingTokenAccount, flpStakeAccount, poolStakedLpVault, custodyAccountMetas, custodyOracleAccountMetas, markets, _i, _a, custody, _b, _c, market, migrateFlp, err_21;
            return __generator(this, function (_d) {
                switch (_d.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        rewardCustody = poolConfig.custodies.find(function (f) { return f.symbol == 'USDC'; });
                        lpTokenMint = poolConfig.stakedLpTokenMint;
                        compoundingTokenMint = poolConfig.compoundingTokenMint;
                        compoudingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(compoundingTokenMint, publicKey, true);
                        flpStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("stake"), publicKey.toBuffer(), poolConfig.poolAddress.toBuffer()], this.programId)[0];
                        poolStakedLpVault = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("staked_lp_token_account"), poolConfig.poolAddress.toBuffer(), lpTokenMint.toBuffer()], this.programId)[0];
                        custodyAccountMetas = [];
                        custodyOracleAccountMetas = [];
                        markets = [];
                        for (_i = 0, _a = poolConfig.custodies; _i < _a.length; _i++) {
                            custody = _a[_i];
                            custodyAccountMetas.push({
                                pubkey: custody.custodyAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                            custodyOracleAccountMetas.push({
                                pubkey: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        for (_b = 0, _c = poolConfig.markets; _b < _c.length; _b++) {
                            market = _c[_b];
                            markets.push({
                                pubkey: market.marketAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        _d.label = 1;
                    case 1:
                        _d.trys.push([1, 3, , 4]);
                        return [4, this.program.methods
                                .migrateFlp({
                                compoundingTokenAmount: amount
                            })
                                .accounts({
                                owner: publicKey,
                                compoundingTokenAccount: compoudingTokenAccount,
                                transferAuthority: poolConfig.transferAuthority,
                                perpetuals: poolConfig.perpetuals,
                                pool: poolConfig.poolAddress,
                                flpStakeAccount: flpStakeAccount,
                                rewardCustody: rewardCustody.custodyAccount,
                                rewardCustodyOracleAccount: this.useExtOracleAccount ? rewardCustody.extOracleAccount : rewardCustody.intOracleAccount,
                                poolStakedLpVault: poolStakedLpVault,
                                poolCompoundingLpVault: poolConfig.compoundingLpVault,
                                lpTokenMint: lpTokenMint,
                                compoundingTokenMint: compoundingTokenMint,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.program.programId,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                            })
                                .remainingAccounts(__spreadArray(__spreadArray(__spreadArray([], custodyAccountMetas, true), custodyOracleAccountMetas, true), markets, true))
                                .instruction()];
                    case 2:
                        migrateFlp = _d.sent();
                        instructions.push(migrateFlp);
                        return [3, 4];
                    case 3:
                        err_21 = _d.sent();
                        console.log("perpClient migrateFlp error:: ", err_21);
                        return [3, 4];
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.compoundingFee = function (poolConfig_1) {
            var args_1 = [];
            for (var _i = 1; _i < arguments.length; _i++) {
                args_1[_i - 1] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([poolConfig_1], args_1, true), void 0, function (poolConfig, rewardTokenSymbol) {
                var instructions, additionalSigners, rewardCustody, lpTokenMint, custodyAccountMetas, custodyOracleAccountMetas, markets, _a, _b, custody, _c, _d, market, compoundingFee, err_22;
                if (rewardTokenSymbol === void 0) { rewardTokenSymbol = 'USDC'; }
                return __generator(this, function (_e) {
                    switch (_e.label) {
                        case 0:
                            instructions = [];
                            additionalSigners = [];
                            rewardCustody = poolConfig.custodies.find(function (f) { return f.symbol == 'USDC'; });
                            lpTokenMint = poolConfig.stakedLpTokenMint;
                            custodyAccountMetas = [];
                            custodyOracleAccountMetas = [];
                            markets = [];
                            for (_a = 0, _b = poolConfig.custodies; _a < _b.length; _a++) {
                                custody = _b[_a];
                                custodyAccountMetas.push({
                                    pubkey: custody.custodyAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                                custodyOracleAccountMetas.push({
                                    pubkey: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            for (_c = 0, _d = poolConfig.markets; _c < _d.length; _c++) {
                                market = _d[_c];
                                markets.push({
                                    pubkey: market.marketAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            _e.label = 1;
                        case 1:
                            _e.trys.push([1, 3, , 4]);
                            return [4, this.program.methods
                                    .compoundFees({})
                                    .accounts({
                                    poolCompoundingLpVault: poolConfig.compoundingLpVault,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    rewardCustody: rewardCustody.custodyAccount,
                                    rewardCustodyOracleAccount: this.useExtOracleAccount ? rewardCustody.extOracleAccount : rewardCustody.intOracleAccount,
                                    lpTokenMint: lpTokenMint,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.program.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                                })
                                    .remainingAccounts(__spreadArray(__spreadArray(__spreadArray([], custodyAccountMetas, true), custodyOracleAccountMetas, true), markets, true))
                                    .instruction()];
                        case 2:
                            compoundingFee = _e.sent();
                            instructions.push(compoundingFee);
                            return [3, 4];
                        case 3:
                            err_22 = _e.sent();
                            console.log("perpClient compoundingFee error:: ", err_22);
                            return [3, 4];
                        case 4: return [2, {
                                instructions: __spreadArray([], instructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.burnAndClaim = function (owner, nftMint, poolConfig, createAta) { return __awaiter(_this, void 0, void 0, function () {
            var preInstructions, instructions, postInstructions, additionalSigners, userTokenAccount, _a, nftTokenAccount, nftTradingAccount, metadataAccount, collectionMetadata, edition, tokenRecord, burnAndClaimInstruction, err_23;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _b.label = 1;
                    case 1:
                        _b.trys.push([1, 7, , 8]);
                        return [4, (0, spl_token_1.getAssociatedTokenAddress)(poolConfig.tokenMint, owner, true)];
                    case 2:
                        userTokenAccount = _b.sent();
                        _a = createAta;
                        if (!_a) return [3, 4];
                        return [4, (0, utils_1.checkIfAccountExists)(userTokenAccount, this.provider.connection)];
                    case 3:
                        _a = !(_b.sent());
                        _b.label = 4;
                    case 4:
                        if (_a) {
                            preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(owner, userTokenAccount, owner, poolConfig.tokenMint));
                        }
                        return [4, (0, spl_token_1.getAssociatedTokenAddress)(nftMint, owner, true)];
                    case 5:
                        nftTokenAccount = _b.sent();
                        nftTradingAccount = web3_js_1.PublicKey.findProgramAddressSync([
                            Buffer.from("trading"),
                            nftMint.toBuffer(),
                        ], this.programId)[0];
                        metadataAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("metadata"), constants_1.METAPLEX_PROGRAM_ID.toBuffer(), nftMint.toBuffer()], constants_1.METAPLEX_PROGRAM_ID)[0];
                        collectionMetadata = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("metadata"), constants_1.METAPLEX_PROGRAM_ID.toBuffer(), poolConfig.nftCollectionAddress.toBuffer()], constants_1.METAPLEX_PROGRAM_ID)[0];
                        edition = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("metadata"), constants_1.METAPLEX_PROGRAM_ID.toBuffer(), nftMint.toBuffer(), Buffer.from("edition")], constants_1.METAPLEX_PROGRAM_ID)[0];
                        tokenRecord = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("metadata"), constants_1.METAPLEX_PROGRAM_ID.toBuffer(), nftMint.toBuffer(), Buffer.from("token_record"), nftTokenAccount.toBuffer()], constants_1.METAPLEX_PROGRAM_ID)[0];
                        return [4, this.program.methods
                                .burnAndClaim({})
                                .accounts({
                                owner: owner,
                                receivingTokenAccount: userTokenAccount,
                                perpetuals: this.perpetuals.publicKey,
                                tokenVault: poolConfig.tokenVault,
                                tokenVaultTokenAccount: poolConfig.tokenVaultTokenAccount,
                                metadataAccount: metadataAccount,
                                collectionMetadata: collectionMetadata,
                                edition: edition,
                                tokenRecord: tokenRecord,
                                tradingAccount: nftTradingAccount,
                                transferAuthority: poolConfig.transferAuthority,
                                metadataProgram: constants_1.METAPLEX_PROGRAM_ID,
                                nftMint: nftMint,
                                nftTokenAccount: nftTokenAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId,
                                receivingTokenMint: poolConfig.tokenMint,
                            })
                                .instruction()];
                    case 6:
                        burnAndClaimInstruction = _b.sent();
                        instructions.push(burnAndClaimInstruction);
                        return [3, 8];
                    case 7:
                        err_23 = _b.sent();
                        console.log("perpClient burnAndClaimInstruction error:: ", err_23);
                        throw err_23;
                    case 8: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.burnAndStake = function (owner, feePayer, nftMint, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var preInstructions, instructions, postInstructions, additionalSigners, tokenStakeAccount, nftTokenAccount, nftTradingAccount, metadataAccount, collectionMetadata, edition, tokenRecord, burnAndStakeInstruction, err_24;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("token_stake"), owner.toBuffer()], this.programId)[0];
                        nftTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(nftMint, owner, true);
                        nftTradingAccount = web3_js_1.PublicKey.findProgramAddressSync([
                            Buffer.from("trading"),
                            nftMint.toBuffer(),
                        ], this.programId)[0];
                        metadataAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("metadata"), constants_1.METAPLEX_PROGRAM_ID.toBuffer(), nftMint.toBuffer()], constants_1.METAPLEX_PROGRAM_ID)[0];
                        collectionMetadata = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("metadata"), constants_1.METAPLEX_PROGRAM_ID.toBuffer(), poolConfig.nftCollectionAddress.toBuffer()], constants_1.METAPLEX_PROGRAM_ID)[0];
                        edition = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("metadata"), constants_1.METAPLEX_PROGRAM_ID.toBuffer(), nftMint.toBuffer(), Buffer.from("edition")], constants_1.METAPLEX_PROGRAM_ID)[0];
                        tokenRecord = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("metadata"), constants_1.METAPLEX_PROGRAM_ID.toBuffer(), nftMint.toBuffer(), Buffer.from("token_record"), nftTokenAccount.toBuffer()], constants_1.METAPLEX_PROGRAM_ID)[0];
                        return [4, this.program.methods
                                .burnAndStake({})
                                .accounts({
                                owner: owner,
                                feePayer: feePayer,
                                perpetuals: this.perpetuals.publicKey,
                                tokenVault: poolConfig.tokenVault,
                                tokenVaultTokenAccount: poolConfig.tokenVaultTokenAccount,
                                tokenStakeAccount: tokenStakeAccount,
                                metadataAccount: metadataAccount,
                                collectionMetadata: collectionMetadata,
                                edition: edition,
                                tokenRecord: tokenRecord,
                                tradingAccount: nftTradingAccount,
                                transferAuthority: poolConfig.transferAuthority,
                                metadataProgram: constants_1.METAPLEX_PROGRAM_ID,
                                nftMint: nftMint,
                                nftTokenAccount: nftTokenAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId
                            })
                                .instruction()];
                    case 2:
                        burnAndStakeInstruction = _a.sent();
                        instructions.push(burnAndStakeInstruction);
                        return [3, 4];
                    case 3:
                        err_24 = _a.sent();
                        console.log("perpClient burnAndStakeInstruction error:: ", err_24);
                        throw err_24;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.depositTokenStake = function (owner, feePayer, depositAmount, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var preInstructions, instructions, postInstructions, additionalSigners, tokenStakeAccount, userTokenAccount, depositTokenStakeInstruction, err_25;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 4, , 5]);
                        tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("token_stake"), owner.toBuffer()], this.programId)[0];
                        userTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.tokenMint, owner, true);
                        return [4, (0, utils_1.checkIfAccountExists)(userTokenAccount, this.provider.connection)];
                    case 2:
                        if (!(_a.sent())) {
                            preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(feePayer, userTokenAccount, owner, poolConfig.tokenMint));
                        }
                        return [4, this.program.methods
                                .depositTokenStake({
                                depositAmount: depositAmount
                            })
                                .accounts({
                                owner: owner,
                                feePayer: feePayer,
                                fundingTokenAccount: userTokenAccount,
                                perpetuals: this.perpetuals.publicKey,
                                tokenVault: poolConfig.tokenVault,
                                tokenVaultTokenAccount: poolConfig.tokenVaultTokenAccount,
                                tokenStakeAccount: tokenStakeAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId,
                                tokenMint: poolConfig.tokenMint,
                            })
                                .instruction()];
                    case 3:
                        depositTokenStakeInstruction = _a.sent();
                        instructions.push(depositTokenStakeInstruction);
                        return [3, 5];
                    case 4:
                        err_25 = _a.sent();
                        console.log("perpClient depositStakingInstruction error:: ", err_25);
                        throw err_25;
                    case 5: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.unstakeTokenRequest = function (owner, unstakeAmount, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var preInstructions, instructions, postInstructions, additionalSigners, tokenStakeAccount, unstakeTokenRequestInstruction, err_26;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("token_stake"), owner.toBuffer()], this.programId)[0];
                        return [4, this.program.methods
                                .unstakeTokenRequest({
                                unstakeAmount: unstakeAmount
                            })
                                .accounts({
                                owner: owner,
                                tokenVault: poolConfig.tokenVault,
                                tokenStakeAccount: tokenStakeAccount,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId
                            })
                                .instruction()];
                    case 2:
                        unstakeTokenRequestInstruction = _a.sent();
                        instructions.push(unstakeTokenRequestInstruction);
                        return [3, 4];
                    case 3:
                        err_26 = _a.sent();
                        console.log("perpClient unstakeTokenRequestInstruction error:: ", err_26);
                        throw err_26;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.unstakeTokenInstant = function (owner, unstakeAmount, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var preInstructions, instructions, postInstructions, additionalSigners, tokenStakeAccount, userTokenAccount, unstakeTokenInstantInstruction, err_27;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 4, , 5]);
                        tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("token_stake"), owner.toBuffer()], this.programId)[0];
                        userTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.tokenMint, owner, true);
                        return [4, (0, utils_1.checkIfAccountExists)(userTokenAccount, this.provider.connection)];
                    case 2:
                        if (!(_a.sent())) {
                            preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(this.provider.wallet.publicKey, userTokenAccount, owner, poolConfig.tokenMint));
                        }
                        return [4, this.program.methods
                                .unstakeTokenInstant({
                                unstakeAmount: unstakeAmount
                            })
                                .accounts({
                                owner: owner,
                                receivingTokenAccount: userTokenAccount,
                                perpetuals: poolConfig.perpetuals,
                                transferAuthority: poolConfig.transferAuthority,
                                tokenVault: poolConfig.tokenVault,
                                tokenVaultTokenAccount: poolConfig.tokenVaultTokenAccount,
                                tokenStakeAccount: tokenStakeAccount,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId,
                                tokenMint: poolConfig.tokenMint,
                            })
                                .instruction()];
                    case 3:
                        unstakeTokenInstantInstruction = _a.sent();
                        instructions.push(unstakeTokenInstantInstruction);
                        return [3, 5];
                    case 4:
                        err_27 = _a.sent();
                        console.log("perpClient unstakeTokenInstantInstruction error:: ", err_27);
                        throw err_27;
                    case 5: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.withdrawToken = function (owner, withdrawRequestId, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var preInstructions, instructions, postInstructions, additionalSigners, tokenStakeAccount, userTokenAccount, withdrawTokenInstruction, err_28;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 4, , 5]);
                        tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("token_stake"), owner.toBuffer()], this.programId)[0];
                        userTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.tokenMint, owner, true);
                        return [4, (0, utils_1.checkIfAccountExists)(userTokenAccount, this.provider.connection)];
                    case 2:
                        if (!(_a.sent())) {
                            preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(this.provider.wallet.publicKey, userTokenAccount, owner, poolConfig.tokenMint));
                        }
                        return [4, this.program.methods
                                .withdrawToken({
                                withdrawRequestId: withdrawRequestId
                            })
                                .accounts({
                                owner: owner,
                                receivingTokenAccount: userTokenAccount,
                                perpetuals: this.perpetuals.publicKey,
                                transferAuthority: poolConfig.transferAuthority,
                                tokenVault: poolConfig.tokenVault,
                                tokenVaultTokenAccount: poolConfig.tokenVaultTokenAccount,
                                tokenStakeAccount: tokenStakeAccount,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId,
                                tokenMint: poolConfig.tokenMint,
                            })
                                .instruction()];
                    case 3:
                        withdrawTokenInstruction = _a.sent();
                        instructions.push(withdrawTokenInstruction);
                        return [3, 5];
                    case 4:
                        err_28 = _a.sent();
                        console.log("perpClient withdrawTokenInstruction error:: ", err_28);
                        throw err_28;
                    case 5: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.cancelUnstakeRequest = function (owner, withdrawRequestId, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var preInstructions, instructions, postInstructions, additionalSigners, tokenStakeAccount, cancelUnstakeRequestInstruction, err_29;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("token_stake"), owner.toBuffer()], this.programId)[0];
                        return [4, this.program.methods
                                .cancelUnstakeTokenRequest({
                                withdrawRequestId: withdrawRequestId
                            })
                                .accounts({
                                owner: owner,
                                tokenVault: poolConfig.tokenVault,
                                tokenStakeAccount: tokenStakeAccount,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId
                            })
                                .instruction()];
                    case 2:
                        cancelUnstakeRequestInstruction = _a.sent();
                        instructions.push(cancelUnstakeRequestInstruction);
                        return [3, 4];
                    case 3:
                        err_29 = _a.sent();
                        console.log("perpClient cancelUnstakeRequestInstruction error:: ", err_29);
                        throw err_29;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.collectTokenReward = function (owner_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 2; _i < arguments.length; _i++) {
                args_1[_i - 2] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([owner_1, poolConfig_1], args_1, true), void 0, function (owner, poolConfig, createUserATA) {
                var publicKey, preInstructions, instructions, postInstructions, additionalSigners, tokenStakeAccount, userTokenAccount, _a, collectTokenRewardInstruction, err_30;
                if (createUserATA === void 0) { createUserATA = true; }
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _b.label = 1;
                        case 1:
                            _b.trys.push([1, 5, , 6]);
                            tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("token_stake"), owner.toBuffer()], this.programId)[0];
                            userTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.tokenMint, owner, true);
                            _a = createUserATA;
                            if (!_a) return [3, 3];
                            return [4, (0, utils_1.checkIfAccountExists)(userTokenAccount, this.provider.connection)];
                        case 2:
                            _a = !(_b.sent());
                            _b.label = 3;
                        case 3:
                            if (_a) {
                                instructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userTokenAccount, publicKey, poolConfig.tokenMint));
                            }
                            return [4, this.program.methods
                                    .collectTokenReward({})
                                    .accounts({
                                    owner: owner,
                                    receivingTokenAccount: userTokenAccount,
                                    perpetuals: this.perpetuals.publicKey,
                                    transferAuthority: poolConfig.transferAuthority,
                                    tokenVault: poolConfig.tokenVault,
                                    tokenVaultTokenAccount: poolConfig.tokenVaultTokenAccount,
                                    tokenStakeAccount: tokenStakeAccount,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    tokenMint: poolConfig.tokenMint,
                                })
                                    .instruction()];
                        case 4:
                            collectTokenRewardInstruction = _b.sent();
                            instructions.push(collectTokenRewardInstruction);
                            return [3, 6];
                        case 5:
                            err_30 = _b.sent();
                            console.log("perpClient collectTokenRewardInstruction error:: ", err_30);
                            throw err_30;
                        case 6: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.collectRevenue = function (owner_1, rewardSymbol_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 3; _i < arguments.length; _i++) {
                args_1[_i - 3] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([owner_1, rewardSymbol_1, poolConfig_1], args_1, true), void 0, function (owner, rewardSymbol, poolConfig, createUserATA) {
                var publicKey, preInstructions, instructions, postInstructions, additionalSigners, rewardCustodyMint, tokenStakeAccount, userTokenAccount, _a, collectRevenueInstruction, err_31;
                if (createUserATA === void 0) { createUserATA = true; }
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _b.label = 1;
                        case 1:
                            _b.trys.push([1, 5, , 6]);
                            rewardCustodyMint = poolConfig.getTokenFromSymbol(rewardSymbol).mintKey;
                            tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("token_stake"), owner.toBuffer()], this.programId)[0];
                            userTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(rewardCustodyMint, owner, true);
                            _a = createUserATA;
                            if (!_a) return [3, 3];
                            return [4, (0, utils_1.checkIfAccountExists)(userTokenAccount, this.provider.connection)];
                        case 2:
                            _a = !(_b.sent());
                            _b.label = 3;
                        case 3:
                            if (_a) {
                                instructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userTokenAccount, publicKey, rewardCustodyMint));
                            }
                            return [4, this.program.methods
                                    .collectRevenue({})
                                    .accounts({
                                    owner: owner,
                                    receivingRevenueAccount: userTokenAccount,
                                    perpetuals: this.perpetuals.publicKey,
                                    transferAuthority: poolConfig.transferAuthority,
                                    tokenVault: poolConfig.tokenVault,
                                    revenueTokenAccount: poolConfig.revenueTokenAccount,
                                    tokenStakeAccount: tokenStakeAccount,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    receivingTokenMint: rewardCustodyMint,
                                })
                                    .instruction()];
                        case 4:
                            collectRevenueInstruction = _b.sent();
                            instructions.push(collectRevenueInstruction);
                            return [3, 6];
                        case 5:
                            err_31 = _b.sent();
                            console.log("perpClient collectRevenueInstruction error:: ", err_31);
                            throw err_31;
                        case 6: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.initRewardVault = function (nftCount, rewardSymbol, collectionMint, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, rewardCustodyMint, instructions, additionalSigners, fbNftProgramData, rewardVault, rewardTokenAccount, nftTransferAuthority, initRewardVault, err_32;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        rewardCustodyMint = poolConfig.getTokenFromSymbol(rewardSymbol).mintKey;
                        instructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        fbNftProgramData = web3_js_1.PublicKey.findProgramAddressSync([this.programFbnftReward.programId.toBuffer()], new web3_js_1.PublicKey("BPFLoaderUpgradeab1e11111111111111111111111"))[0];
                        rewardVault = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("reward_vault")], this.programFbnftReward.programId)[0];
                        rewardTokenAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("reward_token_account")], this.programFbnftReward.programId)[0];
                        nftTransferAuthority = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("transfer_authority")], this.programFbnftReward.programId)[0];
                        return [4, this.programFbnftReward.methods
                                .initRewardVault({
                                nftCount: nftCount
                            })
                                .accounts({
                                admin: publicKey,
                                transferAuthority: nftTransferAuthority,
                                rewardVault: rewardVault,
                                rewardMint: rewardCustodyMint,
                                rewardTokenAccount: rewardTokenAccount,
                                collectionMint: collectionMint,
                                programData: fbNftProgramData,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                rent: web3_js_1.SYSVAR_RENT_PUBKEY
                            })
                                .instruction()];
                    case 2:
                        initRewardVault = _a.sent();
                        instructions.push(initRewardVault);
                        return [3, 4];
                    case 3:
                        err_32 = _a.sent();
                        console.log("perpClient InitRewardVault error:: ", err_32);
                        throw err_32;
                    case 4: return [2, {
                            instructions: __spreadArray([], instructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.distributeReward = function (rewardAmount, rewardSymbol, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, rewardCustodyMint, instructions, additionalSigners, fundingAccount, rewardVault, rewardTokenAccount, distributeReward, err_33;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        rewardCustodyMint = poolConfig.getTokenFromSymbol(rewardSymbol).mintKey;
                        instructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        fundingAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(rewardCustodyMint, publicKey, true);
                        rewardVault = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("reward_vault")], this.programFbnftReward.programId)[0];
                        rewardTokenAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("reward_token_account")], this.programFbnftReward.programId)[0];
                        return [4, this.programFbnftReward.methods
                                .distributeRewards({
                                rewardAmount: rewardAmount
                            })
                                .accounts({
                                admin: publicKey,
                                fundingAccount: fundingAccount,
                                rewardVault: rewardVault,
                                rewardTokenAccount: rewardTokenAccount,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                            })
                                .instruction()];
                    case 2:
                        distributeReward = _a.sent();
                        instructions.push(distributeReward);
                        return [3, 4];
                    case 3:
                        err_33 = _a.sent();
                        console.log("perpClient distributeReward error:: ", err_33);
                        throw err_33;
                    case 4: return [2, {
                            instructions: __spreadArray([], instructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.collectNftReward = function (rewardSymbol_1, poolConfig_1, nftMint_1) {
            var args_1 = [];
            for (var _i = 3; _i < arguments.length; _i++) {
                args_1[_i - 3] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([rewardSymbol_1, poolConfig_1, nftMint_1], args_1, true), void 0, function (rewardSymbol, poolConfig, nftMint, createUserATA) {
                var publicKey, rewardToken, rewardCustodyMint, instructions, additionalSigners, nftTokenAccount, metadataAccount, receivingTokenAccount, _a, rewardRecord, rewardVault, rewardTokenAccount, nftTransferAuthority, collectNftReward, err_34;
                if (createUserATA === void 0) { createUserATA = true; }
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            rewardToken = poolConfig.getTokenFromSymbol(rewardSymbol);
                            rewardCustodyMint = rewardToken.mintKey;
                            instructions = [];
                            additionalSigners = [];
                            _b.label = 1;
                        case 1:
                            _b.trys.push([1, 5, , 6]);
                            nftTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(nftMint, publicKey, true);
                            metadataAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("metadata"), constants_1.METAPLEX_PROGRAM_ID.toBuffer(), nftMint.toBuffer()], constants_1.METAPLEX_PROGRAM_ID)[0];
                            receivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(rewardCustodyMint, publicKey, true, rewardToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            _a = createUserATA;
                            if (!_a) return [3, 3];
                            return [4, (0, utils_1.checkIfAccountExists)(receivingTokenAccount, this.provider.connection)];
                        case 2:
                            _a = !(_b.sent());
                            _b.label = 3;
                        case 3:
                            if (_a) {
                                instructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, receivingTokenAccount, publicKey, rewardCustodyMint, rewardToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            rewardRecord = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("reward_record"), nftMint.toBuffer()], this.programFbnftReward.programId)[0];
                            rewardVault = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("reward_vault")], this.programFbnftReward.programId)[0];
                            rewardTokenAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("reward_token_account")], this.programFbnftReward.programId)[0];
                            nftTransferAuthority = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("transfer_authority")], this.programFbnftReward.programId)[0];
                            return [4, this.programFbnftReward.methods
                                    .collectReward()
                                    .accounts({
                                    owner: publicKey,
                                    feePayer: publicKey,
                                    nftMint: nftMint,
                                    nftTokenAccount: nftTokenAccount,
                                    metadataAccount: metadataAccount,
                                    receivingAccount: receivingTokenAccount,
                                    rewardRecord: rewardRecord,
                                    rewardVault: rewardVault,
                                    rewardTokenAccount: rewardTokenAccount,
                                    transferAuthority: nftTransferAuthority,
                                    systemProgram: web3_js_1.SystemProgram.programId,
                                    tokenProgram: rewardToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                })
                                    .instruction()];
                        case 4:
                            collectNftReward = _b.sent();
                            instructions.push(collectNftReward);
                            return [3, 6];
                        case 5:
                            err_34 = _b.sent();
                            throw err_34;
                        case 6: return [2, {
                                instructions: __spreadArray([], instructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.collectAndDistributeFee = function (rewardSymbol_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 2; _i < arguments.length; _i++) {
                args_1[_i - 2] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([rewardSymbol_1, poolConfig_1], args_1, true), void 0, function (rewardSymbol, poolConfig, createUserATA, nftTradingAccount) {
                var publicKey, rewardToken, rewardCustodyMint, rewardCustodyConfig, preInstructions, instructions, postInstructions, additionalSigners, pool, flpStakeAccount, receivingTokenAccount, _a, tradingAccount, rewardVault, rewardTokenAccount, withdrawStakeInstruction, err_35;
                if (createUserATA === void 0) { createUserATA = true; }
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            rewardToken = poolConfig.getTokenFromSymbol(rewardSymbol);
                            rewardCustodyMint = rewardToken.mintKey;
                            rewardCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(rewardToken.mintKey); });
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _b.label = 1;
                        case 1:
                            _b.trys.push([1, 5, , 6]);
                            pool = poolConfig.poolAddress;
                            flpStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("stake"), publicKey.toBuffer(), pool.toBuffer()], this.program.programId)[0];
                            receivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(rewardCustodyMint, publicKey, true, rewardToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            _a = createUserATA;
                            if (!_a) return [3, 3];
                            return [4, (0, utils_1.checkIfAccountExists)(receivingTokenAccount, this.provider.connection)];
                        case 2:
                            _a = !(_b.sent());
                            _b.label = 3;
                        case 3:
                            if (_a) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, receivingTokenAccount, publicKey, rewardCustodyMint));
                            }
                            tradingAccount = [];
                            if (nftTradingAccount) {
                                tradingAccount.push({
                                    pubkey: nftTradingAccount,
                                    isSigner: false,
                                    isWritable: true,
                                });
                            }
                            rewardVault = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("reward_vault")], this.programFbnftReward.programId)[0];
                            rewardTokenAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("reward_token_account")], this.programFbnftReward.programId)[0];
                            return [4, this.programPerpComposability.methods
                                    .collectAndDistributeFee()
                                    .accounts({
                                    perpProgram: this.programId,
                                    owner: publicKey,
                                    receivingTokenAccount: receivingTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: this.perpetuals.publicKey,
                                    pool: pool,
                                    feeCustody: rewardCustodyConfig.custodyAccount,
                                    flpStakeAccount: flpStakeAccount,
                                    feeCustodyTokenAccount: rewardCustodyConfig.tokenAccount,
                                    systemProgram: web3_js_1.SystemProgram.programId,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    fbnftRewardsProgram: this.programFbnftReward.programId,
                                    rewardVault: rewardVault,
                                    rewardTokenAccount: rewardTokenAccount
                                })
                                    .remainingAccounts(tradingAccount)
                                    .instruction()];
                        case 4:
                            withdrawStakeInstruction = _b.sent();
                            instructions.push(withdrawStakeInstruction);
                            return [3, 6];
                        case 5:
                            err_35 = _b.sent();
                            console.log("perpClient withdrawStake error:: ", err_35);
                            throw err_35;
                        case 6: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.setTriggerPrice = function (targetSymbol, collateralSymbol, side, triggerPrice, isStopLoss, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, targetCustodyConfig, collateralCustodyConfig, marketAccount, positionAccount, instructions, additionalSigners, setTriggerPrice, err_36;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                        collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                        marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                        positionAccount = poolConfig.getPositionFromMarketPk(publicKey, marketAccount);
                        instructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4, this.program.methods
                                .setTriggerPrice({
                                triggerPrice: triggerPrice,
                                isStopLoss: isStopLoss
                            })
                                .accounts({
                                owner: publicKey,
                                perpetuals: this.perpetuals.publicKey,
                                pool: poolConfig.poolAddress,
                                position: positionAccount,
                                market: marketAccount,
                                targetCustody: targetCustodyConfig.custodyAccount,
                                targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                collateralCustody: collateralCustodyConfig.custodyAccount,
                                collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                            })
                                .instruction()];
                    case 2:
                        setTriggerPrice = _a.sent();
                        instructions.push(setTriggerPrice);
                        return [3, 4];
                    case 3:
                        err_36 = _a.sent();
                        console.log("perpClient setTriggerPrice error:: ", err_36);
                        throw err_36;
                    case 4: return [2, {
                            instructions: __spreadArray([], instructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.forceClosePosition = function (positionAccount_2, targetSymbol_1, collateralSymbol_1, side_1, isStopLoss_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 6; _i < arguments.length; _i++) {
                args_1[_i - 6] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([positionAccount_2, targetSymbol_1, collateralSymbol_1, side_1, isStopLoss_1, poolConfig_1], args_1, true), void 0, function (positionAccount, targetSymbol, collateralSymbol, side, isStopLoss, poolConfig, createUserATA, closeUsersWSOLATA, ephemeralSignerPubkey) {
                var payerPubkey, targetCustodyConfig, collateralCustodyConfig, marketAccount, userReceivingTokenAccount, preInstructions, instructions, postInstructions, additionalSigners, _a, forceClosePosition, closeWsolATAIns, err_37;
                if (createUserATA === void 0) { createUserATA = true; }
                if (closeUsersWSOLATA === void 0) { closeUsersWSOLATA = false; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            payerPubkey = this.provider.wallet.publicKey;
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _b.label = 1;
                        case 1:
                            _b.trys.push([1, 5, , 6]);
                            userReceivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey, positionAccount.owner, false, poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            _a = createUserATA;
                            if (!_a) return [3, 3];
                            return [4, (0, utils_1.checkIfAccountExists)(userReceivingTokenAccount, this.provider.connection)];
                        case 2:
                            _a = !(_b.sent());
                            _b.label = 3;
                        case 3:
                            if (_a) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(payerPubkey, userReceivingTokenAccount, positionAccount.owner, poolConfig.getTokenFromSymbol(collateralSymbol).mintKey, poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            return [4, this.program.methods
                                    .forceClosePosition({
                                    privilege: types_1.Privilege.None,
                                    isStopLoss: isStopLoss
                                })
                                    .accounts({
                                    owner: positionAccount.owner,
                                    receivingAccount: userReceivingTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: this.perpetuals.publicKey,
                                    pool: poolConfig.poolAddress,
                                    position: positionAccount.publicKey,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    receivingMint: collateralCustodyConfig.mintKey
                                })
                                    .instruction()];
                        case 4:
                            forceClosePosition = _b.sent();
                            instructions.push(forceClosePosition);
                            if (collateralSymbol == 'WSOL' && closeUsersWSOLATA) {
                                closeWsolATAIns = (0, spl_token_1.createCloseAccountInstruction)(userReceivingTokenAccount, positionAccount.owner, positionAccount.owner);
                                postInstructions.push(closeWsolATAIns);
                            }
                            return [3, 6];
                        case 5:
                            err_37 = _b.sent();
                            console.log("perpClient forceClosePosition error:: ", err_37);
                            throw err_37;
                        case 6: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.placeLimitOrder = function (targetSymbol_1, collateralSymbol_1, reserveSymbol_1, receiveSymbol_1, side_1, limitPrice_1, reserveAmount_1, sizeAmount_1, stopLossPrice_1, takeProfitPrice_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 11; _i < arguments.length; _i++) {
                args_1[_i - 11] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([targetSymbol_1, collateralSymbol_1, reserveSymbol_1, receiveSymbol_1, side_1, limitPrice_1, reserveAmount_1, sizeAmount_1, stopLossPrice_1, takeProfitPrice_1, poolConfig_1], args_1, true), void 0, function (targetSymbol, collateralSymbol, reserveSymbol, receiveSymbol, side, limitPrice, reserveAmount, sizeAmount, stopLossPrice, takeProfitPrice, poolConfig, skipBalanceChecks, ephemeralSignerPubkey) {
                var publicKey, targetCustodyConfig, reserveCustodyConfig, collateralCustodyConfig, receiveCustodyConfig, marketAccount, userReserveTokenAccount, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, accCreationLamports, lamports, unWrappedSolBalance, _a, tokenAccountBalance, _b, positionAccount, orderAccount, placeLimitOrder, err_38;
                if (skipBalanceChecks === void 0) { skipBalanceChecks = false; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                return __generator(this, function (_c) {
                    switch (_c.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                            reserveCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(reserveSymbol).mintKey); });
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                            receiveCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(receiveSymbol).mintKey); });
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            userReserveTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(reserveSymbol).mintKey, publicKey, true, poolConfig.getTokenFromSymbol(reserveSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _c.label = 1;
                        case 1:
                            _c.trys.push([1, 9, , 10]);
                            if (!(reserveSymbol == 'SOL')) return [3, 4];
                            console.log("reserveSymbol === SOL", reserveSymbol);
                            accCreationLamports = this.minimumBalanceForRentExemptAccountLamports;
                            lamports = reserveAmount.add(new anchor_1.BN(accCreationLamports));
                            if (!!skipBalanceChecks) return [3, 3];
                            _a = anchor_1.BN.bind;
                            return [4, this.provider.connection.getBalance(publicKey)];
                        case 2:
                            unWrappedSolBalance = new (_a.apply(anchor_1.BN, [void 0, _c.sent()]))();
                            if (unWrappedSolBalance.lt(lamports)) {
                                throw "Insufficient SOL Funds";
                            }
                            _c.label = 3;
                        case 3:
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports.toNumber(),
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            additionalSigners.push(wrappedSolAccount);
                            return [3, 7];
                        case 4: return [4, (0, utils_1.checkIfAccountExists)(userReserveTokenAccount, this.provider.connection)];
                        case 5:
                            if (!(_c.sent())) {
                                throw "Insufficient Funds , token Account doesn't exist";
                            }
                            if (!!skipBalanceChecks) return [3, 7];
                            _b = anchor_1.BN.bind;
                            return [4, this.provider.connection.getTokenAccountBalance(userReserveTokenAccount)];
                        case 6:
                            tokenAccountBalance = new (_b.apply(anchor_1.BN, [void 0, (_c.sent()).value.amount]))();
                            if (tokenAccountBalance.lt(reserveAmount)) {
                                throw "Insufficient Funds need more ".concat(reserveAmount.sub(tokenAccountBalance), " tokens");
                            }
                            _c.label = 7;
                        case 7:
                            positionAccount = poolConfig.getPositionFromMarketPk(publicKey, marketAccount);
                            orderAccount = poolConfig.getOrderFromMarketPk(publicKey, marketAccount);
                            return [4, this.program.methods
                                    .placeLimitOrder({
                                    limitPrice: limitPrice,
                                    reserveAmount: reserveAmount,
                                    sizeAmount: sizeAmount,
                                    stopLossPrice: stopLossPrice,
                                    takeProfitPrice: takeProfitPrice
                                })
                                    .accounts({
                                    owner: publicKey,
                                    feePayer: publicKey,
                                    fundingAccount: reserveSymbol == 'SOL' ? wrappedSolAccount.publicKey : userReserveTokenAccount,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    position: positionAccount,
                                    order: orderAccount,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    reserveCustody: reserveCustodyConfig.custodyAccount,
                                    reserveOracleAccount: this.useExtOracleAccount ? reserveCustodyConfig.extOracleAccount : reserveCustodyConfig.intOracleAccount,
                                    reserveCustodyTokenAccount: reserveCustodyConfig.tokenAccount,
                                    receiveCustody: receiveCustodyConfig.custodyAccount,
                                    systemProgram: web3_js_1.SystemProgram.programId,
                                    tokenProgram: poolConfig.getTokenFromSymbol(reserveSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    fundingMint: reserveCustodyConfig.mintKey,
                                })
                                    .instruction()];
                        case 8:
                            placeLimitOrder = _c.sent();
                            instructions.push(placeLimitOrder);
                            return [3, 10];
                        case 9:
                            err_38 = _c.sent();
                            console.log("perpClient placeLimitOrder error:: ", err_38);
                            throw err_38;
                        case 10: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.editLimitOrder = function (targetSymbol_1, collateralSymbol_1, reserveSymbol_1, receiveSymbol_1, side_1, orderId_1, limitPrice_1, sizeAmount_1, stopLossPrice_1, takeProfitPrice_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 11; _i < arguments.length; _i++) {
                args_1[_i - 11] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([targetSymbol_1, collateralSymbol_1, reserveSymbol_1, receiveSymbol_1, side_1, orderId_1, limitPrice_1, sizeAmount_1, stopLossPrice_1, takeProfitPrice_1, poolConfig_1], args_1, true), void 0, function (targetSymbol, collateralSymbol, reserveSymbol, receiveSymbol, side, orderId, limitPrice, sizeAmount, stopLossPrice, takeProfitPrice, poolConfig, createUserATA, ephemeralSignerPubkey) {
                var publicKey, targetCustodyConfig, reserveCustodyConfig, collateralCustodyConfig, receiveCustodyConfig, marketAccount, preInstructions, instructions, postInstructions, additionalSigners, wrappedSolAccount, userReceivingTokenAccount, lamports, _a, positionAccount, orderAccount, editLimitOrder, err_39;
                if (createUserATA === void 0) { createUserATA = true; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                            reserveCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(reserveSymbol).mintKey); });
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                            receiveCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(receiveSymbol).mintKey); });
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _b.label = 1;
                        case 1:
                            _b.trys.push([1, 7, , 8]);
                            if (!(reserveSymbol == 'SOL')) return [3, 2];
                            lamports = (this.minimumBalanceForRentExemptAccountLamports);
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports,
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 5];
                        case 2:
                            userReceivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(reserveSymbol).mintKey, publicKey, true, poolConfig.getTokenFromSymbol(reserveSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            _a = createUserATA;
                            if (!_a) return [3, 4];
                            return [4, (0, utils_1.checkIfAccountExists)(userReceivingTokenAccount, this.provider.connection)];
                        case 3:
                            _a = !(_b.sent());
                            _b.label = 4;
                        case 4:
                            if (_a) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userReceivingTokenAccount, publicKey, poolConfig.getTokenFromSymbol(reserveSymbol).mintKey, poolConfig.getTokenFromSymbol(reserveSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            _b.label = 5;
                        case 5:
                            positionAccount = poolConfig.getPositionFromMarketPk(publicKey, marketAccount);
                            orderAccount = poolConfig.getOrderFromMarketPk(publicKey, marketAccount);
                            return [4, this.program.methods
                                    .editLimitOrder({
                                    orderId: orderId,
                                    limitPrice: limitPrice,
                                    sizeAmount: sizeAmount,
                                    stopLossPrice: stopLossPrice,
                                    takeProfitPrice: takeProfitPrice
                                })
                                    .accounts({
                                    owner: publicKey,
                                    feePayer: publicKey,
                                    receivingAccount: reserveSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userReceivingTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    position: positionAccount,
                                    order: orderAccount,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    reserveCustody: reserveCustodyConfig.custodyAccount,
                                    reserveOracleAccount: this.useExtOracleAccount ? reserveCustodyConfig.extOracleAccount : reserveCustodyConfig.intOracleAccount,
                                    reserveCustodyTokenAccount: reserveCustodyConfig.tokenAccount,
                                    receiveCustody: receiveCustodyConfig.custodyAccount,
                                    tokenProgram: poolConfig.getTokenFromSymbol(reserveSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    receivingMint: poolConfig.getTokenFromSymbol(reserveSymbol).mintKey
                                })
                                    .instruction()];
                        case 6:
                            editLimitOrder = _b.sent();
                            instructions.push(editLimitOrder);
                            return [3, 8];
                        case 7:
                            err_39 = _b.sent();
                            console.log("perpClient editLimitOrder error:: ", err_39);
                            throw err_39;
                        case 8: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.executeLimitOrder = function (userPubkey_1, targetSymbol_1, collateralSymbol_1, side_1, orderId_1, poolConfig_1, privilege_1) {
            var args_1 = [];
            for (var _i = 7; _i < arguments.length; _i++) {
                args_1[_i - 7] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([userPubkey_1, targetSymbol_1, collateralSymbol_1, side_1, orderId_1, poolConfig_1, privilege_1], args_1, true), void 0, function (userPubkey, targetSymbol, collateralSymbol, side, orderId, poolConfig, privilege, tokenStakeAccount, userReferralAccount, rebateTokenAccount) {
                var publicKey, targetCustodyConfig, collateralCustodyConfig, marketAccount, preInstructions, instructions, postInstructions, additionalSigners, positionAccount, orderAccount, executeLimitOrder, err_40;
                if (tokenStakeAccount === void 0) { tokenStakeAccount = web3_js_1.PublicKey.default; }
                if (userReferralAccount === void 0) { userReferralAccount = web3_js_1.PublicKey.default; }
                if (rebateTokenAccount === void 0) { rebateTokenAccount = web3_js_1.PublicKey.default; }
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _a.label = 1;
                        case 1:
                            _a.trys.push([1, 3, , 4]);
                            positionAccount = poolConfig.getPositionFromMarketPk(userPubkey, marketAccount);
                            orderAccount = poolConfig.getOrderFromMarketPk(userPubkey, marketAccount);
                            return [4, this.program.methods
                                    .executeLimitOrder({
                                    orderId: orderId,
                                    privilege: privilege
                                })
                                    .accounts({
                                    positionOwner: userPubkey,
                                    feePayer: publicKey,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    position: positionAccount,
                                    order: orderAccount,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    systemProgram: web3_js_1.SystemProgram.programId,
                                    tokenProgram: poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    collateralMint: collateralCustodyConfig.mintKey,
                                })
                                    .remainingAccounts(__spreadArray([], (0, getReferralAccounts_1.getReferralAccounts)(tokenStakeAccount, userReferralAccount, rebateTokenAccount, privilege), true))
                                    .instruction()];
                        case 2:
                            executeLimitOrder = _a.sent();
                            instructions.push(executeLimitOrder);
                            return [3, 4];
                        case 3:
                            err_40 = _a.sent();
                            console.log("perpClient executeLimitOrder error:: ", err_40);
                            throw err_40;
                        case 4: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.executeLimitWithSwap = function (userPubkey_1, targetSymbol_1, collateralSymbol_1, reserveSymbol_1, side_1, orderId_1, poolConfig_1, privilege_1) {
            var args_1 = [];
            for (var _i = 8; _i < arguments.length; _i++) {
                args_1[_i - 8] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([userPubkey_1, targetSymbol_1, collateralSymbol_1, reserveSymbol_1, side_1, orderId_1, poolConfig_1, privilege_1], args_1, true), void 0, function (userPubkey, targetSymbol, collateralSymbol, reserveSymbol, side, orderId, poolConfig, privilege, tokenStakeAccount, userReferralAccount, rebateTokenAccount) {
                var publicKey, targetCustodyConfig, collateralCustodyConfig, reserveCustodyConfig, marketAccount, preInstructions, instructions, postInstructions, additionalSigners, positionAccount, orderAccount, executeLimitWithSwap, err_41;
                if (tokenStakeAccount === void 0) { tokenStakeAccount = web3_js_1.PublicKey.default; }
                if (userReferralAccount === void 0) { userReferralAccount = web3_js_1.PublicKey.default; }
                if (rebateTokenAccount === void 0) { rebateTokenAccount = web3_js_1.PublicKey.default; }
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            publicKey = this.provider.wallet.publicKey;
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                            reserveCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(reserveSymbol).mintKey); });
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _a.label = 1;
                        case 1:
                            _a.trys.push([1, 3, , 4]);
                            positionAccount = poolConfig.getPositionFromMarketPk(userPubkey, marketAccount);
                            orderAccount = poolConfig.getOrderFromMarketPk(userPubkey, marketAccount);
                            return [4, this.program.methods
                                    .executeLimitWithSwap({
                                    orderId: orderId,
                                    privilege: privilege
                                })
                                    .accounts({
                                    positionOwner: userPubkey,
                                    feePayer: publicKey,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    reserveCustody: reserveCustodyConfig.custodyAccount,
                                    reserveCustodyOracleAccount: this.useExtOracleAccount ? reserveCustodyConfig.extOracleAccount : reserveCustodyConfig.intOracleAccount,
                                    position: positionAccount,
                                    order: orderAccount,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    systemProgram: web3_js_1.SystemProgram.programId,
                                    tokenProgram: poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    collateralMint: collateralCustodyConfig.mintKey,
                                })
                                    .remainingAccounts(__spreadArray([], (0, getReferralAccounts_1.getReferralAccounts)(tokenStakeAccount, userReferralAccount, rebateTokenAccount, privilege), true))
                                    .instruction()];
                        case 2:
                            executeLimitWithSwap = _a.sent();
                            instructions.push(executeLimitWithSwap);
                            return [3, 4];
                        case 3:
                            err_41 = _a.sent();
                            console.log("perpClient executeLimitWithSwap error:: ", err_41);
                            throw err_41;
                        case 4: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.placeTriggerOrder = function (targetSymbol, collateralSymbol, receiveSymbol, side, triggerPrice, deltaSizeAmount, isStopLoss, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, targetCustodyConfig, collateralCustodyConfig, receivingCustodyConfig, marketAccount, preInstructions, instructions, postInstructions, additionalSigners, positionAccount, orderAccount, placeTriggerOrder, err_42;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                        collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                        receivingCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(receiveSymbol).mintKey); });
                        marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        positionAccount = poolConfig.getPositionFromMarketPk(publicKey, marketAccount);
                        orderAccount = poolConfig.getOrderFromMarketPk(publicKey, marketAccount);
                        return [4, this.program.methods
                                .placeTriggerOrder({
                                triggerPrice: triggerPrice,
                                deltaSizeAmount: deltaSizeAmount,
                                isStopLoss: isStopLoss
                            })
                                .accounts({
                                owner: publicKey,
                                feePayer: publicKey,
                                perpetuals: poolConfig.perpetuals,
                                pool: poolConfig.poolAddress,
                                position: positionAccount,
                                order: orderAccount,
                                market: marketAccount,
                                targetCustody: targetCustodyConfig.custodyAccount,
                                targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                collateralCustody: collateralCustodyConfig.custodyAccount,
                                collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                receiveCustody: receivingCustodyConfig.custodyAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                            })
                                .instruction()];
                    case 2:
                        placeTriggerOrder = _a.sent();
                        instructions.push(placeTriggerOrder);
                        return [3, 4];
                    case 3:
                        err_42 = _a.sent();
                        console.log("perpClient placeTriggerOrder error:: ", err_42);
                        throw err_42;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.editTriggerOrder = function (targetSymbol, collateralSymbol, receiveSymbol, side, orderId, triggerPrice, deltaSizeAmount, isStopLoss, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, targetCustodyConfig, collateralCustodyConfig, receivingCustodyConfig, marketAccount, preInstructions, instructions, postInstructions, additionalSigners, positionAccount, orderAccount, editTriggerOrder, err_43;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                        collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                        receivingCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(receiveSymbol).mintKey); });
                        marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        positionAccount = poolConfig.getPositionFromMarketPk(publicKey, marketAccount);
                        orderAccount = poolConfig.getOrderFromMarketPk(publicKey, marketAccount);
                        return [4, this.program.methods
                                .editTriggerOrder({
                                orderId: orderId,
                                triggerPrice: triggerPrice,
                                deltaSizeAmount: deltaSizeAmount,
                                isStopLoss: isStopLoss
                            })
                                .accounts({
                                owner: publicKey,
                                perpetuals: poolConfig.perpetuals,
                                pool: poolConfig.poolAddress,
                                position: positionAccount,
                                order: orderAccount,
                                market: marketAccount,
                                targetCustody: targetCustodyConfig.custodyAccount,
                                targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                collateralCustody: collateralCustodyConfig.custodyAccount,
                                collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                receiveCustody: receivingCustodyConfig.custodyAccount,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                            })
                                .instruction()];
                    case 2:
                        editTriggerOrder = _a.sent();
                        instructions.push(editTriggerOrder);
                        return [3, 4];
                    case 3:
                        err_43 = _a.sent();
                        console.log("perpClient editTriggerOrder error:: ", err_43);
                        throw err_43;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.cancelTriggerOrder = function (targetSymbol, collateralSymbol, side, orderId, isStopLoss, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, targetCustodyConfig, collateralCustodyConfig, marketAccount, preInstructions, instructions, postInstructions, additionalSigners, orderAccount, cancelTriggerOrder, err_44;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                        collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                        marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        orderAccount = poolConfig.getOrderFromMarketPk(publicKey, marketAccount);
                        return [4, this.program.methods
                                .cancelTriggerOrder({
                                orderId: orderId,
                                isStopLoss: isStopLoss
                            })
                                .accounts({
                                owner: publicKey,
                                order: orderAccount,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId,
                            })
                                .instruction()];
                    case 2:
                        cancelTriggerOrder = _a.sent();
                        instructions.push(cancelTriggerOrder);
                        return [3, 4];
                    case 3:
                        err_44 = _a.sent();
                        console.log("perpClient cancelTriggerOrder error:: ", err_44);
                        throw err_44;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.cancelAllTriggerOrders = function (targetSymbol, collateralSymbol, side, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, targetCustodyConfig, collateralCustodyConfig, marketAccount, preInstructions, instructions, postInstructions, additionalSigners, orderAccount, positionAccount, cancelAllTriggerOrders, err_45;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                        collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                        marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        orderAccount = poolConfig.getOrderFromMarketPk(publicKey, marketAccount);
                        positionAccount = poolConfig.getPositionFromMarketPk(publicKey, marketAccount);
                        return [4, this.program.methods
                                .cancelAllTriggerOrders()
                                .accounts({
                                position: positionAccount,
                                order: orderAccount,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId,
                            })
                                .instruction()];
                    case 2:
                        cancelAllTriggerOrders = _a.sent();
                        instructions.push(cancelAllTriggerOrders);
                        return [3, 4];
                    case 3:
                        err_45 = _a.sent();
                        console.log("perpClient cancelAllTriggerOrders error:: ", err_45);
                        throw err_45;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.executeTriggerWithSwap = function (owner_1, targetSymbol_1, collateralSymbol_1, receivingSymbol_1, side_1, orderId_1, isStopLoss_1, privilege_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 9; _i < arguments.length; _i++) {
                args_1[_i - 9] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([owner_1, targetSymbol_1, collateralSymbol_1, receivingSymbol_1, side_1, orderId_1, isStopLoss_1, privilege_1, poolConfig_1], args_1, true), void 0, function (owner, targetSymbol, collateralSymbol, receivingSymbol, side, orderId, isStopLoss, privilege, poolConfig, createUserATA, ephemeralSignerPubkey, tokenStakeAccount, userReferralAccount, rebateTokenAccount) {
                var payerPubkey, targetCustodyConfig, collateralCustodyConfig, receivingCustodyConfig, marketAccount, userReceivingTokenAccount, userReceivingTokenAccountCollateral, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, collateralToken, receivingToken, _a, _b, positionAccount, orderAccount, custodyAccountMetas, custodyOracleAccountMetas, _c, _d, custody, executeTriggerWithSwap, err_46;
                if (createUserATA === void 0) { createUserATA = true; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                if (tokenStakeAccount === void 0) { tokenStakeAccount = web3_js_1.PublicKey.default; }
                if (userReferralAccount === void 0) { userReferralAccount = web3_js_1.PublicKey.default; }
                if (rebateTokenAccount === void 0) { rebateTokenAccount = web3_js_1.PublicKey.default; }
                return __generator(this, function (_e) {
                    switch (_e.label) {
                        case 0:
                            payerPubkey = this.provider.wallet.publicKey;
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                            receivingCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(receivingSymbol).mintKey); });
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            collateralToken = poolConfig.getTokenFromSymbol(collateralSymbol);
                            receivingToken = poolConfig.getTokenFromSymbol(receivingSymbol);
                            _e.label = 1;
                        case 1:
                            _e.trys.push([1, 9, , 10]);
                            if (!false) return [3, 2];
                            return [3, 7];
                        case 2:
                            userReceivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(receivingSymbol).mintKey, owner, true, receivingToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            _a = createUserATA;
                            if (!_a) return [3, 4];
                            return [4, (0, utils_1.checkIfAccountExists)(userReceivingTokenAccount, this.provider.connection)];
                        case 3:
                            _a = !(_e.sent());
                            _e.label = 4;
                        case 4:
                            if (_a) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(payerPubkey, userReceivingTokenAccount, owner, poolConfig.getTokenFromSymbol(receivingSymbol).mintKey));
                            }
                            userReceivingTokenAccountCollateral = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey, owner, true, poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            _b = createUserATA;
                            if (!_b) return [3, 6];
                            return [4, (0, utils_1.checkIfAccountExists)(userReceivingTokenAccountCollateral, this.provider.connection)];
                        case 5:
                            _b = !(_e.sent());
                            _e.label = 6;
                        case 6:
                            if (_b) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(payerPubkey, userReceivingTokenAccountCollateral, owner, poolConfig.getTokenFromSymbol(collateralSymbol).mintKey));
                            }
                            _e.label = 7;
                        case 7:
                            positionAccount = poolConfig.getPositionFromMarketPk(owner, marketAccount);
                            orderAccount = poolConfig.getOrderFromMarketPk(owner, marketAccount);
                            custodyAccountMetas = [];
                            custodyOracleAccountMetas = [];
                            for (_c = 0, _d = poolConfig.custodies; _c < _d.length; _c++) {
                                custody = _d[_c];
                                custodyAccountMetas.push({
                                    pubkey: custody.custodyAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                                custodyOracleAccountMetas.push({
                                    pubkey: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            return [4, this.program.methods
                                    .executeTriggerWithSwap({
                                    isStopLoss: isStopLoss,
                                    orderId: orderId,
                                    privilege: privilege
                                })
                                    .accounts({
                                    positionOwner: owner,
                                    feePayer: payerPubkey,
                                    receivingAccount: userReceivingTokenAccount,
                                    collateralAccount: userReceivingTokenAccountCollateral,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    position: positionAccount,
                                    order: orderAccount,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    dispensingCustody: receivingCustodyConfig.custodyAccount,
                                    dispensingOracleAccount: this.useExtOracleAccount ? receivingCustodyConfig.extOracleAccount : receivingCustodyConfig.intOracleAccount,
                                    dispensingCustodyTokenAccount: receivingCustodyConfig.tokenAccount,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    receivingMint: receivingCustodyConfig.mintKey,
                                    receivingTokenProgram: receivingToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    collateralMint: collateralCustodyConfig.mintKey,
                                    collateralTokenProgram: collateralToken.isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID
                                })
                                    .remainingAccounts(__spreadArray([], (0, getReferralAccounts_1.getReferralAccounts)(tokenStakeAccount, userReferralAccount, rebateTokenAccount, privilege), true))
                                    .instruction()];
                        case 8:
                            executeTriggerWithSwap = _e.sent();
                            instructions.push(executeTriggerWithSwap);
                            return [3, 10];
                        case 9:
                            err_46 = _e.sent();
                            console.log("perpClient executeTriggerWithSwap error:: ", err_46);
                            throw err_46;
                        case 10: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.executeTriggerOrder = function (owner_1, targetSymbol_1, collateralSymbol_1, side_1, orderId_1, isStopLoss_1, privilege_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 8; _i < arguments.length; _i++) {
                args_1[_i - 8] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([owner_1, targetSymbol_1, collateralSymbol_1, side_1, orderId_1, isStopLoss_1, privilege_1, poolConfig_1], args_1, true), void 0, function (owner, targetSymbol, collateralSymbol, side, orderId, isStopLoss, privilege, poolConfig, createUserATA, ephemeralSignerPubkey, tokenStakeAccount, userReferralAccount, rebateTokenAccount) {
                var payerPubkey, targetCustodyConfig, collateralCustodyConfig, marketAccount, userReceivingTokenAccount, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, _a, positionAccount, orderAccount, executeTriggerOrder, err_47;
                if (createUserATA === void 0) { createUserATA = true; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                if (tokenStakeAccount === void 0) { tokenStakeAccount = web3_js_1.PublicKey.default; }
                if (userReferralAccount === void 0) { userReferralAccount = web3_js_1.PublicKey.default; }
                if (rebateTokenAccount === void 0) { rebateTokenAccount = web3_js_1.PublicKey.default; }
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            payerPubkey = this.provider.wallet.publicKey;
                            targetCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(targetSymbol).mintKey); });
                            collateralCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey); });
                            marketAccount = poolConfig.getMarketPk(targetCustodyConfig.custodyAccount, collateralCustodyConfig.custodyAccount, side);
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            _b.label = 1;
                        case 1:
                            _b.trys.push([1, 7, , 8]);
                            if (!false) return [3, 2];
                            return [3, 5];
                        case 2:
                            userReceivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(collateralSymbol).mintKey, owner, true, poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            _a = createUserATA;
                            if (!_a) return [3, 4];
                            return [4, (0, utils_1.checkIfAccountExists)(userReceivingTokenAccount, this.provider.connection)];
                        case 3:
                            _a = !(_b.sent());
                            _b.label = 4;
                        case 4:
                            if (_a) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(payerPubkey, userReceivingTokenAccount, owner, poolConfig.getTokenFromSymbol(collateralSymbol).mintKey, poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID));
                            }
                            _b.label = 5;
                        case 5:
                            positionAccount = poolConfig.getPositionFromMarketPk(owner, marketAccount);
                            orderAccount = poolConfig.getOrderFromMarketPk(owner, marketAccount);
                            return [4, this.program.methods
                                    .executeTriggerOrder({
                                    isStopLoss: isStopLoss,
                                    orderId: orderId,
                                    privilege: privilege
                                })
                                    .accounts({
                                    feePayer: payerPubkey,
                                    positionOwner: owner,
                                    receivingAccount: userReceivingTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    position: positionAccount,
                                    order: orderAccount,
                                    market: marketAccount,
                                    targetCustody: targetCustodyConfig.custodyAccount,
                                    targetOracleAccount: this.useExtOracleAccount ? targetCustodyConfig.extOracleAccount : targetCustodyConfig.intOracleAccount,
                                    collateralCustody: collateralCustodyConfig.custodyAccount,
                                    collateralOracleAccount: this.useExtOracleAccount ? collateralCustodyConfig.extOracleAccount : collateralCustodyConfig.intOracleAccount,
                                    collateralCustodyTokenAccount: collateralCustodyConfig.tokenAccount,
                                    tokenProgram: poolConfig.getTokenFromSymbol(collateralSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    receivingMint: collateralCustodyConfig.mintKey
                                })
                                    .remainingAccounts(__spreadArray([], (0, getReferralAccounts_1.getReferralAccounts)(tokenStakeAccount, userReferralAccount, rebateTokenAccount, privilege), true))
                                    .instruction()];
                        case 6:
                            executeTriggerOrder = _b.sent();
                            instructions.push(executeTriggerOrder);
                            return [3, 8];
                        case 7:
                            err_47 = _b.sent();
                            console.log("perpClient executeTriggerOrder error:: ", err_47);
                            throw err_47;
                        case 8: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.migrateTriggerOrder = function (owner, marketAccount, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var payerPubkey, preInstructions, instructions, postInstructions, additionalSigners, positionAccount, orderAccount, migrateTriggerOrder, err_48;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        payerPubkey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        positionAccount = poolConfig.getPositionFromMarketPk(owner, marketAccount);
                        orderAccount = poolConfig.getOrderFromMarketPk(owner, marketAccount);
                        return [4, this.program.methods
                                .migrateTriggerOrder()
                                .accounts({
                                owner: owner,
                                feePayer: payerPubkey,
                                position: positionAccount,
                                order: orderAccount,
                                market: marketAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                            })
                                .instruction()];
                    case 2:
                        migrateTriggerOrder = _a.sent();
                        instructions.push(migrateTriggerOrder);
                        return [3, 4];
                    case 3:
                        err_48 = _a.sent();
                        console.log("perpClient migrateTriggerOrder error:: ", err_48);
                        throw err_48;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.swap = function (userInputTokenSymbol_1, userOutputTokenSymbol_1, amountIn_1, minAmountOut_1, poolConfig_1) {
            var args_1 = [];
            for (var _i = 5; _i < arguments.length; _i++) {
                args_1[_i - 5] = arguments[_i];
            }
            return __awaiter(_this, __spreadArray([userInputTokenSymbol_1, userOutputTokenSymbol_1, amountIn_1, minAmountOut_1, poolConfig_1], args_1, true), void 0, function (userInputTokenSymbol, userOutputTokenSymbol, amountIn, minAmountOut, poolConfig, useFeesPool, createUserATA, unWrapSol, skipBalanceChecks, ephemeralSignerPubkey) {
                var userInputCustodyConfig, userOutputCustodyConfig, publicKey, wrappedSolAccount, preInstructions, instructions, postInstructions, additionalSigners, userOutputTokenAccount, userInputTokenAccount, wsolAssociatedTokenAccount, wsolATAExist, unWrappedSolBalance, _a, wsolAssociatedTokenAccount, closeWsolATAIns, accCreationLamports, lamports, unWrappedSolBalance, _b, tokenAccountBalance, _c, lamports, _d, custodyAccountMetas, custodyOracleAccountMetas, _e, _f, custody, params, inx, closeWsolATAIns, err_49;
                if (useFeesPool === void 0) { useFeesPool = false; }
                if (createUserATA === void 0) { createUserATA = true; }
                if (unWrapSol === void 0) { unWrapSol = false; }
                if (skipBalanceChecks === void 0) { skipBalanceChecks = false; }
                if (ephemeralSignerPubkey === void 0) { ephemeralSignerPubkey = undefined; }
                return __generator(this, function (_g) {
                    switch (_g.label) {
                        case 0:
                            userInputCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(userInputTokenSymbol).mintKey); });
                            if (!userInputCustodyConfig) {
                                throw "userInputCustodyConfig not found";
                            }
                            userOutputCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(userOutputTokenSymbol).mintKey); });
                            if (!userOutputCustodyConfig) {
                                throw "userOutputCustodyConfig not found";
                            }
                            publicKey = this.provider.wallet.publicKey;
                            preInstructions = [];
                            instructions = [];
                            postInstructions = [];
                            additionalSigners = [];
                            if (!(userInputTokenSymbol == 'SOL' && userOutputTokenSymbol == 'WSOL')) return [3, 5];
                            return [4, (0, spl_token_1.getAssociatedTokenAddress)(spl_token_1.NATIVE_MINT, publicKey, true)];
                        case 1:
                            wsolAssociatedTokenAccount = _g.sent();
                            return [4, (0, utils_1.checkIfAccountExists)(wsolAssociatedTokenAccount, this.provider.connection)];
                        case 2:
                            wsolATAExist = _g.sent();
                            if (!wsolATAExist) {
                                instructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, wsolAssociatedTokenAccount, publicKey, spl_token_1.NATIVE_MINT));
                            }
                            if (!!skipBalanceChecks) return [3, 4];
                            _a = anchor_1.BN.bind;
                            return [4, this.provider.connection.getBalance(publicKey)];
                        case 3:
                            unWrappedSolBalance = new (_a.apply(anchor_1.BN, [void 0, _g.sent()]))();
                            if (unWrappedSolBalance.lt(amountIn)) {
                                throw "Insufficient SOL Funds";
                            }
                            _g.label = 4;
                        case 4:
                            instructions.push(web3_js_1.SystemProgram.transfer({
                                fromPubkey: publicKey,
                                toPubkey: wsolAssociatedTokenAccount,
                                lamports: amountIn.toNumber(),
                            }), (0, spl_token_1.createSyncNativeInstruction)(wsolAssociatedTokenAccount));
                            return [2, {
                                    instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                    additionalSigners: additionalSigners
                                }];
                        case 5:
                            if (userInputTokenSymbol == 'WSOL' && userOutputTokenSymbol == 'SOL') {
                                console.log("WSOL=> SOL : NOTE : ONLY WAY IS TO CLOSE THE WSOL ATA and GET ALL SOL ");
                                wsolAssociatedTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(spl_token_1.NATIVE_MINT, publicKey, true);
                                closeWsolATAIns = (0, spl_token_1.createCloseAccountInstruction)(wsolAssociatedTokenAccount, publicKey, publicKey);
                                instructions.push(closeWsolATAIns);
                                return [2, {
                                        instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                        additionalSigners: additionalSigners
                                    }];
                            }
                            _g.label = 6;
                        case 6:
                            _g.trys.push([6, 19, , 20]);
                            if (!(userInputTokenSymbol == 'SOL')) return [3, 9];
                            console.log("userInputTokenSymbol === sol", userInputTokenSymbol);
                            return [4, (0, spl_token_1.getMinimumBalanceForRentExemptAccount)(this.provider.connection)];
                        case 7:
                            accCreationLamports = (_g.sent());
                            console.log("accCreationLamports:", accCreationLamports);
                            lamports = amountIn.add(new anchor_1.BN(accCreationLamports));
                            _b = anchor_1.BN.bind;
                            return [4, this.provider.connection.getBalance(publicKey)];
                        case 8:
                            unWrappedSolBalance = new (_b.apply(anchor_1.BN, [void 0, _g.sent()]))();
                            if (unWrappedSolBalance.lt(amountIn)) {
                                throw "Insufficient SOL Funds";
                            }
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            ;
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports.toNumber(),
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 12];
                        case 9:
                            userInputTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.getTokenFromSymbol(userInputTokenSymbol).mintKey, publicKey, true, poolConfig.getTokenFromSymbol(userInputTokenSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID);
                            return [4, (0, utils_1.checkIfAccountExists)(userInputTokenAccount, this.provider.connection)];
                        case 10:
                            if (!(_g.sent())) {
                                throw "Insufficient Funds , Token Account doesn't exist";
                            }
                            if (!!skipBalanceChecks) return [3, 12];
                            _c = anchor_1.BN.bind;
                            return [4, this.provider.connection.getTokenAccountBalance(userInputTokenAccount)];
                        case 11:
                            tokenAccountBalance = new (_c.apply(anchor_1.BN, [void 0, (_g.sent()).value.amount]))();
                            if (tokenAccountBalance.lt(amountIn)) {
                                throw "Insufficient Funds need more ".concat(amountIn.sub(tokenAccountBalance), " tokens");
                            }
                            _g.label = 12;
                        case 12:
                            if (!(userOutputTokenSymbol == 'SOL')) return [3, 13];
                            lamports = (this.minimumBalanceForRentExemptAccountLamports);
                            if (!ephemeralSignerPubkey) {
                                wrappedSolAccount = new web3_js_1.Keypair();
                                additionalSigners.push(wrappedSolAccount);
                            }
                            ;
                            preInstructions = [
                                web3_js_1.SystemProgram.createAccount({
                                    fromPubkey: publicKey,
                                    newAccountPubkey: (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey),
                                    lamports: lamports,
                                    space: 165,
                                    programId: spl_token_1.TOKEN_PROGRAM_ID,
                                }),
                                (0, spl_token_1.createInitializeAccount3Instruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), spl_token_1.NATIVE_MINT, publicKey),
                            ];
                            postInstructions = [
                                (0, spl_token_1.createCloseAccountInstruction)((ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey), publicKey, publicKey),
                            ];
                            return [3, 17];
                        case 13: return [4, (0, spl_token_1.getAssociatedTokenAddress)(poolConfig.getTokenFromSymbol(userOutputTokenSymbol).mintKey, publicKey, true, poolConfig.getTokenFromSymbol(userOutputTokenSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID)];
                        case 14:
                            userOutputTokenAccount = _g.sent();
                            _d = createUserATA;
                            if (!_d) return [3, 16];
                            return [4, (0, utils_1.checkIfAccountExists)(userOutputTokenAccount, this.provider.connection)];
                        case 15:
                            _d = !(_g.sent());
                            _g.label = 16;
                        case 16:
                            if (_d) {
                                preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, userOutputTokenAccount, publicKey, poolConfig.getTokenFromSymbol(userOutputTokenSymbol).mintKey));
                            }
                            _g.label = 17;
                        case 17:
                            custodyAccountMetas = [];
                            custodyOracleAccountMetas = [];
                            for (_e = 0, _f = poolConfig.custodies; _e < _f.length; _e++) {
                                custody = _f[_e];
                                custodyAccountMetas.push({
                                    pubkey: custody.custodyAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                                custodyOracleAccountMetas.push({
                                    pubkey: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                    isSigner: false,
                                    isWritable: false,
                                });
                            }
                            params = {
                                amountIn: amountIn,
                                minAmountOut: minAmountOut,
                                useFeesPool: useFeesPool
                            };
                            return [4, this.program.methods
                                    .swap(params)
                                    .accounts({
                                    owner: publicKey,
                                    fundingAccount: userInputTokenSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userInputTokenAccount,
                                    receivingAccount: userOutputTokenSymbol == 'SOL' ? (ephemeralSignerPubkey ? ephemeralSignerPubkey : wrappedSolAccount.publicKey) : userOutputTokenAccount,
                                    transferAuthority: poolConfig.transferAuthority,
                                    perpetuals: poolConfig.perpetuals,
                                    pool: poolConfig.poolAddress,
                                    receivingCustody: userInputCustodyConfig.custodyAccount,
                                    receivingCustodyOracleAccount: this.useExtOracleAccount ? userInputCustodyConfig.extOracleAccount : userInputCustodyConfig.intOracleAccount,
                                    receivingCustodyTokenAccount: userInputCustodyConfig.tokenAccount,
                                    dispensingCustody: userOutputCustodyConfig.custodyAccount,
                                    dispensingCustodyOracleAccount: this.useExtOracleAccount ? userOutputCustodyConfig.extOracleAccount : userOutputCustodyConfig.intOracleAccount,
                                    dispensingCustodyTokenAccount: userOutputCustodyConfig.tokenAccount,
                                    eventAuthority: this.eventAuthority.publicKey,
                                    program: this.programId,
                                    ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                    fundingMint: userInputCustodyConfig.mintKey,
                                    fundingTokenProgram: poolConfig.getTokenFromSymbol(userInputTokenSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                    receivingMint: userOutputCustodyConfig.mintKey,
                                    receivingTokenProgram: poolConfig.getTokenFromSymbol(userOutputTokenSymbol).isToken2022 ? spl_token_1.TOKEN_2022_PROGRAM_ID : spl_token_1.TOKEN_PROGRAM_ID,
                                })
                                    .remainingAccounts(__spreadArray(__spreadArray([], custodyAccountMetas, true), custodyOracleAccountMetas, true))
                                    .instruction()];
                        case 18:
                            inx = _g.sent();
                            instructions.push(inx);
                            if (userOutputTokenSymbol == 'SOL' && unWrapSol) {
                                closeWsolATAIns = (0, spl_token_1.createCloseAccountInstruction)(userOutputTokenAccount, publicKey, publicKey);
                                instructions.push(closeWsolATAIns);
                            }
                            return [3, 20];
                        case 19:
                            err_49 = _g.sent();
                            console.error("perpClient Swap error:: ", err_49);
                            throw err_49;
                        case 20: return [2, {
                                instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                                additionalSigners: additionalSigners
                            }];
                    }
                });
            });
        };
        this.swapFeeInternal = function (rewardTokenSymbol, swapTokenSymbol, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var rewardCustody, custody, publicKey, preInstructions, instructions, postInstructions, additionalSigners, custodyAccountMetas, custodyOracleAccountMetas, _i, _a, custody_1, params, inx, err_50;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        rewardCustody = poolConfig.custodies.find(function (f) { return f.symbol == 'USDC'; });
                        if (!rewardCustody) {
                            throw "rewardCustody not found";
                        }
                        custody = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(swapTokenSymbol).mintKey); });
                        if (!custody) {
                            throw "custody not found";
                        }
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _b.label = 1;
                    case 1:
                        _b.trys.push([1, 3, , 4]);
                        custodyAccountMetas = [];
                        custodyOracleAccountMetas = [];
                        for (_i = 0, _a = poolConfig.custodies; _i < _a.length; _i++) {
                            custody_1 = _a[_i];
                            custodyAccountMetas.push({
                                pubkey: custody_1.custodyAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                            custodyOracleAccountMetas.push({
                                pubkey: this.useExtOracleAccount ? custody_1.extOracleAccount : custody_1.intOracleAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        params = {};
                        return [4, this.program.methods
                                .swapFeeInternal(params)
                                .accounts({
                                owner: publicKey,
                                perpetuals: poolConfig.perpetuals,
                                pool: poolConfig.poolAddress,
                                rewardCustody: rewardCustody.custodyAccount,
                                rewardCustodyOracleAccount: this.useExtOracleAccount ? rewardCustody.extOracleAccount : rewardCustody.intOracleAccount,
                                rewardCustodyTokenAccount: rewardCustody.tokenAccount,
                                custody: custody.custodyAccount,
                                custodyOracleAccount: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                custodyTokenAccount: custody.tokenAccount,
                                eventAuthority: this.eventAuthority.publicKey,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                program: this.programId,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY
                            })
                                .remainingAccounts(__spreadArray(__spreadArray([], custodyAccountMetas, true), custodyOracleAccountMetas, true))
                                .instruction()];
                    case 2:
                        inx = _b.sent();
                        instructions.push(inx);
                        return [3, 4];
                    case 3:
                        err_50 = _b.sent();
                        console.error("perpClient Swap error:: ", err_50);
                        throw err_50;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.init = function (admins, config) { return __awaiter(_this, void 0, void 0, function () {
            var perpetualsProgramData, adminMetas, _i, admins_1, admin;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        perpetualsProgramData = web3_js_1.PublicKey.findProgramAddressSync([this.program.programId.toBuffer()], new web3_js_1.PublicKey("BPFLoaderUpgradeab1e11111111111111111111111"))[0];
                        adminMetas = [];
                        for (_i = 0, admins_1 = admins; _i < admins_1.length; _i++) {
                            admin = admins_1[_i];
                            adminMetas.push({
                                isSigner: false,
                                isWritable: false,
                                pubkey: admin,
                            });
                        }
                        return [4, this.program.methods
                                .init(config)
                                .accounts({
                                upgradeAuthority: this.provider.wallet.publicKey,
                                multisig: this.multisig.publicKey,
                                transferAuthority: this.authority.publicKey,
                                perpetuals: this.perpetuals.publicKey,
                                perpetualsProgram: this.program.programId,
                                perpetualsProgramData: perpetualsProgramData,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                            })
                                .remainingAccounts(adminMetas)
                                .rpc()
                                .catch(function (err) {
                                console.error(err);
                                throw err;
                            })];
                    case 1:
                        _a.sent();
                        return [2];
                }
            });
        }); };
        this.setAdminSigners = function (admins, minSignatures) { return __awaiter(_this, void 0, void 0, function () {
            var adminMetas, _i, admins_2, admin, err_51;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        adminMetas = [];
                        for (_i = 0, admins_2 = admins; _i < admins_2.length; _i++) {
                            admin = admins_2[_i];
                            adminMetas.push({
                                isSigner: false,
                                isWritable: false,
                                pubkey: admin,
                            });
                        }
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4, this.program.methods
                                .setAdminSigners({
                                minSignatures: minSignatures,
                            })
                                .accounts({
                                admin: this.admin,
                                multisig: this.multisig.publicKey,
                            })
                                .remainingAccounts(adminMetas)
                                .rpc()];
                    case 2:
                        _a.sent();
                        return [3, 4];
                    case 3:
                        err_51 = _a.sent();
                        if (this.printErrors) {
                            console.error("setAdminSigners err:", err_51);
                        }
                        throw err_51;
                    case 4: return [2];
                }
            });
        }); };
        this.addPool = function (name, maxAumUsd, permissions, metadataSymbol, metadataTitle, metadataUri, stakingFeeShareBps, vpVolumeFactor) { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4, this.program.methods
                            .addPool({
                            name: name,
                            maxAumUsd: maxAumUsd,
                            permissions: permissions,
                            metadataSymbol: metadataSymbol,
                            metadataTitle: metadataTitle,
                            metadataUri: metadataUri,
                            stakingFeeShareBps: stakingFeeShareBps,
                            vpVolumeFactor: vpVolumeFactor
                        })
                            .accounts({
                            admin: this.provider.wallet.publicKey,
                            multisig: this.multisig.publicKey,
                            transferAuthority: this.authority.publicKey,
                            perpetuals: this.perpetuals.publicKey,
                            pool: this.getPoolKey(name),
                            lpTokenMint: this.getPoolLpTokenKey(name),
                            systemProgram: web3_js_1.SystemProgram.programId,
                            tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                            rent: web3_js_1.SYSVAR_RENT_PUBKEY,
                        })
                            .rpc()
                            .catch(function (err) {
                            console.error(err);
                            throw err;
                        })];
                    case 1:
                        _a.sent();
                        return [2];
                }
            });
        }); };
        this.removePool = function (name) { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4, this.program.methods
                            .removePool({})
                            .accounts({
                            admin: this.admin,
                            multisig: this.multisig.publicKey,
                            transferAuthority: this.authority.publicKey,
                            perpetuals: this.perpetuals.publicKey,
                            pool: this.getPoolKey(name),
                            systemProgram: web3_js_1.SystemProgram.programId,
                        })
                            .rpc()
                            .catch(function (err) {
                            console.error(err);
                            throw err;
                        })];
                    case 1:
                        _a.sent();
                        return [2];
                }
            });
        }); };
        this.addCustody = function (poolName, tokenMint, isToken222, isStable, isVirtual, oracle, pricing, permissions, fees, borrowRate, ratios, depegAdjustment) { return __awaiter(_this, void 0, void 0, function () {
            var trx_id, error_3;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        _a.trys.push([0, 2, , 3]);
                        return [4, this.program.methods
                                .addCustody({
                                isStable: isStable,
                                depegAdjustment: depegAdjustment,
                                isVirtual: isVirtual,
                                token22: isToken222,
                                oracle: oracle,
                                pricing: pricing,
                                permissions: permissions,
                                fees: fees,
                                borrowRate: borrowRate,
                                ratios: ratios,
                            })
                                .accounts({
                                admin: this.admin,
                                multisig: this.multisig.publicKey,
                                transferAuthority: this.authority.publicKey,
                                perpetuals: this.perpetuals.publicKey,
                                pool: this.getPoolKey(poolName),
                                custody: this.getCustodyKey(poolName, tokenMint),
                                custodyTokenAccount: this.getCustodyTokenAccountKey(poolName, tokenMint),
                                custodyTokenMint: tokenMint,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                rent: web3_js_1.SYSVAR_RENT_PUBKEY,
                            })
                                .rpc()
                                .catch(function (err) {
                                console.error(err);
                                throw err;
                            })];
                    case 1:
                        trx_id = _a.sent();
                        console.log("trx_id:", "https://explorer.solana.com/tx/".concat(trx_id, "?cluster=devnet"));
                        return [3, 3];
                    case 2:
                        error_3 = _a.sent();
                        console.error("cli error :", error_3);
                        throw error_3;
                    case 3: return [2];
                }
            });
        }); };
        this.editCustody = function (poolName, tokenMint, isStable, oracle, pricing, permissions, fees, borrowRate, ratios) { return __awaiter(_this, void 0, void 0, function () {
            var trx_id;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4, this.program.methods
                            .testingEditCustody({
                            isStable: isStable,
                            oracle: oracle,
                            pricing: pricing,
                            permissions: permissions,
                            fees: fees,
                            borrowRate: borrowRate,
                            ratios: ratios,
                        })
                            .accounts({
                            admin: this.admin,
                            multisig: this.multisig.publicKey,
                            transferAuthority: this.authority.publicKey,
                            perpetuals: this.perpetuals.publicKey,
                            pool: this.getPoolKey(poolName),
                            custody: this.getCustodyKey(poolName, tokenMint),
                            custodyTokenAccount: this.getCustodyTokenAccountKey(poolName, tokenMint),
                            custodyTokenMint: tokenMint,
                            systemProgram: web3_js_1.SystemProgram.programId,
                            tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                            rent: web3_js_1.SYSVAR_RENT_PUBKEY,
                        })
                            .rpc()
                            .catch(function (err) {
                            console.error(err);
                            throw err;
                        })];
                    case 1:
                        trx_id = _a.sent();
                        console.log("trx_id:", "https://explorer.solana.com/tx/".concat(trx_id, "?cluster=devnet"));
                        return [2];
                }
            });
        }); };
        this.removeCustody = function (poolName, tokenMint, ratios, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var custodyConfig, userReceivingTokenAccount;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        custodyConfig = poolConfig.custodies.find(function (f) { return f.mintKey.equals(tokenMint); });
                        userReceivingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(tokenMint, this.admin, true);
                        return [4, this.program.methods
                                .removeCustody({ ratios: ratios })
                                .accounts({
                                admin: this.admin,
                                receivingAccount: userReceivingTokenAccount,
                                multisig: this.multisig.publicKey,
                                transferAuthority: this.authority.publicKey,
                                perpetuals: this.perpetuals.publicKey,
                                pool: this.getPoolKey(poolName),
                                custody: this.getCustodyKey(poolName, tokenMint),
                                custodyTokenAccount: this.getCustodyTokenAccountKey(poolName, tokenMint),
                                custodyOracleAccount: this.useExtOracleAccount ? custodyConfig.extOracleAccount : custodyConfig.intOracleAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                ixSysvar: web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                receivingTokenMint: tokenMint,
                            })
                                .rpc()
                                .catch(function (err) {
                                console.error(err);
                                throw err;
                            })];
                    case 1:
                        _a.sent();
                        return [2];
                }
            });
        }); };
        this.protocolWithdrawFees = function (rewardSymbol, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, custodyConfig, receivingTokenAccount, instructions, additionalSigners, withdrawFeesIx, err_52;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        custodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(rewardSymbol).mintKey); });
                        return [4, (0, spl_token_1.getAssociatedTokenAddress)(poolConfig.getTokenFromSymbol(rewardSymbol).mintKey, publicKey, true)];
                    case 1:
                        receivingTokenAccount = _a.sent();
                        instructions = [];
                        additionalSigners = [];
                        _a.label = 2;
                    case 2:
                        _a.trys.push([2, 4, , 5]);
                        return [4, this.program.methods
                                .withdrawFees({})
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                transferAuthority: this.authority.publicKey,
                                perpetuals: this.perpetuals.publicKey,
                                protocolVault: poolConfig.protocolVault,
                                protocolTokenAccount: poolConfig.protocolTokenAccount,
                                receivingTokenAccount: receivingTokenAccount,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                receivingMint: poolConfig.getTokenFromSymbol(rewardSymbol).mintKey,
                            })
                                .instruction()];
                    case 3:
                        withdrawFeesIx = _a.sent();
                        instructions.push(withdrawFeesIx);
                        return [3, 5];
                    case 4:
                        err_52 = _a.sent();
                        console.log("perpClient setPool error:: ", err_52);
                        throw err_52;
                    case 5: return [2, {
                            instructions: __spreadArray([], instructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.moveProtocolFees = function (rewardSymbol, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, custodyConfig, instructions, additionalSigners, moveProtocolFeesIx, err_53;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        custodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(rewardSymbol).mintKey); });
                        instructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4, this.program.methods
                                .moveProtocolFees()
                                .accounts({
                                transferAuthority: this.authority.publicKey,
                                perpetuals: this.perpetuals.publicKey,
                                tokenVault: poolConfig.tokenVault,
                                pool: poolConfig.poolAddress,
                                custody: custodyConfig.custodyAccount,
                                custodyTokenAccount: custodyConfig.tokenAccount,
                                revenueTokenAccount: poolConfig.revenueTokenAccount,
                                protocolVault: poolConfig.protocolVault,
                                protocolTokenAccount: poolConfig.protocolTokenAccount,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.program.programId,
                                tokenMint: custodyConfig.mintKey,
                            })
                                .instruction()];
                    case 2:
                        moveProtocolFeesIx = _a.sent();
                        instructions.push(moveProtocolFeesIx);
                        return [3, 4];
                    case 3:
                        err_53 = _a.sent();
                        console.log("perpClient setPool error:: ", err_53);
                        throw err_53;
                    case 4: return [2, {
                            instructions: __spreadArray([], instructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.setProtocolFeeShareBps = function (feeShareBps, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, setProtocolFeeShareBpsIx, err_54;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        _a.trys.push([0, 2, , 3]);
                        publicKey = this.provider.wallet.publicKey;
                        return [4, this.program.methods
                                .setProtocolFeeShare({
                                feeShareBps: feeShareBps
                            })
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                protocolVault: poolConfig.protocolVault,
                            })
                                .instruction()];
                    case 1:
                        setProtocolFeeShareBpsIx = _a.sent();
                        return [2, setProtocolFeeShareBpsIx];
                    case 2:
                        err_54 = _a.sent();
                        console.log("perpClient setProtocolFeeShareBpsIx error:: ", err_54);
                        throw err_54;
                    case 3: return [2];
                }
            });
        }); };
        this.setPermissions = function (permissions) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, setPermissionsInstruction, err_55;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4, this.program.methods
                                .setPermissions({
                                permissions: permissions,
                            })
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                perpetuals: this.perpetuals.publicKey
                            })
                                .instruction()];
                    case 2:
                        setPermissionsInstruction = _a.sent();
                        instructions.push(setPermissionsInstruction);
                        return [3, 4];
                    case 3:
                        err_55 = _a.sent();
                        console.log("perpClient setPool error:: ", err_55);
                        throw err_55;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.reimburse = function (tokenMint, amountIn, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var custodyAccountMetas, custodyOracleAccountMetas, markets, _i, _a, custody, _b, _c, market, instructions, additionalSigners, custodyConfig, reimburse, _d, _e, err_56;
            var _f;
            return __generator(this, function (_g) {
                switch (_g.label) {
                    case 0:
                        custodyAccountMetas = [];
                        custodyOracleAccountMetas = [];
                        markets = [];
                        for (_i = 0, _a = poolConfig.custodies; _i < _a.length; _i++) {
                            custody = _a[_i];
                            custodyAccountMetas.push({
                                pubkey: custody.custodyAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                            custodyOracleAccountMetas.push({
                                pubkey: this.useExtOracleAccount ? custody.extOracleAccount : custody.intOracleAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        for (_b = 0, _c = poolConfig.markets; _b < _c.length; _b++) {
                            market = _c[_b];
                            markets.push({
                                pubkey: market.marketAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        }
                        instructions = [];
                        additionalSigners = [];
                        custodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(tokenMint); });
                        _g.label = 1;
                    case 1:
                        _g.trys.push([1, 4, , 5]);
                        _e = (_d = this.program.methods
                            .reimburse({ amountIn: amountIn }))
                            .accounts;
                        _f = {
                            admin: this.provider.wallet.publicKey,
                            multisig: poolConfig.multisig
                        };
                        return [4, (0, spl_token_1.getAssociatedTokenAddress)(tokenMint, this.provider.wallet.publicKey, true)];
                    case 2: return [4, _e.apply(_d, [(_f.fundingAccount = _g.sent(),
                                _f.perpetuals = poolConfig.perpetuals,
                                _f.pool = poolConfig.poolAddress,
                                _f.custody = custodyConfig.custodyAccount,
                                _f.custodyOracleAccount = this.useExtOracleAccount ? custodyConfig.extOracleAccount : custodyConfig.intOracleAccount,
                                _f.custodyTokenAccount = custodyConfig.tokenAccount,
                                _f.tokenProgram = spl_token_1.TOKEN_PROGRAM_ID,
                                _f.program = poolConfig.programId,
                                _f.ixSysvar = web3_js_1.SYSVAR_INSTRUCTIONS_PUBKEY,
                                _f.fundingMint = tokenMint,
                                _f)])
                            .remainingAccounts(__spreadArray(__spreadArray(__spreadArray([], custodyAccountMetas, true), custodyOracleAccountMetas, true), markets, true))
                            .instruction()];
                    case 3:
                        reimburse = _g.sent();
                        instructions.push(reimburse);
                        return [3, 5];
                    case 4:
                        err_56 = _g.sent();
                        console.log("perpClient setPool error:: ", err_56);
                        throw err_56;
                    case 5: return [2, {
                            instructions: __spreadArray([], instructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.setInternalOraclePrice = function (tokenMint, price, expo, conf, ema, publishTime, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var instructions, additionalSigners, custodyConfig, setInternalOraclePrice, err_57;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        instructions = [];
                        additionalSigners = [];
                        custodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(tokenMint); });
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4, this.program.methods
                                .setInternalOraclePrice({
                                price: price,
                                expo: expo,
                                conf: conf,
                                ema: ema,
                                publishTime: publishTime,
                            })
                                .accounts({
                                authority: poolConfig.backupOracle,
                                perpetuals: poolConfig.perpetuals,
                                pool: poolConfig.poolAddress,
                                custody: custodyConfig.custodyAccount,
                                intOracleAccount: custodyConfig.intOracleAccount,
                                extOracleAccount: custodyConfig.extOracleAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                            })
                                .instruction()];
                    case 2:
                        setInternalOraclePrice = _a.sent();
                        instructions.push(setInternalOraclePrice);
                        return [3, 4];
                    case 3:
                        err_57 = _a.sent();
                        console.log("perpClient setInternalOracleAccount error:: ", err_57);
                        throw err_57;
                    case 4: return [2, {
                            instructions: __spreadArray([], instructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.setInternalOraclePriceBatch = function (tokenMintList, tokenInternalPrices, POOL_CONFIGS) { return __awaiter(_this, void 0, void 0, function () {
            var ALL_CUSTODY_CONFIGS, accountMetas, _loop_1, _i, tokenMintList_1, tokenMint, instructions, additionalSigners, setInternalOraclePrice, err_58;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (tokenMintList.length !== tokenInternalPrices.length) {
                            throw new Error("tokenMintList and tokenInternalPrices length mismatch");
                        }
                        ALL_CUSTODY_CONFIGS = POOL_CONFIGS.map(function (f) { return f.custodies; }).flat();
                        accountMetas = [];
                        _loop_1 = function (tokenMint) {
                            var custody = ALL_CUSTODY_CONFIGS.find(function (i) { return i.mintKey.equals(tokenMint); });
                            accountMetas.push({
                                pubkey: custody.custodyAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                            accountMetas.push({
                                pubkey: custody.intOracleAccount,
                                isSigner: false,
                                isWritable: true,
                            });
                            accountMetas.push({
                                pubkey: custody.extOracleAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        };
                        for (_i = 0, tokenMintList_1 = tokenMintList; _i < tokenMintList_1.length; _i++) {
                            tokenMint = tokenMintList_1[_i];
                            _loop_1(tokenMint);
                        }
                        instructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4, this.program.methods
                                .setInternalCurrentPrice({
                                prices: tokenInternalPrices
                            })
                                .accounts({
                                authority: POOL_CONFIGS[0].backupOracle,
                            })
                                .remainingAccounts(__spreadArray([], accountMetas, true))
                                .instruction()];
                    case 2:
                        setInternalOraclePrice = _a.sent();
                        instructions.push(setInternalOraclePrice);
                        return [3, 4];
                    case 3:
                        err_58 = _a.sent();
                        console.log("perpClient setInternalOracleAccount error:: ", err_58);
                        throw err_58;
                    case 4: return [2, {
                            instructions: __spreadArray([], instructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.setInternalOracleEmaPriceBatch = function (tokenMintList, tokenInternalEmaPrices, POOL_CONFIGS) { return __awaiter(_this, void 0, void 0, function () {
            var ALL_CUSTODY_CONFIGS, accountMetas, _loop_2, _i, tokenMintList_2, tokenMint, instructions, additionalSigners, setInternalOraclePrice, err_59;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (tokenMintList.length !== tokenInternalEmaPrices.length) {
                            throw new Error("tokenMintList and tokenInternalPrices length mismatch");
                        }
                        ALL_CUSTODY_CONFIGS = POOL_CONFIGS.map(function (f) { return f.custodies; }).flat();
                        accountMetas = [];
                        _loop_2 = function (tokenMint) {
                            var custody = ALL_CUSTODY_CONFIGS.find(function (i) { return i.mintKey.equals(tokenMint); });
                            accountMetas.push({
                                pubkey: custody.custodyAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                            accountMetas.push({
                                pubkey: custody.intOracleAccount,
                                isSigner: false,
                                isWritable: true,
                            });
                            accountMetas.push({
                                pubkey: custody.extOracleAccount,
                                isSigner: false,
                                isWritable: false,
                            });
                        };
                        for (_i = 0, tokenMintList_2 = tokenMintList; _i < tokenMintList_2.length; _i++) {
                            tokenMint = tokenMintList_2[_i];
                            _loop_2(tokenMint);
                        }
                        instructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4, this.program.methods
                                .setInternalEmaPrice({
                                prices: tokenInternalEmaPrices
                            })
                                .accounts({
                                authority: POOL_CONFIGS[0].backupOracle,
                            })
                                .remainingAccounts(__spreadArray([], accountMetas, true))
                                .instruction()];
                    case 2:
                        setInternalOraclePrice = _a.sent();
                        instructions.push(setInternalOraclePrice);
                        return [3, 4];
                    case 3:
                        err_59 = _a.sent();
                        console.log("perpClient setInternalOracleAccount error:: ", err_59);
                        throw err_59;
                    case 4: return [2, {
                            instructions: __spreadArray([], instructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.renameFlp = function (flag, lpTokenName, lpTokenSymbol, lpTokenUri, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, instructions, additionalSigners, lpTokenMint, lpMetadataAccount, renameFlp, err_60;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        instructions = [];
                        additionalSigners = [];
                        lpTokenMint = poolConfig.stakedLpTokenMint;
                        lpMetadataAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("metadata"), constants_1.METAPLEX_PROGRAM_ID.toBuffer(), lpTokenMint.toBuffer()], constants_1.METAPLEX_PROGRAM_ID)[0];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4, this.program.methods
                                .renameFlp({
                                flag: flag,
                                lpTokenName: lpTokenName,
                                lpTokenSymbol: lpTokenSymbol,
                                lpTokenUri: lpTokenUri,
                            })
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                transferAuthority: poolConfig.transferAuthority,
                                perpetuals: poolConfig.perpetuals,
                                pool: poolConfig.poolAddress,
                                lpTokenMint: lpTokenMint,
                                lpMetadataAccount: lpMetadataAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                metadataProgram: constants_1.METAPLEX_PROGRAM_ID,
                                rent: web3_js_1.SYSVAR_RENT_PUBKEY
                            })
                                .instruction()];
                    case 2:
                        renameFlp = _a.sent();
                        instructions.push(renameFlp);
                        return [3, 4];
                    case 3:
                        err_60 = _a.sent();
                        console.log("perpClient renameFlp error:: ", err_60);
                        return [3, 4];
                    case 4: return [2, {
                            instructions: __spreadArray([], instructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.initStake = function (stakingFeeShareBps, rewardSymbol, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, lpTokenMint, stakedLpTokenAccount, rewardCustodyConfig, initStakeInstruction, err_61;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        lpTokenMint = poolConfig.stakedLpTokenMint;
                        stakedLpTokenAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("staked_lp_token_account"), poolConfig.poolAddress.toBuffer(), lpTokenMint.toBuffer()], this.programId)[0];
                        rewardCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(rewardSymbol).mintKey); });
                        return [4, this.program.methods
                                .initStaking({
                                stakingFeeShareBps: stakingFeeShareBps
                            })
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                transferAuthority: poolConfig.transferAuthority,
                                perpetuals: this.perpetuals.publicKey,
                                pool: poolConfig.poolAddress,
                                custody: rewardCustodyConfig.custodyAccount,
                                lpTokenMint: lpTokenMint,
                                stakedLpTokenAccount: stakedLpTokenAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                rent: web3_js_1.SYSVAR_RENT_PUBKEY
                            })
                                .instruction()];
                    case 2:
                        initStakeInstruction = _a.sent();
                        instructions.push(initStakeInstruction);
                        return [3, 4];
                    case 3:
                        err_61 = _a.sent();
                        console.log("perpClient InitStaking error:: ", err_61);
                        throw err_61;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.initCompounding = function (feeShareBps, metadataTitle, metadataSymbol, metadataUri, rewardSymbol, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, rewardCustodyConfig, compoundingTokenMint, compoundingVault, metadataAccount, initCompoundingInstruction, err_62;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        rewardCustodyConfig = poolConfig.custodies.find(function (i) { return i.mintKey.equals(poolConfig.getTokenFromSymbol(rewardSymbol).mintKey); });
                        compoundingTokenMint = this.getPoolCompoundingTokenKey(poolConfig.poolName);
                        compoundingVault = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("compounding_token_account"), poolConfig.poolAddress.toBuffer(), poolConfig.stakedLpTokenMint.toBuffer()], this.programId)[0];
                        metadataAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("metadata"), constants_1.METAPLEX_PROGRAM_ID.toBuffer(), compoundingTokenMint.toBuffer()], constants_1.METAPLEX_PROGRAM_ID)[0];
                        return [4, this.program.methods
                                .initCompounding({
                                feeShareBps: feeShareBps,
                                metadataTitle: metadataTitle,
                                metadataSymbol: metadataSymbol,
                                metadataUri: metadataUri
                            })
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                transferAuthority: poolConfig.transferAuthority,
                                perpetuals: this.perpetuals.publicKey,
                                pool: poolConfig.poolAddress,
                                custody: rewardCustodyConfig.custodyAccount,
                                lpTokenMint: poolConfig.stakedLpTokenMint,
                                compoundingVault: compoundingVault,
                                compoundingTokenMint: compoundingTokenMint,
                                metadataAccount: metadataAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                metadataProgram: constants_1.METAPLEX_PROGRAM_ID,
                                rent: web3_js_1.SYSVAR_RENT_PUBKEY
                            })
                                .instruction()];
                    case 2:
                        initCompoundingInstruction = _a.sent();
                        instructions.push(initCompoundingInstruction);
                        return [3, 4];
                    case 3:
                        err_62 = _a.sent();
                        console.log("perpClient initCompounding error:: ", err_62);
                        throw err_62;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.initTokenVault = function (token_permissions, tokens_to_distribute, withdrawTimeLimit, withdrawInstantFee, stakeLevel, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, tokenMint, fundingTokenAccount, initTokenVaultInstruction, err_63;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        tokenMint = poolConfig.tokenMint;
                        fundingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(tokenMint, publicKey, true);
                        return [4, this.program.methods
                                .initTokenVault({
                                tokenPermissions: token_permissions,
                                amount: tokens_to_distribute,
                                withdrawTimeLimit: withdrawTimeLimit,
                                withdrawInstantFee: withdrawInstantFee,
                                stakeLevel: stakeLevel,
                            })
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                perpetuals: this.perpetuals.publicKey,
                                transferAuthority: poolConfig.transferAuthority,
                                fundingTokenAccount: fundingTokenAccount,
                                tokenMint: tokenMint,
                                tokenVault: poolConfig.tokenVault,
                                tokenVaultTokenAccount: poolConfig.tokenVaultTokenAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                rent: web3_js_1.SYSVAR_RENT_PUBKEY
                            })
                                .instruction()];
                    case 2:
                        initTokenVaultInstruction = _a.sent();
                        instructions.push(initTokenVaultInstruction);
                        return [3, 4];
                    case 3:
                        err_63 = _a.sent();
                        console.log("perpClient InitTokenVaultInstruction error:: ", err_63);
                        throw err_63;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.setTokenVaultConfig = function (token_permissions, withdrawTimeLimit, withdrawInstantFee, stakeLevel, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, setTokenVaultConfigInstruction, err_64;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4, this.program.methods
                                .setTokenVaultConfig({
                                tokenPermissions: token_permissions,
                                withdrawTimeLimit: withdrawTimeLimit,
                                withdrawInstantFee: withdrawInstantFee,
                                stakeLevel: stakeLevel,
                            })
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                tokenVault: poolConfig.tokenVault,
                                systemProgram: web3_js_1.SystemProgram.programId,
                            })
                                .instruction()];
                    case 2:
                        setTokenVaultConfigInstruction = _a.sent();
                        instructions.push(setTokenVaultConfigInstruction);
                        return [3, 4];
                    case 3:
                        err_64 = _a.sent();
                        console.log("perpClient setTokenVaultConfigInstruction error:: ", err_64);
                        throw err_64;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.withdrawInstantFee = function (poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, receivingTokenAccount, withdrawInstantFeeInstruction, err_65;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 5, , 6]);
                        return [4, (0, spl_token_1.getAssociatedTokenAddress)(poolConfig.tokenMint, publicKey, true)];
                    case 2:
                        receivingTokenAccount = _a.sent();
                        return [4, (0, utils_1.checkIfAccountExists)(receivingTokenAccount, this.provider.connection)];
                    case 3:
                        if (!(_a.sent())) {
                            preInstructions.push((0, spl_token_1.createAssociatedTokenAccountInstruction)(publicKey, receivingTokenAccount, publicKey, poolConfig.tokenMint));
                        }
                        return [4, this.program.methods
                                .withdrawInstantFees({})
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                perpetuals: this.perpetuals.publicKey,
                                transferAuthority: poolConfig.transferAuthority,
                                tokenVault: poolConfig.tokenVault,
                                tokenVaultTokenAccount: poolConfig.tokenVaultTokenAccount,
                                receivingTokenAccount: receivingTokenAccount,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                            })
                                .instruction()];
                    case 4:
                        withdrawInstantFeeInstruction = _a.sent();
                        instructions.push(withdrawInstantFeeInstruction);
                        return [3, 6];
                    case 5:
                        err_65 = _a.sent();
                        console.log("perpClient withdrawInstantFeeInstruction error:: ", err_65);
                        throw err_65;
                    case 6: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.initRevenueTokenAccount = function (feeShareBps, rewardSymbol, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, rewardCustodyMint, initRevenueTokenAccountInstruction, err_66;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        rewardCustodyMint = poolConfig.getTokenFromSymbol(rewardSymbol).mintKey;
                        return [4, this.program.methods
                                .initRevenueTokenAccount({
                                feeShareBps: feeShareBps
                            })
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                perpetuals: this.perpetuals.publicKey,
                                transferAuthority: poolConfig.transferAuthority,
                                tokenVault: poolConfig.tokenVault,
                                rewardMint: rewardCustodyMint,
                                revenueTokenAccount: poolConfig.revenueTokenAccount,
                                protocolVault: poolConfig.protocolVault,
                                protocolTokenAccount: poolConfig.protocolTokenAccount,
                                systemProgram: web3_js_1.SystemProgram.programId,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                rent: web3_js_1.SYSVAR_RENT_PUBKEY
                            })
                                .instruction()];
                    case 2:
                        initRevenueTokenAccountInstruction = _a.sent();
                        instructions.push(initRevenueTokenAccountInstruction);
                        return [3, 4];
                    case 3:
                        err_66 = _a.sent();
                        console.log("perpClient initRevenueTokenAccountInstruction error:: ", err_66);
                        throw err_66;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.distributeTokenReward = function (amount, epochCount, rewardSymbol, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, rewardCustodyMint, fundingTokenAccount, revenueFundingTokenAccount, distributeTokenRewardInstruction, err_67;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        rewardCustodyMint = poolConfig.getTokenFromSymbol(rewardSymbol).mintKey;
                        fundingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(poolConfig.tokenMint, publicKey, true);
                        revenueFundingTokenAccount = (0, spl_token_1.getAssociatedTokenAddressSync)(rewardCustodyMint, publicKey, true);
                        return [4, this.program.methods
                                .distributeTokenReward({
                                amount: amount,
                                epochCount: epochCount,
                            })
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                perpetuals: this.perpetuals.publicKey,
                                transferAuthority: poolConfig.transferAuthority,
                                fundingTokenAccount: fundingTokenAccount,
                                tokenVault: poolConfig.tokenVault,
                                tokenVaultTokenAccount: poolConfig.tokenVaultTokenAccount,
                                tokenProgram: spl_token_1.TOKEN_PROGRAM_ID,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId,
                                tokenMint: poolConfig.tokenMint,
                            })
                                .instruction()];
                    case 2:
                        distributeTokenRewardInstruction = _a.sent();
                        instructions.push(distributeTokenRewardInstruction);
                        return [3, 4];
                    case 3:
                        err_67 = _a.sent();
                        console.log("perpClient distributeTokenRewardInstruction error:: ", err_67);
                        throw err_67;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.setTokenStakeLevel = function (owner, stakeLevel) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, tokenStakeAccount, setTokenStakeLevelInstruction, err_68;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("token_stake"), owner.toBuffer()], this.programId)[0];
                        return [4, this.program.methods
                                .setTokenStakeLevel({
                                level: stakeLevel,
                            })
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                tokenStakeAccount: tokenStakeAccount,
                            })
                                .instruction()];
                    case 2:
                        setTokenStakeLevelInstruction = _a.sent();
                        instructions.push(setTokenStakeLevelInstruction);
                        return [3, 4];
                    case 3:
                        err_68 = _a.sent();
                        console.log("perpClient setTokenStakeLevelInstruction error:: ", err_68);
                        throw err_68;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.setTokenReward = function (owner, amount, epochCount, poolConfig) { return __awaiter(_this, void 0, void 0, function () {
            var publicKey, preInstructions, instructions, postInstructions, additionalSigners, tokenStakeAccount, setTokenRewardInstruction, err_69;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        publicKey = this.provider.wallet.publicKey;
                        preInstructions = [];
                        instructions = [];
                        postInstructions = [];
                        additionalSigners = [];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        tokenStakeAccount = web3_js_1.PublicKey.findProgramAddressSync([Buffer.from("token_stake"), owner.toBuffer()], this.programId)[0];
                        return [4, this.program.methods
                                .setTokenReward({
                                amount: amount,
                                epochCount: epochCount,
                            })
                                .accounts({
                                admin: publicKey,
                                multisig: this.multisig.publicKey,
                                tokenVault: poolConfig.tokenVault,
                                tokenStakeAccount: tokenStakeAccount,
                                eventAuthority: this.eventAuthority.publicKey,
                                program: this.programId
                            })
                                .instruction()];
                    case 2:
                        setTokenRewardInstruction = _a.sent();
                        instructions.push(setTokenRewardInstruction);
                        return [3, 4];
                    case 3:
                        err_69 = _a.sent();
                        console.log("perpClient setTokenRewardInstruction error:: ", err_69);
                        throw err_69;
                    case 4: return [2, {
                            instructions: __spreadArray(__spreadArray(__spreadArray([], preInstructions, true), instructions, true), postInstructions, true),
                            additionalSigners: additionalSigners
                        }];
                }
            });
        }); };
        this.provider = provider;
        (0, anchor_1.setProvider)(provider);
        this.program = new anchor_1.Program(perpetuals_1.IDL, programId);
        this.programPerpComposability = new anchor_1.Program(perp_composability_1.IDL, composabilityProgramId);
        this.programFbnftReward = new anchor_1.Program(fbnft_rewards_1.IDL, fbNftRewardProgramId);
        this.programRewardDistribution = new anchor_1.Program(reward_distribution_1.IDL, rewardDistributionProgramId);
        this.programId = programId;
        this.composabilityProgramId = composabilityProgramId;
        this.admin = this.provider.wallet.publicKey;
        this.multisig = this.findProgramAddress("multisig");
        this.authority = this.findProgramAddress("transfer_authority");
        this.perpetuals = this.findProgramAddress("perpetuals");
        this.eventAuthority = this.findProgramAddress("__event_authority");
        this.eventAuthorityRewardDistribution = this.findProgramAddressFromProgramId("__event_authority", null, this.programRewardDistribution.programId);
        this.minimumBalanceForRentExemptAccountLamports = 2039280;
        this.prioritizationFee = (opts === null || opts === void 0 ? void 0 : opts.prioritizationFee) || 0;
        this.useExtOracleAccount = useExtOracleAccount;
        this.postSendTxCallback = opts === null || opts === void 0 ? void 0 : opts.postSendTxCallback;
        this.txConfirmationCommitment = (_a = opts === null || opts === void 0 ? void 0 : opts.txConfirmationCommitment) !== null && _a !== void 0 ? _a : 'processed';
        this.viewHelper = new ViewHelper_1.ViewHelper(this);
        anchor_1.BN.prototype.toJSON = function () {
            return this.toString(10);
        };
    }
    PerpetualsClient.prototype.getMarketPk = function (targetCustody, collateralCustody, side) {
        return this.findProgramAddress("market", [
            targetCustody,
            collateralCustody,
            side === 'long' ? [1] : [2],
        ]).publicKey;
    };
    PerpetualsClient.prototype.getPositionKey = function (owner, targetCustody, collateralCustody, side) {
        return this.findProgramAddress("position", [
            owner,
            this.getMarketPk(targetCustody, collateralCustody, side),
        ]).publicKey;
    };
    PerpetualsClient.prototype.getOrderAccountKey = function (owner, targetCustody, collateralCustody, side) {
        return this.findProgramAddress("order", [
            owner,
            this.getMarketPk(targetCustody, collateralCustody, side),
        ]).publicKey;
    };
    PerpetualsClient.prototype.getNewRatioHelper = function (amountAdd, amountRemove, custodyAccount, maxPriceOracle, poolAumUsdMax) {
        var newRatio = constants_1.BN_ZERO;
        var tokenAumUsd = maxPriceOracle.getAssetAmountUsd(custodyAccount.assets.owned, custodyAccount.decimals);
        if (amountAdd.gt(constants_1.BN_ZERO) && amountRemove.gt(constants_1.BN_ZERO)) {
            throw new Error("cannot add and remove liquidity together");
        }
        else if (amountAdd.isZero() && amountRemove.isZero()) {
            newRatio = (tokenAumUsd.mul(new anchor_1.BN(constants_1.BPS_POWER))).div(poolAumUsdMax);
        }
        else if (amountAdd.gt(constants_1.BN_ZERO)) {
            var amountUsd = maxPriceOracle.getAssetAmountUsd(amountAdd, custodyAccount.decimals);
            newRatio = ((tokenAumUsd.add(amountUsd)).mul(new anchor_1.BN(constants_1.BPS_POWER))).div(poolAumUsdMax.add(amountUsd));
        }
        else {
            var amountUsd = maxPriceOracle.getAssetAmountUsd(amountRemove, custodyAccount.decimals);
            if (amountUsd.gte(poolAumUsdMax) || amountRemove.gte(custodyAccount.assets.owned)) {
                newRatio = constants_1.BN_ZERO;
            }
            else {
                newRatio = ((tokenAumUsd.sub(amountUsd)).mul(new anchor_1.BN(constants_1.BPS_POWER))).div(poolAumUsdMax.sub(amountUsd));
            }
        }
        return newRatio;
    };
    PerpetualsClient.prototype.getPriceAfterSlippage = function (isEntry, slippageBps, targetPrice, side) {
        if (isEntry) {
            var currentPrice = targetPrice.price;
            var spread_i = (0, utils_1.checkedDecimalCeilMul)(currentPrice, targetPrice.exponent, slippageBps, new anchor_1.BN(-1 * constants_1.BPS_DECIMALS), targetPrice.exponent);
            if ((0, types_1.isVariant)(side, 'long')) {
                return { price: currentPrice.add(spread_i), exponent: targetPrice.exponent.toNumber() };
            }
            else {
                if (spread_i.lt(currentPrice)) {
                    return { price: currentPrice.sub(spread_i), exponent: targetPrice.exponent.toNumber() };
                }
                else {
                    return { price: constants_1.BN_ZERO, exponent: targetPrice.exponent.toNumber() };
                }
                ;
            }
        }
        else {
            var current_price = targetPrice.price;
            var spread_i = (0, utils_1.checkedDecimalCeilMul)(current_price, targetPrice.exponent, slippageBps, new anchor_1.BN(-1 * constants_1.BPS_DECIMALS), targetPrice.exponent);
            if ((0, types_1.isVariant)(side, 'long')) {
                if (spread_i.lt(current_price)) {
                    return { price: current_price.sub(spread_i), exponent: targetPrice.exponent.toNumber() };
                }
                else {
                    return { price: constants_1.BN_ZERO, exponent: targetPrice.exponent.toNumber() };
                }
                ;
            }
            else {
                return { price: current_price.add(spread_i), exponent: targetPrice.exponent.toNumber() };
            }
        }
    };
    PerpetualsClient.prototype.sendTransaction = function (ixs_1) {
        return __awaiter(this, arguments, void 0, function (ixs, opts) {
            if (opts === void 0) { opts = {}; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4, (0, rpc_1.sendTransaction)(this.program.provider, ixs, __assign({ postSendTxCallback: this.postSendTxCallback, prioritizationFee: this.prioritizationFee }, opts))];
                    case 1: return [2, _a.sent()];
                }
            });
        });
    };
    PerpetualsClient.prototype.sendTransactionV3 = function (ixs_1) {
        return __awaiter(this, arguments, void 0, function (ixs, opts) {
            if (opts === void 0) { opts = {}; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4, (0, rpc_1.sendTransactionV3)(this.program.provider, ixs, __assign({ postSendTxCallback: this.postSendTxCallback, prioritizationFee: this.prioritizationFee }, opts))];
                    case 1: return [2, _a.sent()];
                }
            });
        });
    };
    return PerpetualsClient;
}());
exports.PerpetualsClient = PerpetualsClient;
