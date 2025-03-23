class AssetSpec:
    """A specification for an asset to be placed in a scene"""

    def __init__(
        self,
        path: str,
        asset_class: str,
        name: str,
        position: tuple[float, float, float],
        rotation: tuple[float, float, float, float],
    ):
        """Create a new AssetSpec object

        Args:
            path (str): A path to the asset file
            asset_class (str): The class of the asset
            name (str): The name of the asset
            position (tuple[float, float, float]): The position of the asset
            rotation (tuple[float, float, float, float]): The rotation of the asset
        """
        self.path = path
        self.asset_class = asset_class
        self.name = name
        self.pos = position
        self.rot = rotation
