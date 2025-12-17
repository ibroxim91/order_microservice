from fastapi import Request

def get_remote_address(request: Request) -> str:
    """
    Returns the remote address of the client.
    If the request is proxied, it returns the IP address from the X-Forwarded-For header.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host
