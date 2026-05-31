let dragState = null
let activeFigure = null
let activeHandle = null
let isDragging = false

const HANDLE_RADIUS = 3
const CLICK_THRESHOLD = 6

let lastMouse = { x: 0, y: 0 }

function startDrag(e) {
    const coords = getCanvasCoords(e)

    activeFigure = null
    activeHandle = null
    dragState = null

    lastMouse.x = coords.x
    lastMouse.y = coords.y

    const handleHit = findRulerHandle(coords)
    if (handleHit) {
        isDragging = true
        activeFigure = handleHit.index
        activeHandle = handleHit.handle
        dragState = "ruler-handle"
        return
    }

    const bodyHit = findRulerBody(coords)
    if (bodyHit !== null) {
        isDragging = true
        activeFigure = bodyHit
        dragState = "ruler-move"
        return
    }

    const rectHandle = findMeasureRectHandle(coords)
    if (rectHandle) {
        isDragging = true
        activeFigure = rectHandle.index
        activeHandle = rectHandle.handle
        dragState = "measureRect-handle"
        return
    }

    const rectBody = findMeasureRectBody(coords)
    if (rectBody !== null) {
        isDragging = true
        activeFigure = rectBody
        dragState = "measureRect-move"
        return
    }

    const ellipseHandle = findMeasureEllipseHandle(coords)
    if (ellipseHandle) {
        isDragging = true
        activeFigure = ellipseHandle.index
        activeHandle = ellipseHandle.handle
        dragState = "measureEllipse-handle"
        return
    }

    const ellipseBody = findMeasureEllipseBody(coords)
    if (ellipseBody !== null) {
        isDragging = true
        activeFigure = ellipseBody
        dragState = "measureEllipse-move"
        return
    }
}

function onDrag(e) {
    if (!isDragging) return

    const coords = getCanvasCoords(e)

    const dx = coords.x - lastMouse.x
    const dy = coords.y - lastMouse.y

    if (dragState === "ruler-handle") {
        moveRulerHandle(activeFigure, activeHandle, coords.x, coords.y)
    }

    if (dragState === "ruler-move") {
        moveRuler(activeFigure, coords.x, coords.y)
    }

    if (dragState === "measureRect-handle") {
        moveMeasureRectHandle(activeFigure, activeHandle, coords.x, coords.y)
    }

    if (dragState === "measureRect-move") {
        const r = measureRects[activeFigure]

        r[2] += dx
        r[3] += dy
        r[4] += dx
        r[5] += dy
    }

    if (dragState === "measureEllipse-handle") {
        moveMeasureEllipseHandle(activeFigure, activeHandle, coords.x, coords.y)
    }

    if (dragState === "measureEllipse-move") {
        moveMeasureEllipse(activeFigure, coords.x, coords.y)
    }

    lastMouse.x = coords.x
    lastMouse.y = coords.y

    redrawAll()
}

function endDrag() {
    isDragging = false
    dragState = null
    activeFigure = null
    activeHandle = null
}

function distance(x1, y1, x2, y2) {
    return Math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
}