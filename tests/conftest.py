from pathlib import Path

import pytest
from sqlmodel import SQLModel
from sqlmodel.main import default_registry

top_level_path = Path(__file__).resolve().parent.parent
docs_src_path = top_level_path / "docs_src"


@pytest.fixture()
def clear_sqlmodel():
    # Clear the tables in the metadata for the default base model
    SQLModel.metadata.clear()
    # Clear the Models associated with the registry, to avoid warnings
    default_registry.dispose()
    yield
    SQLModel.metadata.clear()
    default_registry.dispose()
