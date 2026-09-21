class SMMPanelException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InsufficientBalanceError(SMMPanelException):
    def __init__(self):
        super().__init__("Insufficient balance", 402)


class ServiceNotFoundError(SMMPanelException):
    def __init__(self):
        super().__init__("Service not found", 404)


class OrderNotFoundError(SMMPanelException):
    def __init__(self):
        super().__init__("Order not found", 404)


class UnauthorizedError(SMMPanelException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)


class ForbiddenError(SMMPanelException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)


class ProviderAPIError(SMMPanelException):
    def __init__(self, message: str = "Provider API error"):
        super().__init__(message, 502)
