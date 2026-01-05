"""
Service de paiement pour le Maroc
Implémentation complète des gateways marocains

Gateways supportés:
- CMI (Centre Monétique Interbancaire)
- PayZen (Lyra)
- Orange Money
- Inwi Money
- Maroc Telecom Cash

Author: ShareYourSales Team
Date: 2026-01-04
"""

import hashlib
import hmac
import base64
import requests
from typing import Dict, Optional, List
from datetime import datetime
import secrets
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class CMIPaymentGateway:
    """
    Intégration CMI (Centre Monétique Interbancaire du Maroc)
    Documentation: https://www.cmi.co.ma/
    """

    def __init__(self, store_key: str, client_id: str, environment: str = "production"):
        """
        Initialise le gateway CMI

        Args:
            store_key: Clé secrète fournie par CMI
            client_id: Identifiant client CMI
            environment: 'production' ou 'test'
        """
        self.store_key = store_key
        self.client_id = client_id
        self.environment = environment

        # URLs selon environnement
        if environment == "production":
            self.base_url = "https://payment.cmi.co.ma/fim/est3Dgate"
        else:
            self.base_url = "https://testpayment.cmi.co.ma/fim/est3Dgate"

    def _generate_hash(self, params: Dict[str, str]) -> str:
        """
        Génère le hash HMAC-SHA512 pour CMI

        Args:
            params: Paramètres de la transaction

        Returns:
            Hash encodé en base64
        """
        # Concaténer les paramètres dans l'ordre CMI
        data_to_hash = (
            f"{params['clientid']}|"
            f"{params['amount']}|"
            f"{params['currency']}|"
            f"{params['oid']}|"
            f"{params['okUrl']}|"
            f"{params['failUrl']}|"
            f"{params['TranType']}|"
            f"{params['rnd']}"
        )

        # HMAC-SHA512
        signature = hmac.new(
            self.store_key.encode('utf-8'),
            data_to_hash.encode('utf-8'),
            hashlib.sha512
        ).digest()

        # Base64
        return base64.b64encode(signature).decode('utf-8')

    def create_payment(
        self,
        amount: float,
        currency: str = "504",  # 504 = MAD (Dirham marocain)
        order_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_name: Optional[str] = None,
        description: Optional[str] = None,
        callback_success_url: str = "",
        callback_failure_url: str = ""
    ) -> Dict[str, str]:
        """
        Crée une transaction de paiement CMI

        Args:
            amount: Montant en MAD
            currency: Code devise (504 pour MAD)
            order_id: ID commande unique
            customer_email: Email client
            customer_name: Nom client
            description: Description paiement
            callback_success_url: URL de retour si succès
            callback_failure_url: URL de retour si échec

        Returns:
            Dict contenant l'URL de paiement et les paramètres
        """
        # Génération order ID si non fourni
        if not order_id:
            order_id = f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"

        # Montant au format CMI (en centimes)
        amount_cmi = str(int(amount * 100))

        # Paramètres requis par CMI
        params = {
            "clientid": self.client_id,
            "amount": amount_cmi,
            "currency": currency,
            "oid": order_id,
            "okUrl": callback_success_url,
            "failUrl": callback_failure_url,
            "TranType": "PreAuth",  # ou "Auth" pour capture immédiate
            "rnd": secrets.token_hex(16),
            "encoding": "UTF-8",
            "lang": "fr",
            "storetype": "3D_PAY_HOSTING",
            "hashAlgorithm": "ver3"
        }

        # Paramètres optionnels
        if customer_email:
            params["email"] = customer_email
        if customer_name:
            params["BillToName"] = customer_name
        if description:
            params["shopurl"] = description

        # Générer le hash de sécurité
        params["hash"] = self._generate_hash(params)

        logger.info(f"CMI payment created: {order_id} - {amount} MAD")

        return {
            "payment_url": self.base_url,
            "params": params,
            "order_id": order_id,
            "method": "POST"
        }

    def verify_callback(self, response_data: Dict[str, str]) -> Dict[str, any]:
        """
        Vérifie le callback de retour CMI

        Args:
            response_data: Données reçues du callback CMI

        Returns:
            Dict avec statut de validation
        """
        # Vérifier le hash de retour
        received_hash = response_data.get("HASH")
        received_hashparams = response_data.get("HASHPARAMS")

        # Reconstruire le hash
        hash_data = ""
        if received_hashparams:
            params_list = received_hashparams.split(":")
            for param in params_list:
                if param in response_data:
                    hash_data += response_data[param] + "|"

        # Ajouter store_key
        hash_data += self.store_key

        # Calculer hash
        calculated_hash = base64.b64encode(
            hashlib.sha512(hash_data.encode('utf-8')).digest()
        ).decode('utf-8')

        # Vérifier
        is_valid = (calculated_hash == received_hash)

        # Statut transaction
        proc_return_code = response_data.get("ProcReturnCode", "")
        response_code = response_data.get("Response", "")

        success = (
            is_valid and
            proc_return_code == "00" and
            response_code == "Approved"
        )

        return {
            "valid": is_valid,
            "success": success,
            "order_id": response_data.get("oid"),
            "transaction_id": response_data.get("TransId"),
            "amount": float(response_data.get("amount", 0)) / 100,
            "message": response_data.get("ErrMsg", ""),
            "raw_data": response_data
        }


