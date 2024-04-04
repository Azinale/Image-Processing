import '@kitware/vtk.js/favicon';
import '@kitware/vtk.js/Rendering/Profiles/All';

import vtkGenericRenderWindow from '@kitware/vtk.js/Rendering/Misc/GenericRenderWindow';
import vtkResourceLoader from '@kitware/vtk.js/IO/Core/ResourceLoader';
import vtkITKHelper from '@kitware/vtk.js/Common/DataModel/ITKHelper';

import vtkInteractorStyleImage from '@kitware/vtk.js/Interaction/Style/InteractorStyleImage';
import vtkImageMapper from '@kitware/vtk.js/Rendering/Core/ImageMapper';
import vtkImageSlice from '@kitware/vtk.js/Rendering/Core/ImageSlice';
import ImageConstants from '@kitware/vtk.js/Rendering/Core/ImageMapper/Constants';
import vtkWidgetManager from '@kitware/vtk.js/Widgets/Core/WidgetManager';
import { xyzToViewType } from '@kitware/vtk.js/Widgets/Widgets3D/ResliceCursorWidget/Constants';
import vtkImageReslice from '@kitware/vtk.js/Imaging/Core/ImageReslice';
import { SlabMode } from '@kitware/vtk.js/Imaging/Core/ImageReslice/Constants';
import vtkResliceCursorWidget from '@kitware/vtk.js/Widgets/Widgets3D/ResliceCursorWidget';
import vtkSphereSource from '@kitware/vtk.js/Filters/Sources/SphereSource';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import { CaptureOn } from '@kitware/vtk.js/Widgets/Core/WidgetManager/Constants';

import vtkHttpDataSetReader from '@kitware/vtk.js/IO/Core/HttpDataSetReader';
import httpDataAccessHelper from '@kitware/vtk.js/IO/Core/DataAccessHelper/HttpDataAccessHelper';


const viewEleX = document.querySelector('#xView');
const viewEleY = document.querySelector('#yView');
const viewEleZ = document.querySelector('#zView');
const mprContainer = [viewEleX, viewEleY, viewEleZ];

const viewAttributes = [];

const resliceCursorWidget = vtkResliceCursorWidget.newInstance();
const widgetState = resliceCursorWidget.getWidgetState();


widgetState
    .getStatesWithLabel('rotation')
    .forEach((handle) => {
        handle.setVisible(false);
    });



for (let i = 0; i < 3; i++) {
    const obj = {};

    const genericRenderWindow = vtkGenericRenderWindow.newInstance();
    genericRenderWindow.setContainer(mprContainer[i]);
    genericRenderWindow.getOpenGLRenderWindow().setSize(mprContainer[i].clientWidth, mprContainer[i].clientHeight);
    genericRenderWindow.resize();
    obj.genericRenderWindow = genericRenderWindow;

    const renderer = genericRenderWindow.getRenderer();
    renderer.getActiveCamera().setParallelProjection(true);
    obj.renderer = renderer;

    const renderWindow = genericRenderWindow.getRenderWindow();
    const interactor = vtkInteractorStyleImage.newInstance();
    renderWindow.getInteractor().setInteractorStyle(interactor);
    obj.renderWindow = renderWindow;

    const widgetManager = vtkWidgetManager.newInstance();
    widgetManager.setRenderer(renderer);
    widgetManager.enablePicking();
    widgetManager.setCaptureOn(CaptureOn.MOUSE_MOVE);
    obj.widgetManager = widgetManager;

    const widgetInstance = widgetManager.addWidget(resliceCursorWidget, xyzToViewType[i]);
    widgetInstance.setScaleInPixels(false);
    widgetInstance.setKeepOrthogonality(true);
    obj.widgetInstance = widgetInstance;

    const reslice = vtkImageReslice.newInstance();
    reslice.setSlabNumberOfSlices(1);
    reslice.setTransformInputSampling(false);
    reslice.setAutoCropOutput(true);
    reslice.setOutputDimensionality(2);
    obj.reslice = reslice;

    const resliceMapper = vtkImageMapper.newInstance();
    resliceMapper.setInputConnection(reslice.getOutputPort());
    obj.resliceMapper = resliceMapper;

    const resliceActor = vtkImageSlice.newInstance();
    resliceActor.setMapper(resliceMapper);
    obj.resliceActor = resliceActor;

    viewAttributes.push(obj);
}

function updateReslice(
    interactionContext = {
        viewType: '',
        reslice: null,
        actor: null,
        renderer: null,
        resetFocalPoint: false, 
        keepFocalPointPosition: false, 
        computeFocalPointOffset: false, 
        spheres: null,
    }
) {
    const modified = resliceCursorWidget.updateReslicePlane(
        interactionContext.reslice,
        interactionContext.viewType
    );

    if (modified) {
        const resliceAxes = interactionContext.reslice.getResliceAxes();
        interactionContext.actor.setUserMatrix(resliceAxes);
    }
    resliceCursorWidget.updateCameraPoints(
        interactionContext.renderer,
        interactionContext.viewType,
        interactionContext.resetFocalPoint,
        interactionContext.keepFocalPointPosition,
        interactionContext.computeFocalPointOffset
    );

    return modified;
}

function setupResliceViews(vtkImage) {
    resliceCursorWidget.setImage(vtkImage);

    const bounds = resliceCursorWidget.getWidgetState().getImage().getBounds();
    const ySlider = document.getElementById('slicingScale');
    ySlider.min = bounds[2];
    ySlider.max = bounds[3];
    ySlider.addEventListener('input', (ev) => {
        let center = resliceCursorWidget.getWidgetState().getCenter();
        resliceCursorWidget.setCenter([center[0], ev.target.value, center[2]]);
        updateReslice({
            viewType: xyzToViewType[0],
            reslice: viewAttributes[0].reslice,
            actor: viewAttributes[0].resliceActor,
            renderer: viewAttributes[0].renderer,
            resetFocalPoint: true, 
            keepFocalPointPosition: false,
            computeFocalPointOffset: true,
        });
        viewAttributes[0].renderWindow.render();
    });

    for (let i = 0; i < 3; i++) {
        const obj = viewAttributes[i];

        obj.reslice.setInputData(vtkImage);
        obj.renderer.addActor(obj.resliceActor);
        const viewType = xyzToViewType[i];

        obj.widgetInstance.onInteractionEvent(
            ({ computeFocalPointOffset, canUpdateFocalPoint }) => {
                const activeViewType = resliceCursorWidget.getWidgetState().getActiveViewType();
                const keepFocalPointPosition = activeViewType !== viewType && canUpdateFocalPoint;
                updateReslice({
                    viewType: viewType,
                    reslice: obj.reslice,
                    actor: obj.resliceActor,
                    renderer: obj.renderer,
                    resetFocalPoint: false,
                    keepFocalPointPosition,
                    computeFocalPointOffset,
                });
            });

        updateReslice({
            viewType: viewType,
            reslice: obj.reslice,
            actor: obj.resliceActor,
            renderer: obj.renderer,
            resetFocalPoint: true, 
            keepFocalPointPosition: false,
            computeFocalPointOffset: true,
        });
        obj.renderWindow.getInteractor().render();
    }
}

const reader = vtkHttpDataSetReader.newInstance({ fetchGzip: true });
reader
    .setUrl('https://kitware.github.io/vtk-js/data/volume/LIDC2.vti')
    .then(() => reader.loadData())
    .then(() => {
        const image = reader.getOutputData();
        setupResliceViews(image);
    });