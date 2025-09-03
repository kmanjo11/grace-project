"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getReferralAccounts = void 0;
var web3_js_1 = require("@solana/web3.js");
var types_1 = require("../types");
var getReferralAccounts = function (tokenStakeAccount, userReferralAccount, rebateTokenAccount, privilege) {
    if ((0, types_1.isVariant)(privilege, 'none')) {
        return [];
    }
    if (tokenStakeAccount.equals(web3_js_1.PublicKey.default) || userReferralAccount.equals(web3_js_1.PublicKey.default) || rebateTokenAccount.equals(web3_js_1.PublicKey.default)) {
        console.log("skipping refferals");
        return [];
    }
    var isStake = (0, types_1.isVariant)(privilege, 'stake');
    return [
        {
            pubkey: userReferralAccount,
            isSigner: false,
            isWritable: !isStake,
        },
        {
            pubkey: tokenStakeAccount,
            isSigner: false,
            isWritable: true,
        },
        {
            pubkey: rebateTokenAccount,
            isSigner: false,
            isWritable: !isStake,
        },
    ];
};
exports.getReferralAccounts = getReferralAccounts;
