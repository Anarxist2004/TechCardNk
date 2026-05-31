let measureRects = []
let actual_measureRect_data = [] // [цвет, толщина, x1, y1, x2, y2, measure_id]

function drawMeasureRect(e) {
    const coords = getCanvasCoords(e)
    const startX = coords.x
    const startY = coords.y

    actual_measureRect_data = []
    actual_measureRect_data.push("yellow", 1)
    actual_measureRect_data.push(startX, startY)
}

function drawingMeasureRect(e) {
    if (!isDrawing) return

    const coords = getCanvasCoords(e)
    const x = coords.x
    const y = coords.y

    const startX = actual_measureRect_data[2]
    const startY = actual_measureRect_data[3]

    const left = Math.min(startX, x)
    const top = Math.min(startY, y)
    const width = Math.abs(x - startX)
    const height = Math.abs(y - startY)

    ctx.strokeStyle = "yellow"
    ctx.lineWidth = 1

    ctx.beginPath()
    ctx.rect(left, top, width, height)
    ctx.stroke()

    drawRectDimensions(left, top, width, height)
}

function measureRectEnd(e) {
    const coords = getCanvasCoords(e)
    const endX = coords.x
    const endY = coords.y

    actual_measureRect_data.push(endX, endY, measure_id)
    measure_id += 1

    measureRects.push([...actual_measureRect_data])
}

function drawAllMeasureRects() {
    measureRects.forEach(rect => {

        const x1 = rect[2]
        const y1 = rect[3]
        const x2 = rect[4]
        const y2 = rect[5]

        const left = Math.min(x1, x2)
        const top = Math.min(y1, y2)
        const width = Math.abs(x2 - x1)
        const height = Math.abs(y2 - y1)

        ctx.strokeStyle = rect[0]
        ctx.lineWidth = rect[1]

        ctx.beginPath()
        ctx.rect(left, top, width, height)
        ctx.stroke()

        drawRectDimensions(left, top, width, height)
    })
}

function drawRectDimensions(x, y, widthPx, heightPx) {

    const width = Math.abs(widthPx) * mmToPx_ratio
    const height = Math.abs(heightPx) * mmToPx_ratio

    ctx.font = "14px Arial"
    ctx.fillStyle = "yellow"
    ctx.strokeStyle = "black"
    ctx.lineWidth = 1
    ctx.textAlign = "center"
    ctx.textBaseline = "bottom"

    const textW = width.toFixed(2)
    ctx.strokeText(textW, x + widthPx / 2, y - 5)
    ctx.fillText(textW, x + widthPx / 2, y - 5)

    const textH = height.toFixed(2)

    ctx.save()
    ctx.translate(x - 5, y + heightPx / 2)
    ctx.rotate(-Math.PI / 2)

    ctx.strokeText(textH, 0, 0)
    ctx.fillText(textH, 0, 0)

    ctx.restore()
}

function findPointInMeasureRect(e) {

    const coords = getCanvasCoords(e)
    const x = coords.x
    const y = coords.y

    let counter = 0

    measureRects.forEach(rect => {

        const x1 = rect[2]
        const y1 = rect[3]
        const x2 = rect[4]
        const y2 = rect[5]

        const left = Math.min(x1, x2)
        const right = Math.max(x1, x2)
        const top = Math.min(y1, y2)
        const bottom = Math.max(y1, y2)

        const tol = 6

        const nearEdge =
            (y >= top - tol && y <= top + tol && x >= left && x <= right) ||
            (y >= bottom - tol && y <= bottom + tol && x >= left && x <= right) ||
            (x >= left - tol && x <= left + tol && y >= top && y <= bottom) ||
            (x >= right - tol && x <= right + tol && y >= top && y <= bottom)

        if (nearEdge) {

            ctx.beginPath()
            ctx.rect(left, top, right - left, bottom - top)
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = rect[1] + 1
            ctx.stroke()

            mouse_over_element = true

            measureRects_without_hovered_element =
                measureRects.slice(0, counter)
                .concat(measureRects.slice(counter + 1))

            element_to_add = [
                "rect",
                [
                    Math.abs(right - left) * mmToPx_ratio,
                    Math.abs(top - bottom) * mmToPx_ratio
                ],
                rect[6]
            ]

            drawMeasureRectHandles(left, top, right, bottom, rect[0])
        }

        counter++
    })
}

function drawMeasureRectHandles(left, top, right, bottom, color) {
    const size = 3

    ctx.fillStyle = "white"
    ctx.strokeStyle = color
    ctx.lineWidth = 1

    const points = [
        [left, top],
        [right, top],
        [left, bottom],
        [right, bottom]
    ]

    points.forEach(p => {
        ctx.beginPath()
        ctx.rect(p[0] - size / 2, p[1] - size / 2, size, size)
        ctx.fill()
        ctx.stroke()
    })
}

function findMeasureRectHandle(coords) {

    const radius = 5

    for (let i = 0; i < measureRects.length; i++) {
        const r = measureRects[i]

        const x1 = r[2]
        const y1 = r[3]
        const x2 = r[4]
        const y2 = r[5]

        const handles = [
            { name: "tl", x: x1, y: y1 },
            { name: "tr", x: x2, y: y1 },
            { name: "bl", x: x1, y: y2 },
            { name: "br", x: x2, y: y2 }
        ]

        for (let h of handles) {
            if (distance(coords.x, coords.y, h.x, h.y) < radius) {
                return { index: i, handle: h.name }
            }
        }
    }
    return null
}

function findMeasureRectBody(coords) {

    for (let i = 0; i < measureRects.length; i++) {
        const r = measureRects[i]

        const x1 = Math.min(r[2], r[4])
        const x2 = Math.max(r[2], r[4])
        const y1 = Math.min(r[3], r[5])
        const y2 = Math.max(r[3], r[5])

        const tol = 6

        const onEdge =
            (coords.y >= y1 - tol && coords.y <= y1 + tol && coords.x >= x1 && coords.x <= x2) ||
            (coords.y >= y2 - tol && coords.y <= y2 + tol && coords.x >= x1 && coords.x <= x2) ||
            (coords.x >= x1 - tol && coords.x <= x1 + tol && coords.y >= y1 && coords.y <= y2) ||
            (coords.x >= x2 - tol && coords.x <= x2 + tol && coords.y >= y1 && coords.y <= y2)

        if (onEdge) return i
    }

    return null
}

function moveMeasureRectHandle(index, handle, x, y) {

    const r = measureRects[index]

    if (handle === "tl") {
        r[2] = x
        r[3] = y
    }

    if (handle === "tr") {
        r[4] = x
        r[3] = y
    }

    if (handle === "bl") {
        r[2] = x
        r[5] = y
    }

    if (handle === "br") {
        r[4] = x
        r[5] = y
    }
}

function moveMeasureRect(index, x, y) {

    const r = measureRects[index]

    const dx = x - mouse_x
    const dy = y - mouse_y

    r[2] += dx
    r[3] += dy
    r[4] += dx
    r[5] += dy
}

function distance(x1, y1, x2, y2) {
    return Math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
}