const viewer = document.querySelector('.viewer')
const canvas = document.getElementById('canvas')
const ctx = canvas.getContext('2d')
const fileInput = document.getElementById('fileInput')
const deleteBtn = document.querySelector('#deleteBtn')

let original_image
let isDrawing = false
let len_etalon = 0
let mmToPx_ratio = (25.4 / 800)
let brightness = 0
let contrast = 0

let delay = 1

lines_without_hovered_element = []
rects_without_hovered_element = []
rulers_without_hovered_element = []
lines_et_without_hovered_element = []
ellipses3_without_hovered_element = []
ellipses_without_hovered_element = []
measureRects_without_hovered_element = []
measureEllipses_without_hovered_element = []
measureEllipses3_without_hovered_element = []
comments_without_hovered_element = []
mouse_over_element = false

mouse_down = false
moving_shov_angle = false
moving_shov_vertical = false
moving_shov_width = false
mouse_x = 0
mouse_y = 0

canvas.width = 800
canvas.height = 500

function getCanvasCoords(e) {
    const rect = canvas.getBoundingClientRect();
    
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    const canvasX = mouseX / zoomLevel;
    const canvasY = mouseY / zoomLevel;
    
    return { x: canvasX, y: canvasY };
}

function loadImageToViewer(imageSrc, imageName = "") {
    if (!imageSrc) return

    const img = new Image()
    img.onload = function() {
        currentImage = img

        const container = document.querySelector(".canvas-container")
        const maxWidth = container?.clientWidth || viewer.clientWidth || img.width
        const maxHeight = container?.clientHeight || viewer.clientHeight || img.height

        let displayWidth = img.width
        let displayHeight = img.height

        if (displayWidth > maxWidth) {
            displayHeight = (maxWidth / displayWidth) * displayHeight
            displayWidth = maxWidth
        }
        if (displayHeight > maxHeight) {
            displayWidth = (maxHeight / displayHeight) * displayWidth
            displayHeight = maxHeight
        }

        canvas.width = img.width
        canvas.height = img.height

        if (canvas.width * canvas.height > 8000000) {
            delay = 300
        } else {
            delay = 1
        }

        ctx.clearRect(0, 0, canvas.width, canvas.height)
        ctx.drawImage(img, 0, 0)

        canvas.style.width = displayWidth + "px"
        canvas.style.height = displayHeight + "px"

        original_image = img

        zoomLevel = 1
        brightness = 0
        contrast = 0
        const brightnessSlider = document.getElementById("brightnessSlider")
        const contrastSlider = document.getElementById("contrastSlider")
        const brightnessValue = document.getElementById("brightnessValue")
        const contrastValue = document.getElementById("contrastValue")
        if (brightnessSlider) brightnessSlider.value = 0
        if (contrastSlider) contrastSlider.value = 0
        if (brightnessValue) brightnessValue.value = 0
        if (contrastValue) contrastValue.value = 0
        setCanvases(0, 0)

        const status = document.getElementById("status")
        if (status) {
            status.textContent = imageName
                ? `Загружено изображение: ${imageName}`
                : "Изображение загружено"
        }
    }
    img.onerror = function() {
        const status = document.getElementById("status")
        if (status) {
            status.textContent = "Не удалось загрузить выбранное изображение"
        }
    }
    img.src = imageSrc
}

window.loadImageToViewer = loadImageToViewer

fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0]
    if (!file) return
    
    const reader = new FileReader()
    reader.onload = function(event) {
        loadImageToViewer(event.target.result, file.name)
    }
    reader.readAsDataURL(file)
    e.target.value = ""
})

canvas.addEventListener("mousedown", (e) => {
    if (e.button === 2) { 
        defectWindow()
        return; 
    }
    deleteElement(e);

    startDrag(e);

    if (isDragging) {
        return
    }
    
    startDraw(e);

    mouse_down = true
    coords = getCanvasCoords(e)
    mouse_x = coords.x
    mouse_y = coords.y
});
continueDraw
canvas.addEventListener("mousemove", continueDraw)
canvas.addEventListener("mousemove", findPointInFigures)
canvas.addEventListener("mousemove", move_shov)
canvas.addEventListener("mousemove", move_shov_width)
canvas.addEventListener("mousemove", update_mouse_coords) 
canvas.addEventListener("mouseout", stopDraw)
canvas.addEventListener("mouseup", stopDraw)
canvas.addEventListener("mousemove", onDrag)
canvas.addEventListener("mouseup", endDrag)

