// для добавления дефекта в аннотацию
measure_id = 0
defects = [] // ["ellipse3", [длина, ширина], measure_id, "пора"], []...
element_to_add = [] // тут временно храним то, что подсветили и добавляем

// дефекты, которые пишутся в таблицу (уже аббревиатуры)
arr_defects_add = []

fixed_element_data = [] // сюда мы фиксируем данные о том элементе, который был выбран, когда мы нажали ПКМ

// для сохранения аннтоации в json
const saveBtn = document.querySelector("#saveBtn")
const popup_save = document.querySelector(".popup_save")
saveBtn.addEventListener("click", () => {
    createTableDefects()
    popup_save.classList.add("show_save_popup")
})

// Функция для создания JS файла с массивами
async function createJSFileWithArrays() {
    // Данные для заполнения массивов
    comment = document.querySelector("#globalAnnotation").value
    const data = {
        ellipses: ellipses,
        ellipses3: ellipses3,
        lines_et: lines_et,
        lines: lines,
        measureEllipses: measureEllipses,
        measureEllipses3: measureEllipses3,
        measureRects: measureRects,
        rects: rects,
        rulers: rulers,
        shov_lines: shov_lines,
        defects: defects,
        comment: comment
    };

    try {
        const response = await fetch('/save_annotation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        console.log('Сохранено:', result);
        return result;
        
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// работа с кнопкой загрузки файла JSON
const loadBtn = document.querySelector("#loadBtn")
const annotationJSONInput = document.querySelector('#annotationJSONInput')
loadBtn.addEventListener("click", () => {
    annotationJSONInput.click()
})

// обработка уже загруженного файла
annotationJSONInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    
    if (!file) return;

    const reader = new FileReader();

    reader.onload = function(e) {
        const text = e.target.result;
        loadAnnotationFromLSON(text); // передача содержимого
    };

    annotationJSONInput.value = "";

    reader.readAsText(file); 
});

// функция для работы с контентом загруженного json
function loadAnnotationFromLSON(text) {
    try {
        const data = JSON.parse(text); // парсим JSON

        // загрузили все эллипсы
        (data["ellipses"]).forEach(element => {
            ellipses.push(element)
        });
        // загрузили все эллипсы3
        (data["ellipses3"]).forEach(element => {
            ellipses3.push(element)
        });
        // загрузили эталонную линию
        (data["lines_et"]).forEach(element => {
            lines_et.push(element)
        });
        // загрузили все линии
        (data["lines"]).forEach(element => {
            lines.push(element)
        });
        // загрузили все измерительные эллипсы
        (data["measureEllipses"]).forEach(element => {
            measureEllipses.push(element)
        });
        // загрузили все измерительные эллипсы 3
        (data["measureEllipses3"]).forEach(element => {
            measureEllipses3.push(element)
        });
        // загрузили все измерительные прямоугольники
        (data["measureRects"]).forEach(element => {
            measureRects.push(element)
        });
        // загрузили все прямоугольники
        (data["rects"]).forEach(element => {
            rects.push(element)
        });
        // загрузили все линейки
        (data["rulers"]).forEach(element => {
            rulers.push(element)
        });
        // загрузили шов
        (data["shov_lines"]).forEach(element => {
            shov_lines.push(element)
        });
        // загрузили дефекты
        (data["defects"]).forEach(defect => {
            defects.push(defect)
        });
        // загрузили комментарий
        document.querySelector("#globalAnnotation").value = data["comment"]

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
        redraw_defects()
        

    } catch (error) {
        console.error("Ошибка парсинга JSON:", error);
    }
}

// функция для работы с добавлением дефектов в аннотацию
function defectWindow() {
    if (mouse_over_element && element_to_add.length > 1) {
        fixed_element_data = element_to_add
        const popup_add = document.querySelector(".popup_add_defect")
        const popup_delete = document.querySelector(".popup_delete_defect")
        if (search_defect_by_id(fixed_element_data[2]) == -1) {
            // этот дефект еще не был доавблен
            popup_add.classList.add("show")
        } else {
            // эффект уже был добавлен, редактируем его или удаляем
            popup_delete.classList.add("show")
        }
        
        isPanning = false;
        canvas.style.cursor = 'crosshair';
    }
}

// функционал кнопок с попапа 1
function popup_btns() {
    const popup = document.querySelector(".popup_add_defect")

    const cancel = document.querySelector(".btn_cancel")
    cancel.addEventListener("click", () => {
        popup.classList.remove("show")
        return
    })
    
    const ok = document.querySelector(".btn_ok")
    ok.addEventListener("click", () => {
        const selector_defect = document.querySelector("#defect_selector")
        fixed_element_data.push(selector_defect.value)
        popup.classList.remove("show")
        defects.push(fixed_element_data)
        redraw_defects()
    })
}
popup_btns()

// функционал кнопок с попапа 2
function popup_delete_btns() {
    const popup = document.querySelector(".popup_delete_defect")

    const cancel = document.querySelector(".btn_cancel2")
    cancel.addEventListener("click", () => {
        popup.classList.remove("show")
        return
    })
    
    const ok = document.querySelector(".btn_ok2")
    ok.addEventListener("click", () => {
        const selector_defect = document.querySelector("#defect_selector2")
        // заменяем название дефекта в плашке
        console.log(fixed_element_data, selector_defect)
        defects.forEach(element => {
            if (element[2] == fixed_element_data[2]) {
                element[3] = selector_defect.value
            }
        });
        popup.classList.remove("show")
        redraw_defects()
    })

    const delete_btn = document.querySelector(".btn_delete2")
    delete_btn.addEventListener("click", () => {
        defects = defects.filter(element => element[2] != fixed_element_data[2])
        popup.classList.remove("show")
        redraw_defects()
    })
}
popup_delete_btns()

// функция для отрисовки дефектов в аннотации
function redraw_defects() {
    const defects_div = document.querySelector(".defects")
    defects_div.innerHTML = ""

    const grouped = {}

    defects.forEach(defect => {
        const defectName = defect[3]

        if (!grouped[defectName]) {
            grouped[defectName] = []
        }

        grouped[defectName].push(defect)
    })

    let new_inner = ""

    Object.keys(grouped).forEach(defectName => {
        const group = grouped[defectName]

        if (group.length === 1) {
            const defect = group[0]
            const sizeText = getDefectSizeText(defect)

            new_inner += `
                <div class="defect defect-single"
                    data-defect-id="${defect[2]}"
                    data-figure="${defect[0]}">
                    <p>${defectName}</p>
                    <p>${sizeText}</p>
                </div>
            `
        } else {
            new_inner += `
                <details class="defect-group">
                    <summary class="defect-group-header">
                        <span>${defectName}</span>
                        <span>${group.length} шт.</span>
                    </summary>

                    <div class="defect-group-content">
            `

            group.forEach((defect, index) => {
                const sizeText = getDefectSizeText(defect)

                new_inner += `
                    <div class="defect defect-child"
                        data-defect-id="${defect[2]}"
                        data-figure="${defect[0]}">
                        <p>${index + 1}. ${defectName}</p>
                        <p>${sizeText}</p>
                    </div>
                `
            })

            new_inner += `
                    </div>
                </details>
            `
        }
    })

    defects_div.innerHTML = new_inner

    const defectCards = document.querySelectorAll(".defect")

    defectCards.forEach(card => {
        card.addEventListener("mouseenter", () => {
            flash_measure(card)
        })

        card.addEventListener("mouseleave", () => {
            redraw()
        })

        card.addEventListener("contextmenu", (e) => {
            e.preventDefault()

            const defectId = card.dataset.defectId
            const defect = defects.find(d => String(d[2]) === String(defectId))

            if (!defect) return

            fixed_element_data = [defect[0], defect[1], defect[2]]

            const popup_delete = document.querySelector(".popup_delete_defect")
            popup_delete.classList.add("show")
        })
    })
}

function getDefectSizeText(defect) {
    const width = Number(defect[1][0])
    const height = Number(defect[1][1])

    const maxSize = Math.max(width, height).toFixed(2)
    const minSize = Math.min(width, height).toFixed(2)

    return `${maxSize} × ${minSize} мм`
}

// id дефекта по measure_id
function search_defect_by_id(m_id) {
    for (i = 0; i < defects.length; i++) {
        if (defects[i][2] == m_id) {
            return i
        }
    }
    return -1
}

// надо подсветить тот дефект, который связан с плашкой при наведении курсора на плашку
function flash_measure(defect_annotation) {
    const defectId = defect_annotation.dataset.defectId
    const figureType = defect_annotation.dataset.figure

    if (figureType == "ellipse3") {
        measureEllipses3.forEach(el => {
            if (String(el[8]) !== String(defectId)) return

            const xA = el[2], yA = el[3]
            const xB = el[4], yB = el[5]
            const xC = el[6], yC = el[7]

            const cx = (xA + xB) / 2
            const cy = (yA + yB) / 2

            const dx = xB - xA
            const dy = yB - yA
            const a = Math.sqrt(dx * dx + dy * dy) / 2
            const angle = Math.atan2(dy, dx)

            const cxC = xC - cx
            const cyC = yC - cy
            const b = Math.sqrt(cxC * cxC + cyC * cyC)

            ctx.beginPath()
            ctx.ellipse(cx, cy, a, b, angle, 0, 2 * Math.PI)
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = el[1] + 2
            ctx.stroke()
        })
    }

    else if (figureType == "rect") {
        measureRects.forEach(rect => {
            if (String(rect[6]) !== String(defectId)) return

            const x1 = rect[2]
            const y1 = rect[3]
            const x2 = rect[4]
            const y2 = rect[5]

            const left = Math.min(x1, x2)
            const right = Math.max(x1, x2)
            const top = Math.min(y1, y2)
            const bottom = Math.max(y1, y2)

            ctx.beginPath()
            ctx.rect(left, top, right - left, bottom - top)
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = rect[1] + 2
            ctx.stroke()
        })
    }

    else if (figureType == "ellipse") {
        measureEllipses.forEach(el => {
            if (String(el[6]) !== String(defectId)) return

            const x1 = el[2]
            const y1 = el[3]
            const x2 = el[4]
            const y2 = el[5]

            const rx = Math.abs(x2 - x1) / 2
            const ry = Math.abs(y2 - y1) / 2
            const cx = (x1 + x2) / 2
            const cy = (y1 + y2) / 2

            ctx.beginPath()
            ctx.ellipse(cx, cy, rx, ry, 0, 0, 2 * Math.PI)
            ctx.strokeStyle = "#fafafa"
            ctx.lineWidth = el[1] + 2
            ctx.stroke()
        })
    }
}

// удалить дефект по айдишнику
function delete_defect_annotation(m_id) {
    for (i = 0; i < defects.length; i++) {
        if (defects[i][2] == m_id) {
            defects = defects.filter(element => element[2] != m_id)
        }
    }
}

// перерисовать без подсвечивания
function redraw() {
    // отрисовываем все время
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    //применяем фильтр ТОЛЬКО к изображению
    ctx.filter = `brightness(${100 + brightness}%) contrast(${100 + contrast}%)`

    if (original_image) {
        ctx.drawImage(original_image, 0, 0)
    }

    //сбрасываем фильтр, чтобы фигуры не искажались
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
}



// ФОРМА СОХРАНЕНИЯ АННОТАЦИИ И ПРОТОКОЛА
const inputs = document.querySelectorAll(".popup_save_input")

inputs.forEach(input => {
    input.style.width = Math.max(input.value.length, input.placeholder.length) + 'ch';
    input.addEventListener('input', () => {
        input.style.width = Math.max(input.value.length, input.placeholder.length) + 'ch';
    });
});

const btn_save_annotation_json = document.querySelector("#btn_save_annotation_json")
const btn_save_protocol_docx = document.querySelector("#btn_save_protocol_docx")
const btn_close_popup_save = document.querySelector("#btn_close_popup_save")

btn_close_popup_save.addEventListener('click', () => {
    popup_save.classList.remove("show_save_popup")
})

btn_save_annotation_json.addEventListener('click', () => {
    // скачать документ с сервера
    createJSFileWithArrays()
    setTimeout(() => {
        window.location.href = "/download_annotation";
    }, 500)
})

btn_save_protocol_docx.addEventListener('click', async (event) => {
    // формируем json 
    const object_name = document.querySelector("#object_name").value
    const object_name_2 = document.querySelector("#object_name_2").value
    const address = document.querySelector("#address").value 
    const made_of = document.querySelector("#made_of").value
    const lab_conclusion = document.querySelector("#lab_conclusion").value
    const chief_name = document.querySelector("#chief_name").value
    const inspector_name = document.querySelector("#inspector_name").value
    data_to_json = {
        "object_name": object_name,
        "object_name_2": object_name_2,
        "address": address,
        "made_of": made_of,
        "lab_conclusion": lab_conclusion,
        "chief_name": chief_name,
        "inspector_name": inspector_name,
        "defects": arr_defects_add
    }
    // загружаем на сервер json
    try {
        const response = await fetch('/save_protocol_docx', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data_to_json)
        });
        
        // получаем файл
        const blob = await response.blob();

        // создаём ссылку и скачиваем
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = 'protocol.docx';
        document.body.appendChild(a);
        a.click();

        a.remove();
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        console.error('Ошибка:', error);
    }

})

