from typing import Literal
from pydantic import BaseModel


class MarkSchema(BaseModel):
    type: Literal["circle", "bar"]


class FieldSchema(BaseModel):
    field: str
    type: Literal["quantitative", "temporal", "ordinal", "nominal"]


class EncodingSchema(BaseModel):
    x: FieldSchema
    y: FieldSchema
    color: FieldSchema | None = None


class VegaLiteSchema(BaseModel):
    mark: MarkSchema
    encoding: EncodingSchema
