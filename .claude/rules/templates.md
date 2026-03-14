# ファイル作成時のテンプレート

## 新規 entity

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class XxxId:
    value: str


@dataclass
class Xxx:
    id: XxxId
    name: str
```

## 新規 usecase

```python
from abc import ABC, abstractmethod


class XxxUseCase:
    def __init__(self, xxx_repository: XxxRepository) -> None:
        self._xxx_repository = xxx_repository

    async def execute(self, input_dto: XxxInputDto) -> XxxOutputDto:
        ...
```

## 新規 repository インターフェース

```python
from abc import ABC, abstractmethod


class XxxRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id: XxxId) -> Xxx | None: ...

    @abstractmethod
    async def save(self, entity: Xxx) -> None: ...
```

## 新規 router

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/xxx", tags=["xxx"])


@router.get("/")
async def get_xxx_list(
    controller: XxxController = Depends(get_xxx_controller),
) -> list[XxxViewModel]:
    return await controller.get_list()
```

## 新規 port インターフェース

```python
from abc import ABC, abstractmethod


class XxxPort(ABC):
    @abstractmethod
    async def send(self, message: XxxMessage) -> None: ...
```
