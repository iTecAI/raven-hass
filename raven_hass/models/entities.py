from datetime import date, datetime
from enum import IntFlag, StrEnum
from typing import Any, Literal
from pydantic import BaseModel, computed_field, model_validator


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


class HAEntity(BaseModel):
    entity_id: str
    domain: Platform
    name: str
    state: str | int | float | bool | None
    last_changed: datetime
    last_updated: datetime
    context: HAContext
    attributes: BaseAttributes

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


class AlarmControlPanelEntity(HAEntity):
    domain: Platform.ALARM_CONTROL_PANEL
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


class BinarySensorEntity(HAEntity):
    domain: Platform.BINARY_SENSOR
    attributes: BinarySensorAttributes


# Button


class ButtonDeviceClass(StrEnum):
    IDENTIFY = "identify"
    RESTART = "restart"
    UPDATE = "update"


class ButtonAttributes(BaseAttributes):
    device_class: ButtonDeviceClass | None = None


class ButtonEntity(HAEntity):
    domain: Platform.BUTTON
    attributes: ButtonAttributes


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


class CalendarEntity(HAEntity):
    domain: Platform.CALENDAR
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


class CameraEntity(HAEntity):
    domain: Platform.CAMERA
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


class ClimateEntity(HAEntity):
    domain: Platform.CLIMATE
    attributes: ClimateAttributes


# Conversation


class ConversationAttributes(BaseAttributes):
    supported_languages: list[str] | Literal["*"]


class ConversationEntity(HAEntity):
    domain: Platform.CONVERSATION
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


class CoverEntity(HAEntity):
    domain: Platform.COVER
    attributes: CoverAttributes


# Date


class DateAttributes(BaseAttributes):
    native_value: date | None = None


class DateEntity(HAEntity):
    domain: Platform.DATE
    attributes: DateAttributes


# Date


class DateTimeAttributes(BaseAttributes):
    native_value: datetime | None = None


class DateTimeEntity(HAEntity):
    domain: Platform.DATETIME
    attributes: DateAttributes


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


class DeviceTrackerEntity(HAEntity):
    domain: Platform.DEVICE_TRACKER
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


class EventEntity(HAEntity):
    domain: Platform.EVENT
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


class FanEntity(HAEntity):
    domain: Platform.FAN
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


class HumidifierEntity(HAEntity):
    domain: Platform.HUMIDIFIER
    attributes: HumidifierAttributes


# Image


class ImageAttributes(BaseAttributes):
    content_type: str = "image/jpeg"
    image_last_updated: datetime | None = None
    image_url: str | None = None


class ImageEntity(HAEntity):
    domain: Platform.IMAGE
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


class LawnMowerEntity(HAEntity):
    domain: Platform.LAWN_MOWER
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


class LightEntity(HAEntity):
    domain: Platform.LIGHT
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


class LockEntity(HAEntity):
    domain: Platform.LOCK
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


class MediaPlayerEntity(HAEntity):
    domain: Platform.MEDIA_PLAYER
    attributes: MediaPlayerAttributes
