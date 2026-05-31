let lines_et = []
let actual_line_et_data = [] // [цвет, толщина, x1, y1, x2, y2]

// старт отрисовки линии
function drawLineEt(e) {
    const coords = getCanvasCoords(e);
    startX = coords.x;
    startY = coords.y;

    actual_line_et_data = []
    actual_line_et_data.push("purple", 3)
    actual_line_et_data.push(startX, startY)

    ctx.moveTo(startX, startY)
}

function drawAllLinesEt() {
    lines_et.forEach(line => {
        ctx.beginPath()
        ctx.moveTo(line[2], line[3])
        ctx.lineTo(line[4], line[5])
        ctx.strokeStyle = line[0]
        ctx.lineWidth = line[1]
        ctx.lineCap = 'round'
        ctx.stroke()
    })
}
// рисование линии
function drawingLineEt(e) {
    if (!isDrawing) {
        return
    }

    lines_et = []

    const coords = getCanvasCoords(e);
    const x = coords.x;
    const y = coords.y;
    
    const startX = actual_line_et_data[2];
    const startY = actual_line_et_data[3];

    // парамемтры рисования
    ctx.strokeStyle = "purple"
    ctx.lineWidth = 3
    ctx.lineCap = 'round'
    // рисование линии
    ctx.beginPath()
    ctx.moveTo(startX, startY)
    ctx.lineTo(x, y)
    ctx.stroke()
}

function findPointInLineEt(e){

    const coords = getCanvasCoords(e)
    const x = coords.x
    const y = coords.y

    let counter = 0

    lines_et.forEach(line=>{

        const x1 = line[2]
        const y1 = line[3]
        const x2 = line[4]
        const y2 = line[5]

        const dx = x2 - x1
        const dy = y2 - y1

        const length2 = dx*dx + dy*dy

        let t = ((x-x1)*dx + (y-y1)*dy) / length2
        t = Math.max(0, Math.min(1, t))

        const projX = x1 + t*dx
        const projY = y1 + t*dy

        const distX = x - projX
        const distY = y - projY

        const dist = Math.sqrt(distX*distX + distY*distY)

        if(dist < 6){

            ctx.beginPath()
            ctx.moveTo(x1,y1)
            ctx.lineTo(x2,y2)
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = line[1]
            ctx.stroke()

            mouse_over_element = true

            lines_et_without_hovered_element =
                lines_et.slice(0,counter)
                .concat(lines_et.slice(counter+1))

            element_to_add = []
        }

        counter++

    })
}
// завершение линии
function lineEtEnd(e) {
    const coords = getCanvasCoords(e);
    const endX = coords.x;
    const endY = coords.y;
    actual_line_et_data.push(endX, endY)
    lines_et.push((actual_line_et_data))

    const dx = endX - startX;
    const dy = endY - startY;
    const length = Math.sqrt(dx * dx + dy * dy);
    len_etalon = length
    mmToPx(length)
}
// подсчет миллиметров в пикселях
function mmToPx(length) {
    const selectElement = document.getElementById('etalonValue');
    let line_mm = 0
    if (selectElement.value == 1) {
        line_mm = 30
    } else if (selectElement.value == 2) {
        line_mm = 45
    } else if (selectElement.value == 3) {
        line_mm = 60
    }
    mmToPx_ratio = line_mm / length
}