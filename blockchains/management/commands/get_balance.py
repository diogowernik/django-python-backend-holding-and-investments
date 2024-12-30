from django.core.management.base import BaseCommand
from django.conf import settings
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import os

class Command(BaseCommand):
    help = 'Obter saldo de SOL'

    def handle(self, *args, **options):
        rpc_url = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        public_key_str = os.environ.get("SOLANA_WALLET_PUBLIC_KEY")

        if not public_key_str:
            self.stdout.write(self.style.ERROR("A PUBLIC_KEY da wallet não está configurada no .env"))
            return

        client = Client(rpc_url)
        wallet_address = Pubkey.from_string(public_key_str)

        # Obter saldo em SOL
        sol_response = client.get_balance(wallet_address)
        sol_balance = sol_response.value / 1_000_000_000
        self.stdout.write(self.style.SUCCESS(f"Saldo da carteira {public_key_str}: {sol_balance} SOL"))
