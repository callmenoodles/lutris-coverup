import enum


class ResizeMethod(enum.Enum):
    NONE = enum.auto()
    STRETCH = enum.auto()
    CROP = enum.auto()


class AssetType(enum.Enum):
    ALL = enum.auto()
    COVERS = enum.auto()
    BANNERS = enum.auto()
    ICONS = enum.auto()
