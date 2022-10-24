from pydantic import BaseModel, Extra, Field
from pydantic.generics import GenericModel
from typing import Any, Generic, Literal, Tuple, TypeVar, Union
from typing_extensions import Annotated
from enum import Enum

PointType = tuple[float, float, float]
LayerType = Literal["new", "image", "segmentation", "annotation", "mesh"]
DataPanelLayoutTypes = Literal[
    "xy", "yz", "xz", "xy-3d", "yz-3d", "xz-3d", "4panel", "3d"
]

NavigationLinkType = Literal["linked", "unlinked", "relative"]

T = TypeVar("T")

Quaternion = Tuple[float, float, float, float]


class Linked(GenericModel, Generic[T]):
    link: NavigationLinkType | None = "linked"
    value: T | None


class Model(BaseModel):
    class Config:
        extra = Extra.forbid


class UnitQuaternion(Model):
    pass


class ToolNameEnum(str, Enum):
    annotatePoint = "annotatePoint"
    annotateLine = "annotateLine"
    annotateBoundingBox = "annotateBoundingBox"
    annotateSphere = "annotateSphere"
    blend = "blend"
    opacity = "opacity"
    crossSectionRenderScale = "crossSectionRenderScale"
    selectedAlpha = "selectedAlpha"
    notSelectedAlpha = "notSelectedAlpha"
    objectAlpha = "objectAlpha"
    hideSegmentZero = "hideSegmentZero"
    baseSegmentColoring = "baseSegmentColoring"
    ignoreNullVisibleSet = "ignoreNullVisibleSet"
    colorSeed = "colorSeed"
    segmentDefaultColor = "segmentDefaultColor"
    meshRenderScale = "meshRenderScale"
    saturation = "saturation"
    skeletonRendering_mode2d = "skeletonRendering.mode2d"
    skeletonRendering_lineWidth2d = "skeletonRendering.lineWidth2d"
    skeletonRendering_lineWidth3d = "skeletonRendering.lineWidth3d"
    shaderControl = "shaderControl"
    mergeSegments = "mergeSegments"
    splitSegments = "splitSegments"
    selectSegments = "selectSegments"


class Tool(Model):
    type: ToolNameEnum


class ControlTool(Tool):
    control: str


class SidePanelLocation(Model):
    flex: float | None = 1.0
    side: str | None
    visible: bool | None
    size: int | None
    row: int | None
    col: int | None


class SelectedLayerState(SidePanelLocation):
    layer: str | None


class StatisticsDisplayState(SidePanelLocation):
    pass


class LayerSidePanelState(SidePanelLocation):
    tab: str | None
    tabs: list[str]


class HelpPanelState(SidePanelLocation):
    pass


class LayerListPanelState(SidePanelLocation):
    pass


class CoordinateArray(Model):
    coordinates: list[str]
    labels: list[str]


DimensionScale = tuple[float, str] | tuple[None, None, CoordinateArray]

CoordinateSpace = dict[str, DimensionScale]


class LayerDataSubsource(Model):
    enabled: bool


class CoordinateSpaceTransform(Model):
    outputDimensions: CoordinateSpace
    inputDimensions: CoordinateSpace | None
    sourceRank: int | None
    matrix: list[list[int]] | None


class LayerDataSource(Model):
    url: str
    transform: CoordinateSpaceTransform | None
    subsources: dict[str, bool] | None
    enableDefaultSubsources: bool | None = True
    CoordinateSpaceTransform: CoordinateSpaceTransform | None


class Layer(Model):
    source: LayerDataSource | str | list[str | LayerDataSource]
    name: str
    visible: bool | None
    tab: str | None
    type: LayerType | None
    layerDimensions: CoordinateSpace | None
    layerPosition: float | None
    panels: list[LayerSidePanelState] | None
    pick: bool | None
    tool_bindings: dict[str, Tool] | None
    tool: Tool | None


class PointAnnotationLayer(Layer):
    points: list[PointType]


class AnnotationLayerOptions(Model):
    annotationColor: str | None


class InvlerpParameters(Model):
    range: tuple[float, float] | tuple[int, int] | None
    window: tuple[float, float] | tuple[int, int] | None
    channel: list[int] | None


ShaderControls = dict[str, float | InvlerpParameters]


class NewLayer(Layer):
    type: Literal["new"]


class ImageLayer(Layer):
    type: Literal["image"]
    shader: str | None
    shaderControls: ShaderControls | None
    opacity: float = 0.05
    blend: str | None
    crossSectionRenderScale: float | None = 1.0


class SkeletonRenderingOptions(Model):
    shader: str
    shaderControls: ShaderControls
    mode2d: str | None
    lineWidth2d: float | None = 2.0
    mode3d: str | None
    lineWidth3d: float | None = 1.0


