function process_defects(arr_defects) {

    pora = {}

    treshina = {}
    treshina_vdol_shva = {}
    treshina_poperek_shva = {}
    treshina_razvetvl = {}

    neprovar = {}
    neprovar_v_korne = {}
    neprovar_mezh_valikami = {}
    neprovar_po_razdelke = {}

    shlak = {}
    volfram = {}
    okis = {}
    kromki = {}

    function process_defect(defect_obj, single, sizes) {
        if (single) {
            d = Math.max(sizes[0], sizes[1])
            d = normalize_mm(d)
            abbr = "" + d
            if (!defect_obj[abbr]) {
                defect_obj[abbr] = 1
            } else {
                defect_obj[abbr] += 1
            }
        } else {
            d_len = normalize_mm(sizes[0])
            d_width = normalize_mm(sizes[1])
            abbr = "" + Math.max(d_len, d_width) + " × " + Math.min(d_len, d_width)
            if (!defect_obj[abbr]) {
                defect_obj[abbr] = 1
            } else {
                defect_obj[abbr] += 1
            }
        }
    }

    arr_defects.forEach(defect => {
        sizes = defect[1]
        name = defect[3]
        // поры
        if (name == "Пора") { process_defect(pora, true, sizes) }
        // трещины
        if (name == "Трещина") { process_defect(treshina, true, sizes) }
        if (name == "Трещина вдоль шва") { process_defect(treshina_vdol_shva, true, sizes) }
        if (name == "Трещина поперек шва") { process_defect(treshina_poperek_shva, true, sizes) }
        if (name == "Трещина разветвленная") { process_defect(treshina_razvetvl, true, sizes) }
        // непровары
        if (name == "Непровар") { process_defect(neprovar, true, sizes) }
        if (name == "Непровар в корне") { process_defect(neprovar_v_korne, true, sizes) }
        if (name == "Непровар между валиками") { process_defect(neprovar_mezh_valikami, true, sizes) }
        if (name == "Непровар по разделке") { process_defect(neprovar_po_razdelke, true, sizes) }
        // включения
        if (name == "Шлаковые включения") { process_defect(shlak, false, sizes) }
        if (name == "Вольфрамовые включения") { process_defect(volfram, false, sizes) }
        if (name == "Окисные включения") { process_defect(okis, false, sizes) }
        // смещение кромок
        if (name == "Смещение кромок") { process_defect(kromki, true, sizes) }
    });

    // массив со всеми дефектами для записи
    result_defects = []

    function filter_defects(defect_obj, letters) {
        for (let key of Object.keys(defect_obj)) {
            result_defects.push((defect_obj[key] + letters + key).replaceAll(".", ",").replace("1", ""))
        }
    } 

    // фильтруем записи по порам
    filter_defects(pora, "П")
    // фильтруем записи по трещинам
    filter_defects(treshina, "Т")
    // фильтруем записи по трещинам вдоль шва
    filter_defects(treshina_vdol_shva, "Тв")
    // фильтруем записи по трещинам поперек шва
    filter_defects(treshina_poperek_shva, "Тп")
    // фильтруем записи по трещинам разветвленным
    filter_defects(treshina_razvetvl, "Тр")
    // фильтруем записи по непроварам
    filter_defects(neprovar, "Н")
    // фильтруем записи по непроварам в корне
    filter_defects(neprovar_v_korne, "Нк")
    // фильтруем записи по непроварам между валиками
    filter_defects(neprovar_mezh_valikami, "Нв")
    // фильтруем записи по непроварам по раздлелке
    filter_defects(neprovar_po_razdelke, "Нр")
    // фильтруем записи по шлаковым включениям
    filter_defects(shlak, "Ш")
    // фильтруем записи по вольфрамовым включениям
    filter_defects(volfram, "В")
    // фильтруем записи по окисным включениям
    filter_defects(okis, "О")
    // фильтруем записи по смещениям кромок
    filter_defects(kromki, "Скр")

    return result_defects
}