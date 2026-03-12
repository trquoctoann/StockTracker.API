from app.core.config import settings


def get_pagination_params(page: int = 1, page_size: int | None = None) -> tuple[int, int]:
    if page_size is None:
        page_size = settings.DEFAULT_PAGE_SIZE
    page_size = min(page_size, settings.MAX_PAGE_SIZE)
    offset = (max(page, 1) - 1) * page_size
    return offset, page_size
