class AssetSpec:
    def __init__(
        self,
        path: str,
        asset_class: str,
        name: str,
        position: tuple[float, float, float],
        rotation: tuple[float, float, float, float],
    ):
        self.path = path
        self.asset_class = asset_class
        self.name = name
        self.pos = position
        self.rot = rotation
