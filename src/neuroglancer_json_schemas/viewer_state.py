from pydantic import BaseModel, Extra, Field
from pydantic.generics import GenericModel
from typing import Dict, Generic, Optional, Literal, List, Tuple, TypeVar, Union
from typing_extensions import Annotated
from enum import Enum

PointType = Tuple[float, float, float]
LayerType = Literal["new", "image", "segmentation", "annotation", "mesh"]
DataPanelLayoutTypes = Literal[
    "xy", "yz", "xz", "xy-3d", "yz-3d", "xz-3d", "4panel", "3d"
]

NavigationLinkType = Literal["linked", "unlinked", "relative"]

T = TypeVar("T")

Quaternion = Tuple[float, float, float, float]


class Linked(GenericModel, Generic[T]):
    link: Optional[NavigationLinkType] = "linked"
    value: Optional[T]


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
    flex: Optional[float] = 1.0
    side: Optional[str]
    visible: Optional[bool]
    size: Optional[int]
    row: Optional[int]
    col: Optional[int]


class SelectedLayerState(SidePanelLocation):
    layer: Optional[str]


class StatisticsDisplayState(SidePanelLocation):
    pass


class LayerSidePanelState(SidePanelLocation):
    tab: Optional[str]
    tabs: List[str]


class HelpPanelState(SidePanelLocation):
    pass


class LayerListPanelState(SidePanelLocation):
    pass


class CoordinateArray(Model):
    coordinates: List[str]
    labels: List[str]


DimensionScale = Union[Tuple[float, str], Tuple[None, None, CoordinateArray]]

CoordinateSpace = Dict[str, DimensionScale]


class LayerDataSubsource(Model):
    enabled: bool


class CoordinateSpaceTransform(Model):
    outputDimensions: CoordinateSpace
    inputDimensions: Optional[CoordinateSpace]
    sourceRank: Optional[int]
    matrix: List[List[int]]


class LayerDataSource(Model):
    url: str
    transform: Optional[CoordinateSpaceTransform]
    subsources: Dict[str, bool]
    enableDefaultSubsources: Optional[bool] = True


class Layer(Model):
    source: List[Union[str, LayerDataSource]] | Union[str, LayerDataSource]
    name: str
    visible: Optional[bool]
    tab: Optional[str]
    type: Optional[LayerType]
    layerDimensions: Optional[CoordinateSpace]
    layerPosition: Optional[float]
    panels: Optional[List[LayerSidePanelState]]
    pick: Optional[bool]
    tool_bindings: Optional[Dict[str, Tool]]
    tool: Optional[Tool]


class PointAnnotationLayer(Layer):
    points: List[PointType]


class AnnotationLayerOptions(Model):
    annotationColor: Optional[str]


class InvlerpParameters(Model):
    range: Optional[Tuple[float, float]]
    window: Optional[Tuple[float, float]]
    channel: Optional[List[int]]


ShaderControls = Union[float, str, InvlerpParameters, Dict[str, float]]


class NewLayer(Layer):
    type: Literal["new"]


class ImageLayer(Layer):
    type: Literal["image"]
    shader: Optional[str]
    shaderControls: Optional[ShaderControls]
    opacity: float = 0.05
    blend: Optional[str]
    crossSectionRenderScale: Optional[float] = 1.0


class SkeletonRenderingOptions(Model):
    shader: str
    shaderControls: ShaderControls
    mode2d: Optional[str]
    lineWidth2d: Optional[float] = 2.0
    mode3d: Optional[str]
    lineWidth3d: Optional[float] = 1.0


class SegmentationLayer(Layer):
    type: Literal["segmentation"]
    segments: Optional[List[str]]
    equivalences: Optional[Dict[int, int]]
    hideSegmentZero: Optional[bool] = True
    selectedAlpha: Optional[float] = 0.5
    notSelectedAlpha: Optional[float] = 0.0
    objectAlpha: Optional[float] = 1.0
    saturation: Optional[float] = 1.0
    ignoreNullVisibleSet: Optional[bool] = True
    skeletonRendering: Optional[SkeletonRenderingOptions]
    colorSeed: Optional[int] = 0
    crossSectionRenderScale: Optional[float] = 1.0
    meshRenderScale: Optional[float] = 10.0
    meshSilhouetteRendering: Optional[float] = 0.0
    segmentQuery: Optional[str]
    segmentColors: Optional[Dict[int, str]]
    segmentDefaultColor: Optional[str]
    linkedSegmentationGroup: Optional[str]
    linkedSegmentationColorGroup: Optional[Union[str, Literal[False]]]


