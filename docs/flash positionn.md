import { TransactionInstruction, Signer, PublicKey, ComputeBudgetProgram } from "@solana/web3.js";
import { Side, Privilege } from "flash-sdk";

// Use this when you want to close the position and get the same collateral token back
// For example closing a BTC position getting BTC back 
const closePosition = async (targetTokenSymbol: string, side: Side) => {
    const slippageBps: number = 800 // 0.8%
    const instructions: TransactionInstruction[] = []
    let additionalSigners: Signer[] = []

    const targetToken = POOL_CONFIG.tokens.find(t => t.symbol === targetTokenSymbol)!;
    const userRecievingToken = POOL_CONFIG.tokens.find(t => t.symbol === targetTokenSymbol)!;

   const priceMap = await getPrices();

    const targetTokenPrice = priceMap.get(targetTokenSymbol)!.price

    const priceAfterSlippage = flashClient.getPriceAfterSlippage(false, new BN(slippageBps), targetTokenPrice, side)

    const openPositionData =await flashClient.closePosition(
        targetToken.symbol,
        userRecievingToken.symbol,
        priceAfterSlippage,
        side,
        POOL_CONFIG,
        Privilege.None
    )

    instructions.push(...openPositionData.instructions)
    additionalSigners.push(...openPositionData.additionalSigners)

    const setCULimitIx = ComputeBudgetProgram.setComputeUnitLimit({ units: 600_000 }) // addLiquidity
    const trxId = await flashClient.sendTransaction([setCULimitIx, ...instructions])
    console.log('trxId :>> ', trxId);
}

closePosition('BTC', Side.Long);
Open position with different Collateral:
Copy
import { getMint } from "@solana/spl-token";
import { TransactionInstruction, Signer, PublicKey, ComputeBudgetProgram } from "@solana/web3.js";
import { Side, uiDecimalsToNative, PoolAccount, PoolDataClient, CustodyAccount, BN_ZERO, BPS_DECIMALS, Privilege } from "flash-sdk";

