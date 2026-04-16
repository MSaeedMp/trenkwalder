from dataclasses import dataclass
from enum import Enum
from string import Formatter

from app.core.errors.exceptions import BusinessError


@dataclass(frozen=True)
class ErrorSpec:
    message: str
    exception: type[BusinessError]


class BaseCatalog(Enum):
    def build(self, **params: object) -> BusinessError:
        spec: ErrorSpec = self.value
        expected = _extract_placeholders(spec.message)
        provided = frozenset(params.keys())

        if provided != expected:
            missing = sorted(expected - provided)
            extra = sorted(provided - expected)
            raise ValueError(
                f"{type(self).__name__}.{self.name}: "
                f"expected params {sorted(expected)}, got {sorted(provided)} "
                f"(missing={missing}, extra={extra})"
            )

        return spec.exception(
            spec.message.format(**params),
            code=self.name,
            metadata=dict(params),
        )


def _extract_placeholders(template: str) -> frozenset[str]:
    return frozenset(name for _, name, _, _ in Formatter().parse(template) if name)
