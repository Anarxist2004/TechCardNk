let ellipses3 = []
let ellipse3_status = 1
let actual_ellipse3_data = [] // [цвет, толщина, xo, y0, x1, y1, x2, y2]
let points3 = [] // временные точки для отображения до построения эллипса

// функция рисования маркера точки
function drawPointMarker(x, y) {
    ctx.fillStyle = "red"
    ctx.beginPath()
    ctx.arc(x, y, 2, 0, 2 * Math.PI)
    ctx.fill()
}

// рисуем эллипс по 3 точкам
function drawEllipse3(e) {
    const coords = getCanvasCoords(e);
    const x = coords.x;
    const y = coords.y;

    // сохраняем точки
    points3.push({x, y});

    // рисуем саму точку на canvas
    drawPointMarker(x, y);

    if (ellipse3_status == 1) {
        actual_ellipse3_data = []
        actual_ellipse3_data.push(colorPicker.value, sizeSlider.value)
        actual_ellipse3_data.push(x, y)
        ellipse3_status = 2
    } else if (ellipse3_status == 2) {
        actual_ellipse3_data.push(x, y)
        ellipse3_status = 3
    } else if (ellipse3_status == 3) {
        actual_ellipse3_data.push(x, y)

        // находим центр (середина AB)
        const O = {
            x: (actual_ellipse3_data[2] + actual_ellipse3_data[4]) / 2,
            y: (actual_ellipse3_data[3] + actual_ellipse3_data[5]) / 2
        }
        // большая полуось (половина расстояния AB)
        const dx = actual_ellipse3_data[4] - actual_ellipse3_data[2]
        const dy = actual_ellipse3_data[5] - actual_ellipse3_data[3]
        const a = Math.sqrt(dx*dx + dy*dy) / 2
        // угол поворота (направление большой оси)
        const angle = Math.atan2(dy, dx)
        // малая полуось (расстояние от центра до точки C)
        const cx = actual_ellipse3_data[6] - O.x
        const cy = actual_ellipse3_data[7] - O.y
        const b = Math.sqrt(cx*cx + cy*cy)

        // рисуем эллипс
        ctx.strokeStyle = colorPicker.value
        ctx.lineWidth = sizeSlider.value
        ctx.lineCap = 'round'
        ctx.beginPath()
        ctx.ellipse(O.x, O.y, a, b, angle, 0, 2 * Math.PI)
        ctx.stroke()

        // сохраняем эллипс
        ellipses3.push([colorPicker.value, sizeSlider.value, O.x, O.y, a, b, angle])

        // очищаем временные точки
        points3 = []

        // возвращаем статус на 1
        ellipse3_status = 1
    }
}

// отрисовка всех предыдущих эллипсов и временных точек
function drawAllEllipses3() {
    // сначала старые эллипсы
    ellipses3.forEach(ellipse => {
        ctx.strokeStyle = ellipse[0]
        ctx.lineWidth = ellipse[1]
        ctx.lineCap = 'round'
        ctx.beginPath()
        ctx.ellipse(ellipse[2], ellipse[3], ellipse[4], ellipse[5], ellipse[6], 0, 2 * Math.PI)
        ctx.stroke()
    })
    // затем временные точки
    points3.forEach(pt => drawPointMarker(pt.x, pt.y))
}

function findPointInEllipse3(e){

    const coords = getCanvasCoords(e)
    const x = coords.x
    const y = coords.y

    let counter = 0

    ellipses3.forEach(el=>{

        const cx = el[2]
        const cy = el[3]
        const a = el[4]
        const b = el[5]
        const angle = el[6]

        // поворачиваем координаты обратно
        const cos = Math.cos(-angle)
        const sin = Math.sin(-angle)

        const dx = x - cx
        const dy = y - cy

        const xr = dx*cos - dy*sin
        const yr = dx*sin + dy*cos

        const value =
            (xr*xr)/(a*a) +
            (yr*yr)/(b*b)

        if(value > 0.9 && value < 1.1){

            ctx.beginPath()
            ctx.ellipse(cx, cy, a, b, angle, 0, Math.PI*2)
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = el[1]
            ctx.stroke()

            mouse_over_element = true

            ellipses3_without_hovered_element =
                ellipses3.slice(0,counter)
                .concat(ellipses3.slice(counter+1))

            element_to_add = []
        }

        counter++

    })
}