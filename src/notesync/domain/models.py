"""Pure order values and product validation; no storage or platform access."""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


MAX_NOTE_COMMENTS = 1000


class ContractError(ValueError):
    """Input or requested transition violates the manual POC contract."""


def normalized(value: str) -> str:
    return unicodedata.normalize("NFKC", value).upper().strip()


@dataclass(frozen=True)
class ProductConfig:
    scope_key: str
    note_key: str
    aliases: dict[str, str]
    limits: dict[str, int]
    default_sku: str | None
    document: dict

    @classmethod
    def from_document(cls, doc: dict) -> ProductConfig:
        require_keys(doc, {"format_version", "scope_key", "note_key", "products", "default_sku"})
        if type(doc["format_version"]) is not int or doc["format_version"] != 1:
            raise ContractError("商品設定版本必須是整數 1")
        scope, note = nonempty(doc["scope_key"]), nonempty(doc["note_key"])
        if not isinstance(doc["products"], list) or not doc["products"]:
            raise ContractError("商品清單不得為空")
        limits: dict[str, int] = {}
        aliases: dict[str, str] = {}
        for product in doc["products"]:
            require_keys(product, {"sku", "name", "aliases", "max_quantity"})
            sku = normalized(nonempty(product["sku"]))
            nonempty(product["name"])
            if not re.fullmatch(r"[A-Z][A-Z0-9_-]{0,31}", sku) or sku in limits:
                raise ContractError("SKU 須為唯一 ASCII 代號（最多 32 字元）")
            maximum = product["max_quantity"]
            if type(maximum) is not int or not 1 <= maximum <= 999999:
                raise ContractError("數量上限必須是 1–999999 的整數")
            if not isinstance(product["aliases"], list):
                raise ContractError("aliases 必須是清單")
            for alias in [sku, *product["aliases"]]:
                key = normalized(nonempty(alias))
                if not re.fullmatch(r"[A-Z][A-Z0-9_-]{0,31}", key):
                    raise ContractError("POC 商品別名只支援 ASCII 代號")
                if key in aliases and aliases[key] != sku:
                    raise ContractError("商品代號／別名衝突")
                aliases[key] = sku
            limits[sku] = maximum
        default = doc["default_sku"]
        if default is not None:
            default = normalized(nonempty(default))
            if default not in limits:
                raise ContractError("預設商品不存在")
        return cls(scope, note, aliases, limits, default, doc)


def nonempty(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError("必要文字欄位不得為空")
    return value


def require_keys(value: object, keys: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != keys:
        raise ContractError(f"欄位必須完全符合：{', '.join(sorted(keys))}")


@dataclass(frozen=True)
class ParseResult:
    status: str
    items: dict[str, int]
    reason: str
