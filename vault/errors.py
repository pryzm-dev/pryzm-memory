"""Erreurs du coffre. Les messages ne contiennent jamais de contenu ni de secret."""


class VaultError(Exception):
    pass


class VaultLocked(VaultError):
    """Compte scellé, mais aucune clé de coffre ouverte pour cette requête."""


class VaultBusy(VaultError):
    """Scellement en cours : écritures suspendues quelques secondes."""


class VaultTampered(VaultError):
    """Valeur chiffrée altérée, mauvaise clé ou mauvais contexte (AAD)."""


class WrongSecret(VaultError):
    """Mot de passe, phrase ou jeton incapable d'ouvrir l'enveloppe."""


class SealVerifyError(VaultError):
    """Une valeur chiffrée ne redonne pas exactement l'original."""
