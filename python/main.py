from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# Node access params
RPC_URL = "http://alice:password@127.0.0.1:18443"

def main():
    try:
        # General client for non-wallet-specific commands
        client = AuthServiceProxy(RPC_URL)

        # Get blockchain info
        blockchain_info = client.getblockchaininfo()

        print("Blockchain Info:", blockchain_info)

        # Create/Load the wallets, named 'Miner' and 'Trader'. Have logic to optionally create/load them if they do not exist or are not loaded already.

        # Generate spendable balances in the Miner wallet. Determine how many blocks need to be mined.

        # Load the Trader wallet and generate a new address.

        # Send 20 BTC from Miner to Trader.

        # Check the transaction in the mempool.

        # Mine 1 block to confirm the transaction.

        # Extract all required transaction details.

        # Write the data to ../out.txt in the specified format given in readme.md.
    except Exception as e:
        print("Error occurred: {}".format(e))

if __name__ == "__main__":
    main()
