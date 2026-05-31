let shov_lines = [] // цвет, толщина, x1, y1, x2, y2

// отрисовка всех линий шва
function drawAllShovLines() {
    shov_lines.forEach(line => {
        ctx.beginPath()
        ctx.moveTo(line[2], line[3])
        ctx.lineTo(line[4], line[5])
        ctx.strokeStyle = line[0]
        ctx.lineWidth = line[1]
        ctx.lineCap = 'round'
        ctx.stroke()
    })
}

// поиск точки на линии шва
function findPointInShovMiddle(e) {
    if (shov_lines.length == 0) {
        return 0
    }
    line_middle = shov_lines[0]
    const coords = getCanvasCoords(e);
    const x = coords.x;
    const y = coords.y;

    k = ((line_middle[3] - line_middle[5]) / (line_middle[2] - line_middle[4]))
    b = line_middle[3] - k * line_middle[2]

    const left_to_right = line_middle[2] < line_middle[4] 
    if (left_to_right) {
        left_side = line_middle[2]
        right_side = line_middle[4]
    } else {
        left_side = line_middle[4]
        right_side = line_middle[2]
    }

    const bottom_to_top = line_middle[3] < line_middle[5] 
    if (bottom_to_top) {
        bottom_side = line_middle[3]
        top_side = line_middle[5]
    } else {
        bottom_side = line_middle[5]
        top_side = line_middle[3]
    }

    const horizontal_line_condotion = (y >= k * x + b - 7) && (y <= k * x + b + 7) && x >= left_side && x <= right_side
    const vertical_line_condition = (x >= (y-b)/k - 7) && (x <= (y-b)/k + 7) && y >= bottom_side && y <= top_side

    if (x > line_middle[4] / 2) {
        if (horizontal_line_condotion || vertical_line_condition) {
            // оп - нашли, подсветили
            ctx.beginPath()
            ctx.moveTo(Math.floor(line_middle[4]/2), (Math.abs(line_middle[5]-line_middle[3])/2)+Math.min(line_middle[5], line_middle[3]))
            ctx.lineTo(line_middle[4], line_middle[5]) 
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = line_middle[1]
            ctx.lineCap = 'round'
            ctx.stroke()
            // сказали, что мышь на элементе
            mouse_over_element = true
            // возвращаем значение, что трогали правую часть
            element_to_add = []
            return 1
        }
    } else if (x < line_middle[4] / 2) {
        if (horizontal_line_condotion || vertical_line_condition) {
            // оп - нашли, подсветили
            ctx.beginPath()
            ctx.moveTo(0, line_middle[3])
            ctx.lineTo(Math.floor(line_middle[4]/2), (Math.abs(line_middle[5]-line_middle[3])/2)+Math.min(line_middle[5], line_middle[3])) 
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = line_middle[1]
            ctx.lineCap = 'round'
            ctx.stroke()
            // сказали, что мышь на элементе
            mouse_over_element = true
            // возвращаем значение, что трогали левую часть
            element_to_add = []
            return 2
        }
    }
}

// поиск точки на линии
function findPointInShovBottom(e) {
    if (shov_lines.length == 0) {
        return 0
    }
    line_bottom = shov_lines[2]
    const coords = getCanvasCoords(e);
    const x = coords.x;
    const y = coords.y;

    k = ((line_bottom[3] - line_bottom[5]) / (line_bottom[2] - line_bottom[4]))
    b = line_bottom[3] - k * line_bottom[2]

    const left_to_right = line_bottom[2] < line_bottom[4] 
    if (left_to_right) {
        left_side = line_bottom[2]
        right_side = line_bottom[4]
    } else {
        left_side = line_bottom[4]
        right_side = line_bottom[2]
    }

    const bottom_to_top = line_bottom[3] < line_bottom[5] 
    if (bottom_to_top) {
        bottom_side = line_bottom[3]
        top_side = line_bottom[5]
    } else {
        bottom_side = line_bottom[5]
        top_side = line_bottom[3]
    }

    const horizontal_line_condotion = (y >= k * x + b - 7) && (y <= k * x + b + 7) && x >= left_side && x <= right_side
    const vertical_line_condition = (x >= (y-b)/k - 7) && (x <= (y-b)/k + 7) && y >= bottom_side && y <= top_side

    if (horizontal_line_condotion || vertical_line_condition) {
        // оп - нашли, подсветили
        ctx.beginPath()
        ctx.moveTo(line_bottom[2], line_bottom[3])
        ctx.lineTo(line_bottom[4], line_bottom[5]) 
        ctx.strokeStyle = "#fafafa"
        ctx.lineWidth = line_bottom[1]
        ctx.lineCap = 'round'
        ctx.stroke()
        // сказали, что мышь на элементе
        mouse_over_element = true
        return 1
    }
}