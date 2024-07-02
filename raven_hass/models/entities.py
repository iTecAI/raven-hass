from datetime import date, datetime, time
from enum import IntEnum, IntFlag, StrEnum
from typing import Any, ClassVar, Literal
from pydantic import BaseModel, computed_field, model_validator
from .util import Registry, RegisteredModel
from .service import Service
from .ws_messages import WSResult

REGISTRY = Registry()

class Platform(StrEnum):

    AIR_QUALITY = "air_quality"
    ALARM_CONTROL_PANEL = "alarm_control_panel"
    BINARY_SENSOR = "binary_sensor"
    BUTTON = "button"
    CALENDAR = "calendar"
    CAMERA = "camera"
    CLIMATE = "climate"
    CONVERSATION = "conversation"
    COVER = "cover"
    DATE = "date"
    DATETIME = "datetime"
    DEVICE_TRACKER = "device_tracker"
    EVENT = "event"
    FAN = "fan"
    GEO_LOCATION = "geo_location"
    HUMIDIFIER = "humidifier"
    IMAGE = "image"
    IMAGE_PROCESSING = "image_processing"
    LAWN_MOWER = "lawn_mower"
    LIGHT = "light"
    LOCK = "lock"
    MAILBOX = "mailbox"
    MEDIA_PLAYER = "media_player"
    NOTIFY = "notify"
    NUMBER = "number"
    REMOTE = "remote"
    SCENE = "scene"
    SELECT = "select"
    SENSOR = "sensor"
    SIREN = "siren"
    STT = "stt"
    SWITCH = "switch"
    TEXT = "text"
    TIME = "time"
    TODO = "todo"
    TTS = "tts"
    VACUUM = "vacuum"
    VALVE = "valve"
    UPDATE = "update"
    WAKE_WORD = "wake_word"
    WATER_HEATER = "water_heater"
    WEATHER = "weather"


class UnitOfTemperature(StrEnum):
    """Temperature units."""

    CELSIUS = "°C"
    FAHRENHEIT = "°F"
    KELVIN = "K"


class HAContext(BaseModel):
    id: str
    parent_id: str | None = None
    user_id: str | None = None


class EntityCategory(StrEnum):
    CONFIG = "config"
    DIAGNOSTIC = "diagnostic"


class BinaryState(StrEnum):
    STATE_ON = "on"
    STATE_OFF = "off"


class BaseAttributes(BaseModel):
    assumed_state: bool = False
    attribution: str | None = None
    available: bool = True
    device_class: str | None = None
    entity_picture: str | None = None
    extra_state_attributes: dict | None = None
    has_entity_name: bool = False
    name: str | None = None
    should_poll: bool = True
    state: str | int | float | None = None
    supported_features: int | None = None
    translation_key: str | None = None
    translation_placeholders: dict | None = None
    device_info: dict | None = None
    entity_category: EntityCategory | None = None
    entity_registry_enabled_default: bool = True
    entity_registry_visible_default: bool = True
    unique_id: str | None = None
    capability_attributes: dict | None = None
    force_update: bool = False
    icon: str | None = None
    state_attributes: dict | None = None
    unit_of_measurement: str | None = None
    enabled: bool = True


@REGISTRY.register("entity_base")
class HAEntity(RegisteredModel):
    entity_id: str
    domain: str
    name: str
    state: str | int | float | bool | None
    last_changed: datetime
    last_updated: datetime
    context: HAContext
    attributes: BaseAttributes

    def is_domain(self, domain: str) -> bool:
        return domain == self.domain

    @model_validator(mode="before")
    @classmethod
    def expand_id(cls, data: Any) -> Any:
        if isinstance(data, dict):
            _data = data.copy()
        elif isinstance(data, BaseModel):
            _data = data.model_dump()
        else:
            raise ValueError("Invalid data type")

        parts = data["entity_id"].split(".", maxsplit=1)
        if len(parts) == 2:
            _data["domain"] = parts[0]
            _data["name"] = parts[1]

        return _data

    @classmethod
    def resolve_entity(cls, data: dict) -> "HAEntity | None":
        if "entity_id" in data.keys():
            domain = data["entity_id"].split(".")[0]
            constructor = REGISTRY[domain]
            if constructor:
                return constructor(**data)

            try:
                return HAEntity(**data)
            except:
                pass
        return None

    async def call_service(
        self, service: Service | str, data: dict | None = None
    ) -> WSResult:
        if isinstance(service, Service):
            domain = service.domain
            svc = service.service
        else:
            domain, svc = service.split(".", maxsplit=1)

        return await self.client.send_ws_command(
            "call_service",
            domain=domain,
            service=svc,
            service_data=data,
            target={"entity_id": self.entity_id},
        )


# Alarm control panel


class AlarmControlPanelStates(StrEnum):
    DISARMED = "disarmed"
    ARMED_HOME = "armed_home"
    ARMED_AWAY = "armed_away"
    ARMED_NIGHT = "armed_night"
    ARMED_VACATION = "armed_vacation"
    ARMED_CUSTOM = "armed_custom_bypass"
    PENDING = "pending"
    ARMING = "arming"
    DISARMING = "disarming"
    TRIGGERED = "triggered"


class AlarmControlPanelCodeFormat(StrEnum):
    TEXT = "text"
    NUMBER = "number"


class AlarmControlPanelEntityFeature(IntFlag):
    ARM_HOME = 1
    ARM_AWAY = 2
    ARM_NIGHT = 4
    TRIGGER = 8
    ARM_CUSTOM_BYPASS = 16
    ARM_VACATION = 32


class AlarmControlPanelAttributes(BaseAttributes):
    state: AlarmControlPanelStates | None
    code_arm_required: bool = True
    changed_by: str | None = None
    supported_features: AlarmControlPanelEntityFeature | None = None


