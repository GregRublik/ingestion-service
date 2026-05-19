class APIException(Exception):
    def __init__(self, status_code: int, error: str):
        self.status_code = status_code
        self.error = error

class DatabaseUnavailableException(Exception):
    status_code = 503

    def __init__(self, _original_error: Exception):
        self.error = f"Database unavailable" # print(_original_error: Exception)
        print(_original_error)
        super().__init__(self.error)

class ModelAlreadyExistsException(BaseException):
    """Объект уже существует"""

class ModelNotFoundException(Exception):
    """Объект не найден"""

class ModelMultipleResultsFoundException(BaseException):
    """При ожидании одного объекта нашлось несколько экземпляров"""

class DocumentNotFoundException(ModelNotFoundException):
    """Документ не найден"""
    detail = "document not found"

class DocumentAlreadyExistsException(ModelAlreadyExistsException):
    """Документ уже существует"""
    detail = "document already exists"

class DocumentException(BaseException):
    """Ошибка при работе с документом"""

    detail = "Error Document"

class NoSuchBucketException(BaseException):
    """Не найдено хранилище"""

    detail = "no such bucket"