class PayZenGateway:
    """
    Intégration PayZen (Lyra Network) pour le Maroc
    Documentation: https://payzen.io/
    """

    def __init__(self, shop_id: str, secret_key: str, environment: str = "production"):
        """
        Initialise le gateway PayZen

        Args:
            shop_id: Identifiant boutique PayZen
            secret_key: Clé secrète PayZen
            environment: 'production' ou 'test'
        """
        self.shop_id = shop_id
        self.secret_key = secret_key
        self.environment = environment

        # URLs selon environnement
        if environment == "production":
            self.base_url = "https://secure.payzen.eu/vads-payment/"
        else:
            self.base_url = "https://secure.payzen.eu/vads-payment/"

    def _calculate_signature(self, params: Dict[str, str]) -> str:
        """
        Calcule la signature PayZen (SHA256)

        Args:
            params: Paramètres de la transaction

        Returns:
            Signature encodée
        """
        # Trier les paramètres par clé (vads_*)
        sorted_params = sorted(
            [(k, v) for k, v in params.items() if k.startswith('vads_')],
            key=lambda x: x[0]
        )

        # Concaténer valeurs
        content = "+".join([str(v) for k, v in sorted_params])

        # Ajouter la clé secrète
        content += "+" + self.secret_key

        # SHA256
        signature = hashlib.sha256(content.encode('utf-8')).hexdigest()

        return signature

    def create_payment(
        self,
        amount: float,
        currency: str = "504",  # 504 = MAD
        order_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_info: Optional[Dict] = None,
        callback_url: str = ""
    ) -> Dict[str, any]:
        """
        Crée une transaction PayZen

        Args:
            amount: Montant en MAD
            currency: Code devise (504 pour MAD)
            order_id: ID commande
            customer_email: Email client
            customer_info: Infos client (nom, adresse, etc.)
            callback_url: URL de notification

        Returns:
            Dict avec URL et paramètres de paiement
        """
        if not order_id:
            order_id = f"PZ_{datetime.now().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"

        # Montant en centimes
        amount_cents = str(int(amount * 100))

        # Timestamp
        trans_date = datetime.now().strftime("%Y%m%d%H%M%S")

        # Paramètres PayZen (préfixe vads_)
        params = {
            "vads_site_id": self.shop_id,
            "vads_ctx_mode": "TEST" if self.environment == "test" else "PRODUCTION",
            "vads_trans_id": secrets.token_hex(3),  # 6 caractères
            "vads_trans_date": trans_date,
            "vads_amount": amount_cents,
            "vads_currency": currency,
            "vads_action_mode": "INTERACTIVE",
            "vads_page_action": "PAYMENT",
            "vads_version": "V2",
            "vads_payment_config": "SINGLE",
            "vads_order_id": order_id,
            "vads_url_return": callback_url
        }

        # Informations client
        if customer_email:
            params["vads_cust_email"] = customer_email

        if customer_info:
            if "name" in customer_info:
                params["vads_cust_name"] = customer_info["name"]
            if "phone" in customer_info:
                params["vads_cust_phone"] = customer_info["phone"]
            if "address" in customer_info:
                params["vads_cust_address"] = customer_info["address"]
            if "city" in customer_info:
                params["vads_cust_city"] = customer_info["city"]
            if "zip" in customer_info:
                params["vads_cust_zip"] = customer_info["zip"]
            if "country" in customer_info:
                params["vads_cust_country"] = customer_info["country"]

        # Calculer signature
        params["signature"] = self._calculate_signature(params)

        logger.info(f"PayZen payment created: {order_id} - {amount} MAD")

        return {
            "payment_url": self.base_url,
            "params": params,
            "order_id": order_id,
            "method": "POST"
        }

    def verify_callback(self, response_data: Dict[str, str]) -> Dict[str, any]:
        """
        Vérifie le callback PayZen

        Args:
            response_data: Données reçues

        Returns:
            Dict avec statut de validation
        """
        received_signature = response_data.get("signature", "")

        # Recalculer signature
        calculated_signature = self._calculate_signature(response_data)

        is_valid = (received_signature == calculated_signature)

        # Statut transaction
        trans_status = response_data.get("vads_trans_status", "")
        success = (is_valid and trans_status == "AUTHORISED")

        return {
            "valid": is_valid,
            "success": success,
            "order_id": response_data.get("vads_order_id"),
            "transaction_id": response_data.get("vads_trans_id"),
            "amount": float(response_data.get("vads_amount", 0)) / 100,
            "status": trans_status,
            "raw_data": response_data
        }