@REGISTRY.register(Platform.ALARM_CONTROL_PANEL)
class AlarmControlPanelEntity(HAEntity):
    domain: Literal[Platform.ALARM_CONTROL_PANEL]
    attributes: AlarmControlPanelAttributes


# Binary sensor


class BinarySensorDeviceClass(StrEnum):
    BATTERY = "battery"
    BATTERY_CHARGING = "battery_charging"
    CO = "carbon_monoxide"
    COLD = "cold"
    CONNECTIVITY = "connectivity"
    DOOR = "door"
    GARAGE_DOOR = "garage_door"
    GAS = "gas"
    HEAT = "heat"
    LIGHT = "light"
    LOCK = "lock"
    MOISTURE = "moisture"
    MOTION = "motion"
    MOVING = "moving"
    OCCUPANCY = "occupancy"
    OPENING = "opening"
    PLUG = "plug"
    POWER = "power"
    PRESENCE = "presence"
    PROBLEM = "problem"
    RUNNING = "running"
    SAFETY = "safety"
    SMOKE = "smoke"
    SOUND = "sound"
    TAMPER = "tamper"
    UPDATE = "update"
    VIBRATION = "vibration"
    WINDOW = "window"


class BinarySensorAttributes(BaseAttributes):
    is_on: bool | None = None
    device_class: BinarySensorDeviceClass | None = None


@REGISTRY.register(Platform.BINARY_SENSOR)
class BinarySensorEntity(HAEntity):
    domain: Literal[Platform.BINARY_SENSOR]
    attributes: BinarySensorAttributes


# Button


class ButtonDeviceClass(StrEnum):
    IDENTIFY = "identify"
    RESTART = "restart"
    UPDATE = "update"


class ButtonAttributes(BaseAttributes):
    device_class: ButtonDeviceClass | None = None


@REGISTRY.register(Platform.BUTTON, "input_button")
class ButtonEntity(HAEntity):
    domain: Literal[Platform.BUTTON]
    attributes: ButtonAttributes

    def is_domain(self, domain: str) -> bool:
        return domain in [Platform.BUTTON, "input_button"]


# Calendar


class CalendarEvent(BaseModel):
    start: datetime | date
    end: datetime | date
    summary: str
    location: str | None = None
    description: str | None = None
    uid: str | None = None
    recurrence_id: str | None = None
    rrule: str | None = None


class CalendarEntityFeature(IntFlag):
    CREATE_EVENT = 1
    DELETE_EVENT = 2
    UPDATE_EVENT = 4


class CalendarAttributes(BaseAttributes):
    supported_features: CalendarEntityFeature | None = None
    event: CalendarEvent | None = None


@REGISTRY.register(Platform.CALENDAR)
class CalendarEntity(HAEntity):
    domain: Literal[Platform.CALENDAR]
    state: BinaryState | None
    attributes: CalendarAttributes


# Camera


class CameraEntityFeature(IntFlag):
    ON_OFF = 1
    STREAM = 2


class CameraStreamType(StrEnum):
    HLS = "hls"
    WEB_RTC = "web_rtc"


class CameraAttributes(BaseAttributes):
    supported_features: CameraEntityFeature | None = None
    brand: str | None = None
    frame_interval: float = 0.5
    frontend_stream_type: CameraStreamType | None = None
    is_on: bool = True
    is_recording: bool = False
    is_streaming: bool = False
    model: str | None = None
    motion_detection_enabled: bool = False
    use_stream_for_stills: bool = False


@REGISTRY.register(Platform.CAMERA)
class CameraEntity(HAEntity):
    domain: Literal[Platform.CAMERA]
    attributes: CameraAttributes


# Climate


class HVACMode(StrEnum):
    OFF = "off"
    HEAT = "heat"
    COOL = "cool"
    HEAT_COOL = "heat_cool"
    AUTO = "auto"
    DRY = "dry"
    FAN_ONLY = "fan_only"


class HVACAction(StrEnum):
    COOLING = "cooling"
    DRYING = "drying"
    FAN = "fan"
    HEATING = "heating"
    IDLE = "idle"
    OFF = "off"
    PREHEATING = "preheating"


class ClimateEntityFeature(IntFlag):
    TARGET_TEMPERATURE = 1
    TARGET_TEMPERATURE_RANGE = 2
    TARGET_HUMIDITY = 4
    FAN_MODE = 8
    PRESET_MODE = 16
    SWING_MODE = 32
    AUX_HEAT = 64
    TURN_OFF = 128
    TURN_ON = 256


class ClimateAttributes(BaseAttributes):
    current_humidity: float | None = None
    current_temperature: float | None = None
    fan_mode: str | None = None
    fan_modes: list[str] | None = None
    hvac_action: HVACAction | None = None
    hvac_mode: HVACMode | None = None
    hvac_modes: list[HVACMode] = []
    max_humidity: float = 99
    max_temp: float = 35
    min_humidity: float = 30
    min_temp: float = 7
    precision: float = 1
    preset_mode: str | None = None
    preset_modes: list[str] | None = None
    swing_mode: str | None = None
    swing_modes: list[str] | None = None
    target_humidity: float | None = None
    target_temperature: float | None = None
    target_temperature_high: float | None = None
    target_temperature_low: float | None = None
    target_temperature_step: float | None = None
    temperature_unit: UnitOfTemperature | str = UnitOfTemperature.CELSIUS
    supported_features: ClimateEntityFeature | None = None


@REGISTRY.register(Platform.CLIMATE)
class ClimateEntity(HAEntity):
    domain: Literal[Platform.CLIMATE]
    attributes: ClimateAttributes


# Conversation


class ConversationAttributes(BaseAttributes):
    supported_languages: list[str] | Literal["*"]


@REGISTRY.register(Platform.CONVERSATION)
class ConversationEntity(HAEntity):
    domain: Literal[Platform.CONVERSATION]
    attributes: ConversationAttributes


# Cover


