from pydantic import BaseModel
from typing import Dict, Optional, Literal, List, Tuple, Union
from enum import Enum

PointType = Tuple[float, float, float]
LayerType = Literal['image', 'segmentation']
DataPanelLayoutTypes = Literal['xy', 'yz', 'xz', 'xy-3d', 'yz-3d', 'xz-3d', '4panel', '3d']
NavigationLinkType = Literal['linked', 'unlinked', 'relative']

class UnitQuaternion(BaseModel):
    pass

class ToolNameEnum(str, Enum):
    annotatePoint = 'annotatePoint'
    annotateLine = 'annotateLine'
    annotateBoundingBox = 'annotateBoundingBox'
    annotateSphere = 'annotateSphere'
    blend = 'blend'
    opacity = 'opacity'
    crossSectionRenderScale = 'crossSectionRenderScale'
    selectedAlpha = 'selectedAlpha'
    notSelectedAlpha = 'notSelectedAlpha'
    objectAlpha = 'objectAlpha'
    hideSegmentZero = 'hideSegmentZero'
    baseSegmentColoring = 'baseSegmentColoring'
    ignoreNullVisibleSet = 'ignoreNullVisibleSet'
    colorSeed = 'colorSeed'
    segmentDefaultColor = 'segmentDefaultColor'
    meshRenderScale = 'meshRenderScale'
    saturation = 'saturation'
    skeletonRendering_mode2d = 'skeletonRendering.mode2d'
    skeletonRendering_lineWidth2d = 'skeletonRendering.lineWidth2d'
    skeletonRendering_lineWidth3d = 'skeletonRendering.lineWidth3d'
    shaderControl = 'shaderControl'
    mergeSegments = 'mergeSegments'
    splitSegments = 'splitSegments'
    selectSegments = 'selectSegments'


class Tool(BaseModel):
    type: ToolNameEnum

class ControlTool(Tool):
    control: str

class SidePanelLocation(BaseModel):
    flex: Optional[float] = 1.0
    side: Optional[str]
    visible: Optional[bool]
    size: Optional[int]
    row: Optional[int]
    col = Optional[int]

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

class CoordinateSpace(BaseModel):
    pass

class LayerSidePanelState(BaseModel):
    pass

class Layer(BaseModel):
    type: Optional[LayerType]
    layerDimensions: CoordinateSpace
    layerPosition: Optional[float]
    panels: List[LayerSidePanelState]
    pick: Optional[bool]
    tool_bindings: Dict[str, Tool]
    tool: Optional[Tool]

class PointAnnotationLayer(Layer):
    points: List[PointType]

class CoordinateSpaceTransform(BaseModel):
    outputDimensions: CoordinateSpace
    inputDimensions: Optional[CoordinateSpace]
    sourceRank: Optional[int]
    matrix: List[List[int]]

class LayerDataSubsource(BaseModel):
    enabled: bool

class LayerDataSource(BaseModel):
    url: URL
    transform: Optional[CoordinateSpaceTransform]
    subsources: Dict[str, LayerDataSubsource]
    enableDefaultSubsources: Optional[bool] = True

class AnnotationLayerOptions(BaseModel):
    annotationColor: Optional[str]

class InvlerpParameters(BaseModel):
    range: Optional[Tuple[float, float]]
    window: Optional[Tuple[float, float]]
    channel: Optional[List[int]]

ShaderControls = Union[float, str, InvlerpParameters]

class ImageLayer(Layer)    :
    source: List[LayerDataSource]
    shader: str
    shaderControls: ShaderControls
    opacity: float = .05
    blend: Optional[str]
    crossSectionRenderScale: Optional[float] = 1.0


class SkeletonRenderingOptions(BaseModel):
    shader: str
    shaderControls:  ShaderControls
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
    linkedSegmentationColorGroup: Optional[Union[str, Literal[False]]

class SingleMeshLayer(Layer):
    vertexAttributeSources: Optional[List[str]]
    shader: str
    vertexAttributeNames: Optional[List[Union[str, None]]

class AnnotationBase(BaseModel):
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

class EllipseAnnotation(AnnotationBase):
    center: List[float]
    radii: List[float]

Annotations = Union[PointAnnotation, LineAnnotation, EllipsoidAnnotation, AxisAlignedBoundBoxAnnotation]

class AnnotationPropertySpec(BaseModel):
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

LayerTypes = Union[ImagerLayer,
                   SegmentationLayer,
                   PointAnnotationLayer,
                   AnnotationLayer,
                   SingleMeshLayer]


class DataPanelLayout(BaseModel):
    type: str
    crossSections: CrossSectionMap
    orthographicProjection: Optional[bool]


LayoutSpecification = Union[str, StackLayout, LayerGroupViewer, DataPanelLayout]

class StackLayout(BaseModel):
    type: Literal['row', 'column']
    children: List[LayoutSpecification]

T = TypeVar('T')
class Linked(GenericModel, Generic[T]):
    link: Optional[NavigationLinkType] = 'linked'
    value: Optional[T]


class LayerGroupViewer(BaseModel):
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


class ViewerState(BaseModel):
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
