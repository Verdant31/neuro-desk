import requests
import json
import os
import sys
from datetime import datetime
from helpers.logging_config import get_logger
from utils import get_api_url, get_root_path

logger = get_logger(__name__)
root_path = get_root_path()


class AuthValidator:
    def __init__(self):
        self.auth_server_url = get_api_url()
        self.auth_data_file = os.path.join(root_path, '.auth_cache')

    def _load_cached_auth(self):
        """Carrega dados de autenticação em cache"""
        try:
            if os.path.exists(self.auth_data_file):
                with open(self.auth_data_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Falha ao carregar auth em cache: {e}")
        return None

    def _save_auth_cache(self, auth_data):
        """Salva dados de autenticação em cache"""
        try:
            with open(self.auth_data_file, 'w') as f:
                json.dump(auth_data, f)
        except Exception as e:
            logger.warning(f"Falha ao salvar cache de auth: {e}")

    def _validate_token_online(self, token):
        """Valida token com o servidor de autenticação"""
        try:
            response = requests.post(
                f"{self.auth_server_url}/api/tauri-validate-token",
                headers={
                    "Authorization": f"Bearer {token}",
                },
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException as e:
            logger.warning(f"Falha ao validar token online: {e}")
            return False

    def _validate_subscription_status(self, auth_data):
        """Valida se a assinatura está ativa"""
        if not auth_data or 'subscription_status' not in auth_data:
            return False

        valid_statuses = ['active', 'trialing']
        return auth_data['subscription_status'] in valid_statuses

    def validate_access(self):
        """
        Valida se o usuário tem acesso ao script
        Returns: (is_valid, error_message)
        """
        logger.info("Validando acesso do usuário...")

        # 1. Tenta carregar cache de autenticação
        cached_auth = self._load_cached_auth()
        # 2. Se não há cache, requer autenticação online
        if not cached_auth:
            logger.error(
                "Nenhum dado de autenticação encontrado. Por favor, autentique-se através do app Tauri primeiro.")
            return False, "Autenticação necessária. Por favor, abra o aplicativo OS Assistant e faça login."

        # 3. Valida assinatura
        if not self._validate_subscription_status(cached_auth):
            logger.error("Assinatura inválida ou inativa")
            return False, "Sua assinatura não está ativa. Por favor, verifique o status da sua assinatura."

        # 5. Cache expirado - tenta validar online
        if 'access_token' in cached_auth:
            if self._validate_token_online(cached_auth['access_token']):
                # Atualiza timestamp do cache
                cached_auth['last_validated'] = datetime.now().isoformat()
                self._save_auth_cache(cached_auth)
                logger.info("Token validado online e cache atualizado")
                return True, None
            else:
                logger.error("Falha na validação do token")
                # Remove cache inválido
                if os.path.exists(self.auth_data_file):
                    os.remove(self.auth_data_file)
                return False, "Autenticação expirou. Por favor, faça login novamente através do aplicativo OS Assistant."

        logger.error("Nenhum método de autenticação válido disponível")
        return False, "Autenticação necessária. Por favor, abra o aplicativo OS Assistant e faça login."


def validate_script_access():
    """
    Função de conveniência para validar acesso ao script
    """
    validator = AuthValidator()
    is_valid, error_message = validator.validate_access()

    if not is_valid:
        print(f"\n❌ Acesso Negado: {error_message}")
        print("Por favor, abra o aplicativo OS Assistant e certifique-se de que está logado com uma assinatura ativa.")
        sys.exit(1)

    logger.info("✅ Autenticação validada - iniciando OS Assistant")
    return True
