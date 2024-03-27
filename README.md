## Async-SQLModel

Async-SQLModel is an extension module of [SQLmodel](https://sqlmodel.tiangolo.com/). It enables the creation of awaitable fields in SQLModel, making it compatible with asynchronous programming, particularly beneficial when utilizing asynchronous relationship fields.

Async-SQLModel is based on Python type annotations, and compatible with existing SQLModel models.

Async-SQLModel is available under the [MIT License](./LICENSE).

## Installation

```
$ pip install async-sqlmodel
```

## Usage

### Create a AsyncSQLModel Model

You could create a **AsyncSQLModel** model like this:

```python
from typing import Optional

from sqlmodel import Field
from async_sqlmodel import AsyncSQLModel


class Hero(AsyncSQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
```

### Add an AwaitableField

Adding an **AwaitableField** yields an awaitable field for the `field` specified in the argument.

```python
from typing import Optional
from collections.abc import Awaitable

from sqlmodel import Field
from async_sqlmodel import AsyncSQLModel, AwaitableField


class Hero(AsyncSQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    awt_name: Awaitable[str] = AwaitableField(field="name")
```

This allows fields which may be subject to lazy loading or deferred / unexpiry loading to be accessed like this:

```python
hero = Hero(name="Rusty-Man")
async_session.add(hero)
await async_session.commit()

# the fields of "hero" have expired.
# Therefore, accessing them will raise MissingGreenlet error
print(hero.name)
# E    sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; 
#      can't call await_only() here. Was IO attempted in an unexpected place? 
#      (Background on this error at: https://sqlalche.me/e/20/xd2s) 

# it works!
print(await hero.awt_name) # Rusty-Man
```

### Use an AwaitableField with Relationship

You can use an **AwaitableField** with **Relationship**.

```python
from typing import Optional
from collections.abc import Awaitable

from sqlmodel import Field, select
from async_sqlmodel import AsyncSQLModel, AwaitableField


class Team(AsyncSQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    heroes: List["Hero"] = Relationship()
    awt_heroes: Awaitable[List["Hero"]] = AwaitableField(field="heroes")


class Hero(AsyncSQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    team: Optional[Team] = Relationship(back_populates="heroes")
    awt_team: Awaitable[Optional[Team]] = AwaitableField(field="team")
```

Using an with Relationship fields can resolve the issues encountered during lazy loading:

```python
hero = (
    await session.exec(select(Hero).where(Hero.id == hero_rusty_man.id))
).one()

# loading lazy loading attribute will raise MissingGreenlet error
team = hero.team 
# E    sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; 
#      can't call await_only() here. Was IO attempted in an unexpected place? 
#      (Background on this error at: https://sqlalche.me/e/20/xd2s) 

# it works!
team = await hero.awt_team
```