const openPositionWithSwap = async (inputTokenSymbol: string, outputTokenSymbol: string, inputAmount: string, side: Side) => {

    const slippageBps: number = 800 // 0.8%

    const instructions: TransactionInstruction[] = []
    let additionalSigners: Signer[] = []

    const inputToken = POOL_CONFIG.tokens.find(t => t.symbol === inputTokenSymbol)!;
    const outputToken = POOL_CONFIG.tokens.find(t => t.symbol === outputTokenSymbol)!;

    const priceMap = await getPrices();

    const inputTokenPrice = priceMap.get(inputToken.symbol)!.price
    const inputTokenPriceEma = priceMap.get(inputToken.symbol)!.emaPrice
    const outputTokenPrice = priceMap.get(outputToken.symbol)!.price
    const outputTokenPriceEma = priceMap.get(outputToken.symbol)!.emaPrice

    await flashClient.loadAddressLookupTable(POOL_CONFIG)

    const priceAfterSlippage = flashClient.getPriceAfterSlippage(
        true,
        new BN(slippageBps),
        outputTokenPrice,
        side
    )

    const collateralWithFee = uiDecimalsToNative(inputAmount, inputToken.decimals);
    const leverage = 1.1;

    const inputCustody = POOL_CONFIG.custodies.find(c => c.symbol === inputToken.symbol)!;
    const outputCustody = POOL_CONFIG.custodies.find(c => c.symbol === outputToken.symbol)!;

    const custodies = await flashClient.program.account.custody.fetchMultiple([inputCustody.custodyAccount, outputCustody.custodyAccount]);
    const poolAccount = PoolAccount.from(POOL_CONFIG.poolAddress, await flashClient.program.account.pool.fetch(POOL_CONFIG.poolAddress));

    const allCustodies = await flashClient.program.account.custody.all()

    const lpMintData = await getMint(flashClient.provider.connection, POOL_CONFIG.stakedLpTokenMint);

    const poolDataClient = new PoolDataClient(
        POOL_CONFIG,
        poolAccount,
        lpMintData,
        [...allCustodies.map(c => CustodyAccount.from(c.publicKey, c.account))],
    )

    let lpStats = poolDataClient.getLpStats(await getPrices())

    const inputCustodyAccount = CustodyAccount.from(inputCustody.custodyAccount, custodies[0]!);
    const ouputCustodyAccount = CustodyAccount.from(outputCustody.custodyAccount, custodies[1]!);
    
    const size = flashClient.getSizeAmountWithSwapSync(
        collateralWithFee,
        leverage.toString(),
        Side.Long,
        poolAccount,
        inputTokenPrice,
        inputTokenPriceEma,
        inputCustodyAccount,
        outputTokenPrice,
        outputTokenPriceEma,
        ouputCustodyAccount,
        outputTokenPrice,
        outputTokenPriceEma,
        ouputCustodyAccount,
        outputTokenPrice,
        outputTokenPriceEma,
        ouputCustodyAccount,
        lpStats.totalPoolValueUsd,
        POOL_CONFIG,
        uiDecimalsToNative(`${5}`, 2) // trading discount depending on your nft level
    )

    const minAmountOut = flashClient.getSwapAmountAndFeesSync(
        collateralWithFee,
        BN_ZERO,
        poolAccount,
        inputTokenPrice,
        inputTokenPriceEma,
        CustodyAccount.from(inputCustody.custodyAccount, custodies[0]!),
        outputTokenPrice,
        outputTokenPriceEma,
        CustodyAccount.from(outputCustody.custodyAccount, custodies[1]!),
        lpStats.totalPoolValueUsd,
        POOL_CONFIG
    ).minAmountOut

    const minAmountOutAfterSlippage = minAmountOut
        .mul(new BN(10 ** BPS_DECIMALS - slippageBps))
        .div(new BN(10 ** BPS_DECIMALS))

    const openPositionData = await flashClient.swapAndOpen(
        outputToken.symbol,
        outputToken.symbol,
        inputToken.symbol,
        collateralWithFee,
        minAmountOutAfterSlippage,
        priceAfterSlippage,
        size,
        side,
        POOL_CONFIG,
        Privilege.None
    )

    instructions.push(...openPositionData.instructions)
    additionalSigners.push(...openPositionData.additionalSigners)

    const setCULimitIx = ComputeBudgetProgram.setComputeUnitLimit({ units: 600_000 }) // addLiquidity
    const trxId = await flashClient.sendTransaction([setCULimitIx, ...instructions])

    console.log('trx :>> ', trxId);
}
Close Position and Receive Collateral in a Different Token:
Copy
import { TransactionInstruction, Signer, PublicKey, ComputeBudgetProgram } from "@solana/web3.js";
import { CustodyAccount, PositionAccount, getUnixTs, Privilege } from "flash-sdk";

