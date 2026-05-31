let measureEllipses = []
let actual_measureEllipse_data = [] // [цвет, толщина, x1, y1, x2, y2, measure_id]

// старт рисования эллипса
function drawMeasureEllipse(e) {
    const coords = getCanvasCoords(e)
    const startX = coords.x
    const startY = coords.y

    actual_measureEllipse_data = []
    actual_measureEllipse_data.push("yellow", 1)
    actual_measureEllipse_data.push(startX, startY)
}

// отрисовка всех измерительных эллипсов
function drawAllMeasureEllipses() {
    measureEllipses.forEach(el => {
        const x1 = el[2], y1 = el[3]
        const x2 = el[4], y2 = el[5]
        const rx = Math.abs(x2 - x1)/2
        const ry = Math.abs(y2 - y1)/2
        const cx = (x1 + x2)/2
        const cy = (y1 + y2)/2

        ctx.strokeStyle = el[0]
        ctx.lineWidth = el[1]
        ctx.beginPath()
        ctx.ellipse(cx, cy, rx, ry, 0, 0, 2 * Math.PI)
        ctx.stroke()

        drawEllipseDimensions(x1, y1, x2, y2)
    })
}

// рисование во время движения мыши
function drawingMeasureEllipse(e) {
    if (!isDrawing) return
    const coords = getCanvasCoords(e)
    const x = coords.x
    const y = coords.y

    const x1 = actual_measureEllipse_data[2]
    const y1 = actual_measureEllipse_data[3]

    const rx = Math.abs(x - x1)/2
    const ry = Math.abs(y - y1)/2
    const cx = (x + x1)/2
    const cy = (y + y1)/2

    ctx.strokeStyle = "yellow"
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.ellipse(cx, cy, rx, ry, 0, 0, 2 * Math.PI)
    ctx.stroke()

    drawEllipseDimensions(x1, y1, x, y)
}

// завершение рисования
function measureEllipseEnd(e) {
    const coords = getCanvasCoords(e)
    const x2 = coords.x
    const y2 = coords.y

    actual_measureEllipse_data.push(x2, y2, measure_id)
    measure_id += 1
    measureEllipses.push(actual_measureEllipse_data)
}

// рисуем размеры эллипса (ширина и высота)
function drawEllipseDimensions(x1, y1, x2, y2) {
    const width = Math.abs(x2 - x1) * mmToPx_ratio
    const height = Math.abs(y2 - y1) * mmToPx_ratio

    ctx.font = "14px Arial"
    ctx.fillStyle = "yellow"
    ctx.strokeStyle = "black"
    ctx.lineWidth = 1
    ctx.textAlign = "center"
    ctx.textBaseline = "bottom"

    // ширина сверху
    ctx.strokeText(width.toFixed(2), (x1 + x2)/2, Math.min(y1, y2) - 20)
    ctx.fillText(width.toFixed(2), (x1 + x2)/2, Math.min(y1, y2) - 20)

    // высота слева
    ctx.save()
    ctx.translate(Math.min(x1, x2) - 5, (y1 + y2)/2)
    ctx.rotate(-Math.PI / 2)
    ctx.strokeText(height.toFixed(2), 0, 0 - 10)
    ctx.fillText(height.toFixed(2), 0, 0 - 10)
    ctx.restore()
}

function findPointInMeasureEllipse(e) {
    const coords = getCanvasCoords(e)
    const x = coords.x
    const y = coords.y
    const tol = 6

    let counter = 0
    measureEllipses.forEach(el => {
        const x1 = el[2], y1 = el[3], x2 = el[4], y2 = el[5]
        const rx = Math.abs(x2 - x1)/2
        const ry = Math.abs(y2 - y1)/2
        const cx = (x1 + x2)/2
        const cy = (y1 + y2)/2

        const value = ((x - cx)*(x - cx))/(rx*rx) + ((y - cy)*(y - cy))/(ry*ry)
        if(value >= 0.9 && value <= 1.1) {
            ctx.beginPath()
            ctx.ellipse(cx, cy, rx, ry, 0, 0, 2*Math.PI)
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = el[1] + 1
            ctx.stroke()

            mouse_over_element = true

            measureEllipses_without_hovered_element =
                measureEllipses.slice(0, counter)
                .concat(measureEllipses.slice(counter+1))
            element_to_add = ["ellipse", [Math.abs(rx*2) * mmToPx_ratio, Math.abs(ry*2) * mmToPx_ratio], el[6]]
        }

        counter++
    })
}

let hoveredMeasureEllipse = null

function drawEllipseHandles(x1, y1, x2, y2) {
    const cx = (x1 + x2) / 2
    const cy = (y1 + y2) / 2

    const rx = Math.abs(x2 - x1) / 2
    const ry = Math.abs(y2 - y1) / 2

    const size = 3

    const points = [
        [cx, cy - ry],
        [cx, cy + ry], 
        [cx - rx, cy], 
        [cx + rx, cy]  
    ]

    ctx.fillStyle = "white"
    ctx.strokeStyle = "yellow"
    ctx.lineWidth = 1

    points.forEach(p => {
        ctx.beginPath()
        ctx.rect(p[0] - size / 2, p[1] - size / 2, size, size)
        ctx.fill()
        ctx.stroke()
    })
}

