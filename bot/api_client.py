import httpx
from bot.config import BACKEND_API_URL


class APIError(Exception):
    pass


async def api_request(method: str, path: str, token: str = None, data: dict = None) -> dict:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            if method == "GET":
                response = await client.get(f"{BACKEND_API_URL}{path}", headers=headers, params=data)
            elif method == "POST":
                response = await client.post(f"{BACKEND_API_URL}{path}", headers=headers, json=data)
            elif method == "PUT":
                response = await client.put(f"{BACKEND_API_URL}{path}", headers=headers, json=data)
            else:
                raise APIError(f"Unsupported method: {method}")

            if response.status_code >= 400:
                detail = response.json().get("detail", "Unknown error") if response.text else "Unknown error"
                raise APIError(detail)
            return response.json()
        except httpx.RequestError as e:
            raise APIError(f"Connection error: {str(e)}")


async def login(email: str, password: str) -> dict:
    return await api_request("POST", "/api/v1/auth/login", data={"email": email, "password": password})


async def get_me(token: str) -> dict:
    return await api_request("GET", "/api/v1/auth/me", token=token)


async def get_categories(token: str) -> list:
    return await api_request("GET", "/api/v1/services/categories", token=token)


async def get_services(token: str, category_id: str = None) -> list:
    params = {}
    if category_id:
        params["category_id"] = category_id
    return await api_request("GET", "/api/v1/services", token=token, data=params)


async def create_order(token: str, service_id: str, target_url: str, quantity: int) -> dict:
    return await api_request("POST", "/api/v1/orders", token=token, data={
        "service_id": service_id,
        "target_url": target_url,
        "quantity": quantity,
    })


async def get_my_orders(token: str) -> list:
    return await api_request("GET", "/api/v1/orders", token=token)


async def get_order(token: str, order_id: str) -> dict:
    return await api_request("GET", f"/api/v1/orders/{order_id}", token=token)


async def cancel_order(token: str, order_id: str) -> dict:
    return await api_request("POST", f"/api/v1/orders/{order_id}/cancel", token=token)


async def topup(token: str, amount: float, method: str, tx_reference: str = None) -> dict:
    data = {"amount": amount, "method": method}
    if tx_reference:
        data["tx_reference"] = tx_reference
    return await api_request("POST", "/api/v1/payments/topup", token=token, data=data)