const closePositionWithSwap = async (userRecievingTokenSymbol: string) => {  
    const slippageBps: number = 800 // 0.8%

    const instructions: TransactionInstruction[] = []
    let additionalSigners: Signer[] = []

    // get all your positions
    const positions = await flashClient.getUserPositions(flashClient.provider.publicKey, POOL_CONFIG);

    // choose the position you want to close
    const positionToClose = positions[1];

    const marketConfig = POOL_CONFIG.markets.find(f => f.marketAccount.equals(positionToClose.market))!;

    const custodies = await flashClient.program.account.custody.fetchMultiple([marketConfig.targetCustody, marketConfig.collateralCustody]);

    const userRecievingToken = POOL_CONFIG.tokens.find(t => t.symbol === userRecievingTokenSymbol)!;
    const targetCustodyAccount = CustodyAccount.from(marketConfig.targetCustody, custodies[0]!);
    const collateralCustodyAccount = CustodyAccount.from(marketConfig.collateralCustody, custodies[1]!);
    const side = marketConfig.side!;
    const positionAccount = PositionAccount.from(positionToClose.pubkey, positionToClose);;

    const targetToken = POOL_CONFIG.tokens.find(t => t.mintKey.equals(marketConfig.targetMint))!;
    const collateralToken = POOL_CONFIG.tokens.find(t => t.mintKey.equals(marketConfig.collateralMint))!;

    const priceMap = await getPrices()

    const targetTokenPrice = priceMap.get(targetToken.symbol)!.price
    const targetTokenPriceEma = priceMap.get(targetToken.symbol)!.emaPrice
    const collateralTokenPrice = priceMap.get(collateralToken.symbol)!.price
    const collateralTokenPriceEma = priceMap.get(collateralToken.symbol)!.emaPrice
    const userRecievingTokenPrice = priceMap.get(userRecievingToken.symbol)!.price

    const { closeAmount, feesAmount } = flashClient.getFinalCloseAmountSync(
        positionAccount,
        marketConfig.targetCustody.equals(marketConfig.collateralCustody),
        marketConfig.side,
        targetTokenPrice,
        targetTokenPriceEma,
        targetCustodyAccount,
        collateralTokenPrice,
        collateralTokenPriceEma,
        collateralCustodyAccount,
        new BN(getUnixTs()),
        POOL_CONFIG
    )

    const receiveUsd = collateralTokenPrice.getAssetAmountUsd(closeAmount, collateralToken.decimals)

    const minAmountOut = userRecievingTokenPrice.getTokenAmount(
        receiveUsd,
        userRecievingToken.decimals
    )

    const priceAfterSlippage = flashClient.getPriceAfterSlippage(false, new BN(slippageBps), targetTokenPrice, side)

    const minAmountOutWithSlippage = minAmountOut
        .mul(new BN(100 - Number(0.8)))
        .div(new BN(100))
    
    const closePositionWithSwapData = await flashClient.closeAndSwap(
        targetToken.symbol,
        userRecievingToken.symbol,
        collateralToken.symbol,
        minAmountOutWithSlippage,
        priceAfterSlippage,
        side,
        POOL_CONFIG,
        Privilege.None
    )

    instructions.push(...closePositionWithSwapData.instructions)
    additionalSigners.push(...closePositionWithSwapData.additionalSigners)

    const setCULimitIx = ComputeBudgetProgram.setComputeUnitLimit({ units: 600_000 }) // addLiquidity
    const trxId = await flashClient.sendTransaction([setCULimitIx, ...instructions])

    console.log('trx :>> ', trxId);
}

closePositionWithSwap('USDC')
Set Full or Partial Take Profit or Stop Loss on an Existing Position:
NOTE : 
Stop Loss:

Must be above Liquidation Price and below Current Price for LONG

Must be below Liquidation Price above Current Price for SHORT

Take Profit:

Must be above Current Price for LONG

Must be below Current Price for SHORT

Virtual tokens Take Profit must be below Max Profit Price for LONG