function drawAllMeasureEllipses() {
    measureEllipses.forEach((el, i) => {

        const x1 = el[2], y1 = el[3]
        const x2 = el[4], y2 = el[5]

        const cx = (x1 + x2) / 2
        const cy = (y1 + y2) / 2

        const rx = Math.abs(x2 - x1) / 2
        const ry = Math.abs(y2 - y1) / 2

        ctx.strokeStyle = el[0]
        ctx.lineWidth = el[1]

        ctx.beginPath()
        ctx.ellipse(cx, cy, rx, ry, 0, 0, 2 * Math.PI)
        ctx.stroke()

        drawEllipseDimensions(x1, y1, x2, y2)

        if (hoveredMeasureEllipse === i) {
            drawEllipseHandles(x1, y1, x2, y2)
        }
    })
}

function findPointInMeasureEllipse(e) {

    hoveredMeasureEllipse = null

    const coords = getCanvasCoords(e)
    const x = coords.x
    const y = coords.y

    let counter = 0

    measureEllipses.forEach(el => {
        const x1 = el[2], y1 = el[3]
        const x2 = el[4], y2 = el[5]

        const cx = (x1 + x2) / 2
        const cy = (y1 + y2) / 2

        const rx = Math.abs(x2 - x1) / 2
        const ry = Math.abs(y2 - y1) / 2

        if (rx === 0 || ry === 0) {
            counter++
            return
        }

        const value =
            ((x - cx) * (x - cx)) / (rx * rx) +
            ((y - cy) * (y - cy)) / (ry * ry)

        const tol = 0.2

        if (value >= 1 - tol && value <= 1 + tol) {

            hoveredMeasureEllipse = counter

            ctx.beginPath()
            ctx.ellipse(cx, cy, rx, ry, 0, 0, 2 * Math.PI)
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = el[1] + 1
            ctx.stroke()

            mouse_over_element = true

            measureEllipses_without_hovered_element =
                measureEllipses.slice(0, counter)
                    .concat(measureEllipses.slice(counter + 1))

            element_to_add = [
                "ellipse",
                [Math.abs(rx * 2) * mmToPx_ratio, Math.abs(ry * 2) * mmToPx_ratio],
                el[6]
            ]

            drawEllipseHandles(x1, y1, x2, y2)
        }

        counter++
    })
}

function findMeasureEllipseHandle(coords) {
    const radius = 5

    for (let i = 0; i < measureEllipses.length; i++) {
        const el = measureEllipses[i]

        const x1 = el[2], y1 = el[3]
        const x2 = el[4], y2 = el[5]

        const cx = (x1 + x2) / 2
        const cy = (y1 + y2) / 2

        const rx = Math.abs(x2 - x1) / 2
        const ry = Math.abs(y2 - y1) / 2

        const handles = [
            { name: "top", x: cx, y: cy - ry },
            { name: "bottom", x: cx, y: cy + ry },
            { name: "left", x: cx - rx, y: cy },
            { name: "right", x: cx + rx, y: cy }
        ]

        for (let h of handles) {
            if (distance(coords.x, coords.y, h.x, h.y) < radius) {
                return { index: i, handle: h.name }
            }
        }
    }

    return null
}

function findMeasureEllipseBody(coords) {

    for (let i = 0; i < measureEllipses.length; i++) {
        const el = measureEllipses[i]

        const x1 = el[2], y1 = el[3]
        const x2 = el[4], y2 = el[5]

        const cx = (x1 + x2) / 2
        const cy = (y1 + y2) / 2

        const rx = Math.abs(x2 - x1) / 2
        const ry = Math.abs(y2 - y1) / 2

        if (rx === 0 || ry === 0) continue

        const dx = coords.x - cx
        const dy = coords.y - cy

        const value =
            (dx * dx) / (rx * rx) +
            (dy * dy) / (ry * ry)

        const tol = 0.2

        if (value >= 1 - tol && value <= 1 + tol) {
            return i
        }
    }

    return null
}

function moveMeasureEllipseHandle(index, handle, x, y) {
    const el = measureEllipses[index]

    if (handle === "left") el[2] = x
    if (handle === "right") el[4] = x
    if (handle === "top") el[3] = y
    if (handle === "bottom") el[5] = y
}

function moveMeasureEllipse(index, x, y) {
    const el = measureEllipses[index]

    const dx = x - lastMouse.x
    const dy = y - lastMouse.y

    el[2] += dx
    el[3] += dy
    el[4] += dx
    el[5] += dy

    lastMouse.x = x
    lastMouse.y = y
}