// генерация таблицы дефектов во  всплывающем окне 
function createTableDefects() {

    arr_defects_add = process_defects(defects)
    
    // генерация таблицы
    const table = document.getElementById("defectsTable")
    table.innerHTML = ""
    // заголовки
    const headers = ["Тип и номер стыка по сварочной схеме","№ и размеры снимка, мм",
        "Клеймо сварщика","Чувств. контроля по НТД, мм","Чувстви-тельность контроля, мм",
        "Обнаруженные дефекты","Процент от толщины стенки","Сумм. длина на 100,[300] мм снимка, стык {}, мм",
        "Оценка стыка","Объём контроля, %","Примечание"]
    function addHeader(table) {
        const tr = document.createElement("tr")
        headers.forEach(h => {
            const td = document.createElement("td")
            td.textContent = h
            tr.appendChild(td)
        })
        table.appendChild(tr)
    }
    addHeader(table)
    // сама таблица
    arr_defects_add.forEach(defect => {
        const tr = document.createElement("tr")
        for (i = 0; i < 11; i++) {
            const td = document.createElement("td")
            td.textContent = " "
            if (i == 5) {
                td.textContent = defect
            }
            tr.appendChild(td)
        }
        table.appendChild(tr)
    })
}

// 0,2; 0,3; 0,4; 0,5; 0,6; 0,8; 1,0; 1,2; 1,5; 2,0; 2,5; 3,0 мм
function normalize_mm(len_mm) {
    if (len_mm < 0.2) return 0.2 
    
    if (len_mm < 0.25) return 0.2
    
    if (len_mm < 0.35) return 0.3
    
    if (len_mm < 0.45) return 0.4
    
    if (len_mm < 0.55) return 0.5
    
    if (len_mm < 0.7) return 0.6
    
    if (len_mm < 0.9) return 0.8
    
    if (len_mm < 1.1) return 1.0
    
    if (len_mm < 1.35) return 1.2
    
    if (len_mm < 1.75) return 1.5
    
    if (len_mm < 2.25) return 2.0
    
    if (len_mm < 2.75) return 2.5
    
    if (len_mm < 3.5) return 3.0
    
    if (len_mm > 3.5) return Math.round(len_mm)
}