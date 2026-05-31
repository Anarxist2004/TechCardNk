let ellipses = []
let actual_ellipse_data = [] // [цвет, толщина, xo, y0, middleX, middleY, radiusX, radiusY]

// старт отрисовки эллипса
function drawEllipse(e) {
    const coords = getCanvasCoords(e);
    const startX = coords.x;
    const startY = coords.y;
    

    actual_ellipse_data = []
    actual_ellipse_data.push(colorPicker.value, sizeSlider.value)
    actual_ellipse_data.push(startX, startY)

    ctx.moveTo(startX, startY)
}
// отрисовка всех предыдущих эллипсов
function drawAllEllipses() {
    ellipses.forEach(ellipse => {
        drawAnyEllipse(ellipse)
    })
}
// рисование эллипса
function drawingEllipse(e) {
    if (!isDrawing) {
        return
    }

    actual_ellipse_data = actual_ellipse_data.slice(0,4)

    const coords = getCanvasCoords(e);
    const x = coords.x;
    const y = coords.y;

    // параметры рисования
    ctx.strokeStyle = colorPicker.value
    ctx.lineWidth = sizeSlider.value
    // подсчет значений
    const x0 = actual_ellipse_data[2]
    const y0 = actual_ellipse_data[3]
    let radiusX = 0
    let radiusY = 0
    let middleX = 0
    let middleY = 0
    if (x > x0 && y > y0) { 
        radiusX = (x-x0)/2
        radiusY = (y-y0)/2
        middleX = x0+radiusX
        middleY = y0+radiusY
    } else if (x > x0 && y < y0) {
        radiusX = (x-x0)/2
        radiusY = (y0-y)/2
        middleX = x0+radiusX
        middleY = y+radiusY
    } else if (x < x0 && y < y0) {
        radiusX = (x0-x)/2
        radiusY = (y0-y)/2
        middleX = x+radiusX
        middleY = y+radiusY
    } else if (x < x0 && y > y0) { 
        radiusX = (x0-x)/2
        radiusY = (y-y0)/2
        middleX = x+radiusX
        middleY = y0+radiusY
    }
    // рисование эллипса
    ctx.beginPath()
    ctx.ellipse(middleX, middleY, radiusX, radiusY, 0, 0, Math.PI * 2);
    ctx.stroke()

    // заполнение массива эллипса
    actual_ellipse_data.push(middleX, middleY, radiusX, radiusY)
}
// рисуем любой эллипс
function drawAnyEllipse(ellipse) {
    // параметры рисования
    ctx.strokeStyle = ellipse[0]
    ctx.lineWidth = ellipse[1]
    // рисование эллипса
    ctx.beginPath()
    ctx.ellipse(ellipse[4], ellipse[5], ellipse[6], ellipse[7], 0, 0, Math.PI * 2);
    ctx.stroke()
}
// поиск точки на эллипсе
function findPointInEllipse(e) {
    let counter = 0 
    ellipses.forEach(ellipse => {
        const coords = getCanvasCoords(e);
        const x = coords.x;
        const y = coords.y;

        const h = ellipse[4]
        const k = ellipse[5]
        const a = ellipse[6]
        const b = ellipse[7]

        // погрешность в пикселях
        const accuracy = 5
        // условие >= 1
        const condition_1 = (x - h)**2 / (a - accuracy)**2 + (y - k)**2 / (b - accuracy)**2 >= 1
        // условие <= 1
        const condition_2 = (x - h)**2 / (a + accuracy)**2 + (y - k)**2 / (b + accuracy)**2 <= 1

        if (condition_1 && condition_2) {
            // параметры рисования
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = ellipse[1]
            // рисование эллипса
            ctx.beginPath()
            ctx.ellipse(ellipse[4], ellipse[5], ellipse[6], ellipse[7], 0, 0, Math.PI * 2);
            ctx.stroke()
            mouse_over_element = true
            ellipses_without_hovered_element = ellipses.slice(0, counter).concat(ellipses.slice(counter+1))

            element_to_add = []
        }
        counter++
    })
}
// завершение эллипса
function ellipseEnd(e) {
    ellipses.push((actual_ellipse_data))
}