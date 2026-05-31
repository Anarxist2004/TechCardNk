let measureEllipses3 = []
let measureEllipses3_without_hovered_element = []
let actual_measureEllipse3_data = []  // [цвет, толщина, xA, yA, xB, yB, xC, yC, measure_id]
let points_measure3 = []
let measureEllipse3_status = 1

// рисуем маркер точки
function drawPointMarker(x, y) {
    ctx.fillStyle = "red"
    ctx.beginPath()
    ctx.arc(x, y, 1, 0, 2 * Math.PI)
    ctx.fill()
}

// старт рисования эллипса по 3 точкам
function drawMeasureEllipse3(e) {
    const coords = getCanvasCoords(e)
    const x = coords.x
    const y = coords.y

    points_measure3.push({x, y})
    drawPointMarker(x, y)

    if(measureEllipse3_status === 1) {
        actual_measureEllipse3_data = ["yellow", 1, x, y]
        measureEllipse3_status = 2
    } else if(measureEllipse3_status === 2) {
        actual_measureEllipse3_data.push(x, y)
        measureEllipse3_status = 3
    } else if(measureEllipse3_status === 3) {
        actual_measureEllipse3_data.push(x, y, measure_id)
        measure_id += 1
        drawCurrentMeasureEllipse3(actual_measureEllipse3_data)
        measureEllipses3.push(actual_measureEllipse3_data)
        points_measure3 = []
        measureEllipse3_status = 1
    }
}

// отрисовка всех эллипсов
function drawAllMeasureEllipses3() {
    measureEllipses3.forEach(el => drawCurrentMeasureEllipse3(el))
    points_measure3.forEach(pt => drawPointMarker(pt.x, pt.y))
}

// отрисовка одного эллипса + подписи
function drawCurrentMeasureEllipse3(el) {
    const xA = el[2], yA = el[3]
    const xB = el[4], yB = el[5]
    const xC = el[6], yC = el[7]

    const cx = (xA + xB)/2
    const cy = (yA + yB)/2

    const dx = xB - xA
    const dy = yB - yA
    const a = Math.sqrt(dx*dx + dy*dy)/2
    const angle = Math.atan2(dy, dx)

    const cxC = xC - cx
    const cyC = yC - cy
    const b = Math.sqrt(cxC*cxC + cyC*cyC)

    ctx.strokeStyle = el[0]
    ctx.lineWidth = el[1]
    ctx.beginPath()
    ctx.ellipse(cx, cy, a, b, angle, 0, 2*Math.PI)
    ctx.stroke()

    drawEllipseDimensionsEllipse3(cx, cy, a, b, angle)
}

function drawEllipseDimensionsEllipse3(cx, cy, a, b, angle) {
    ctx.save()
    ctx.translate(cx, cy)

    let angleBig = angle
    if(angleBig > Math.PI/2 || angleBig < -Math.PI/2) angleBig += Math.PI

    ctx.save()
    ctx.rotate(angleBig)
    ctx.font = "14px Arial"
    ctx.fillStyle = "yellow"
    ctx.strokeStyle = "black"
    ctx.lineWidth = 1
    ctx.textAlign = "center"
    ctx.textBaseline = "bottom"

    const offsetBig = 17
    ctx.strokeText((a*2*mmToPx_ratio).toFixed(2), 0, -b - offsetBig)
    ctx.fillText((a*2*mmToPx_ratio).toFixed(2), 0, -b - offsetBig)
    ctx.restore()

    let angleSmall = angle - Math.PI/2
    if(angleSmall > Math.PI/2 || angleSmall < -Math.PI/2) angleSmall += Math.PI

    ctx.save()
    ctx.rotate(angleSmall)
    ctx.font = "14px Arial"
    ctx.fillStyle = "yellow"
    ctx.strokeStyle = "black"
    ctx.lineWidth = 1
    ctx.textAlign = "center"
    ctx.textBaseline = "bottom"

    const offsetSmall = 27
    ctx.strokeText((b*2*mmToPx_ratio).toFixed(2), 0, -a - offsetSmall)
    ctx.fillText((b*2*mmToPx_ratio).toFixed(2), 0, -a - offsetSmall)
    ctx.restore()

    ctx.restore()
}

function findPointInMeasureEllipse3(e) {
    const coords = getCanvasCoords(e)
    const x = coords.x
    const y = coords.y

    let counter = 0
    measureEllipses3.forEach(el => {
        const xA = el[2], yA = el[3]
        const xB = el[4], yB = el[5]
        const xC = el[6], yC = el[7]

        const cx = (xA + xB)/2
        const cy = (yA + yB)/2

        const dx = xB - xA
        const dy = yB - yA
        const a = Math.sqrt(dx*dx + dy*dy)/2
        const angle = Math.atan2(dy, dx)

        const cxC = xC - cx
        const cyC = yC - cy
        const b = Math.sqrt(cxC*cxC + cyC*cyC)

        const cosA = Math.cos(-angle)
        const sinA = Math.sin(-angle)
        const xr = (x - cx) * cosA - (y - cy) * sinA
        const yr = (x - cx) * sinA + (y - cy) * cosA

        const val = (xr*xr)/(a*a) + (yr*yr)/(b*b)

        if(val >= 0.9 && val <= 1.1) {
            ctx.beginPath()
            ctx.ellipse(cx, cy, a, b, angle, 0, 2*Math.PI)
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = el[1] + 1
            ctx.stroke()

            mouse_over_element = true

            measureEllipses3_without_hovered_element =
                measureEllipses3.slice(0, counter)
                .concat(measureEllipses3.slice(counter+1))
            element_to_add = ["ellipse3", [Math.abs(a*2) * mmToPx_ratio, Math.abs(b*2) * mmToPx_ratio], el[8]]
            console.log(element_to_add[2])
        }

        counter++
    })
}
