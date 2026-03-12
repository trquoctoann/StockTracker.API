from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