class CoverDeviceClass(StrEnum):
    AWNING = "awning"
    BLIND = "blind"
    CURTAIN = "curtain"
    DAMPER = "damper"
    DOOR = "door"
    GARAGE = "garage"
    GATE = "gate"
    SHADE = "shade"
    SHUTTER = "shutter"
    WINDOW = "window"


class CoverEntityFeature(IntFlag):
    OPEN = 1
    CLOSE = 2
    SET_POSITION = 4
    STOP = 8
    OPEN_TILT = 16
    CLOSE_TILT = 32
    STOP_TILT = 64
    SET_TILT_POSITION = 128


class CoverAttributes(BaseAttributes):
    current_cover_position: int | None = None
    current_cover_tilt_position: int | None = None
    is_closed: bool | None = None
    is_closing: bool | None = None
    is_opening: bool | None = None
    device_class: CoverDeviceClass | None = None
    supported_features: CoverEntityFeature | None = None


@REGISTRY.register(Platform.COVER)
class CoverEntity(HAEntity):
    domain: Literal[Platform.COVER]
    attributes: CoverAttributes


# Date


class DateAttributes(BaseAttributes):
    native_value: date | None = None


@REGISTRY.register(Platform.DATE)
class DateEntity(HAEntity):
    domain: Literal[Platform.DATE]
    attributes: DateAttributes


# Datetime


class DateTimeAttributes(BaseAttributes):
    native_value: datetime | None = None


@REGISTRY.register(Platform.DATETIME, "input_datetime")
class DateTimeEntity(HAEntity):
    domain: Literal[Platform.DATETIME]
    attributes: DateAttributes

    def is_domain(self, domain: str) -> bool:
        return domain in [Platform.DATETIME, "input_datetime"]


# Device trackers


class SourceType(StrEnum):
    GPS = "gps"
    ROUTER = "router"
    BLUETOOTH = "bluetooth"
    BLUETOOTH_LE = "bluetooth_le"


class ScannerAttributes(BaseAttributes):
    battery_level: int | None = None
    hostname: str | None = None
    ip_address: str | None = None
    is_connected: bool = False
    mac_address: str | None = None
    source_type: SourceType | None = None


class TrackerAttributes(BaseAttributes):
    battery_level: int | None = None
    latitude: float | None = None
    location_accuracy: int = 0
    location_name: str | None = None
    longitude: float | None = None
    source_type: SourceType | None = None


@REGISTRY.register(Platform.DEVICE_TRACKER)
class DeviceTrackerEntity(HAEntity):
    domain: Literal[Platform.DEVICE_TRACKER]
    attributes: ScannerAttributes | TrackerAttributes

    @computed_field
    @property
    def tracker_type(self) -> Literal["scanner", "tracker"]:
        return (
            "scanner" if isinstance(self.attributes, ScannerAttributes) else "tracker"
        )


# Event


class EventDeviceClass(StrEnum):
    BUTTON = "button"
    DOORBELL = "doorbell"
    MOTION = "motion"


class EventAttributes(BaseAttributes):
    event_types: list[str] = []
    device_class: EventDeviceClass | None = None


@REGISTRY.register(Platform.EVENT)
class EventEntity(HAEntity):
    domain: Literal[Platform.EVENT]
    attributes: EventAttributes


# Fan


class FanEntityFeature(IntFlag):
    SET_SPEED = 1
    OSCILLATE = 2
    DIRECTION = 4
    PRESET_MODE = 8


class FanAttributes(BaseAttributes):
    current_direction: str | None = None
    is_on: bool | None = None
    oscillating: bool | None = None
    percentage: int | None = 0
    preset_mode: str | None = None
    preset_modes: list[str] | None = None
    speed_count: int = 100
    supported_features: FanEntityFeature | None = None


@REGISTRY.register(Platform.FAN)
class FanEntity(HAEntity):
    domain: Literal[Platform.FAN]
    attributes: FanAttributes


# Humidifier


class HumidifierDeviceClass(StrEnum):
    HUMIDIFIER = "humidifier"
    DEHUMIDIFIER = "dehumidifier"


class HumidifierAction(StrEnum):
    HUMIDIFYING = "humidifying"
    DRYING = "drying"
    IDLE = "idle"
    OFF = "off"


class HumidifierEntityFeature(IntFlag):
    MODES = 1


class HumidifierAttributes(BaseAttributes):
    action: HumidifierAction | None = None
    available_modes: list[str] | None = None
    current_humidity: float | None = None
    device_class: HumidifierDeviceClass | None = None
    is_on: bool | None = None
    max_humidity: float = 100
    min_humidity: float = 0
    mode: str | None = None
    target_humidity: float | None = None
    supported_features: HumidifierEntityFeature | None = None


@REGISTRY.register(Platform.HUMIDIFIER)
class HumidifierEntity(HAEntity):
    domain: Literal[Platform.HUMIDIFIER]
    attributes: HumidifierAttributes


# Image


class ImageAttributes(BaseAttributes):
    content_type: str = "image/jpeg"
    image_last_updated: datetime | None = None
    image_url: str | None = None


@REGISTRY.register(Platform.IMAGE)
class ImageEntity(HAEntity):
    domain: Literal[Platform.IMAGE]
    attributes: ImageAttributes


# Lawn mower


class LawnMowerActivity(StrEnum):
    ERROR = "error"
    PAUSED = "paused"
    MOWING = "mowing"
    DOCKED = "docked"


class LawnMowerEntityFeature(IntFlag):
    START_MOWING = 1
    PAUSE = 2
    DOCK = 4


class LawnMowerAttributes(BaseAttributes):
    activity: LawnMowerActivity | None = None
    supported_features: LawnMowerEntityFeature | None = None


@REGISTRY.register(Platform.LAWN_MOWER)
class LawnMowerEntity(HAEntity):
    domain: Literal[Platform.LAWN_MOWER]
    attributes: LawnMowerAttributes


# Light


class LightEntityFeature(IntFlag):
    EFFECT = 4
    FLASH = 8
    TRANSITION = 32


