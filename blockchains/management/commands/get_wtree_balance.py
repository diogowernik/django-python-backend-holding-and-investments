from django.core.management.base import BaseCommand
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solana.rpc.types import TokenAccountOpts
import json
import os

class Command(BaseCommand):
    help = 'Obter saldo do token WTREE utilizando JSON parsed'

    def handle(self, *args, **options):
        # Configurações da Solana
        rpc_url = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        wallet_public_key = os.environ.get("SOLANA_WALLET_PUBLIC_KEY")
        token_mint_str = "DSDogw8bYAfNiVHkLqdJKEBNMX3d4Sob7N2tj8oZpump"  # Mint do token WTREE

        if not wallet_public_key:
            self.stdout.write(self.style.ERROR("PUBLIC_KEY não configurado no .env"))
            return

        # Inicializa o cliente Solana
        client = Client(rpc_url)
        wallet_pubkey = Pubkey.from_string(wallet_public_key)
        token_mint = Pubkey.from_string(token_mint_str)
        token_program_id = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")  # SPL Token Program ID

        # Configurar as opções
        opts = TokenAccountOpts(
            program_id=token_program_id,
            mint=token_mint
        )

        try:
            # Obtém as contas associadas ao proprietário com JSON parsed
            response = client.get_token_accounts_by_owner_json_parsed(
                wallet_pubkey,
                opts
            )

            # Exibe a resposta completa para depuração
            print("Resposta completa:", json.dumps(response.value, indent=2))


            # Verifica se existem contas retornadas
            token_accounts = response["result"]["value"]
            if not token_accounts:
                self.stdout.write(self.style.WARNING(
                    f"Nenhuma conta de token encontrada para o mint {token_mint_str}. Você provavelmente não possui WTREE."
                ))
                return

            # Filtra as contas do mint específico
            for account in token_accounts:
                account_data = account["account"]["data"]["parsed"]["info"]
                if account_data["mint"] == token_mint_str:
                    balance = account_data["tokenAmount"]["uiAmount"]
                    decimals = account_data["tokenAmount"]["decimals"]
                    self.stdout.write(self.style.SUCCESS(
                        f"Saldo do token WTREE ({token_mint_str}): {balance} (decimais: {decimals})"
                    ))
                    return

            # Caso nenhuma conta corresponda ao mint
            self.stdout.write(self.style.WARNING(
                f"Nenhuma conta de token correspondente ao mint {token_mint_str} encontrada."
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao buscar saldo do token: {e}"))
