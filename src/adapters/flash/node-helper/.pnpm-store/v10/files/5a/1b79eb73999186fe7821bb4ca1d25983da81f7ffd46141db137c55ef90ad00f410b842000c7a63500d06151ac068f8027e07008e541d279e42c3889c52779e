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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.PoolConfig = void 0;
var web3_js_1 = require("@solana/web3.js");
var PoolConfig_json_1 = __importDefault(require("./PoolConfig.json"));
var types_1 = require("./types");
var PoolConfig = (function () {
    function PoolConfig(programId, perpComposibilityProgramId, fbNftRewardProgramId, cluster, poolName, poolAddress, stakedLpTokenMint, compoundingTokenMint, stakedLpVault, compoundingLpVault, lpDecimals, compoundingLpTokenSymbol, stakedLpTokenSymbol, perpetuals, transferAuthority, tokenMint, tokenVault, tokenVaultTokenAccount, revenueTokenAccount, protocolVault, protocolTokenAccount, multisig, addressLookupTableAddresses, backupOracle, nftCollectionAddress, rewardDistributionProgram, tokens, custodies, markets) {
        var _this = this;
        this.programId = programId;
        this.perpComposibilityProgramId = perpComposibilityProgramId;
        this.fbNftRewardProgramId = fbNftRewardProgramId;
        this.cluster = cluster;
        this.poolName = poolName;
        this.poolAddress = poolAddress;
        this.stakedLpTokenMint = stakedLpTokenMint;
        this.compoundingTokenMint = compoundingTokenMint;
        this.stakedLpVault = stakedLpVault;
        this.compoundingLpVault = compoundingLpVault;
        this.lpDecimals = lpDecimals;
        this.compoundingLpTokenSymbol = compoundingLpTokenSymbol;
        this.stakedLpTokenSymbol = stakedLpTokenSymbol;
        this.perpetuals = perpetuals;
        this.transferAuthority = transferAuthority;
        this.tokenMint = tokenMint;
        this.tokenVault = tokenVault;
        this.tokenVaultTokenAccount = tokenVaultTokenAccount;
        this.revenueTokenAccount = revenueTokenAccount;
        this.protocolVault = protocolVault;
        this.protocolTokenAccount = protocolTokenAccount;
        this.multisig = multisig;
        this.addressLookupTableAddresses = addressLookupTableAddresses;
        this.backupOracle = backupOracle;
        this.nftCollectionAddress = nftCollectionAddress;
        this.rewardDistributionProgram = rewardDistributionProgram;
        this.tokens = tokens;
        this.custodies = custodies;
        this.markets = markets;
        this.getTokenFromSymbol = function (symbol) {
            return _this.tokens.find(function (f) { return f.symbol.toUpperCase() === symbol.toUpperCase(); });
        };
        this.getTokenFromMintString = function (mint) {
            return _this.tokens.find(function (f) { return f.mintKey.toBase58() === mint; });
        };
        this.getTokenFromMintPk = function (mint) {
            return _this.tokens.find(function (f) { return f.mintKey.equals(mint); });
        };
    }
    PoolConfig.prototype.getAllTokenMints = function () {
        return Array.from(this.tokens.map(function (token) { return new web3_js_1.PublicKey(token.mintKey); }));
    };
    PoolConfig.prototype.getMarketConfigByPk = function (marketAccountPk) {
        var market = this.markets.find(function (f) { return f.marketAccount.equals(marketAccountPk); });
        if (!market)
            throw new Error("No such market ".concat(marketAccountPk.toBase58(), " exists."));
        return market;
    };
    PoolConfig.prototype.getMarketConfig = function (targetCustody, collateralCustody, side) {
        var marketAccountPk = this.getMarketPk(targetCustody, collateralCustody, side);
        var market = this.markets.find(function (f) { return f.marketAccount.equals(marketAccountPk); });
        if (!market)
            return null;
        return market;
    };
    PoolConfig.prototype.getMarketPk = function (targetCustody, collateralCustody, side) {
        return web3_js_1.PublicKey.findProgramAddressSync([
            Buffer.from('market'),
            targetCustody.toBuffer(),
            collateralCustody.toBuffer(),
            Buffer.from([(0, types_1.isVariant)(side, 'long') ? 1 : 2])
        ], this.programId)[0];
    };
    PoolConfig.prototype.getPositionFromMarketPk = function (owner, marketAccount) {
        return web3_js_1.PublicKey.findProgramAddressSync([
            Buffer.from("position"),
            owner.toBuffer(),
            marketAccount.toBuffer(),
        ], this.programId)[0];
    };
    PoolConfig.prototype.getOrderFromMarketPk = function (owner, marketAccount) {
        return web3_js_1.PublicKey.findProgramAddressSync([
            Buffer.from("order"),
            owner.toBuffer(),
            marketAccount.toBuffer(),
        ], this.programId)[0];
    };
    PoolConfig.prototype.getPositionFromCustodyPk = function (owner, targetCustody, collateralCustody, side) {
        return web3_js_1.PublicKey.findProgramAddressSync([
            Buffer.from("position"),
            owner.toBuffer(),
            this.getMarketPk(targetCustody, collateralCustody, side).toBuffer(),
        ], this.programId)[0];
    };
    PoolConfig.prototype.doesMarketExist = function (pubkey) {
        return;
    };
    PoolConfig.prototype.getAllMarketPks = function () {
        return this.markets.map(function (m) { return m.marketAccount; });
    };
    PoolConfig.prototype.getNonStableTokens = function () {
        return Array.from(this.tokens
            .filter(function (token) { return !token.isStable; })
            .map(function (token) { return new web3_js_1.PublicKey(token.mintKey); }));
    };
    PoolConfig.prototype.getAllCustodies = function () {
        return Array.from(this.custodies.map(function (custody) { return new web3_js_1.PublicKey(custody.custodyAccount); }));
    };
    PoolConfig.prototype.getNonStableCustodies = function () {
        return Array.from(this.custodies
            .filter(function (custody) { return !custody.isStable; })
            .map(function (custody) { return new web3_js_1.PublicKey(custody.custodyAccount); }));
    };
    PoolConfig.getCustodyConfig = function (custodyAccountPk, poolName, cluster) {
        return this.fromIdsByName(poolName, cluster).custodies.find(function (f) { return f.custodyAccount.toBase58() === custodyAccountPk.toString(); });
    };
    PoolConfig.prototype.getCustodyIdFromCustodyAccount = function (custodyAccountPk) {
        return this.custodies.find(function (f) { return f.custodyAccount.toBase58() === custodyAccountPk.toString(); }).custodyId;
    };
    PoolConfig.prototype.getCustodyAccountFromCustodyId = function (custodyId) {
        return this.custodies.find(function (f) { return f.custodyId === custodyId; }).custodyAccount;
    };
    PoolConfig.getTokensInPool = function (name, cluster) {
        var poolConfig = PoolConfig_json_1.default.pools.find(function (pool) { return pool['poolName'] === name && cluster === pool['cluster']; });
        if (!poolConfig)
            throw new Error("No pool config ".concat(name, " found in Ids!"));
        var tokens = poolConfig['tokens'].map(function (i) {
            return __assign(__assign({}, i), { usdPrecision: i.usdPrecision, tokenPrecision: i.tokenPrecision, mintKey: new web3_js_1.PublicKey(i.mintKey) });
        });
        return tokens;
    };
    PoolConfig.buildPoolconfigFromJson = function (poolConfig) {
        var tokens;
        try {
            tokens = poolConfig['tokens'].map(function (i) {
                return __assign(__assign({}, i), { mintKey: new web3_js_1.PublicKey(i.mintKey) });
            });
        }
        catch (error) {
            console.log("ERROR: buildPoolconfigFromJson  unable to load tokens ");
        }
        var custodies;
        try {
            custodies = poolConfig['custodies'].map(function (i, index) {
                return __assign(__assign({}, i), { custodyId: i.custodyId, custodyAccount: new web3_js_1.PublicKey(i.custodyAccount), tokenAccount: new web3_js_1.PublicKey(i.tokenAccount), mintKey: new web3_js_1.PublicKey(i.mintKey), intOracleAccount: new web3_js_1.PublicKey(i.intOracleAddress), extOracleAccount: new web3_js_1.PublicKey(i.extOracleAddress), usdPrecision: i.usdPrecision, tokenPrecision: i.tokenPrecision });
            });
        }
        catch (error) {
            console.log("ERROR: buildPoolconfigFromJson  unable to load custodies ");
        }
        var addressLookupTableAddresses;
        try {
            addressLookupTableAddresses = poolConfig['addressLookupTableAddresses'].map(function (i) {
                return new web3_js_1.PublicKey(i);
            });
        }
        catch (error) {
            console.log("ERROR: buildPoolconfigFromJson  unable to load addressLookupTableAddresses ");
        }
        var markets;
        try {
            markets = poolConfig['markets'].map(function (i) {
                return __assign(__assign({}, i), { marketAccount: new web3_js_1.PublicKey(i.marketAccount), marketCorrelation: i.marketCorrelation, pool: new web3_js_1.PublicKey(i.pool), targetCustody: new web3_js_1.PublicKey(i.targetCustody), collateralCustody: new web3_js_1.PublicKey(i.collateralCustody), side: i.side === 'long' ? types_1.Side.Long : types_1.Side.Short, maxLev: i.maxLev, targetMint: new web3_js_1.PublicKey(i.targetMint), collateralMint: new web3_js_1.PublicKey(i.collateralMint) });
            });
        }
        catch (error) {
            console.log("ERROR: buildPoolconfigFromJson  unable to load markets ");
        }
        return new PoolConfig(new web3_js_1.PublicKey(poolConfig.programId), new web3_js_1.PublicKey(poolConfig.perpComposibilityProgramId), new web3_js_1.PublicKey(poolConfig.fbNftRewardProgramId), poolConfig.cluster, poolConfig.poolName, new web3_js_1.PublicKey(poolConfig.poolAddress), new web3_js_1.PublicKey(poolConfig.stakedLpTokenMint), new web3_js_1.PublicKey(poolConfig.compoundingTokenMint), new web3_js_1.PublicKey(poolConfig.stakedLpVault), new web3_js_1.PublicKey(poolConfig.compoundingLpVault), poolConfig.lpDecimals, poolConfig.compoundingLpTokenSymbol, poolConfig.stakedLpTokenSymbol, new web3_js_1.PublicKey(poolConfig.perpetuals), new web3_js_1.PublicKey(poolConfig.transferAuthority), new web3_js_1.PublicKey(poolConfig.tokenMint), new web3_js_1.PublicKey(poolConfig.tokenVault), new web3_js_1.PublicKey(poolConfig.tokenVaultTokenAccount), new web3_js_1.PublicKey(poolConfig.revenueTokenAccount), new web3_js_1.PublicKey(poolConfig.protocolVault), new web3_js_1.PublicKey(poolConfig.protocolTokenAccount), new web3_js_1.PublicKey(poolConfig.multisig), addressLookupTableAddresses, new web3_js_1.PublicKey(poolConfig.backupOracle), new web3_js_1.PublicKey(poolConfig.nftCollectionAddress), {
            programId: new web3_js_1.PublicKey(poolConfig.rewardDistributionProgram.programId),
            rewardMint: new web3_js_1.PublicKey(poolConfig.rewardDistributionProgram.rewardMint),
            rewardTokenAccount: new web3_js_1.PublicKey(poolConfig.rewardDistributionProgram.rewardTokenAccount),
            rewardVault: new web3_js_1.PublicKey(poolConfig.rewardDistributionProgram.rewardVault),
            transferAuthority: new web3_js_1.PublicKey(poolConfig.rewardDistributionProgram.transferAuthority),
        }, tokens, custodies, markets);
    };
    PoolConfig.fromIdsByName = function (name, cluster) {
        var poolConfig = PoolConfig_json_1.default.pools.find(function (pool) { return pool['poolName'] === name && cluster === pool['cluster']; });
        if (!poolConfig) {
            throw new Error("No pool with ".concat(name, " found!"));
        }
        return PoolConfig.buildPoolconfigFromJson(poolConfig);
    };
    PoolConfig.fromIdsByPk = function (poolPk, cluster) {
        var poolConfig = PoolConfig_json_1.default.pools.find(function (pool) { return pool['poolAddress'] === poolPk.toString() && cluster === pool['cluster']; });
        if (!poolConfig) {
            throw new Error("No pool with ".concat(poolPk.toString(), " found!"));
        }
        return PoolConfig.buildPoolconfigFromJson(poolConfig);
    };
    return PoolConfig;
}());
exports.PoolConfig = PoolConfig;
