def paginate(page: int, per_page: int) -> tuple[int, int]:
    offset = max(page - 1, 0) * per_page
    return offset, per_page