class MeshLayer(Layer):
    type: Literal["mesh"]
    vertexAttributeSources: Optional[List[str]]
    shader: str
    vertexAttributeNames: Optional[List[Union[str, None]]]


class AnnotationBase(Model):
    id: Optional[str]
    type: str
    description: Optional[str]
    segments: Optional[List[int]]
    props: List[Union[int, str]]


class PointAnnotation(AnnotationBase):
    point: List[float]


class LineAnnotation(AnnotationBase):
    pointA: List[float]
    pointB: List[float]


AxisAlignedBoundingBoxAnnotation = LineAnnotation


class EllipsoidAnnotation(AnnotationBase):
    center: List[float]
    radii: List[float]


Annotations = Union[
    PointAnnotation,
    LineAnnotation,
    EllipsoidAnnotation,
    AxisAlignedBoundingBoxAnnotation,
]


class AnnotationPropertySpec(Model):
    id: str
    type: str
    description: Optional[str]
    default: Optional[Union[float, str]]
    enum_values: Optional[List[Union[float, str]]]
    enum_labels: Optional[List[str]]


class AnnotationLayer(Layer, AnnotationLayerOptions):
    type: Literal["annotation"]
    annotations: Optional[List[Annotations]]
    annotationProperties: Optional[List[AnnotationPropertySpec]]
    annotationRelationships: Optional[List[str]]
    linkedSegmentationLayer: Dict[str, str]
    filterBySegmentation: List[str]
    ignoreNullSegmentFilter: Optional[bool] = True
    shader: Optional[str]
    shaderControls: Optional[ShaderControls]


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
    position: Linked[List[float]]
    orientation: Linked[Quaternion]
    scale: Linked[float]


class DataPanelLayout(Model):
    type: str
    crossSections: Dict[str, CrossSection]
    orthographicProjection: Optional[bool]


class LayerGroupViewer(Model):
    type: str
    layers: List[str]
    layout: DataPanelLayout
    position: Linked[List[float]]
    crossSectionOrientation: Linked[Quaternion]
    crossSectionScale: Linked[float]
    crossSectionDepth: Linked[float]
    projectionOrientation: Linked[Tuple[float, float, float, float]]
    projectionScale: Linked[float]
    projectionDepth: Linked[float]


LayoutSpecification = Union[str, LayerGroupViewer, DataPanelLayout]


class StackLayout(Model):
    type: Literal["row", "column"]
    children: List[LayoutSpecification]


class ViewerState(Model):
    title: Optional[str]
    dimensions: Optional[CoordinateSpace]
    relativeDisplayScales: Optional[Dict[str, float]]
    displayDimensions: Optional[List[str]]
    position: Optional[Tuple[float, float, float]]
    crossSectionOrientation: Optional[Quaternion]
    crossSectionScale: Optional[float]
    crossSectionDepth: Optional[float]
    projectionScale: Optional[float]
    projectionDeth: Optional[float]
    projectionOrientation: Optional[Quaternion]
    showSlices: Optional[bool] = True
    showAxisLines: Optional[bool] = True
    showScaleBar: Optional[bool] = True
    showDefaultAnnotations: Optional[bool] = True
    gpuMemoryLimit: Optional[int]
    systemMemoryLimit: Optional[int]
    concurrentDownloads: Optional[int]
    prefetch: Optional[bool] = True
    layers: List[LayerType]
    layout: LayoutSpecification
    crossSectionBackgroundColor: Optional[str]
    projectionBackgroundColor: Optional[str]
    selectedLayer: Optional[SelectedLayerState]
    statistics: Optional[StatisticsDisplayState]
    helpPanel: Optional[HelpPanelState]
    layerListPanel: Optional[LayerListPanelState]
    partialViewport: Optional[Quaternion] = (0, 0, 1, 1)
    selection: Optional[Dict[str, int]]


def main():
    print(ViewerState.schema_json(indent=2))


if __name__ == "__main__":
    main()
