from enum import StrEnum
from typing import Any, Literal
from pydantic import BaseModel, field_validator
from .util import Registry


class EntityFilterSelectorConfig(BaseModel):
    integration: str | None = None
    domain: str | list[str] | None = None
    device_class: str | list[str] | None = None
    supported_features: list[str] | None = None


class DeviceFilterSelectorConfig(BaseModel):
    integration: str | None = None
    manufacturer: str | None = None
    model: str | None = None


REGISTRY = Registry()


@REGISTRY.register("action")
class ActionSelector(BaseModel):
    selector_type: Literal["action"]


@REGISTRY.register("addon")
class AddonSelector(BaseModel):
    selector_type: Literal["addon"]
    name: str | None = None
    slug: str | None = None


@REGISTRY.register("area")
class AreaSelector(BaseModel):
    selector_type: Literal["area"]
    entity: EntityFilterSelectorConfig | list[EntityFilterSelectorConfig] | None = None
    device: DeviceFilterSelectorConfig | list[DeviceFilterSelectorConfig] | None = None
    multiple: bool = False


@REGISTRY.register("assist_pipeline")
class AssistPipelineSelector(BaseModel):
    selector_type: Literal["assist_pipeline"]


@REGISTRY.register("attribute")
class AttributeSelector(BaseModel):
    selector_type: Literal["attribute"]
    entity_id: str
    hide_attributes: list[str] = []


@REGISTRY.register("backup_location")
class BackupLocationSelector(BaseModel):
    selector_type: Literal["backup_location"]


@REGISTRY.register("color_rgb")
class ColorRGBSelector(BaseModel):
    selector_type: Literal["color_rgb"]


@REGISTRY.register("color_temp")
class ColorTempSelector(BaseModel):
    selector_type: Literal["color_temp"]
    unit: Literal["kelvin", "mired"] = "mired"
    min: int | None = None
    max: int | None = None
    min_mired: int | None = None
    max_mired: int | None = None


@REGISTRY.register("condition")
class ConditionSelector(BaseModel):
    selector_type: Literal["condition"]


@REGISTRY.register("config_entry")
class ConfigEntrySelector(BaseModel):
    selector_type: Literal["config_entry"]


@REGISTRY.register("qr_code")
class QrCodeSelector(BaseModel):
    selector_type: Literal["qr_code"]
    data: str
    scale: int | None = None
    error_correction_level: Literal["low", "medium", "quartile", "high"] | None = None


@REGISTRY.register("conversation_agent")
class ConversationAgentSelector(BaseModel):
    selector_type: Literal["conversation_agent"]
    language: str | None = None


@REGISTRY.register("country")
class CountrySelector(BaseModel):
    selector_type: Literal["country"]
    countries: list[str] | None = None
    no_sort: bool = False


@REGISTRY.register("date")
class DateSelector(BaseModel):
    selector_type: Literal["date"]


@REGISTRY.register("datetime")
class DateTimeSelector(BaseModel):
    selector_type: Literal["datetime"]


@REGISTRY.register("device")
class DeviceSelector(BaseModel):
    selector_type: Literal["device"]
    entity: EntityFilterSelectorConfig | list[EntityFilterSelectorConfig] | None = None
    multiple: bool = False
    filter: DeviceFilterSelectorConfig | list[DeviceFilterSelectorConfig] | None = None


@REGISTRY.register("duration")
class DurationSelector(BaseModel):
    selector_type: Literal["duration"]
    enable_day: bool | None = None
    allow_negative: bool | None = None


@REGISTRY.register("entity")
class EntitySelector(BaseModel):
    selector_type: Literal["entity"]
    exclude_entities: list[str] | None = None
    include_entities: list[str] | None = None
    multiple: bool = False
    filter: EntityFilterSelectorConfig | list[EntityFilterSelectorConfig] | None = None


@REGISTRY.register("floor")
class FloorSelector(BaseModel):
    selector_type: Literal["floor"]
    entity: EntityFilterSelectorConfig | list[EntityFilterSelectorConfig] | None = None
    device: DeviceFilterSelectorConfig | list[DeviceFilterSelectorConfig] | None = None
    multiple: bool = False


@REGISTRY.register("label")
class LabelSelector(BaseModel):
    selector_type: Literal["label"]
    multiple: bool = False


@REGISTRY.register("language")
class LanguageSelector(BaseModel):
    selector_type: Literal["language"]
    languages: list[str] | None = None
    native_name: bool = False
    no_sort: bool = False


@REGISTRY.register("location")
class LocationSelector(BaseModel):
    selector_type: Literal["location"]
    radius: bool | None = None
    icon: str | None = None


@REGISTRY.register("media")
class MediaSelector(BaseModel):
    selector_type: Literal["media"]


@REGISTRY.register("state")
class StateSelector(BaseModel):
    selector_type: Literal["state"]
    entity_id: str


