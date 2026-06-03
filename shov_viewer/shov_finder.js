const find_shov = document.querySelector(".find_shov")
const delete_shov = document.querySelector(".delete_shov")

const MAX_SHOV_UPLOAD_SIDE = 1800
const MAX_SHOV_UPLOAD_PIXELS = 2500000

find_shov.addEventListener("click", () => {
    void save_img_to_server()
})

delete_shov.addEventListener("click", () => {
    func_delete_shov()
})

function getShovUploadCanvas() {
    const maxSideScale = MAX_SHOV_UPLOAD_SIDE / Math.max(canvas.width, canvas.height)
    const pixelScale = Math.sqrt(MAX_SHOV_UPLOAD_PIXELS / (canvas.width * canvas.height))
    const scale = Math.min(1, maxSideScale, pixelScale)

    if (scale >= 1) {
        return canvas
    }

    const uploadCanvas = document.createElement("canvas")
    uploadCanvas.width = Math.max(2, Math.round(canvas.width * scale))
    uploadCanvas.height = Math.max(2, Math.round(canvas.height * scale))

    const uploadCtx = uploadCanvas.getContext("2d")
    uploadCtx.drawImage(canvas, 0, 0, uploadCanvas.width, uploadCanvas.height)

    return uploadCanvas
}

function canvasToPngBlob(targetCanvas) {
    return new Promise((resolve, reject) => {
        targetCanvas.toBlob((blob) => {
            if (!blob) {
                reject(new Error("Не удалось подготовить изображение для построения шва"))
                return
            }
            resolve(blob)
        }, "image/png")
    })
}

function setShovStatus(text) {
    const status = document.getElementById("status")
    if (status) {
        status.textContent = text
    }
}

function drawShovFromCoordinates(coords) {
    const [y1_middle, y2_middle, y1_top, y2_top, y1_bottom, y2_bottom, width, height] = coords
    const scaleY = height ? canvas.height / height : 1

    shov_lines = []
    shov_lines.push(["#00008f", 2, 0, y1_middle * scaleY, canvas.width, y2_middle * scaleY])
    shov_lines.push(["#00008f", 2, 0, y1_top * scaleY, canvas.width, y2_top * scaleY])
    shov_lines.push(["#00008f", 2, 0, y1_bottom * scaleY, canvas.width, y2_bottom * scaleY])

    if (typeof redraw === "function") {
        redraw()
    } else {
        drawAllShovLines()
    }
}

async function save_img_to_server() {
    try {
        if (!original_image) {
            throw new Error("Сначала загрузите изображение")
        }

        setShovStatus("Построение шва...")

        const uploadCanvas = getShovUploadCanvas()
        const blob = await canvasToPngBlob(uploadCanvas)
        const formData = new FormData()
        formData.append("file", blob, "shov.png")

        const response = await fetch("/find_shov", {
            method: "POST",
            body: formData,
            credentials: "same-origin",
        })
        const text = await response.text()
        let data = {}
        try {
            data = JSON.parse(text || "{}")
        } catch (error) {
            data = {}
        }

        if (!response.ok) {
            throw new Error(data.detail || text || "Не удалось построить шов")
        }

        if (data.status !== "success" || !Array.isArray(data.coordinates)) {
            throw new Error("Сервер вернул неверный формат координат шва")
        }

        drawShovFromCoordinates(data.coordinates)
        setShovStatus("Шов построен")
    } catch (error) {
        console.error("Ошибка построения шва:", error)
        setShovStatus(error.message || "Не удалось построить шов")
        alert(error.message || "Не удалось построить шов")
    }
}

function func_delete_shov() {
    shov_lines = []
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    if (original_image) {
        ctx.drawImage(original_image, 0, 0)
    }

    drawAllLines()
    drawAllLinesEt()
    drawAllRulers()
    drawAllMeasureEllipses()
    drawAllRects()
    drawAllEllipses()
    drawAllEllipses3()
    drawAllMeasureEllipses3()
    drawAllMeasureRects()
    drawAllShovLines()
}
