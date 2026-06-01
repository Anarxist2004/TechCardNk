(() => {
    const openBtn = document.getElementById("selectSavedImageBtn")
    const modal = document.getElementById("techCardImageModal")
    const list = document.getElementById("techCardImageList")
    const status = document.getElementById("techCardImageModalStatus")

    if (!openBtn || !modal || !list || !status) {
        return
    }

    let isLoaded = false
    let isLoading = false

    function formatDate(value) {
        if (!value) {
            return "дата не указана"
        }

        const parsed = new Date(value)
        if (Number.isNaN(parsed.getTime())) {
            return String(value)
        }

        return parsed.toLocaleString("ru-RU")
    }

    function setStatus(text) {
        status.textContent = text
    }

    function setModalOpen(nextOpen) {
        modal.classList.toggle("hidden", !nextOpen)
        modal.setAttribute("aria-hidden", nextOpen ? "false" : "true")
    }

    function normalizeCards(payload) {
        if (!Array.isArray(payload)) {
            return []
        }

        return payload.map((card) => ({
            id: card.id,
            name: card.name || `Техкарта #${card.id}`,
            updatedAt: card.updated_at || card.updatedAt || card.created_at || card.createdAt,
            images: Array.isArray(card.images)
                ? card.images.filter((image) => image && image.preview)
                : [],
        }))
    }

    function renderCards(cards) {
        list.innerHTML = ""

        if (cards.length === 0) {
            list.innerHTML = '<div class="tech-card-image-modal__empty">Сохранённые техкарты не найдены.</div>'
            setStatus("Нет данных для выбора")
            return
        }

        const cardsWithImages = cards.filter((card) => card.images.length > 0)

        if (cardsWithImages.length === 0) {
            list.innerHTML = '<div class="tech-card-image-modal__empty">В сохранённых техкартах пока нет снимков.</div>'
            setStatus(`${cards.length} техкарт без снимков`)
            return
        }

        setStatus(`Доступно техкарт: ${cardsWithImages.length}`)

        cardsWithImages.forEach((card) => {
            const cardEl = document.createElement("section")
            cardEl.className = "tech-card-image-card"

            const header = document.createElement("div")
            header.className = "tech-card-image-card__header"

            const title = document.createElement("h3")
            title.textContent = card.name

            const meta = document.createElement("span")
            meta.textContent = `Обновлена: ${formatDate(card.updatedAt)}`

            header.append(title, meta)

            const imagesEl = document.createElement("div")
            imagesEl.className = "tech-card-image-card__images"

            card.images.forEach((image, index) => {
                const button = document.createElement("button")
                button.type = "button"
                button.className = "tech-card-image-card__image"
                button.title = image.name || `Снимок ${index + 1}`

                const img = document.createElement("img")
                img.src = image.preview
                img.alt = image.name || `Снимок ${index + 1}`
                img.loading = "lazy"

                const caption = document.createElement("span")
                caption.textContent = image.name || `Снимок ${index + 1}`

                button.append(img, caption)
                button.addEventListener("click", () => {
                    if (typeof window.loadImageToViewer !== "function") {
                        setStatus("Модуль просмотра ещё не готов")
                        return
                    }

                    window.loadImageToViewer(image.preview, image.name || card.name)
                    setModalOpen(false)
                })

                imagesEl.appendChild(button)
            })

            cardEl.append(header, imagesEl)
            list.appendChild(cardEl)
        })
    }

    async function loadCards() {
        if (isLoading) {
            return
        }

        isLoading = true
        setStatus("Загрузка списка...")
        list.innerHTML = '<div class="tech-card-image-modal__empty">Загрузка...</div>'

        try {
            const response = await fetch("/techcard/listSavedTechCardImages", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "same-origin",
                body: JSON.stringify({}),
            })

            const data = await response.json().catch(() => ({}))

            if (!response.ok) {
                throw new Error(data.detail || `HTTP ${response.status}`)
            }

            renderCards(normalizeCards(data))
            isLoaded = true
        } catch (error) {
            console.error("Не удалось загрузить снимки техкарт:", error)
            list.innerHTML = '<div class="tech-card-image-modal__empty">Не удалось загрузить список техкарт.</div>'
            setStatus(error.message || "Ошибка загрузки")
        } finally {
            isLoading = false
        }
    }

    openBtn.addEventListener("click", () => {
        setModalOpen(true)
        if (!isLoaded) {
            void loadCards()
        }
    })

    modal.querySelectorAll("[data-close-tech-card-images]").forEach((element) => {
        element.addEventListener("click", () => setModalOpen(false))
    })

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !modal.classList.contains("hidden")) {
            setModalOpen(false)
        }
    })
})()
