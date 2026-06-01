(() => {
    const status = document.getElementById("expertHistoryStatus")
    const annotationList = document.getElementById("expertAnnotationHistory")
    const protocolList = document.getElementById("expertProtocolHistory")
    const refreshBtn = document.getElementById("refreshExpertHistory")

    if (!status || !annotationList || !protocolList || !refreshBtn) {
        return
    }

    let isLoading = false
    let shouldReloadAfterCurrentRequest = false

    function formatDate(value) {
        if (!value) return "дата не указана"
        const parsed = new Date(value)
        if (Number.isNaN(parsed.getTime())) return String(value)
        return parsed.toLocaleString("ru-RU")
    }

    function setEmpty(message = "История пока пустая.") {
        annotationList.innerHTML = `<div class="expert-history__empty">${message}</div>`
        protocolList.innerHTML = `<div class="expert-history__empty">${message}</div>`
    }

    function setStatus(text) {
        status.textContent = text
    }

    async function readResponseJson(response) {
        const text = await response.text()
        if (!text) return {}

        try {
            return JSON.parse(text)
        } catch (error) {
            return {}
        }
    }

    function requestDeletePassword(label) {
        return new Promise((resolve) => {
            const overlay = document.createElement("div")
            overlay.className = "expert-history-delete"

            const dialog = document.createElement("form")
            dialog.className = "expert-history-delete__dialog"

            const title = document.createElement("h3")
            title.textContent = `Удалить ${label}?`

            const text = document.createElement("p")
            text.textContent = "Введите пароль от вашей учетной записи для подтверждения удаления."

            const input = document.createElement("input")
            input.type = "password"
            input.autocomplete = "current-password"
            input.required = true
            input.placeholder = "Пароль"

            const actions = document.createElement("div")
            actions.className = "expert-history-delete__actions"

            const cancelButton = document.createElement("button")
            cancelButton.type = "button"
            cancelButton.className = "tool-btn"
            cancelButton.textContent = "Отмена"

            const submitButton = document.createElement("button")
            submitButton.type = "submit"
            submitButton.className = "tool-btn expert-history__delete"
            submitButton.textContent = "Удалить"

            function close(value) {
                overlay.remove()
                resolve(value)
            }

            cancelButton.addEventListener("click", () => close(null))
            overlay.addEventListener("click", (event) => {
                if (event.target === overlay) close(null)
            })
            dialog.addEventListener("submit", (event) => {
                event.preventDefault()
                close(input.value)
            })

            actions.append(cancelButton, submitButton)
            dialog.append(title, text, input, actions)
            overlay.appendChild(dialog)
            document.body.appendChild(overlay)
            input.focus()
        })
    }

    async function deleteArtifact(item, type) {
        const label = type === "annotation" ? "аннотацию" : "протокол проверки"
        if (!item.canDelete || !item.deleteUrl) {
            alert("Удалить может только владелец записи.")
            return
        }

        const password = await requestDeletePassword(label)
        if (!password) {
            return
        }

        try {
            const response = await fetch(item.deleteUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "same-origin",
                body: JSON.stringify({ password }),
            })
            const data = await readResponseJson(response)
            if (!response.ok) {
                throw new Error(data.detail || "Не удалось удалить запись")
            }

            if (data.history) {
                renderHistory(data.history)
            } else {
                void loadHistory()
            }
            setStatus(type === "annotation" ? "Аннотация удалена." : "Протокол проверки удален.")
        } catch (error) {
            console.error("Не удалось удалить запись:", error)
            alert(error.message || "Не удалось удалить запись")
        }
    }

    function createArtifactCard(item, type) {
        const row = document.createElement("article")
        row.className = "expert-history__item"

        const meta = document.createElement("div")
        meta.className = "expert-history__meta"

        const author = document.createElement("strong")
        author.textContent = item.author || "Неизвестный пользователь"

        const created = document.createElement("span")
        created.textContent = formatDate(item.createdAt)

        meta.append(author, created)

        const actions = document.createElement("div")
        actions.className = "expert-history__actions"

        if (type === "annotation") {
            const loadButton = document.createElement("button")
            loadButton.type = "button"
            loadButton.className = "tool-btn"
            loadButton.textContent = "Загрузить"
            loadButton.addEventListener("click", async () => {
                try {
                    const response = await fetch(item.loadUrl, { credentials: "same-origin" })
                    const text = await response.text()
                    if (!response.ok) {
                        let errorData = {}
                        try {
                            errorData = JSON.parse(text || "{}")
                        } catch (error) {
                            errorData = {}
                        }
                        throw new Error(errorData.detail || "Не удалось загрузить аннотацию")
                    }
                    if (typeof window.loadAnnotationFromText !== "function") {
                        throw new Error("Модуль аннотаций ещё не готов")
                    }
                    window.loadAnnotationFromText(text)
                    setStatus(`Аннотация загружена: ${formatDate(item.createdAt)}`)
                } catch (error) {
                    console.error("Не удалось загрузить аннотацию:", error)
                    alert(error.message || "Не удалось загрузить аннотацию")
                }
            })
            actions.appendChild(loadButton)
        }

        const download = document.createElement("a")
        download.className = "tool-btn expert-history__download"
        download.href = item.downloadUrl
        download.textContent = type === "annotation" ? "JSON" : "Скачать"
        download.download = ""
        actions.appendChild(download)

        if (item.canDelete) {
            const deleteButton = document.createElement("button")
            deleteButton.type = "button"
            deleteButton.className = "tool-btn expert-history__delete"
            deleteButton.textContent = "Удалить"
            deleteButton.addEventListener("click", () => {
                void deleteArtifact(item, type)
            })
            actions.appendChild(deleteButton)
        }

        row.append(meta, actions)
        return row
    }

    function renderHistory(history) {
        const annotations = Array.isArray(history?.annotations) ? history.annotations : []
        const protocols = Array.isArray(history?.protocols) ? history.protocols : []

        annotationList.innerHTML = ""
        protocolList.innerHTML = ""

        if (annotations.length === 0) {
            annotationList.innerHTML = '<div class="expert-history__empty">Аннотаций пока нет.</div>'
        } else {
            annotations.forEach((item) => annotationList.appendChild(createArtifactCard(item, "annotation")))
        }

        if (protocols.length === 0) {
            protocolList.innerHTML = '<div class="expert-history__empty">Протоколов пока нет.</div>'
        } else {
            protocols.forEach((item) => protocolList.appendChild(createArtifactCard(item, "protocol")))
        }

        setStatus(`Аннотаций: ${annotations.length}; протоколов: ${protocols.length}`)
    }

    async function loadHistory() {
        const image = window.currentExpertImage
        if (!image?.key) {
            setStatus("Откройте снимок, чтобы увидеть аннотации и протоколы.")
            setEmpty("Снимок не выбран.")
            return
        }

        if (isLoading) {
            shouldReloadAfterCurrentRequest = true
            return
        }
        isLoading = true
        setStatus("Загрузка истории...")

        try {
            const response = await fetch("/expert/image-history", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "same-origin",
                body: JSON.stringify({ image }),
            })
            const data = await response.json()
            if (!response.ok) {
                throw new Error(data.detail || "Не удалось загрузить историю")
            }
            renderHistory(data)
        } catch (error) {
            console.error("Не удалось загрузить историю снимка:", error)
            setStatus(error.message || "Не удалось загрузить историю")
            setEmpty("История недоступна.")
        } finally {
            isLoading = false
            if (shouldReloadAfterCurrentRequest) {
                shouldReloadAfterCurrentRequest = false
                void loadHistory()
            }
        }
    }

    refreshBtn.addEventListener("click", () => {
        void loadHistory()
    })

    window.addEventListener("expert-image-loaded", () => {
        void loadHistory()
    })

    window.addEventListener("expert-history-refresh", () => {
        void loadHistory()
    })

    window.addEventListener("expert-history-updated", (event) => {
        if (event.detail) {
            renderHistory(event.detail)
        } else {
            void loadHistory()
        }
    })

    setEmpty("Снимок не выбран.")
})()