@REGISTRY.register("target")
class TargetSelector(BaseModel):
    selector_type: Literal["target"]
    entity: EntityFilterSelectorConfig | list[EntityFilterSelectorConfig] | None = None
    device: DeviceFilterSelectorConfig | list[DeviceFilterSelectorConfig] | None = None


@REGISTRY.register("template")
class TemplateSelector(BaseModel):
    selector_type: Literal["template"]


@REGISTRY.register("theme")
class ThemeSelector(BaseModel):
    selector_type: Literal["theme"]


@REGISTRY.register("time")
class TimeSelector(BaseModel):
    selector_type: Literal["time"]


@REGISTRY.register("trigger")
class TriggerSelector(BaseModel):
    selector_type: Literal["trigger"]


@REGISTRY.register("file")
class FileSelector(BaseModel):
    selector_type: Literal["file"]
    accept: str


@REGISTRY.register("icon")
class IconSelector(BaseModel):
    selector_type: Literal["icon"]
    placeholder: str | None = None


class TextSelectorType(StrEnum):
    """Enum for text selector types."""

    COLOR = "color"
    DATE = "date"
    DATETIME_LOCAL = "datetime-local"
    EMAIL = "email"
    MONTH = "month"
    NUMBER = "number"
    PASSWORD = "password"
    SEARCH = "search"
    TEL = "tel"
    TEXT = "text"
    TIME = "time"
    URL = "url"
    WEEK = "week"


@REGISTRY.register("text")
class TextSelector(BaseModel):
    selector_type: Literal["text"]
    multiline: bool = False
    prefix: str | None = None
    suffix: str | None = None
    type: TextSelectorType = TextSelectorType.TEXT
    autocomplete: str | None = None
    multiple: bool = False


class SelectOption(BaseModel):
    label: str
    value: str


@REGISTRY.register("select")
class SelectSelector(BaseModel):
    selector_type: Literal["select"]
    options: list[SelectOption]
    multiple: bool = False
    custom_value: bool = False
    mode: Literal["list", "dropdown"] | None = None
    translation_key: str | None = None
    sort: bool = False

    @field_validator("options")
    @classmethod
    def norm_options(cls, v: list[str | dict[str, str]]) -> list[SelectOption]:
        return [
            (
                SelectOption(label=i, value=i)
                if isinstance(i, str)
                else SelectOption(label=i.get("label", ""), value=i.get("value", ""))
            )
            for i in v
        ]


@REGISTRY.register("number")
class NumberSelector(BaseModel):
    selector_type: Literal["number"]
    min: int | float | None = None
    max: int | float | None = None
    step: int | float | None = None
    mode: Literal["box", "slider"] | None = None
    unit_of_measurement: str | None = None


@REGISTRY.register("boolean")
class BooleanSelector(BaseModel):
    selector_type: Literal["boolean"]


@REGISTRY.register("object")
class ObjectSelector(BaseModel):
    selector_type: Literal["object"]


@REGISTRY.register("constant")
class ConstantSelector(BaseModel):
    selector_type: Literal["constant"]
    value: Any = None
    label: str | None = None


SelectorTypes = (
    SelectSelector
    | AreaSelector
    | DateSelector
    | FileSelector
    | IconSelector
    | TextSelector
    | TimeSelector
    | StateSelector
    | AddonSelector
    | FloorSelector
    | LabelSelector
    | MediaSelector
    | ThemeSelector
    | ActionSelector
    | DeviceSelector
    | EntitySelector
    | NumberSelector
    | ObjectSelector
    | QrCodeSelector
    | TargetSelector
    | BooleanSelector
    | CountrySelector
    | TriggerSelector
    | ColorRGBSelector
    | DateTimeSelector
    | DurationSelector
    | LanguageSelector
    | LocationSelector
    | TemplateSelector
    | AttributeSelector
    | ColorTempSelector
    | ConditionSelector
    | ConstantSelector
    | AssistPipelineSelector
)


class ServiceField(BaseModel):
    id: str
    name: str
    description: str | None = None
    advanced: bool = False
    required: bool = False
    example: str | None = None
    filter: dict | None = None
    selector: SelectorTypes | None = None

    @field_validator("selector")
    @classmethod
    def transform_selector(cls, v: any) -> SelectorTypes | None:
        if isinstance(v, dict):
            if "selector_type" in v.keys():
                constructor = REGISTRY[v["selector_type"]]
                if constructor:
                    return constructor(**v)
                return None
            if len(v.keys()) > 0:
                key = list(v.keys())[0]
                constructor = REGISTRY[key]
                if constructor:
                    return constructor(selector_type=key, **v)
                return None
        return v


class Service(BaseModel):
    domain: str
    service: str
    name: str
    description: str | None = None
    target: dict[str, Any] = {}
    fields: dict[str, ServiceField] = {}
