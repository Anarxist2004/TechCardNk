let lines = []
let actual_line_data = [] // [цвет, толщина, x1, y1, x2, y2]

function drawLine(e) {
    const coords = getCanvasCoords(e);
    const startX = coords.x;
    const startY = coords.y;

    actual_line_data = []
    actual_line_data.push(colorPicker.value, sizeSlider.value)
    actual_line_data.push(startX, startY)

    ctx.moveTo(startX, startY)
}
// отрисовка всех предыдущих линий
function drawAllLines() {
    lines.forEach(line => {
        ctx.beginPath()
        ctx.moveTo(line[2], line[3])
        ctx.lineTo(line[4], line[5])
        ctx.strokeStyle = line[0]
        ctx.lineWidth = line[1]
        ctx.lineCap = 'round'
        ctx.stroke()
    })
}

function drawingLine(e) {
    if (!isDrawing) {
        return
    }

    const coords = getCanvasCoords(e);
    const x = coords.x;
    const y = coords.y;
    
    const startX = actual_line_data[2];
    const startY = actual_line_data[3];
    
    // Рисуем текущую линию
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(x, y);
    ctx.strokeStyle = colorPicker.value;
    ctx.lineWidth = sizeSlider.value;
    ctx.lineCap = 'round';
    ctx.stroke();
}

// поиск точки на линии
function findPointInLine(e) {
    counter = 0
    lines.forEach(line => {
        const coords = getCanvasCoords(e);
        const x = coords.x;
        const y = coords.y;

        k = ((line[3] - line[5]) / (line[2] - line[4]))
        b = line[3] - k * line[2]

        const left_to_right = line[2] < line[4] 
        if (left_to_right) {
            left_side = line[2]
            right_side = line[4]
        } else {
            left_side = line[4]
            right_side = line[2]
        }

        const bottom_to_top = line[3] < line[5] 
        if (bottom_to_top) {
            bottom_side = line[3]
            top_side = line[5]
        } else {
            bottom_side = line[5]
            top_side = line[3]
        }

        const horizontal_line_condotion = (y >= k * x + b - 7) && (y <= k * x + b + 7) && x >= left_side && x <= right_side
        const vertical_line_condition = (x >= (y-b)/k - 7) && (x <= (y-b)/k + 7) && y >= bottom_side && y <= top_side

        if (horizontal_line_condotion || vertical_line_condition) {
            ctx.beginPath()
            ctx.moveTo(line[2], line[3])
            ctx.lineTo(line[4], line[5])
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = line[1]
            ctx.lineCap = 'round'
            ctx.stroke()
            mouse_over_element = true
            lines_without_hovered_element = lines.slice(0, counter).concat(lines.slice(counter+1))

            element_to_add = []
        }
        counter++
    })
}
// завершение линии
function lineEnd(e) {
    const coords = getCanvasCoords(e);
    const endX = coords.x;
    const endY = coords.y;
    actual_line_data.push(endX, endY)
    lines.push((actual_line_data))
}