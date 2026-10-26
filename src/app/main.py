from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.routes import item
from app.core.config import settings
from app.core.database import close_db, init_db
from app.schemas.base import ApiResponse

logging.basicConfig(
    level=logging.DEBUG if settings.is_development else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """應用程式生命週期管理：啟動與關閉時各做一次。"""
    await init_db()
    logger.info("%s v%s 啟動完成", settings.APP_NAME, settings.APP_VERSION)
    yield
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=ApiResponse, tags=["Health"])
async def root() -> ApiResponse:
    """根路徑健康檢查。"""
    return ApiResponse(
        data={
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "env": settings.APP_ENV,
        },
        message=f"{settings.APP_NAME} is running",
    )


# ---------- 註冊路由 ----------
# 新增模組時，在此加一行 include_router 即可。
app.include_router(item.router, prefix=settings.API_V1_PREFIX)


# ---------- 全域例外處理 ----------


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """處理 HTTP 例外，回傳統一格式。

    註冊在 Starlette 的 HTTPException 上（FastAPI 的 HTTPException 繼承自它），
    這樣連路由層拋出的 404 / 405 也會走統一格式。
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            success=False,
            message=str(exc.detail),
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """處理請求驗證錯誤，回傳統一格式。"""
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(
            ApiResponse(
                success=False,
                data=exc.errors(),
                message="Validation error",
            ).model_dump()
        ),
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """處理未預期的例外：開發環境回傳細節，正式環境只回傳通用訊息。"""
    logger.exception("未處理的例外：%s %s", request.method, request.url.path)
    message = str(exc) if settings.is_development else "Internal server error"
    return JSONResponse(
        status_code=500,
        content=ApiResponse(success=False, message=message).model_dump(),
    )