class ColorMode(StrEnum):
    UNKNOWN = "unknown"
    ONOFF = "onoff"
    BRIGHTNESS = "brightness"
    COLOR_TEMP = "color_temp"
    HS = "hs"
    XY = "xy"
    RGB = "rgb"
    RGBW = "rgbw"
    RGBWW = "rgbww"
    WHITE = "white"


class LightAttributes(BaseAttributes):
    brightness: int | None = None
    color_mode: ColorMode | None = None
    color_temp_kelvin: int | None = None
    effect: str | None = None
    effect_list: list[str] | None = None
    hs_color: tuple[float, float] | None = None
    is_on: bool | None = None
    max_color_temp_kelvin: int | None = None
    min_color_temp_kelvin: int | None = None
    rgb_color: tuple[int, int, int] | None = None
    rgbw_color: tuple[int, int, int, int] | None = None
    rgbww_color: tuple[int, int, int, int, int] | None = None
    supported_color_modes: list[ColorMode] | None = None
    xy_color: tuple[float, float] | None = None
    supported_features: LightEntityFeature | None = None


@REGISTRY.register(Platform.LIGHT)
class LightEntity(HAEntity):
    domain: Literal[Platform.LIGHT]
    attributes: LightAttributes


# Lock


class LockFeatures(IntFlag):
    OPEN = 1


class LockAttributes(BaseAttributes):
    changed_by: str | None = None
    code_format: str | None = None
    is_locked: bool | None = None
    is_locking: bool | None = None
    is_unlocking: bool | None = None
    is_jammed: bool | None = None
    is_opening: bool | None = None
    is_open: bool | None = None
    supported_features: LockFeatures | None = None


@REGISTRY.register(Platform.LOCK)
class LockEntity(HAEntity):
    domain: Literal[Platform.LOCK]
    attributes: LockAttributes


# Media player


class MediaPlayerState(StrEnum):
    """State of media player entities."""

    OFF = "off"
    ON = "on"
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    STANDBY = "standby"
    BUFFERING = "buffering"


class MediaClass(StrEnum):
    """Media class for media player entities."""

    ALBUM = "album"
    APP = "app"
    ARTIST = "artist"
    CHANNEL = "channel"
    COMPOSER = "composer"
    CONTRIBUTING_ARTIST = "contributing_artist"
    DIRECTORY = "directory"
    EPISODE = "episode"
    GAME = "game"
    GENRE = "genre"
    IMAGE = "image"
    MOVIE = "movie"
    MUSIC = "music"
    PLAYLIST = "playlist"
    PODCAST = "podcast"
    SEASON = "season"
    TRACK = "track"
    TV_SHOW = "tv_show"
    URL = "url"
    VIDEO = "video"


class MediaType(StrEnum):
    """Media type for media player entities."""

    ALBUM = "album"
    APP = "app"
    APPS = "apps"
    ARTIST = "artist"
    CHANNEL = "channel"
    CHANNELS = "channels"
    COMPOSER = "composer"
    CONTRIBUTING_ARTIST = "contributing_artist"
    EPISODE = "episode"
    GAME = "game"
    GENRE = "genre"
    IMAGE = "image"
    MOVIE = "movie"
    MUSIC = "music"
    PLAYLIST = "playlist"
    PODCAST = "podcast"
    SEASON = "season"
    TRACK = "track"
    TVSHOW = "tvshow"
    URL = "url"
    VIDEO = "video"


class RepeatMode(StrEnum):
    """Repeat mode for media player entities."""

    ALL = "all"
    OFF = "off"
    ONE = "one"


class MediaPlayerEntityFeature(IntFlag):
    """Supported features of the media player entity."""

    PAUSE = 1
    SEEK = 2
    VOLUME_SET = 4
    VOLUME_MUTE = 8
    PREVIOUS_TRACK = 16
    NEXT_TRACK = 32

    TURN_ON = 128
    TURN_OFF = 256
    PLAY_MEDIA = 512
    VOLUME_STEP = 1024
    SELECT_SOURCE = 2048
    STOP = 4096
    CLEAR_PLAYLIST = 8192
    PLAY = 16384
    SHUFFLE_SET = 32768
    SELECT_SOUND_MODE = 65536
    BROWSE_MEDIA = 131072
    REPEAT_SET = 262144
    GROUPING = 524288
    MEDIA_ANNOUNCE = 1048576
    MEDIA_ENQUEUE = 2097152


class MediaPlayerDeviceClass(StrEnum):
    """Device class for media players."""

    TV = "tv"
    SPEAKER = "speaker"
    RECEIVER = "receiver"


class MediaPlayerAttributes(BaseAttributes):
    app_id: str | None = None
    app_name: str | None = None
    device_class: MediaPlayerDeviceClass
    group_members: list[str] | None = None
    is_volume_muted: bool | None = None
    media_album_artist: str | None = None
    media_album_name: str | None = None
    media_artist: str | None = None
    media_channel: str | None = None
    media_content_id: str | None = None
    media_content_type: MediaType | str | None = None
    media_duration: int | None = None
    media_episode: str | None = None
    media_image_hash: str | None = None
    media_image_remotely_accessible: bool | None = None
    media_image_url: str | None = None
    media_playlist: str | None = None
    media_position: int | None = None
    media_position_updated_at: datetime | None = None
    media_season: str | None = None
    media_series_title: str | None = None
    media_title: str | None = None
    media_track: int | None = None
    repeat: RepeatMode | str | None = None
    shuffle: bool | None = None
    sound_mode: str | None = None
    sound_mode_list: list[str] | None = None
    source: str | None = None
    source_list: list[str] | None = None
    state: MediaPlayerState | None = None
    volume_level: float | None = None
    volute_step: float | None = 0.1
    supported_features: MediaPlayerEntityFeature | None = None


