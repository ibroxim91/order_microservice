from fastapi import Request

def get_remote_address(request: Request) -> str:
    """
    Foydalanuvchi IP manzilini qaytaradi.
    Agar proxy orqali kelgan bo‘lsa, X-Forwarded-For headerdan oladi.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # bir nechta IP bo‘lsa, birinchi IP ni olamiz
        return forwarded.split(",")[0].strip()
    return request.client.host
