. Submit Transaction Endpoint
Copy
https://gmgn.ai/txproxy/v1/send_transaction
Request Method: POST

After receiving the routing interface response, decode the base64 string and deserialize using VersionedTransaction, sign with the local wallet, and then encode the signed transaction in base64 and post to the endpoint:

Copy
  const swapTransactionBuf = Buffer.from(route.data.raw_tx.swapTransaction, 'base64')
  const transaction = VersionedTransaction.deserialize(swapTransactionBuf)
  transaction.sign([wallet.payer])
  const signedTx = Buffer.from(transaction.serialize()).toString("base64")
Request Parameters:

chain

string

only suport sol so far

signedTx

string

Signed transaction, base64-encoded string

isAntiMev

bool

Optional, set 'true' when swap with JITO Anti-MEV

Return Parameters:

code

int

Error code, 0

msg

string

Error code, success

data

Object

{
"hash": "2WN388zpPEy5zZR1uDGRqYbWotHFWo2Y6atAwfLGwUvDEi8LGk93X9S5pimNMv4uQgpJNf6SFQbZF83XbvgTuikj"
"resArr": [
{
"hash": "2WN388zpPEy5zZR1uDGRqYbWotHFWo2Y6atAwfLGwUvDEi8LGk93X9S5pimNMv4uQgpJNf6SFQbZF83XbvgTuikj",
"err": null
},
{
"hash": "2WN388zpPEy5zZR1uDGRqYbWotHFWo2Y6atAwfLGwUvDEi8LGk93X9S5pimNMv4uQgpJNf6SFQbZF83XbvgTuikj",
"err": null
}
]
}

3. Transaction Status Query Endpoint:
Copy
https://gmgn.ai/defi/router/v1/sol/tx/get_transaction_status?hash=${hash}&last_valid_height=${lastValidBlockHeight}
Request Method: GET

Request Parameters:

Parameter
Type
Description
hash

string

Transaction hash returned after submission, e.g., 3Qr9Kb8XfQiTa2E4butFRdVgWb9jTorcQaCPx3zx9fETyZhnffVdjagGU7PkwJVX8X9Js4xvUjybCaNjvFGozoLR

last_valid_height

int

Block height at the time of transaction creation, e.g., 221852977

Return Fields:

Parameter
Type
Description
code

int

0

msg

string

success

data

Object

{ success: true, expired: false }

Explanation of data Fields:

success: Whether the transaction was successfully added to the blockchain, true if successful.

failed: Whether the transaction was added to the blockchain but failed, true if it failed.

expired: Whether the transaction has expired. If expired=true and success=false, the transaction has expired and needs to be resubmitted. Generally, a transaction expires after 60 seconds.

If success=true, the transaction has been successfully added to the blockchain.

Example code:

Copy
import { Wallet } from '@project-serum/anchor'
import { Connection, Keypair, VersionedTransaction,LAMPORTS_PER_SOL } from '@solana/web3.js'
import bs58 from 'bs58';
import fetch from 'node-fetch'
import sleep from './util/sleep.js'
const inputToken = 'So11111111111111111111111111111111111111112'
const outputToken = '7EYnhQoR9YM3N7UoaKRoA44Uy8JeaZV3qyouov87awMs'
const amount = '50000000'
const fromAddress = '2kpJ5QRh16aRQ4oLZ5LnucHFDAZtEFz6omqWWMzDSNrx'
const slippage = 0.5
// GMGN API domain
const API_HOST = 'https://gmgn.ai'
async function main() {
  // Wallet initialization, skip this step if using Phantom
  const wallet = new Wallet(Keypair.fromSecretKey(bs58.decode(process.env.PRIVATE_KEY || '')))
  console.log(`wallet address: ${wallet.publicKey.toString()}`)
  // Get quote and unsigned transaction
  const quoteUrl = `${AdPI_HOST}/defi/router/v1/sol/tx/get_swap_route?token_in_address=${inputToken}&token_out_address=${outputToken}&in_amount=${amount}&from_address=${fromAddress}&slippage=${slippage}`
  let route = await fetch(quoteUrl)
  route = await route.json()
  console.log(route)
  // Sign transaction
  const swapTransactionBuf = Buffer.from(route.data.raw_tx.swapTransaction, 'base64')
  const transaction = VersionedTransaction.deserialize(swapTransactionBuf)
  transaction.sign([wallet.payer])
  const signedTx = Buffer.from(transaction.serialize()).toString('base64')
  console.log(signedTx)
  // Submit transaction
  let res = await fetch(`${API_HOST}/txproxy/v1/send_transaction`,
    {
      method: 'POST',
      headers: {'content-type': 'application/json'},
      body: JSON.stringify(
        {
          "chain": "sol",
          "signedTx": signedTx
        }
      )
    })
  res = await res.json()
  console.log(res)
  // Check transaction status
  // If the transaction is successful, success returns true
  // If is does not go through，expired=true will be returned after 60 seconds
  while (true) {
    const hash =  res.data.hash
    const lastValidBlockHeight = route.data.raw_tx.lastValidBlockHeight
    const statusUrl = `${API_HOST}/defi/router/v1/sol/tx/get_transaction_status?hash=${hash}&last_valid_height=${lastValidBlockHeight}`
    let status = await fetch(statusUrl)
    status = await status.json()
    console.log(status)
    if (status && (status.data.success === true || status.data.expired === true))
      break
    await sleep(1000)
  }
}
main()