@REGISTRY.register(Platform.MEDIA_PLAYER)
class MediaPlayerEntity(HAEntity):
    domain: Literal[Platform.MEDIA_PLAYER]
    attributes: MediaPlayerAttributes


# Notify
@REGISTRY.register(Platform.NOTIFY)
class NotifyEntity(HAEntity):
    domain: Literal[Platform.NOTIFY]


# Number
class NumberMode(StrEnum):
    """Modes for number entities."""

    AUTO = "auto"
    BOX = "box"
    SLIDER = "slider"


class NumericalDeviceClass(StrEnum):
    """Device class for numbers."""

    # NumberDeviceClass should be aligned with SensorDeviceClass

    APPARENT_POWER = "apparent_power"
    """Apparent power.

    Unit of measurement: `VA`
    """

    AQI = "aqi"
    """Air Quality Index.

    Unit of measurement: `None`
    """

    ATMOSPHERIC_PRESSURE = "atmospheric_pressure"
    """Atmospheric pressure.

    Unit of measurement: `UnitOfPressure` units
    """

    BATTERY = "battery"
    """Percentage of battery that is left.

    Unit of measurement: `%`
    """

    CO = "carbon_monoxide"
    """Carbon Monoxide gas concentration.

    Unit of measurement: `ppm` (parts per million)
    """

    CO2 = "carbon_dioxide"
    """Carbon Dioxide gas concentration.

    Unit of measurement: `ppm` (parts per million)
    """

    CONDUCTIVITY = "conductivity"
    """Conductivity.

    Unit of measurement: `S/cm`, `mS/cm`, `µS/cm`
    """

    CURRENT = "current"
    """Current.

    Unit of measurement: `A`,  `mA`
    """

    DATA_RATE = "data_rate"
    """Data rate.

    Unit of measurement: UnitOfDataRate
    """

    DATA_SIZE = "data_size"
    """Data size.

    Unit of measurement: UnitOfInformation
    """

    DISTANCE = "distance"
    """Generic distance.

    Unit of measurement: `LENGTH_*` units
    - SI /metric: `mm`, `cm`, `m`, `km`
    - USCS / imperial: `in`, `ft`, `yd`, `mi`
    """

    DURATION = "duration"
    """Fixed duration.

    Unit of measurement: `d`, `h`, `min`, `s`, `ms`
    """

    ENERGY = "energy"
    """Energy.

    Unit of measurement: `Wh`, `kWh`, `MWh`, `MJ`, `GJ`
    """

    ENERGY_STORAGE = "energy_storage"
    """Stored energy.

    Use this device class for sensors measuring stored energy, for example the amount
    of electric energy currently stored in a battery or the capacity of a battery.

    Unit of measurement: `Wh`, `kWh`, `MWh`, `MJ`, `GJ`
    """

    FREQUENCY = "frequency"
    """Frequency.

    Unit of measurement: `Hz`, `kHz`, `MHz`, `GHz`
    """

    GAS = "gas"
    """Gas.

    Unit of measurement:
    - SI / metric: `m³`
    - USCS / imperial: `ft³`, `CCF`
    """

    HUMIDITY = "humidity"
    """Relative humidity.

    Unit of measurement: `%`
    """

    ILLUMINANCE = "illuminance"
    """Illuminance.

    Unit of measurement: `lx`
    """

    IRRADIANCE = "irradiance"
    """Irradiance.

    Unit of measurement:
    - SI / metric: `W/m²`
    - USCS / imperial: `BTU/(h⋅ft²)`
    """

    MOISTURE = "moisture"
    """Moisture.

    Unit of measurement: `%`
    """

    MONETARY = "monetary"
    """Amount of money.

    Unit of measurement: ISO4217 currency code

    See https://en.wikipedia.org/wiki/ISO_4217#Active_codes for active codes
    """

    NITROGEN_DIOXIDE = "nitrogen_dioxide"
    """Amount of NO2.

    Unit of measurement: `µg/m³`
    """

    NITROGEN_MONOXIDE = "nitrogen_monoxide"
    """Amount of NO.

    Unit of measurement: `µg/m³`
    """

    NITROUS_OXIDE = "nitrous_oxide"
    """Amount of N2O.

    Unit of measurement: `µg/m³`
    """

    OZONE = "ozone"
    """Amount of O3.

    Unit of measurement: `µg/m³`
    """

    PH = "ph"
    """Potential hydrogen (acidity/alkalinity).

    Unit of measurement: Unitless
    """

    PM1 = "pm1"
    """Particulate matter <= 1 μm.

    Unit of measurement: `µg/m³`
    """

    PM10 = "pm10"
    """Particulate matter <= 10 μm.

    Unit of measurement: `µg/m³`
    """

    PM25 = "pm25"
    """Particulate matter <= 2.5 μm.

    Unit of measurement: `µg/m³`
    """

    POWER_FACTOR = "power_factor"
    """Power factor.

    Unit of measurement: `%`, `None`
    """

    POWER = "power"
    """Power.

    Unit of measurement: `W`, `kW`
    """

    PRECIPITATION = "precipitation"
    """Accumulated precipitation.

    Unit of measurement: UnitOfPrecipitationDepth
    - SI / metric: `cm`, `mm`
    - USCS / imperial: `in`
    """

    PRECIPITATION_INTENSITY = "precipitation_intensity"
    """Precipitation intensity.

    Unit of measurement: UnitOfVolumetricFlux
    - SI /metric: `mm/d`, `mm/h`
    - USCS / imperial: `in/d`, `in/h`
    """

    PRESSURE = "pressure"
    """Pressure.

    Unit of measurement:
    - `mbar`, `cbar`, `bar`
    - `Pa`, `hPa`, `kPa`
    - `inHg`
    - `psi`
    """

    REACTIVE_POWER = "reactive_power"
    """Reactive power.

    Unit of measurement: `var`
    """

    SIGNAL_STRENGTH = "signal_strength"
    """Signal strength.

    Unit of measurement: `dB`, `dBm`
    """

    SOUND_PRESSURE = "sound_pressure"
    """Sound pressure.

    Unit of measurement: `dB`, `dBA`
    """

    SPEED = "speed"
    """Generic speed.

    Unit of measurement: `SPEED_*` units or `UnitOfVolumetricFlux`
    - SI /metric: `mm/d`, `mm/h`, `m/s`, `km/h`
    - USCS / imperial: `in/d`, `in/h`, `ft/s`, `mph`
    - Nautical: `kn`
    """

    SULPHUR_DIOXIDE = "sulphur_dioxide"
    """Amount of SO2.

    Unit of measurement: `µg/m³`
    """

    TEMPERATURE = "temperature"
    """Temperature.

    Unit of measurement: `°C`, `°F`, `K`
    """

    VOLATILE_ORGANIC_COMPOUNDS = "volatile_organic_compounds"
    """Amount of VOC.

    Unit of measurement: `µg/m³`
    """

    VOLATILE_ORGANIC_COMPOUNDS_PARTS = "volatile_organic_compounds_parts"
    """Ratio of VOC.

    Unit of measurement: `ppm`, `ppb`
    """

    VOLTAGE = "voltage"
    """Voltage.

    Unit of measurement: `V`, `mV`
    """

    VOLUME = "volume"
    """Generic volume.

    Unit of measurement: `VOLUME_*` units
    - SI / metric: `mL`, `L`, `m³`
    - USCS / imperial: `ft³`, `CCF`, `fl. oz.`, `gal` (warning: volumes expressed in
    USCS/imperial units are currently assumed to be US volumes)
    """

    VOLUME_STORAGE = "volume_storage"
    """Generic stored volume.

    Use this device class for sensors measuring stored volume, for example the amount
    of fuel in a fuel tank.

    Unit of measurement: `VOLUME_*` units
    - SI / metric: `mL`, `L`, `m³`
    - USCS / imperial: `ft³`, `CCF`, `fl. oz.`, `gal` (warning: volumes expressed in
    USCS/imperial units are currently assumed to be US volumes)
    """

    VOLUME_FLOW_RATE = "volume_flow_rate"
    """Generic flow rate

    Unit of measurement: UnitOfVolumeFlowRate
    - SI / metric: `m³/h`, `L/min`
    - USCS / imperial: `ft³/min`, `gal/min`
    """

    WATER = "water"
    """Water.

    Unit of measurement:
    - SI / metric: `m³`, `L`
    - USCS / imperial: `ft³`, `CCF`, `gal` (warning: volumes expressed in
    USCS/imperial units are currently assumed to be US volumes)
    """

    WEIGHT = "weight"
    """Generic weight, represents a measurement of an object's mass.

    Weight is used instead of mass to fit with every day language.

    Unit of measurement: `MASS_*` units
    - SI / metric: `µg`, `mg`, `g`, `kg`
    - USCS / imperial: `oz`, `lb`
    """

    WIND_SPEED = "wind_speed"
    """Wind speed.

    Unit of measurement: `SPEED_*` units
    - SI /metric: `m/s`, `km/h`
    - USCS / imperial: `ft/s`, `mph`
    - Nautical: `kn`
    """


