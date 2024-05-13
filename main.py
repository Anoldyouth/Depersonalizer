import traceback

from fastapi import FastAPI
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from src.depersonalizer import Depersonalizer

app = FastAPI(
    title="Depersonalizer",
    description="Depersonalizer API",
)


class DepersonalizeRequest(BaseModel):
    text_for_depersonalize: str = Field(
        examples=["Егоров Егор Егорович"],
        description='Текст, содержащий персональные данные'
    )


class DepersonalizeResponse(BaseModel):
    depersonalized_text: str = Field(
        examples=["Иванов Иван Иванович"],
        description='Обезличенный текст'
    )


class Error(BaseModel):
    error_type: str = Field(
        examples=["Exception"],
        description='Тип ошибки'
    )
    error_message: str = Field(
        examples=["Invalid variable type"],
        description='Описание ошибки'
    )
    line_number: int = Field(
        examples=[15],
        description='Номер строки с ошибкой'
    )
    stack_trace: list[str] = Field(
        description='Путь до ошибки'
    )


class ErrorResponse(BaseModel):
    error: Error = Field(
        description='Описание возникшей ошибки'
    )


@app.post(
    '/depersonalize',
    tags=['depersonalize'],
    summary='Метод для обезличивания данных',
    description='Метод предназначен для обезличивания персональных данных в тексте',
    response_model=DepersonalizeResponse,
    response_model_exclude_unset=True,
    responses={
        500: {'model': ErrorResponse, 'description': "Error response"}
    }
)
def depersonalize(
        request: DepersonalizeRequest
) -> DepersonalizeResponse:
    depersonalizer = Depersonalizer()
    result = depersonalizer.handle(request.text_for_depersonalize)

    return DepersonalizeResponse(depersonalized_text=result)


@app.exception_handler(Exception)
async def unexpected_exception_handler(exc: Exception):
    exc_type, exc_value, exc_traceback = exc.__traceback__
    tb_list = traceback.extract_tb(exc_traceback)

    error_info = {
        "error_type": str(exc_type),
        "error_message": str(exc_value),
        "line_number": tb_list[-1][1],
        "stack_trace": traceback.format_tb(exc_traceback)
    }

    return JSONResponse(
        content={"error": error_info},
        status_code=500
    )