function startDraw(e) {
    isDrawing = true
    let tool = window.currentTool
    if (tool == "line") {
        drawLine(e)
    } else if (tool == "rectangle") {
        drawRect(e)
    } else if (tool == "ellipse") {
        drawEllipse(e)
    } else if (tool == "line_etalon") {
        drawLineEt(e)
    } else if (tool == "ruler") {
        drawRuler(e)
    } else if (tool == "ellipse3") {
        drawEllipse3(e)
    } else if (tool == "measureRect") {
        drawMeasureRect(e)
    } else if (tool == "measureEllipse") {
        drawMeasureEllipse(e)
    } else if (tool == "measureEllipse3") {
        drawMeasureEllipse3(e)
    } else if (tool == "comment") {
        if (editComment(e)) return
        createComment(e)
    }
}

function deleteElement(e) {
    if (mouse_over_element == true) {
        if (deleteBtn.classList.contains("active")) {
            ctx.clearRect(0, 0, canvas.width, canvas.height)
            if (original_image) {
                ctx.drawImage(original_image, 0, 0)
            }  
            comments = comments_without_hovered_element
            lines = lines_without_hovered_element
            rects = rects_without_hovered_element
            ellipses = ellipses_without_hovered_element
            ellipses3 = ellipses3_without_hovered_element
            measureRects = measureRects_without_hovered_element
            rulers = rulers_without_hovered_element
            lines_et = lines_et_without_hovered_element
            measureEllipses = measureEllipses_without_hovered_element
            measureEllipses3 = measureEllipses3_without_hovered_element
            drawAllShovLines()
            drawAllLines()
            drawAllRects()
            drawAllEllipses()
            drawAllEllipses3()
            drawAllLinesEt()
            drawAllMeasureEllipses()
            drawAllMeasureEllipses3()
            drawAllMeasureRects()
            drawAllRulers()
            drawAllComments()
            setTimeout(() => {
                console.log("TIMEOUT")
                drawAllLines()
                drawAllRects()
                drawAllEllipses()
                drawAllEllipses3()
                drawAllLinesEt()
                drawAllMeasureEllipses()
                drawAllMeasureEllipses3()
                drawAllMeasureRects()
                drawAllRulers()
                drawAllComments()
            }, 100)
            delete_defect_annotation(element_to_add[2])
            console.log(element_to_add)
            redraw_defects()
        }
    }
}

let lock_updating_canvas = false
setInterval(() => {
    lock_updating_canvas = false
}, delay)
function continueDraw(e) {
    mouse_over_element = false
    lines_without_hovered_element = lines
    rects_without_hovered_element = rects
    ellipses_without_hovered_element = ellipses
    ellipses3_without_hovered_element = ellipses3
    measureRects_without_hovered_element = measureRects
    measureEllipses_without_hovered_element = measureEllipses
    measureEllipses3_without_hovered_element = measureEllipses3
    rulers_without_hovered_element = rulers
    lines_et_without_hovered_element = lines_et
    comments_without_hovered_element = comments

    function updating_canvas(do_it_right_now = false) {
        if (lock_updating_canvas && !do_it_right_now) return
        lock_updating_canvas = true

        ctx.clearRect(0, 0, canvas.width, canvas.height)

        ctx.filter = `brightness(${100 + brightness}%) contrast(${100 + contrast}%)`

        if (original_image) {
            ctx.drawImage(original_image, 0, 0)
        }

        ctx.filter = "none"

        drawAllShovLines()
        drawAllLines()
        drawAllLinesEt()
        drawAllRulers()
        drawAllMeasureEllipses()
        drawAllRects()
        drawAllEllipses()
        drawAllEllipses3()
        drawAllMeasureEllipses3()
        drawAllMeasureRects()
        drawAllComments()
    }

    updating_canvas()
    
    let tool = window.currentTool
    if (tool == "line") {
        updating_canvas(true)
        drawingLine(e)
    } else if (tool == "rectangle") {
        updating_canvas(true)
        drawingRect(e)
    } else if (tool == "ellipse") {
        updating_canvas(true)
        drawingEllipse(e)
    } else if (tool == "line_etalon") {
        updating_canvas(true)
        drawingLineEt(e)
    } else if (tool == "ruler") {
        updating_canvas(true)
        drawingRuler(e)
    } else if (tool == "measureRect") {
        updating_canvas(true)
        drawingMeasureRect(e)
    } else if (tool == "measureEllipse") {
        updating_canvas(true)
        drawingMeasureEllipse(e)
    } 
}

