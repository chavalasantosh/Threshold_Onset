"""
Custom exceptions for semantic discovery module.

Enterprise-grade exception hierarchy.
"""


class SemanticDiscoveryError(Exception):
    """Base exception for semantic discovery module."""
    
    def __init__(self, message: str, phase: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.phase = phase
        self.details = details or {}
    
    def __str__(self):
        base = self.message
        if self.phase:
            base = f"[{self.phase}] {base}"
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            base = f"{base} ({details_str})"
        return base


class ConsequenceFieldError(SemanticDiscoveryError):
    """Error in consequence field computation."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, phase="phase5", details=details)


class MeaningDiscoveryError(SemanticDiscoveryError):
    """Error in meaning discovery."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, phase="phase6", details=details)


class RoleEmergenceError(SemanticDiscoveryError):
    """Error in role emergence."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, phase="phase7", details=details)


class ConstraintDiscoveryError(SemanticDiscoveryError):
    """Error in constraint discovery."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, phase="phase8", details=details)


class FluencyGenerationError(SemanticDiscoveryError):
    """Error in fluency generation."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, phase="phase9", details=details)