Copy
const setTpAndSlForMarket = async (takeProfitPriceUi: number | undefined, stopLossPriceUi: number | undefined, market: PublicKey) => {
    const marketConfig = POOL_CONFIG.markets.find(f => f.marketAccount.equals(market))!;

    if (!marketConfig) return

    const targetCustodyConfig = POOL_CONFIG.custodies.find(c => c.custodyAccount.equals(marketConfig.targetCustody))!;
    const collateralCustodyConfig = POOL_CONFIG.custodies.find(c => c.custodyAccount.equals(marketConfig.collateralCustody))!;

    let instructions: TransactionInstruction[] = []
    let additionalSigners: Signer[] = []
    let COMPUTE_LIMIT = 0

    const position = (await flashClient.getUserPositions(flashClient.provider.publicKey, POOL_CONFIG)).filter(f => !f.sizeAmount.isZero()).find(p => p.market.equals(market));

    if(!position) throw new Error(`No open position for market : ${market.toBase58()}`)

    if (takeProfitPriceUi) {
        const triggerPriceNative = uiDecimalsToNative(takeProfitPriceUi.toString(), targetCustodyConfig.decimals);

        const triggerOraclePrice = new OraclePrice({
            price: new BN(triggerPriceNative.toString()),
            exponent:( new BN(targetCustodyConfig.decimals)).neg(),
            confidence: BN_ZERO,
            timestamp: BN_ZERO,
        })
        
        // also for Virtual tokens Take Profit must be below Max Profit Price for LONG 
        // if (targetCustodyConfig.isVirtual && isVariant(marketConfig.side, 'long')) {
        //     const maxProfitPrice = perpClient.getMaxProfitPriceSync(
        //         position.entryOraclePrice,
        //         false,
        //         isVariant(marketConfig.side, 'long') ? Side.Long : Side.Short,
        //         position.positionAccount
        //     )
        //     const maxProfitPriceUi = maxProfitPrice.toUiPrice(8)
        //     const maxProfitNum = Number(maxProfitPriceUi)
        //     if (takeProfitPriceUi >= maxProfitNum) {
        //         throw Error("Take Profit must be below Max Profit Price");
        //         return;
        //     }
        // }

        const triggerContractOraclePrice = triggerOraclePrice.toContractOraclePrice()

        const result = await flashClient.placeTriggerOrder(
            targetCustodyConfig.symbol,
            collateralCustodyConfig.symbol,
            isVariant(marketConfig.side, 'long') ? Side.Long : Side.Short,
            triggerContractOraclePrice,
            position.sizeAmount, // can be partial amount here
            false,
            collateralCustodyConfig.custodyId,
            POOL_CONFIG
        )
        instructions.push(...result.instructions)
        additionalSigners.push(...result.additionalSigners)
        COMPUTE_LIMIT = 90_000
    }

    if (stopLossPriceUi) {
        const triggerPriceNative = uiDecimalsToNative(stopLossPriceUi.toString(), targetCustodyConfig.decimals);

        const triggerOraclePrice = new OraclePrice({
            price: new BN(triggerPriceNative.toString()),
            exponent:( new BN(targetCustodyConfig.decimals)).neg(),
            confidence: BN_ZERO,
            timestamp: BN_ZERO,
        })

        const triggerContractOraclePrice = triggerOraclePrice.toContractOraclePrice()

        const result = await flashClient.placeTriggerOrder(
            targetCustodyConfig.symbol,
            collateralCustodyConfig.symbol,
            isVariant(marketConfig.side, 'long') ? Side.Long : Side.Short,
            triggerContractOraclePrice,
            position.sizeAmount, // can be partial amount here
            true,
            collateralCustodyConfig.custodyId,
            POOL_CONFIG
        )
        instructions.push(...result.instructions)
        additionalSigners.push(...result.additionalSigners)
        COMPUTE_LIMIT = COMPUTE_LIMIT + 90_000
    }

    const setCULimitIx = ComputeBudgetProgram.setComputeUnitLimit({ units: COMPUTE_LIMIT })

    await flashClient.loadAddressLookupTable(POOL_CONFIG)

    const trxId = await flashClient.sendTransaction([setCULimitIx, ...instructions])

    console.log('trx :>> ', trxId);
}

setTpAndSlForMarket(
    300, // $300
    100, // $100
    new PublicKey('3vHoXbUvGhEHFsLUmxyC6VWsbYDreb1zMn9TAp5ijN5K'), // sol long market
)
Getting Liquidation Price of Current Active Position 
Copy
const getLiquidationPrice = async (positionPubKey : PublicKey) => {
   
    const data =  await flashClient.getLiquidationPriceView(positionPubKey, POOL_CONFIG)
    if(!data){
        throw new Error('position not found')
    }
     const LiqOraclePrice = OraclePrice.from({
                        price: data.price,
                        exponent: new BN(data.exponent),
                        confidence: new BN(0),
                        timestamp: new BN(0),
                    })

    console.log('price :>> ', LiqOraclePrice.toUiPrice(6) );
    return LiqOraclePrice.toUiPrice(6) // 6 is the decimals precision for liquidation price, you can change it based on your needs
}