from pxr import UsdShade, Sdf
    
class MaterialHandler:

    def __call__(self, material_file: str, material_name: str, stage: object):
        """

        """
        material_path = f"World/Materials/{material_name}"
        shader_path = material_path + "/Shader"
        material = self.createMaterial(stage, material_path)
        shader = self.crateShader(stage, shader_path, material_name, material_file)
        material = self.connectMaterialShader(material, shader)
        return material

    def createMaterial(self, stage, material_path) -> UsdShade.Material:  # type: ignore
        material = UsdShade.Material.Define(stage, Sdf.Path(material_path))  # type: ignore
        return material

    def crateShader(self, stage, shader_path, material_name, material_file) -> UsdShade.Shader:  # type: ignore
        shader = UsdShade.Shader.Define(stage, Sdf.Path(shader_path))  # type: ignore
        shader.CreateIdAttr().Set(f"mdl::{material_name}::{material_name}")
        shader.CreateInput("info:sourceAsset", Sdf.ValueTypeNames.Asset).Set(material_file)  # type: ignore
        return shader

    def connectMaterialShader(self, material, shader) -> UsdShade.Material:  # type: ignore
        material.CreateSurfaceOutput().ConnectToSource(shader, "out")
        return material
