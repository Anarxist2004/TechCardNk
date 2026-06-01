window.currentTool = "line";
const tools = document.querySelectorAll(".tool-btn")

tools.forEach(tool => {
    tool.addEventListener("click", (e) => {
        if (tool.closest(".dropdown")) return;
        if (tool.id === "selectSavedImageBtn") return;

        clearAllActive()
        tool.classList.add("active")
        currentTool = tool.dataset.tool
    })
})

function clearAllActive() {
    tools.forEach(tool => {
        tool.classList.remove("active")
    });
}

const sizeSlider = document.querySelector("#sizeSlider")
const sizeValue = document.querySelector("#sizeValue")
sizeSlider.addEventListener("change", () => {
    sizeValue.textContent = sizeSlider.value + "px"
})

let zoomLevel = 1;
const ZOOM_STEP = 0.1;
const MAX_ZOOM = 10;
const MIN_ZOOM = 0.1;
const zoomInBtn = document.getElementById('zoomIn');
const zoomOutBtn = document.getElementById('zoomOut');
const resetZoomBtn = document.getElementById('resetZoom');
const canvasContainer = document.querySelector('.canvas-container');

function clearCanvas() {
    ctx.fillStyle = 'white'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    lines = []       
    rects = []
    ellipses = []
    ellipses3 = []
    lines_et = []
    rulers = []
    measureRects = []
    measureEllipses = []
    measureEllipses3 = []
    shov_lines = []
    defects = []
    comments = []
    redraw_defects()
}
document.querySelector('#clearBtn').addEventListener('click', function() {
    clearCanvas()
    if (original_image) {
        ctx.drawImage(original_image, 0, 0)
    }
})

if (canvasContainer) {
    canvasContainer.addEventListener('wheel', function(e) {
        e.preventDefault();
        
        if (!original_image && !currentImage) return;
        
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        const pointX = (mouseX / rect.width) * 100;
        const pointY = (mouseY / rect.height) * 100;
        
        const oldZoom = zoomLevel;
        
        if (e.deltaY < 0) {
            zoomLevel = Math.min(zoomLevel + ZOOM_STEP, MAX_ZOOM);
        } else {
            zoomLevel = Math.max(zoomLevel - ZOOM_STEP, MIN_ZOOM);
        }
        
        if (oldZoom !== zoomLevel) {
            setCanvases(pointX, pointY)
            document.getElementById('status').textContent = `Масштаб: ${Math.round(zoomLevel * 100)}%`;
        }
    }, { passive: false });
}

function setCanvases(pointX, pointY) {
    canvas.dataset.transformOrigin = `${pointX}% ${pointY}%`;
    
    canvas.style.transformOrigin = `${pointX}% ${pointY}%`;
    canvas.style.transform = `scale(${zoomLevel})`;

    updateCommentInputPosition()
}

let isPanning = false;
let lastX, lastY;

canvas.addEventListener('mousedown', (e) => {
    if (e.button === 2) {
        isPanning = true;
        lastX = e.clientX;
        lastY = e.clientY;
        canvas.style.cursor = 'grabbing';
        e.preventDefault();
    }
});

