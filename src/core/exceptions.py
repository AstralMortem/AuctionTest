from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette import status as status
from .log import logger


class AuctionError(Exception):
    def __init__(
        self,
        code: int,
        title: str,
        message: str | None = None,
        detail: dict | None = None,
        headers: dict | None = None,
    ):
        self.code = code
        self.title = title
        self.message = message
        self.detail = detail
        self.headers = headers

    def to_response(self):
        payload = {
            "status_code": self.code,
            "title": self.title,
            "message": self.message,
        }
        if self.detail:
            payload["detail"] = self.detail
        logger.error(f"[{self.code}] {self.title} - {self.message}")
        return JSONResponse(payload, status_code=self.code, headers=self.headers)


def set_errror(app: FastAPI):
    @app.exception_handler(AuctionError)
    async def handle_auction_error(request, exc: AuctionError):
        return exc.to_response()