class NumberAttributes(BaseAttributes):
    device_class: NumericalDeviceClass | str | None = None
    mode: NumberMode | str = NumberMode.AUTO
    native_max_value: float = 100
    native_min_value: float = 0
    native_step: float = 1
    native_value: float = 0
    native_unit_of_measurement: str | None = None


@REGISTRY.register(Platform.NUMBER, "input_number")
class NumberEntity(HAEntity):
    domain: Literal[Platform.NUMBER]
    attributes: NumberAttributes

    def is_domain(self, domain: str) -> bool:
        return domain in [Platform.NUMBER, "input_number"]


# Remote


class RemoteEntityFeature(IntFlag):
    """Supported features of the remote entity."""

    LEARN_COMMAND = 1
    DELETE_COMMAND = 2
    ACTIVITY = 4


class RemoteAttributes(BaseAttributes):
    supported_features: RemoteEntityFeature | None = None
    current_activity: str | None = None
    activity_list: list[str] | None = None


@REGISTRY.register(Platform.REMOTE)
class RemoteEntity(HAEntity):
    domain: Literal[Platform.REMOTE]
    attributes: RemoteAttributes


# Scene


@REGISTRY.register(Platform.SCENE)
class SceneEntity(HAEntity):
    domain: Literal[Platform.SCENE]


# Select


class SelectAttributes(BaseAttributes):
    current_option: str | None = None
    options: list[str] = []


@REGISTRY.register(Platform.SELECT, "input_select")
class SelectEntity(HAEntity):
    domain: Literal[Platform.SELECT]
    attributes: SelectAttributes

    def is_domain(self, domain: str) -> bool:
        return domain in [Platform.SELECT, "input_select"]


# Sensor
class SensorStateClass(StrEnum):
    MEASUREMENT = "measurement"
    TOTAL = "total"
    TOTAL_INCREASING = "total_increasing"


class SensorAttributes(BaseAttributes):
    device_class: NumericalDeviceClass | str | None = None
    last_reset: datetime | None = None
    native_unit_of_measurement: str | None = None
    native_value: Any = None
    options: list | None = None
    state_class: SensorStateClass | str | None = None
    suggested_display_precision: int | None = None
    suggested_unit_of_measurement: str | None = None


@REGISTRY.register(Platform.SENSOR)
class SensorEntity(HAEntity):
    domain: Literal[Platform.SENSOR]
    attributes: SensorAttributes


# Siren
class SirenEntityFeature(IntFlag):
    """Supported features of the siren entity."""

    TURN_ON = 1
    TURN_OFF = 2
    TONES = 4
    VOLUME_SET = 8
    DURATION = 16


class SirenAttributes(BaseAttributes):
    is_on: bool | None = None
    available_tones: list | dict | None = None
    supported_features: SirenEntityFeature | None = None


