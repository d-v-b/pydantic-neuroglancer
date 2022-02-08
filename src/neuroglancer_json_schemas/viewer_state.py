import argparse
from pydantic import BaseModel, Extra
from pydantic.generics import GenericModel
from typing import Dict, Generic, Optional, Literal, List, Tuple, TypeVar, Union
from enum import Enum

PointType = Tuple[float, float, float]
LayerType = Literal["image", "segmentation"]
DataPanelLayoutTypes = Literal[
    "xy", "yz", "xz", "xy-3d", "yz-3d", "xz-3d", "4panel", "3d"
]

NavigationLinkType = Literal["linked", "unlinked", "relative"]

T = TypeVar("T")


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
    # col = Optional[int]


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


class CoordinateSpace(Model):
    pass


class LayerSidePanelState(Model):
    pass


class Layer(Model):
    type: Optional[LayerType]
    layerDimensions: CoordinateSpace
    layerPosition: Optional[float]
    panels: List[LayerSidePanelState]
    pick: Optional[bool]
    tool_bindings: Dict[str, Tool]
    tool: Optional[Tool]


class PointAnnotationLayer(Layer):
    points: List[PointType]


class CoordinateSpaceTransform(Model):
    outputDimensions: CoordinateSpace
    inputDimensions: Optional[CoordinateSpace]
    sourceRank: Optional[int]
    matrix: List[List[int]]


class LayerDataSubsource(Model):
    enabled: bool


class LayerDataSource(Model):
    url: str
    transform: Optional[CoordinateSpaceTransform]
    subsources: Dict[str, LayerDataSubsource]
    enableDefaultSubsources: Optional[bool] = True


class AnnotationLayerOptions(Model):
    annotationColor: Optional[str]


class InvlerpParameters(Model):
    range: Optional[Tuple[float, float]]
    window: Optional[Tuple[float, float]]
    channel: Optional[List[int]]


ShaderControls = Union[float, str, InvlerpParameters]


class ImageLayer(Layer):
    source: List[LayerDataSource]
    shader: str
    shaderControls: ShaderControls
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
    segments: List[int]
    equivalences: Dict[int, int]
    hideSegmentZero: Optional[bool] = True
    selectedAlpha: Optional[float] = 0.5
    notSelectedAlpha: Optional[float] = 0.0
    objectAlpha: Optional[float] = 1.0
    saturation: Optional[float] = 1.0
    ignoreNullVisibleSet: Optional[bool] = True
    skeletonRendering: SkeletonRenderingOptions
    colorSeed: Optional[int] = 0
    crossSectionRenderScale: Optional[float] = 1.0
    meshRenderScale: Optional[float] = 10.0
    meshSilhouetteRendering: Optional[float] = 0.0
    segmentQuery: Optional[str]
    segmentColors: Dict[int, str]
    segmentDefaultColor: str
    linkedSegmentationGroup: Optional[str]
    linkedSegmentationColorGroup: Optional[Union[str, Literal[False]]]


class SingleMeshLayer(Layer):
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
    PointAnnotation, LineAnnotation, EllipsoidAnnotation, AxisAlignedBoundingBoxAnnotation
]


class AnnotationPropertySpec(Model):
    id: str
    type: str
    description: Optional[str]
    default: Optional[Union[float, str]]
    enum_values: Optional[List[Union[float, str]]]
    enum_labels: Optional[List[str]]


class AnnotationLayer(Layer, AnnotationLayerOptions):
    source: List[LayerDataSource]
    annotations: List[Annotations]
    annotationProperties: List[AnnotationPropertySpec]
    annotationRelationships: List[str]
    linkedSegmentationLayer: Dict[str, str]
    filterBySegmentation: List[str]
    ignoreNullSegmentFilter: Optional[bool] = True
    shader: str
    shaderControls: ShaderControls


LayerTypes = Union[
    ImageLayer,
    SegmentationLayer,
    PointAnnotationLayer,
    AnnotationLayer,
    SingleMeshLayer,
]

class CrossSection(Model):
    width: int = 1000
    height: int = 1000
    position: Linked[List[float]]
    orientation: Linked[Tuple[float, float, float, float]]
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
    crossSectionOrientation: Linked[Tuple[float, float, float, float]]
    crossSectionScale: Linked[float]
    crossSectionDepth: Linked[float]
    projectionOrientation: Linked[Tuple[float, float, float, float]]
    projectionScale: Linked[float]
    projectionDepth: Linked[float]


class StackLayout(Model):
    type: Literal["row", "column"]
    children: List['LayoutSpecification']

LayoutSpecification = Union[str, StackLayout, LayerGroupViewer, DataPanelLayout]

class ViewerState(Model):
    title: Optional[str]
    dimensions: CoordinateSpace
    relativeDisplayScales: Optional[Dict[str, float]]
    displayDimensions: Optional[List[str]]
    position: Tuple[float, float, float]
    crossSectionOrientation: Optional[Tuple[float, float, float, float]]
    crossSectionScale: Optional[float]
    crossSectionDepth: Optional[float]
    projectionScale: Optional[float]
    projectionDeth: Optional[float]
    projectionOrientation: Tuple[float, float, float, float]
    showSlices: Optional[bool] = True
    showAxisLines: Optional[bool] = True
    showScaleBar: Optional[bool] = True
    showDefaultAnnotations: Optional[bool] = True
    gpuMemoryLimit: Optional[int]
    systemMemoryLimit: Optional[int]
    concurrentDownloads: Optional[int]
    prefetch: Optional[bool] = True
    layers: List[Layer]
    layout: LayoutSpecification
    crossSectionBackgroundColor: Optional[str]
    projectionBackgroundColor: Optional[str]
    selectedLayer: SelectedLayerState
    statistics: StatisticsDisplayState
    helpPanel: HelpPanelState
    layerListPanel: LayerListPanelState
    partialViewport: Optional[Tuple[float, float, float, float]] = (0, 0, 1, 1)

def main():
    print(ViewerState.schema_json(indent=2))

if __name__ == '__main__':
    main()