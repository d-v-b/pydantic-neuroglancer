from __future__ import annotations

from pydantic import BaseModel, Extra, Field
from pydantic.generics import GenericModel
from typing import Generic, Literal, Optional, TypeVar, Union
from typing_extensions import Annotated
from enum import Enum

PointType = tuple[float, float, float]
LayerType = Literal["new", "image", "segmentation", "annotation", "mesh"]
DataPanelLayoutTypes = Literal[
    "xy", "yz", "xz", "xy-3d", "yz-3d", "xz-3d", "4panel", "3d"
]

NavigationLinkType = Literal["linked", "unlinked", "relative"]

T = TypeVar("T")

Quaternion = tuple[float, float, float, float]


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
    tabs: list[str]


class HelpPanelState(SidePanelLocation):
    pass


class LayerListPanelState(SidePanelLocation):
    pass


class CoordinateArray(Model):
    coordinates: list[str]
    labels: list[str]


DimensionScale = Union[tuple[float, str], tuple[None, None, CoordinateArray]]

CoordinateSpace = dict[str, DimensionScale]


class LayerDataSubsource(Model):
    enabled: bool


class CoordinateSpaceTransform(Model):
    outputDimensions: CoordinateSpace
    inputDimensions: Optional[CoordinateSpace]
    sourceRank: Optional[int]
    matrix: Optional[list[list[int]]]


class LayerDataSource(Model):
    url: str
    transform: Optional[CoordinateSpaceTransform]
    subsources: Optional[dict[str, bool]]
    enableDefaultSubsources: Optional[bool] = True
    CoordinateSpaceTransform: Optional[CoordinateSpaceTransform]


class Layer(Model):
    type: Literal['image', 'annotation', 'segmentation', 'mesh', 'new']
    source: Union[LayerDataSource, str, list[Union[str, LayerDataSource]]]
    tab: Optional[str]
    name: str
    visible: Optional[bool]
    type: Optional[LayerType]
    layerDimensions: Optional[CoordinateSpace]
    layerPosition: Optional[float]
    panels: Optional[list[LayerSidePanelState]]
    pick: Optional[bool]
    tool_bindings: Optional[dict[str, Tool]]
    tool: Optional[Tool]


class PointAnnotationLayer(Layer):
    points: list[PointType]


class AnnotationLayerOptions(Model):
    annotationColor: Optional[str]


class InvlerpParameters(Model):
    range: Union[tuple[float, float], tuple[int, int], None]
    window: Union[tuple[float, float], tuple[int, int], None]
    channel: Optional[list[int]]


ShaderControls = dict[str, Union[float, InvlerpParameters]]


class NewLayer(Layer):
    type: Literal["new"]


class ImageLayer(Layer):
    type: Literal["image"] = 'image'
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
    type: Literal["segmentation"] = 'segmentation'
    segments: Union[list[Union[str, int]], None]  # the order of the types in the union matters
    equivalences: Optional[dict[int, int]]
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
    segmentColors: Optional[dict[int, str]]
    segmentDefaultColor: Optional[str]
    linkedSegmentationGroup: Optional[str]
    linkedSegmentationColorGroup: Optional[Union[str, Literal[False]]]


class MeshLayer(Layer):
    type: Literal["mesh"] = 'mesh'
    vertexAttributeSources: Optional[list[str]]
    shader: str
    vertexAttributeNames: Optional[list[Union[str, None]]]


class AnnotationBase(Model):
    id: Optional[str]
    type: str
    description: Optional[str]
    segments: Optional[list[int]]
    props: list[Union[int, str]]


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
    Union[
        PointAnnotation, LineAnnotation, EllipsoidAnnotation, AxisAlignedBoundingBoxAnnotation]
)


class AnnotationPropertySpec(Model):
    id: str
    type: str
    description: Optional[str]
    default: Union[float, str, None]
    enum_values: Optional[list[Union[float, str]]]
    enum_labels: Optional[list[str]]


class AnnotationLayer(Layer, AnnotationLayerOptions):
    type: Literal["annotation"] = "annotation"
    annotations: Optional[list[Annotations]]
    annotationProperties: Optional[list[AnnotationPropertySpec]]
    annotationRelationships: Optional[list[str]]
    linkedSegmentationLayer: dict[str, str]
    filterBySegmentation: list[str]
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
    position: Linked[list[float]]
    orientation: Linked[Quaternion]
    scale: Linked[float]


class DataPanelLayout(Model):
    type: str
    crossSections: dict[str, CrossSection]
    orthographicProjection: Optional[bool]


class LayerGroupViewer(Model):
    type: str
    layers: list[str]
    layout: DataPanelLayout
    position: Linked[list[float]]
    crossSectionOrientation: Linked[Quaternion]
    crossSectionScale: Linked[float]
    crossSectionDepth: Linked[float]
    projectionOrientation: Linked[Quaternion]
    projectionScale: Linked[float]
    projectionDepth: Linked[float]


LayoutSpecification = Union[str, LayerGroupViewer, DataPanelLayout]


class StackLayout(Model):
    type: Literal["row", "column"]
    children: list[LayoutSpecification]


class ViewerState(Model):
    title: Optional[str]
    dimensions: Optional[CoordinateSpace]
    relativeDisplayScales: Optional[dict[str, float]]
    displayDimensions: Optional[list[str]]
    position: Optional[tuple[float, float, float]]
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
    layers: list[LayerType]
    selectedLayer: Optional[SelectedLayerState]
    layout: LayoutSpecification = '4panel'
    crossSectionBackgroundColor: Optional[str]
    projectionBackgroundColor: Optional[str]
    statistics: Optional[StatisticsDisplayState]
    helpPanel: Optional[HelpPanelState]
    layerListPanel: Optional[LayerListPanelState]
    partialViewport: Optional[Quaternion] = (0, 0, 1, 1)
    selection: Optional[dict[str, int]]


def main():
    print(ViewerState.schema_json(indent=2))


if __name__ == "__main__":
    main()