class SegmentationLayer(Layer):
    type: Literal["segmentation"]
    segments: list[
        str | int
    ] | None  # the order of the types in the union matters -- str | int works, but int | str does not
    equivalences: dict[int, int] | None
    hideSegmentZero: bool | None = True
    selectedAlpha: float | None = 0.5
    notSelectedAlpha: float | None = 0.0
    objectAlpha: float | None = 1.0
    saturation: float | None = 1.0
    ignoreNullVisibleSet: bool | None = True
    skeletonRendering: SkeletonRenderingOptions | None
    colorSeed: int | None = 0
    crossSectionRenderScale: float | None = 1.0
    meshRenderScale: float | None = 10.0
    meshSilhouetteRendering: float | None = 0.0
    segmentQuery: str | None
    segmentColors: dict[int, str] | None
    segmentDefaultColor: str | None
    linkedSegmentationGroup: str | None
    linkedSegmentationColorGroup: Union[str, Literal[False]] | None


class MeshLayer(Layer):
    type: Literal["mesh"]
    vertexAttributeSources: list[str] | None
    shader: str
    vertexAttributeNames: list[str | None] | None


class AnnotationBase(Model):
    id: str | None
    type: str
    description: str | None
    segments: list[int] | None
    props: list[int | str]


class PointAnnotation(AnnotationBase):
    point: list[float]


class LineAnnotation(AnnotationBase):
    pointA: list[float]
    pointB: list[float]


AxisAlignedBoundingBoxAnnotation = LineAnnotation


class EllipsoidAnnotation(AnnotationBase):
    center: list[float]
    radii: list[float]


Annotations = (
    PointAnnotation
    | LineAnnotation
    | EllipsoidAnnotation
    | AxisAlignedBoundingBoxAnnotation
)


class AnnotationPropertySpec(Model):
    id: str
    type: str
    description: str | None
    default: float | str | None
    enum_values: list[float | str] | None
    enum_labels: list[str] | None


class AnnotationLayer(Layer, AnnotationLayerOptions):
    type: Literal["annotation"]
    annotations: list[Annotations] | None
    annotationProperties: list[AnnotationPropertySpec] | None
    annotationRelationships: list[str] | None
    linkedSegmentationLayer: dict[str, str]
    filterBySegmentation: list[str]
    ignoreNullSegmentFilter: bool | None = True
    shader: str | None
    shaderControls: ShaderControls | None


LayerType = Annotated[
    Union[
        ImageLayer,
        SegmentationLayer,
        AnnotationLayer,
        MeshLayer,
        NewLayer,
    ],
    Field(discriminator="type"),
]


class CrossSection(Model):
    width: int = 1000
    height: int = 1000
    position: Linked[list[float]]
    orientation: Linked[Quaternion]
    scale: Linked[float]


class DataPanelLayout(Model):
    type: str
    crossSections: dict[str, CrossSection]
    orthographicProjection: bool | None


class LayerGroupViewer(Model):
    type: str
    layers: list[str]
    layout: DataPanelLayout
    position: Linked[list[float]]
    crossSectionOrientation: Linked[Quaternion]
    crossSectionScale: Linked[float]
    crossSectionDepth: Linked[float]
    projectionOrientation: Linked[tuple[float, float, float, float]]
    projectionScale: Linked[float]
    projectionDepth: Linked[float]


LayoutSpecification = str | LayerGroupViewer | DataPanelLayout


class StackLayout(Model):
    type: Literal["row", "column"]
    children: list[LayoutSpecification]


class ViewerState(Model):
    title: str | None
    dimensions: CoordinateSpace | None
    relativeDisplayScales: dict[str, float] | None
    displayDimensions: list[str] | None
    position: tuple[float, float, float] | None
    crossSectionOrientation: Quaternion | None
    crossSectionScale: float | None
    crossSectionDepth: float | None
    projectionScale: float | None
    projectionDeth: float | None
    projectionOrientation: Quaternion | None
    showSlices: bool | None = True
    showAxisLines: bool | None = True
    showScaleBar: bool | None = True
    showDefaultAnnotations: bool | None = True
    gpuMemoryLimit: int | None
    systemMemoryLimit: int | None
    concurrentDownloads: int | None
    prefetch: bool | None = True
    layers: list[LayerType]
    layout: LayoutSpecification
    crossSectionBackgroundColor: str | None
    projectionBackgroundColor: str | None
    selectedLayer: SelectedLayerState | None
    statistics: StatisticsDisplayState | None
    helpPanel: HelpPanelState | None
    layerListPanel: LayerListPanelState | None
    partialViewport: Quaternion | None = (0, 0, 1, 1)
    selection: dict[str, int] | None


def main():
    print(ViewerState.schema_json(indent=2))


if __name__ == "__main__":
    main()
