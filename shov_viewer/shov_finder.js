const find_shov = document.querySelector(".find_shov")
find_shov.addEventListener("click", () => {
    save_img_to_server()
})

function save_img_to_server() {
    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('file', blob, 'shov.png');
        fetch('/find_shov', {
            method: 'POST',
            body: formData
        })
        .then(async response => {
            const text = await response.text();
            if (!response.ok) {
                throw new Error(text);
            }
            return JSON.parse(text);
        })
        .then(data => {
            if (data.status === 'success' && data.coordinates) {
                const [y1_middle, y2_middle, y1_top, y2_top, y1_bottom, y2_bottom, width, height] = data.coordinates;
                
                // удаляем старые линии шва, если есть
                shov_lines = []
                // Добавляем три новые линии
                shov_lines.push(['#00008f', 2, 0, y1_middle, width, y2_middle]);
                shov_lines.push(['#00008f', 2, 0, y1_top, width, y2_top]);
                shov_lines.push(['#00008f', 2, 0, y1_bottom, width, y2_bottom]);
                // рисуем шов
                drawAllShovLines()
            }
        })
        .catch(error => console.error('Ошибка:', error));
    }, 'image/png');
}

const delete_shov = document.querySelector(".delete_shov")
delete_shov.addEventListener("click", () => {
    func_delete_shov()
})

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