window.addEventListener('mousemove', (e) => {
    if (isPanning) {
        const dx = e.clientX - lastX;
        const dy = e.clientY - lastY;
    
        let currentX = 0, currentY = 0;
        if (canvas.style.transform) {
            const match = canvas.style.transform.match(/translate\(([-\d.]+)px, ([-\d.]+)px/);
            if (match) {
                currentX = parseFloat(match[1]) || 0;
                currentY = parseFloat(match[2]) || 0;
            }
        }
        
        console.log(canvas.width)
        canvas.style.transform = `translate(${currentX + dx}px, ${currentY + dy}px) scale(${zoomLevel})`;
        updateCommentInputPosition()

        lastX = e.clientX;
        lastY = e.clientY;
    }
});

window.addEventListener('mouseup', (e) => {
    if (e.button === 2) {
        isPanning = false;
        canvas.style.cursor = 'crosshair';
    }
});

canvas.addEventListener('contextmenu', (e) => {
    e.preventDefault();
});

zoomInBtn.addEventListener('click', function() {
    if (zoomLevel < MAX_ZOOM) {
        zoomLevel = Math.min(zoomLevel + ZOOM_STEP, MAX_ZOOM);
        
        const transform = canvas.style.transform;
        const match = transform.match(/translate\(([-\d.]+)px, ([-\d.]+)px/);
        const currentX = match ? parseFloat(match[1]) : 0;
        const currentY = match ? parseFloat(match[2]) : 0;
        
        canvas.style.transform = `translate(${currentX}px, ${currentY}px) scale(${zoomLevel})`;
        updateCommentInputPosition()
        document.getElementById('status').textContent = `Масштаб: ${Math.round(zoomLevel * 100)}%`;
    }
});

zoomOutBtn.addEventListener('click', function() {
    if (zoomLevel > MIN_ZOOM) {
        zoomLevel = Math.max(zoomLevel - ZOOM_STEP, MIN_ZOOM);
        
        const transform = canvas.style.transform;
        const match = transform.match(/translate\(([-\d.]+)px, ([-\d.]+)px/);
        const currentX = match ? parseFloat(match[1]) : 0;
        const currentY = match ? parseFloat(match[2]) : 0;
        
        canvas.style.transform = `translate(${currentX}px, ${currentY}px) scale(${zoomLevel})`;
        updateCommentInputPosition()
        document.getElementById('status').textContent = `Масштаб: ${Math.round(zoomLevel * 100)}%`;
    }
});

resetZoomBtn.addEventListener('click', function() {
    zoomLevel = 1;
    canvas.style.transform = `translate(0px, 0px) scale(1)`;
    updateCommentInputPosition()
    document.getElementById('status').textContent = `Масштаб: 100%`;
});

const etalonTypeSelect = document.getElementById("etalonType")
const etalonValueSelect = document.getElementById("etalonValue")

const ETALON_CONFIG = {
    groove: [
        { value: "1", label: "1", mm: 30 },
        { value: "2", label: "2", mm: 45 },
        { value: "3", label: "3", mm: 60 }
    ],

    plate: [
        { value: "1",  label: "1",  mm: 25 },
        { value: "2",  label: "2",  mm: 25 },
        { value: "3",  label: "3",  mm: 25 },
        { value: "4",  label: "4",  mm: 25 },
        { value: "5",  label: "5",  mm: 25 },
        { value: "6",  label: "6",  mm: 35 },
        { value: "7",  label: "7",  mm: 35 },
        { value: "8",  label: "8",  mm: 35 },
        { value: "9",  label: "9",  mm: 35 },
        { value: "10", label: "10", mm: 45 },
        { value: "11", label: "11", mm: 45 },
        { value: "12", label: "12", mm: 45 }
    ],

    wire: [
        { value: "-", label: "-", mm: 20 }
    ]
}

function fillEtalonNumbers() {
    const selectedType = etalonTypeSelect.value
    const options = ETALON_CONFIG[selectedType]

    etalonValueSelect.innerHTML = ""

    options.forEach(option => {
        const el = document.createElement("option")
        el.value = option.value
        el.textContent = option.label
        etalonValueSelect.appendChild(el)
    })
}

function getSelectedEtalonLengthMm() {
    const selectedType = etalonTypeSelect.value
    const selectedValue = etalonValueSelect.value

    const found = ETALON_CONFIG[selectedType].find(
        item => String(item.value) === String(selectedValue)
    )

    return found ? found.mm : 1
}

etalonTypeSelect.addEventListener("change", () => {
    fillEtalonNumbers()

    if (len_etalon > 0) {
        mmToPx(len_etalon)
        continueDraw({ clientX: mouse_x, clientY: mouse_y })
    }
})

etalonValueSelect.addEventListener("change", () => {
    if (len_etalon > 0) {
        mmToPx(len_etalon)
        continueDraw({ clientX: mouse_x, clientY: mouse_y })
    }
})

fillEtalonNumbers()

class DropdownManager {
    constructor() {
        this.dropdowns = Array.from(document.querySelectorAll('.dropdown'));
        this.activeDropdown = null;

        this.init();
    }

    init() {
        this.dropdowns.forEach(dropdown => {
            const btn = dropdown.querySelector('.dropdown-btn');
            const content = dropdown.querySelector('.dropdown-content');

            btn.addEventListener('click', (e) => {
                e.stopPropagation(); 

                if (this.activeDropdown && this.activeDropdown !== dropdown) {
                    this.closeDropdown(this.activeDropdown);
                }

                if (dropdown.classList.contains('open')) {
                    this.closeDropdown(dropdown);
                } else {
                    this.openDropdown(dropdown);
                }
            });

            content.querySelectorAll('.dropdown-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();

                    content.querySelectorAll('.dropdown-item').forEach(i => i.classList.remove('active'));
                    item.classList.add('active');

                    btn.textContent = item.textContent + ' ↓';

                    this.closeDropdown(dropdown);

                    if (item.dataset.tool) {
                        window.currentTool = item.dataset.tool;
                        updateToolStatus(item.textContent);
                    }
                });
            });
        });

        document.addEventListener('click', () => this.closeAllDropdowns());

        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeAllDropdowns();
        });
    }

    openDropdown(dropdown) {
        dropdown.classList.add('open');
        this.activeDropdown = dropdown;
    }

    closeDropdown(dropdown) {
        dropdown.classList.remove('open');
        if (this.activeDropdown === dropdown) this.activeDropdown = null;
    }

    closeAllDropdowns() {
        this.dropdowns.forEach(d => d.classList.remove('open'));
        this.activeDropdown = null;
    }
}

