let rulers = []
let actual_ruler_data = [] // [цвет, толщина, x1, y1, x2, y2]
let linewidth = 1

function drawRuler(e) {
    const coords = getCanvasCoords(e);
    const startX = coords.x;
    const startY = coords.y;

    actual_ruler_data = []
    actual_ruler_data.push("yellow", linewidth)
    actual_ruler_data.push(startX, startY, startX, startY)

    ctx.moveTo(startX, startY)
}

function drawingRuler(e) {
    if (!isDrawing) return

    const coords = getCanvasCoords(e)
    const x = coords.x
    const y = coords.y

    const startX = actual_ruler_data[2]
    const startY = actual_ruler_data[3]

    ctx.strokeStyle = "yellow"
    ctx.lineWidth = linewidth
    ctx.lineCap = "round"

    ctx.beginPath()
    ctx.moveTo(startX, startY)
    ctx.lineTo(x, y)
    ctx.stroke()

    const dx = x - startX
    const dy = y - startY
    const length = Math.sqrt(dx * dx + dy * dy) * mmToPx_ratio 

    drawLengthText(startX, startY, x, y, length)
}

function rulerEnd(e) {
    const coords = getCanvasCoords(e)
    const endX = coords.x
    const endY = coords.y

    actual_ruler_data[4] = endX
    actual_ruler_data[5] = endY

    const startX = actual_ruler_data[2]
    const startY = actual_ruler_data[3]

    const dx = endX - startX
    const dy = endY - startY
    const length = Math.sqrt(dx * dx + dy * dy)

    if (length >= 5) {
        rulers.push([...actual_ruler_data])
    }
}

function drawAllRulers() {
    rulers.forEach(ruler => {
        const x1 = ruler[2]
        const y1 = ruler[3]
        const x2 = ruler[4]
        const y2 = ruler[5]

        ctx.beginPath()
        ctx.moveTo(x1, y1)
        ctx.lineTo(x2, y2)

        ctx.strokeStyle = ruler[0]
        ctx.lineWidth = ruler[1]
        ctx.lineCap = "round"
        ctx.stroke()

        const dx = x2 - x1
        const dy = y2 - y1
        const length = Math.sqrt(dx * dx + dy * dy) * mmToPx_ratio 

        drawLengthText(x1, y1, x2, y2, length)
    })
}

function findPointInRuler(e) {
    const coords = getCanvasCoords(e)
    const x = coords.x
    const y = coords.y

    let counter = 0

    rulers.forEach(ruler => {

        const x1 = ruler[2]
        const y1 = ruler[3]
        const x2 = ruler[4]
        const y2 = ruler[5]

        const dx = x2 - x1
        const dy = y2 - y1

        const length2 = dx * dx + dy * dy

        let t = ((x - x1) * dx + (y - y1) * dy) / length2
        t = Math.max(0, Math.min(1, t))

        const projX = x1 + t * dx
        const projY = y1 + t * dy

        const dist = Math.sqrt(
            (x - projX) * (x - projX) +
            (y - projY) * (y - projY)
        )

        if (dist < 6) {
            ctx.beginPath()
            ctx.moveTo(x1, y1)
            ctx.lineTo(x2, y2)
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = ruler[1]
            ctx.stroke()

            mouse_over_element = true

            rulers_without_hovered_element =
                rulers.slice(0, counter)
                .concat(rulers.slice(counter + 1))

            element_to_add = []
            drawRulerDragPoints(x1, y1, x2, y2, ruler[0])
        }

        counter++
    })
}

function drawRulerDragPoints(x1, y1, x2, y2, color) {
    const size = 3

    ctx.fillStyle = "white"
    ctx.strokeStyle = color
    ctx.lineWidth = 1

    ctx.beginPath()
    ctx.rect(x1 - size / 2, y1 - size / 2, size, size)
    ctx.fill()
    ctx.stroke()

    ctx.beginPath()
    ctx.rect(x2 - size / 2, y2 - size / 2, size, size)
    ctx.fill()
    ctx.stroke()
}

function drawLengthText(x1, y1, x2, y2, length) {
    const midX = (x1 + x2) / 2
    const midY = (y1 + y2) / 2

    let dx = x2 - x1
    let dy = y2 - y1
    let angle = Math.atan2(dy, dx)

    if (angle > Math.PI / 2 || angle < -Math.PI / 2) {
        angle += Math.PI
    }

    ctx.save()
    ctx.translate(midX, midY)
    ctx.rotate(angle)

    ctx.font = "14px Arial"
    ctx.fillStyle = "yellow"
    ctx.strokeStyle = "black"
    ctx.lineWidth = linewidth
    ctx.textAlign = "center"
    ctx.textBaseline = "bottom"

    const text = length.toFixed(2)

    ctx.strokeText(text, 0, -10)
    ctx.fillText(text, 0, -10)

    ctx.restore()
}

function findRulerHandle(coords) {
    for (let i = 0; i < rulers.length; i++) {
        const r = rulers[i]

        const handles = [
            { name: "start", x: r[2], y: r[3] },
            { name: "end", x: r[4], y: r[5] }
        ]

        for (let h of handles) {
            if (distance(coords.x, coords.y, h.x, h.y) < HANDLE_RADIUS) {
                return { index: i, handle: h.name }
            }
        }
    }
    return null
}

function findRulerBody(coords) {
    for (let i = 0; i < rulers.length; i++) {
        const r = rulers[i]

        const dist = pointToSegmentDistance(
            coords.x, coords.y,
            r[2], r[3],
            r[4], r[5]
        )

        if (dist < CLICK_THRESHOLD) {
            return i
        }
    }
    return null
}

function moveRulerHandle(index, handle, x, y) {
    const r = rulers[index]

    if (handle === "start") {
        r[2] = x
        r[3] = y
    }

    if (handle === "end") {
        r[4] = x
        r[5] = y
    }
}

function moveRuler(index, x, y) {
    const r = rulers[index]

    const dx = x - lastMouse.x
    const dy = y - lastMouse.y

    r[2] += dx
    r[3] += dy
    r[4] += dx
    r[5] += dy

    lastMouse.x = x
    lastMouse.y = y
}

function distance(x1, y1, x2, y2) {
    return Math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
}

function pointToSegmentDistance(px, py, x1, y1, x2, y2) {
    const dx = x2 - x1
    const dy = y2 - y1

    if (dx === 0 && dy === 0) {
        return distance(px, py, x1, y1)
    }

    const t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    const clamped = Math.max(0, Math.min(1, t))

    const projX = x1 + clamped * dx
    const projY = y1 + clamped * dy

    return distance(px, py, projX, projY)
}