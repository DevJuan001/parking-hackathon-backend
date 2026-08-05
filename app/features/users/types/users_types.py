from typing import Literal, get_args


ProviderType = Literal["Google", "GitHub", "Local"]
VALID_PROVIDERS: frozenset[str] = frozenset(get_args(ProviderType))