@REGISTRY.register(Platform.SIREN)
class SirenEntity(HAEntity):
    domain: Literal[Platform.SIREN]
    attributes: SirenAttributes


# STT
class AudioCodecs(StrEnum):
    """Supported Audio codecs."""

    PCM = "pcm"
    OPUS = "opus"


class AudioFormats(StrEnum):
    """Supported Audio formats."""

    WAV = "wav"
    OGG = "ogg"


class AudioBitRates(IntEnum):
    """Supported Audio bit rates."""

    BITRATE_8 = 8
    BITRATE_16 = 16
    BITRATE_24 = 24
    BITRATE_32 = 32


class AudioSampleRates(IntEnum):
    """Supported Audio sample rates."""

    SAMPLERATE_8000 = 8000
    SAMPLERATE_11000 = 11000
    SAMPLERATE_16000 = 16000
    SAMPLERATE_18900 = 18900
    SAMPLERATE_22000 = 22000
    SAMPLERATE_32000 = 32000
    SAMPLERATE_37800 = 37800
    SAMPLERATE_44100 = 44100
    SAMPLERATE_48000 = 48000


class AudioChannels(IntEnum):
    """Supported Audio channel."""

    CHANNEL_MONO = 1
    CHANNEL_STEREO = 2


class SpeechResultState(StrEnum):
    """Result state of speech."""

    SUCCESS = "success"
    ERROR = "error"


class STTAttributes(BaseAttributes):
    supported_languages: list[str] = []
    supported_formats: list[AudioFormats] = []
    supported_codecs: list[AudioCodecs] = []
    supported_bit_rates: list[AudioBitRates] = []
    supported_sample_rates: list[AudioSampleRates] = []
    supported_channels: list[AudioChannels]


@REGISTRY.register(Platform.STT)
class STTEntity(HAEntity):
    domain: Literal[Platform.STT]
    attributes: STTAttributes


# Switch
class SwitchDeviceClass(StrEnum):
    OUTLET = "outlet"
    SWITCH = "switch"


class SwitchAttributes(BaseAttributes):
    is_on: bool | None = None
    device_class: SwitchDeviceClass | None = None


@REGISTRY.register(Platform.SWITCH, "input_boolean")
class SwitchEntity(HAEntity):
    domain: Literal[Platform.SWITCH]
    attributes: SwitchAttributes

    def is_domain(self, domain: str) -> bool:
        return domain in [Platform.SWITCH, "input_boolean"]


# Text


class TextMode(StrEnum):
    TEXT = "text"
    PASSWORD = "password"


class TextAttributes(BaseAttributes):
    mode: TextMode = TextMode.TEXT
    native_max: int = 100
    native_min: int = 0
    pattern: str | None = None
    native_value: str = ""


@REGISTRY.register(Platform.TEXT, "input_text")
class TextEntity(HAEntity):
    domain: Literal[Platform.TEXT]
    attributes: TextAttributes

    def is_domain(self, domain: str) -> bool:
        return domain in [Platform.TEXT, "input_text"]


# Time
class TimeAttributes(BaseAttributes):
    native_value: time | None = None


@REGISTRY.register(Platform.TIME)
class TimeEntity(HAEntity):
    domain: Literal[Platform.TIME]
    attributes: TimeAttributes


# Todo list
class TodoListEntityFeature(IntFlag):
    """Supported features of the To-do List entity."""

    CREATE_TODO_ITEM = 1
    DELETE_TODO_ITEM = 2
    UPDATE_TODO_ITEM = 4
    MOVE_TODO_ITEM = 8
    SET_DUE_DATE_ON_ITEM = 16
    SET_DUE_DATETIME_ON_ITEM = 32
    SET_DESCRIPTION_ON_ITEM = 64


class TodoItemStatus(StrEnum):
    """Status or confirmation of a To-do List Item.

    This is a subset of the statuses supported in rfc5545.
    """

    NEEDS_ACTION = "needs_action"
    COMPLETED = "completed"


class TodoListItem(BaseModel):
    uid: str | None = None
    summary: str | None = None
    status: TodoItemStatus | None = None
    due: date | datetime | None = None
    description: str | None = None


class TodoListAttributes(BaseAttributes):
    todo_items: list[TodoListItem] | None = None
    supported_features: TodoListEntityFeature | None = None


@REGISTRY.register(Platform.TODO)
class TodoListEntity(HAEntity):
    domain: Literal[Platform.TODO]
    attributes: TodoListAttributes


# TTS


class TTSAttributes(BaseAttributes):
    supported_languages: list[str] = []
    default_language: str | None = None
    supported_options: list[str] | None = None
    default_options: dict[str, Any] | None = None


@REGISTRY.register(Platform.TTS)
class TTSEntity(HAEntity):
    domain: Literal[Platform.TTS]
    attributes: TTSAttributes


# Update
class UpdateEntityFeature(IntFlag):
    """Supported features of the update entity."""

    INSTALL = 1
    SPECIFIC_VERSION = 2
    PROGRESS = 4
    BACKUP = 8
    RELEASE_NOTES = 16


class UpdateDeviceClass(StrEnum):
    """Device class for update."""

    FIRMWARE = "firmware"


class UpdateAttributes(BaseAttributes):
    auto_update: bool = False
    in_progress: bool | int | None = None
    installed_version: str | None = None
    latest_version: str | None = None
    release_summary: str | None = None
    release_url: str | None = None
    title: str | None = None
    supported_features: UpdateEntityFeature | None = None
    device_class: UpdateDeviceClass | None = None


@REGISTRY.register(Platform.UPDATE)
class UpdateEntity(HAEntity):
    domain: Literal[Platform.UPDATE]
    attributes: UpdateAttributes


