let rects = []
let actual_rect_data = [] // [цвет, толщина, координаты прямоугольника...]

// старт отрисовки прямоугольника
function drawRect(e) {

    const coords = getCanvasCoords(e);

    actual_rect_data = []
    actual_rect_data.push(colorPicker.value, sizeSlider.value)
    actual_rect_data.push(coords.x, coords.y)

    ctx.moveTo(coords.x, coords.y)
}
// отрисовка всех предыдущих прямоугольников
function drawAllRects() {
    rects.forEach(rect => {
        drawAnyRect(rect)
    })
}
// рисование прямоугольника
function drawingRect(e) {
    if (!isDrawing) {
        return
    }

    actual_rect_data = actual_rect_data.slice(0,4)

    const coords = getCanvasCoords(e);
    const x3 = coords.x;
    const y3 = coords.y;

    const x0 = actual_rect_data[2]
    const y0 = actual_rect_data[3]

    ctx.strokeStyle = actual_rect_data[0]
    ctx.lineWidth = actual_rect_data[1]
    ctx.lineCap = 'round'
    // начало
    ctx.beginPath()
    ctx.moveTo(x0, y0)
    // 1 линия
    ctx.lineTo(x3, y0)
    // 2 линия
    ctx.lineTo(x3, y3)
    // 3 линия
    ctx.lineTo(x0, y3)
    // 4 линия
    ctx.lineTo(x0, y0)
    ctx.closePath()
    ctx.stroke()
    
    // заполнение массива прямоугольнкиа
    actual_rect_data.push(x3, y0, x3, y3, x0, y3, x0, y0)
}
// рисуем прямоугольник по точкам
function drawAnyRect(rect) {
    // параметры рисования
    ctx.strokeStyle = rect[0]
    ctx.lineWidth = rect[1]
    ctx.lineCap = 'round'
    // начало
    ctx.beginPath()
    ctx.moveTo(rect[2], rect[3])
    // 1 линия
    ctx.lineTo(rect[4], rect[5])
    // 2 линия
    ctx.lineTo(rect[6], rect[7])
    // 3 линия
    ctx.lineTo(rect[8], rect[9])
    // 4 линия
    ctx.lineTo(rect[2], rect[3])
    ctx.closePath()
    ctx.stroke()
}
// поиск точки на прямоугольнике
function findPointInRect(e) {
    let counter = 0 
    rects.forEach(rect => {
        const coords = getCanvasCoords(e);
        const x = coords.x;
        const y = coords.y;

        const x0 = rect[2]
        const y0 = rect[3]
        const x3 = rect[6]
        const y3 = rect[7]

        if (x0 < x3 && y0 > y3) {
            // сектор 1
            if ((x >= x0 && x <= x3 && y >= y3 - 7 && y <= y3 + 7) || (x >= x0 && x <= x3 && y >= y0 - 7 && y <= y0 + 7) 
                || (y <= y0 && y >= y3 && x >= x0 - 7 && x <= x0 + 7) || (y <= y0 && y >= y3 && x >= x3 - 7 && x <= x3 + 7))  {
                drawThisRect()
            }
        } else if (x0 > x3 && y0 > y3) {
            // сектор 2
            if ((x >= x3 && x <= x0 && y >= y3 - 7 && y <= y3 + 7) || (x >= x3 && x <= x0 && y >= y0 - 7 && y <= y0 + 7) 
                || (y <= y0 && y >= y3 && x >= x3 - 7 && x <= x3 + 7) || (y <= y0 && y >= y3 && x >= x0 - 7 && x <= x0 + 7))  {
                drawThisRect()
            }
        } else if (x0 > x3 && y0 < y3) {
            // сектор 3
            if ((x >= x3 && x <= x0 && y >= y3 - 7 && y <= y3 + 7) || (x >= x3 && x <= x0 && y >= y0 - 7 && y <= y0 + 7) 
                || (y >= y0 && y <= y3 && x >= x3 - 7 && x <= x3 + 7) || (y >= y0 && y <= y3 && x >= x0 - 7 && x <= x0 + 7))  {
                drawThisRect()
            } 
        } else if (x0 < x3 && y0 < y3) {
            // сектор 4
            if ((x <= x3 && x >= x0 && y >= y3 - 7 && y <= y3 + 7) || (x <= x3 && x >= x0 && y >= y0 - 7 && y <= y0 + 7) 
                || (y >= y0 && y <= y3 && x >= x3 - 7 && x <= x3 + 7) || (y >= y0 && y <= y3 && x >= x0 - 7 && x <= x0 + 7))  {
                drawThisRect()
            }
        }

        function drawThisRect() {
            // параметры рисования
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = rect[1]
            ctx.lineCap = 'round'
            // начало
            ctx.beginPath()
            ctx.moveTo(rect[2], rect[3])
            // 1 линия
            ctx.lineTo(rect[4], rect[5])
            // 2 линия
            ctx.lineTo(rect[6], rect[7])
            // 3 линия
            ctx.lineTo(rect[8], rect[9])
            // 4 линия
            ctx.lineTo(rect[2], rect[3])
            ctx.closePath()
            ctx.stroke()

            // сказали, что мышь на элементе
            mouse_over_element = true
            // передаем массив без этой линии
            rects_without_hovered_element = rects.slice(0, counter).concat(rects.slice(counter+1))

            element_to_add = []
        }   
        counter++
    })
}
// завершение прямоугольника
function rectEnd(e) {
    rects.push((actual_rect_data))
}