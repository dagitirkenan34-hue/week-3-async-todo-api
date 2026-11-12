from contextlib import asynccontextmanager
from secrets import compare_digest
from collections.abc import AsyncIterator

from fastapi import (
    APIRouter, Depends, FastAPI, Header,
    HTTPException, Query, status
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import engine, get_session
from app.models import Todo, AuditLog
from app.schemas import (
    EchoRequest, EchoResponse,
    TodoCreate, TodoUpdate,
    TodoResponse, AuditLogResponse
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("Async Todo API başlatıldı!")
    yield
    await engine.dispose()
    print("Veritabanı bağlantısı kapatıldı!")


app = FastAPI(
    title="Async Todo & Log API",
    description="Hafta 3 Python Backend Projesi",
    version="1.0.0",
    lifespan=lifespan,
)


async def verify_api_key(
    x_api_key: str = Header(..., alias="X-API-Key")
):
    if not compare_digest(x_api_key, settings.api_key):
        raise HTTPException(
            status_code=401,
            detail="Geçersiz API Key!"
        )
    return True


router = APIRouter(
    dependencies=[Depends(verify_api_key)]
)


@router.post("/echo", response_model=EchoResponse)
async def echo(data: EchoRequest):
    return EchoResponse(
        message=data.message,
        sender=data.sender,
        success=True
    )


@router.post(
    "/todos",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_todo(
    data: TodoCreate,
    session: AsyncSession = Depends(get_session)
):
    todo = Todo(
        title=data.title,
        description=data.description
    )

    session.add(todo)
    await session.flush()

    session.add(AuditLog(
        action="created",
        details=f"Todo oluşturuldu: {todo.title}",
        todo_id=todo.id
    ))

    await session.commit()

    result = await session.execute(
        select(Todo)
        .options(selectinload(Todo.logs))
        .where(Todo.id == todo.id)
    )

    return result.scalar_one()


@router.get("/todos", response_model=list[TodoResponse])
async def get_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Todo)
        .options(selectinload(Todo.logs))
        .order_by(Todo.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Todo)
        .options(selectinload(Todo.logs))
        .where(Todo.id == todo_id)
    )

    todo = result.scalar_one_or_none()

    if todo is None:
        raise HTTPException(404, "Todo bulunamadı!")

    return todo


@router.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    data: TodoUpdate,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Todo).where(Todo.id == todo_id)
    )
    todo = result.scalar_one_or_none()

    if todo is None:
        raise HTTPException(404, "Todo bulunamadı!")

    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(400, "Güncellenecek alan gönderilmedi!")

    if changes.get("title", "not_provided") is None:
        raise HTTPException(422, "Todo başlığı boş olamaz!")

    if changes.get("completed", "not_provided") is None:
        raise HTTPException(422, "Tamamlanma durumu boş olamaz!")

    for field, value in changes.items():
        setattr(todo, field, value)

    session.add(AuditLog(
        action="updated",
        details=f"Güncellenen alanlar: {', '.join(changes.keys())}",
        todo_id=todo.id
    ))

    await session.commit()

    result = await session.execute(
        select(Todo)
        .options(selectinload(Todo.logs))
        .where(Todo.id == todo_id)
        .execution_options(populate_existing=True)
    )

    return result.scalar_one()


@router.delete("/todos/{todo_id}")
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Todo).where(Todo.id == todo_id)
    )
    todo = result.scalar_one_or_none()

    if todo is None:
        raise HTTPException(404, "Todo bulunamadı!")

    session.add(AuditLog(
        action="deleted",
        details=f"Todo silindi: {todo.title} (ID: {todo.id})",
        todo_id=None
    ))

    await session.delete(todo)
    await session.commit()

    return {"message": "Todo başarıyla silindi!"}


@router.get("/logs", response_model=list[AuditLogResponse])
async def get_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(AuditLog)
        .order_by(AuditLog.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


app.include_router(router)


@app.get("/")
async def root():
    return {
        "message": "Async Todo API çalışıyor!",
        "docs": "/docs"
    }