# Vacuum
class VacuumEntityFeature(IntFlag):
    """Supported features of the vacuum entity."""

    TURN_ON = 1  # Deprecated, not supported by StateVacuumEntity
    TURN_OFF = 2  # Deprecated, not supported by StateVacuumEntity
    PAUSE = 4
    STOP = 8
    RETURN_HOME = 16
    FAN_SPEED = 32
    BATTERY = 64
    STATUS = 128  # Deprecated, not supported by StateVacuumEntity
    SEND_COMMAND = 256
    LOCATE = 512
    CLEAN_SPOT = 1024
    MAP = 2048
    STATE = 4096  # Must be set by vacuum platforms derived from StateVacuumEntity
    START = 8192


class VacuumEntityState(StrEnum):
    CLEANING = "cleaning"
    DOCKED = "docked"
    RETURNING = "returning"
    ERROR = "error"


class VacuumAttributes(BaseAttributes):
    battery_icon: str | None = None
    battery_level: int | None = None
    fan_speed: str | None = None
    fan_speed_list: list | None = None
    name: str | None = None
    state: VacuumEntityState | None = None
    supported_features: VacuumEntityFeature | None = None


@REGISTRY.register(Platform.VACUUM)
class VacuumEntity(HAEntity):
    domain: Literal[Platform.VACUUM]
    attributes: VacuumAttributes
    state: VacuumEntityState | Any


# Valve
class ValveDeviceClass(StrEnum):
    """Device class for valve."""

    # Refer to the valve dev docs for device class descriptions
    WATER = "water"
    GAS = "gas"


# mypy: disallow-any-generics
class ValveEntityFeature(IntFlag):
    """Supported features of the valve entity."""

    OPEN = 1
    CLOSE = 2
    SET_POSITION = 4
    STOP = 8


class ValveState(StrEnum):
    OPENING = "opening"
    OPEN = "open"
    CLOSING = "closing"
    CLOSED = "closed"


class ValveAttributes(BaseAttributes):
    current_valve_position: int | None = None
    is_closed: bool | None = None
    is_closing: bool | None = None
    is_opening: bool | None = None
    reports_position: bool = False
    device_class: ValveDeviceClass | None = None
    supported_features: ValveEntityFeature | None = None
    state: ValveState | None = None


@REGISTRY.register(Platform.VALVE)
class ValveEntity(HAEntity):
    domain: Literal[Platform.VALVE]
    attributes: ValveAttributes
    state: ValveState | Any


# Wake words
class WakeWord(BaseModel):
    id: str | None = None
    name: str | None = None
    phrase: str | None = None


class WakeWordAttributes(BaseAttributes):
    supported_wake_words: list[WakeWord] = []


@REGISTRY.register(Platform.WAKE_WORD)
class WakeWordEntity(HAEntity):
    domain: Literal[Platform.WAKE_WORD]
    attributes: WakeWordAttributes


# Water heater
class WaterHeaterEntityFeature(IntFlag):
    TARGET_TEMPERATURE = 1
    OPERATION_MODE = 2
    AWAY_MODE = 4
    ON_OFF = 8


class WaterHeaterStates(StrEnum):
    ECO = "eco"
    ELECTRIC = "electric"
    PERFORMANCE = "performance"
    HIGH_DEMAND = "high_demand"
    HEAT_PUMP = "heat_pump"
    GAS = "gas"
    OFF = "off"


class WaterHeaterAttributes(BaseAttributes):
    min_temp: float = 110
    max_temp: float = 140
    current_temperature: float | None = None
    target_temperature: float | None = None
    target_temperature_high: float | None = None
    target_temperature_low: float | None = None
    temperature_unit: str | UnitOfTemperature | None = None
    current_operation: str | None = None
    operation_list: list[str] | None = None
    supported_features: WaterHeaterEntityFeature | None = None
    is_away_mode_on: bool | None = None
    state: WaterHeaterStates | Any = None


@REGISTRY.register(Platform.WATER_HEATER)
class WaterHeaterEntity(HAEntity):
    domain: Literal[Platform.WATER_HEATER]
    attributes: WaterHeaterAttributes
    state: WaterHeaterStates | Any


# Weather
class WeatherEntityFeature(IntFlag):
    """Supported features of the update entity."""

    FORECAST_DAILY = 1
    FORECAST_HOURLY = 2
    FORECAST_TWICE_DAILY = 4


class WeatherForecast(BaseModel):
    condition: str | None = None
    datetime: str | None = None
    humidity: float | None = None
    precipitation_probability: float | None = None
    cloud_coverage: float | None = None
    native_precipitation: float | None = None
    precipitation: float | None = None
    native_pressure: float | None = None
    pressure: float | None = None
    native_temperature: float | None = None
    temperature: float | None = None
    native_templow: float | None = None
    templow: float | None = None
    native_apparent_temperature: float | None = None
    wind_bearing: float | str | None = None
    native_wind_gust_speed: float | None = None
    native_wind_speed: float | None = None
    wind_speed: float | None = None
    native_dew_point: float | None = None
    uv_index: float | None = None
    is_daytime: bool | None = None


class WeatherAttributes(BaseAttributes):
    condition: str | None = None
    datetime: str | None = None
    humidity: float | None = None
    precipitation_probability: float | None = None
    cloud_coverage: float | None = None
    native_precipitation: float | None = None
    precipitation: float | None = None
    native_pressure: float | None = None
    pressure: float | None = None
    native_temperature: float | None = None
    temperature: float | None = None
    native_templow: float | None = None
    templow: float | None = None
    native_apparent_temperature: float | None = None
    wind_bearing: float | str | None = None
    native_wind_gust_speed: float | None = None
    native_wind_speed: float | None = None
    wind_speed: float | None = None
    native_dew_point: float | None = None
    uv_index: float | None = None
    is_daytime: bool | None = None
    ozone: float | None = None
    forecast: list[WeatherForecast] | None = None


@REGISTRY.register(Platform.WEATHER)
class WeatherEntity(HAEntity):
    domain: Literal[Platform.WEATHER]
    attributes: WeatherAttributes
