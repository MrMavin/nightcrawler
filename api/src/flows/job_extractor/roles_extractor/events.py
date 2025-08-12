from llama_index.core.workflow import (
    Event,
)


class RolesExtractorEvent(Event):
    roles: str