function updateToolStatus(name) {
    const tools = document.querySelectorAll(".tool-btn");
    tools.forEach(tool => tool.classList.remove('active'));

    const status = document.getElementById('status');
    if (status) status.textContent = `Выбран инструмент: ${name}`;
}

document.addEventListener('DOMContentLoaded', () => {
    new DropdownManager();
});

const bcBtn = document.getElementById("bcBtn")
const bcPanel = document.getElementById("bcPanel")

bcBtn.addEventListener("click", (e) => {
    e.stopPropagation()
    bcPanel.classList.toggle("hidden")
})

document.addEventListener("click", (e) => {
    if (!bcPanel.contains(e.target) && e.target !== bcBtn) {
        bcPanel.classList.add("hidden")
    }
})

const brightnessSlider = document.getElementById("brightnessSlider")
const contrastSlider = document.getElementById("contrastSlider")
const brightnessValue = document.getElementById("brightnessValue")
const contrastValue = document.getElementById("contrastValue")
const resetBC = document.getElementById("resetBC")

brightnessSlider.addEventListener("input", () => {
    brightness = parseInt(brightnessSlider.value)
    brightnessValue.value = brightness
    continueDraw({clientX: mouse_x, clientY: mouse_y})
})

contrastSlider.addEventListener("input", () => {
    contrast = parseInt(contrastSlider.value)
    contrastValue.value = contrast
    continueDraw({clientX: mouse_x, clientY: mouse_y})
})

brightnessValue.addEventListener("input", () => {
    let val = parseInt(brightnessValue.value) || 0
    val = Math.max(-100, Math.min(100, val))
    brightness = val
    brightnessSlider.value = val
    continueDraw({clientX: mouse_x, clientY: mouse_y})
})

contrastValue.addEventListener("input", () => {
    let val = parseInt(contrastValue.value) || 0
    val = Math.max(-100, Math.min(100, val))
    contrast = val
    contrastSlider.value = val
    continueDraw({clientX: mouse_x, clientY: mouse_y})
})

resetBC.addEventListener("click", () => {
    brightness = 0
    contrast = 0
    brightnessSlider.value = 0
    contrastSlider.value = 0
    brightnessValue.value = 0
    contrastValue.value = 0
    continueDraw({clientX: mouse_x, clientY: mouse_y})
})

const globalAnnotation = document.getElementById("globalAnnotation");

globalAnnotation.value = localStorage.getItem("globalAnnotation") || "";

globalAnnotation.addEventListener("input", () => {
    localStorage.setItem("globalAnnotation", globalAnnotation.value);
});
