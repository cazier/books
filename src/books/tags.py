import datetime
import uuid

import fastapi
import pydantic


class Book(pydantic.BaseModel):
    title: str = pydantic.Field(alias="sortTitle")
    author: str = pydantic.Field(alias="sortAuthor")


class Tag(pydantic.BaseModel):
    name: str
    description: str = ""
    created: datetime.datetime = pydantic.Field(alias="createTime")
    uuid: pydantic.UUID4 = pydantic.Field(default_factory=uuid.uuid4)
    count: int = pydantic.Field(alias="totalTaggings")


class GetTag(Tag):
    books: list[Book] = pydantic.Field(default_factory=list)


tags = fastapi.APIRouter(prefix="tags")


@tags.get("/")
def tags_get(request: fastapi.Request) -> list[Tag]:
    return []