function findPointInFigures(e) {
    if (isDragging) return

    findPointInLine(e)
    findPointInRect(e)
    findPointInEllipse(e)
    findPointInEllipse3(e)
    findPointInRuler(e)
    findPointInLineEt(e)
    findPointInMeasureRect(e)
    findPointInMeasureEllipse(e)
    findPointInMeasureEllipse3(e)
    findPointInShovMiddle(e)
    findPointInShovBottom(e)
    findPointInComments(e)
}

function move_shov(e) {
    side_of_shov = findPointInShovMiddle(e)
    const coords = getCanvasCoords(e)
    const x = coords.x;
    const y = coords.y;
    if (((mouse_down && side_of_shov == 1) || moving_shov_angle) && !moving_shov_width) { 
        moving_shov_angle = true 
        if (y < mouse_y) { 
            shov_lines[0][3] += mouse_y - y
            shov_lines[0][5] -= mouse_y - y

            shov_lines[1][3] += mouse_y - y
            shov_lines[1][5] -= mouse_y - y

            shov_lines[2][3] += mouse_y - y
            shov_lines[2][5] -= mouse_y - y
        } else if (y > mouse_y) { // значит тянем мышью вниз
            shov_lines[0][3] -= y - mouse_y
            shov_lines[0][5] += y - mouse_y

            shov_lines[1][3] -= y - mouse_y
            shov_lines[1][5] += y - mouse_y

            shov_lines[2][3] -= y - mouse_y
            shov_lines[2][5] += y - mouse_y
        }
    } else if (((mouse_down && side_of_shov == 2) || moving_shov_vertical) && !moving_shov_width) { 
        moving_shov_vertical = true 
        if (y < mouse_y) {
            shov_lines[0][3] -= mouse_y - y
            shov_lines[0][5] -= mouse_y - y

            shov_lines[1][3] -= mouse_y - y
            shov_lines[1][5] -= mouse_y - y

            shov_lines[2][3] -= mouse_y - y
            shov_lines[2][5] -= mouse_y - y
        } else if (y > mouse_y) {
            shov_lines[0][3] += y - mouse_y
            shov_lines[0][5] += y - mouse_y

            shov_lines[1][3] += y - mouse_y
            shov_lines[1][5] += y - mouse_y

            shov_lines[2][3] += y - mouse_y
            shov_lines[2][5] += y - mouse_y
        }
    }
}

function move_shov_width(e) {
    mouse_over_bottom = findPointInShovBottom(e)
    const coords = getCanvasCoords(e)
    const x = coords.x
    const y = coords.y
    if (((mouse_down == true && mouse_over_bottom == 1) || moving_shov_width) && !moving_shov_vertical && !moving_shov_angle) {
        moving_shov_width = true
        if (y < mouse_y) {
            shov_lines[1][3] += mouse_y - y
            shov_lines[1][5] += mouse_y - y

            shov_lines[2][3] -= mouse_y - y
            shov_lines[2][5] -= mouse_y - y
        } else if (y > mouse_y) { 
            shov_lines[1][3] -= y - mouse_y
            shov_lines[1][5] -= y - mouse_y

            shov_lines[2][3] += y - mouse_y
            shov_lines[2][5] += y - mouse_y
        }
    }
}

function update_mouse_coords(e) {
    const coords = getCanvasCoords(e)
    const x = coords.x
    const y = coords.y
    mouse_x = x
    mouse_y = y
}

function stopDraw(e) {
    if (isDrawing) {
        let tool = window.currentTool

        if (tool == "line") {
            lineEnd(e)
        } else if (tool == "rectangle") {
            rectEnd(e)
        } else if (tool == "ellipse") {
            ellipseEnd(e)
        } else if (tool == "line_etalon") {
            lineEtEnd(e)
        } else if (tool == "ruler") {
            rulerEnd(e)
        } else if (tool == "measureRect") {
            measureRectEnd(e)
        } else if (tool == "measureEllipse") {
            measureEllipseEnd(e)
        } 
    }

    isDrawing = false
    mouse_down = false
    moving_shov_angle = false
    moving_shov_vertical = false
    moving_shov_width = false
}