class OrangeMoneyGateway:
    """
    Intégration Orange Money Maroc
    Mobile money pour paiements via téléphone
    """

    def __init__(self, merchant_code: str, api_key: str, environment: str = "production"):
        """
        Initialise Orange Money

        Args:
            merchant_code: Code marchand Orange Money
            api_key: Clé API
            environment: 'production' ou 'test'
        """
        self.merchant_code = merchant_code
        self.api_key = api_key
        self.environment = environment

        if environment == "production":
            self.base_url = "https://api.orange.com/orange-money-webpay/ma/v1"
        else:
            self.base_url = "https://api.orange.com/orange-money-webpay/dev/v1"

    def create_payment(
        self,
        amount: float,
        phone_number: str,
        order_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Crée un paiement Orange Money

        Args:
            amount: Montant en MAD
            phone_number: Numéro téléphone client (format: 06XXXXXXXX)
            order_id: ID commande
            description: Description paiement

        Returns:
            Dict avec token de paiement
        """
        if not order_id:
            order_id = f"OM_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "merchant_key": self.merchant_code,
            "currency": "OUV",  # OUV = Orange Unit Value (équivalent MAD)
            "order_id": order_id,
            "amount": int(amount),
            "return_url": "",
            "cancel_url": "",
            "notif_url": "",
            "lang": "fr",
            "reference": order_id,
            "payment_method": "mobile_money",
            "customer": {
                "msisdn": phone_number.replace("+212", "").replace(" ", "")
            }
        }

        if description:
            payload["description"] = description

        try:
            response = requests.post(
                f"{self.base_url}/webpayment",
                json=payload,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            logger.info(f"Orange Money payment created: {order_id}")

            return {
                "success": True,
                "payment_token": data.get("payment_token"),
                "payment_url": data.get("payment_url"),
                "order_id": order_id,
                "expires_at": data.get("expire_at")
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Orange Money API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class InwiMoneyGateway:
    """
    Intégration Inwi Money Maroc
    Mobile money wallet pour paiements via téléphone
    """

    def __init__(self, merchant_id: str, api_key: str, environment: str = "production"):
        """
        Initialise Inwi Money

        Args:
            merchant_id: ID marchand Inwi Money
            api_key: Clé API
            environment: 'production' ou 'test'
        """
        self.merchant_id = merchant_id
        self.api_key = api_key
        self.environment = environment

        if environment == "production":
            self.base_url = "https://api.inwi.ma/payment/v1"
        else:
            self.base_url = "https://sandbox.inwi.ma/payment/v1"

    def create_payment(
        self,
        amount: float,
        phone_number: str,
        order_id: Optional[str] = None,
        description: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Crée un paiement Inwi Money

        Args:
            amount: Montant en MAD
            phone_number: Numéro téléphone client (format: 06XXXXXXXX)
            order_id: ID commande
            description: Description paiement
            callback_url: URL de callback

        Returns:
            Dict avec résultat de paiement
        """
        if not order_id:
            order_id = f"INWI_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Merchant-ID": self.merchant_id
        }

        # Format du numéro: retirer +212 et espaces
        clean_phone = phone_number.replace("+212", "").replace(" ", "")

        payload = {
            "merchant_id": self.merchant_id,
            "order_id": order_id,
            "amount": float(amount),
            "currency": "MAD",
            "customer_phone": clean_phone,
            "description": description or f"Paiement commande {order_id}",
            "callback_url": callback_url or "",
            "return_url": callback_url or "",
            "language": "fr"
        }

        try:
            response = requests.post(
                f"{self.base_url}/init",
                json=payload,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            logger.info(f"Inwi Money payment created: {order_id}")

            return {
                "success": True,
                "transaction_id": data.get("transaction_id"),
                "payment_url": data.get("payment_url"),
                "order_id": order_id,
                "status": data.get("status", "pending"),
                "expires_at": data.get("expires_at")
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Inwi Money API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "order_id": order_id
            }

    def check_payment_status(self, transaction_id: str) -> Dict[str, any]:
        """
        Vérifie le statut d'un paiement Inwi Money

        Args:
            transaction_id: ID de transaction Inwi

        Returns:
            Dict avec statut du paiement
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Merchant-ID": self.merchant_id
        }

        try:
            response = requests.get(
                f"{self.base_url}/status/{transaction_id}",
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": data.get("status"),
                "amount": data.get("amount"),
                "order_id": data.get("order_id")
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Inwi Money status check error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class MarocTelecomCashGateway:
    """
    Intégration Maroc Telecom Cash (MT Cash)
    Service de paiement mobile de Maroc Telecom
    """

    def __init__(self, merchant_code: str, api_key: str, secret_key: str, environment: str = "production"):
        """
        Initialise MT Cash

        Args:
            merchant_code: Code marchand MT Cash
            api_key: Clé API
            secret_key: Clé secrète pour signatures
            environment: 'production' ou 'test'
        """
        self.merchant_code = merchant_code
        self.api_key = api_key
        self.secret_key = secret_key
        self.environment = environment

        if environment == "production":
            self.base_url = "https://api.mtcash.ma/v2"
        else:
            self.base_url = "https://sandbox.mtcash.ma/v2"

    def _generate_signature(self, params: Dict[str, str]) -> str:
        """
        Génère la signature HMAC-SHA256 pour MT Cash

        Args:
            params: Paramètres de la transaction

        Returns:
            Signature encodée
        """
        # Trier les paramètres par clé
        sorted_params = sorted(params.items())

        # Concaténer clé=valeur avec &
        data_string = "&".join([f"{k}={v}" for k, v in sorted_params])

        # HMAC-SHA256
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            data_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return signature

    def create_payment(
        self,
        amount: float,
        phone_number: str,
        order_id: Optional[str] = None,
        description: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Crée un paiement MT Cash

        Args:
            amount: Montant en MAD
            phone_number: Numéro téléphone client (format: 06XXXXXXXX ou 07XXXXXXXX)
            order_id: ID commande
            description: Description paiement
            callback_url: URL de callback

        Returns:
            Dict avec résultat de paiement
        """
        if not order_id:
            order_id = f"MTCASH_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Format du numéro
        clean_phone = phone_number.replace("+212", "").replace(" ", "")

        # Paramètres pour signature
        params = {
            "merchant_code": self.merchant_code,
            "order_id": order_id,
            "amount": str(int(amount * 100)),  # Montant en centimes
            "currency": "MAD",
            "customer_phone": clean_phone,
            "timestamp": datetime.now().isoformat()
        }

        # Générer signature
        signature = self._generate_signature(params)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Signature": signature
        }

        payload = {
            **params,
            "description": description or f"Paiement {order_id}",
            "callback_url": callback_url or "",
            "return_url": callback_url or "",
            "language": "fr"
        }

        try:
            response = requests.post(
                f"{self.base_url}/payments/create",
                json=payload,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            logger.info(f"MT Cash payment created: {order_id}")

            return {
                "success": True,
                "transaction_id": data.get("transaction_id"),
                "payment_token": data.get("payment_token"),
                "payment_url": data.get("payment_url"),
                "order_id": order_id,
                "status": data.get("status", "initiated"),
                "qr_code": data.get("qr_code_url"),  # MT Cash supporte les QR codes
                "expires_at": data.get("expires_at")
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"MT Cash API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "order_id": order_id
            }

    def verify_callback(self, response_data: Dict[str, str]) -> Dict[str, any]:
        """
        Vérifie le callback MT Cash

        Args:
            response_data: Données reçues du callback

        Returns:
            Dict avec statut de validation
        """
        received_signature = response_data.get("signature", "")

        # Retirer la signature pour recalculer
        params_to_verify = {k: v for k, v in response_data.items() if k != "signature"}

        # Recalculer signature
        calculated_signature = self._generate_signature(params_to_verify)

        is_valid = (received_signature == calculated_signature)

        # Statut transaction
        transaction_status = response_data.get("status", "")
        success = (is_valid and transaction_status == "completed")

        return {
            "valid": is_valid,
            "success": success,
            "order_id": response_data.get("order_id"),
            "transaction_id": response_data.get("transaction_id"),
            "amount": float(response_data.get("amount", 0)) / 100,
            "status": transaction_status,
            "raw_data": response_data
        }


class MoroccoPaymentService:
    """
    Service unifié pour tous les paiements Maroc
    """

    def __init__(self, config: Dict[str, Dict]):
        """
        Initialise le service avec config pour tous les gateways

        Args:
            config: Configuration des gateways
                {
                    "cmi": {"store_key": "...", "client_id": "..."},
                    "payzen": {"shop_id": "...", "secret_key": "..."},
                    "orange_money": {"merchant_code": "...", "api_key": "..."},
                    "inwi_money": {"merchant_id": "...", "api_key": "..."},
                    "maroc_telecom": {"merchant_code": "...", "api_key": "...", "secret_key": "..."}
                }
        """
        self.cmi = None
        self.payzen = None
        self.orange_money = None
        self.inwi_money = None
        self.maroc_telecom = None

        # Initialiser les gateways disponibles
        if "cmi" in config:
            self.cmi = CMIPaymentGateway(**config["cmi"])

        if "payzen" in config:
            self.payzen = PayZenGateway(**config["payzen"])

        if "orange_money" in config:
            self.orange_money = OrangeMoneyGateway(**config["orange_money"])

        if "inwi_money" in config:
            self.inwi_money = InwiMoneyGateway(**config["inwi_money"])

        if "maroc_telecom" in config:
            self.maroc_telecom = MarocTelecomCashGateway(**config["maroc_telecom"])

    def create_payment(
        self,
        provider: str,
        amount: float,
        **kwargs
    ) -> Dict[str, any]:
        """
        Crée un paiement avec le provider spécifié

        Args:
            provider: 'cmi', 'payzen', 'orange_money', 'inwi_money', ou 'maroc_telecom'
            amount: Montant en MAD
            **kwargs: Paramètres spécifiques au provider

        Returns:
            Résultat de création de paiement
        """
        if provider == "cmi" and self.cmi:
            return self.cmi.create_payment(amount, **kwargs)
        elif provider == "payzen" and self.payzen:
            return self.payzen.create_payment(amount, **kwargs)
        elif provider == "orange_money" and self.orange_money:
            return self.orange_money.create_payment(amount, **kwargs)
        elif provider == "inwi_money" and self.inwi_money:
            return self.inwi_money.create_payment(amount, **kwargs)
        elif provider == "maroc_telecom" and self.maroc_telecom:
            return self.maroc_telecom.create_payment(amount, **kwargs)
        else:
            return {
                "success": False,
                "error": f"Provider {provider} not configured or not available"
            }

    def verify_callback(self, provider: str, response_data: Dict) -> Dict:
        """
        Vérifie un callback de paiement

        Args:
            provider: 'cmi', 'payzen', 'orange_money', 'inwi_money', ou 'maroc_telecom'
            response_data: Données reçues

        Returns:
            Résultat de vérification
        """
        if provider == "cmi" and self.cmi:
            return self.cmi.verify_callback(response_data)
        elif provider == "payzen" and self.payzen:
            return self.payzen.verify_callback(response_data)
        elif provider == "maroc_telecom" and self.maroc_telecom:
            return self.maroc_telecom.verify_callback(response_data)
        else:
            return {
                "valid": False,
                "error": f"Provider {provider} not configured"
            }

    def get_available_providers(self) -> List[str]:
        """
        Retourne la liste des providers configurés et disponibles

        Returns:
            Liste des noms de providers disponibles
        """
        providers = []
        if self.cmi:
            providers.append("cmi")
        if self.payzen:
            providers.append("payzen")
        if self.orange_money:
            providers.append("orange_money")
        if self.inwi_money:
            providers.append("inwi_money")
        if self.maroc_telecom:
            providers.append("maroc_telecom")
        return providers
