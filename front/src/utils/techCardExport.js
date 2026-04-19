const DISPLAY_MODE_NUMBER_ONLY = 'number_only';
const DISPLAY_MODE_IMAGE_FULL = 'image_full';
const DISPLAY_MODE_SECTION_HEADER = 'section_header';
const DISPLAY_MODE_OPERATIONS_ROW = 'operations_row';
const IMAGE_FRAME_COLOR = '#98785c';

/** Значения поля subtitle для блока 2 (API / шаблон). */
export const PARAM_SUBTITLE_BLOCK2 = {
  GENERAL: 'general',
  WELD_PARAMETERS: 'weld_parameters',
  REQUIREMENTS: 'requirements',
};

const escapeHtml = (value = '') => String(value)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;');

/**
 * Word: растр перед вставкой умеренно вписываем в рамку (см. prepareExportImages),
 * чтобы таблица не разъезжалась; размеры мягче, чем «жёсткие» 260×380 px.
 */
const EXPORT_IMG_DIAGRAM = { maxW: 420, maxH: 560 };
const EXPORT_IMG_GENERIC = { maxW: 900, maxH: 1200 };
const EXPORT_IMG_EXTRA = { maxW: 520, maxH: 700 };

const WORD_IMG_TABLE_CELL = 'width:100%;max-width:100%;height:auto;max-height:95mm;object-fit:contain;display:block;margin:0 auto;mso-width-percent:1000;';
const WORD_IMG_TABLE_CELL_FULL = 'width:100%;max-width:100%;height:auto;max-height:130mm;object-fit:contain;display:block;margin:0 auto;mso-width-percent:1000;';
const WORD_IMG_EXTRA = 'width:100%;max-width:100%;height:auto;max-height:60mm;object-fit:contain;display:block;margin:0 auto;mso-width-percent:1000;';
const WORD_DIAGRAM_IMG_STYLE = 'width:100%;max-width:100%;height:auto;max-height:68mm;object-fit:contain;display:block;margin:0 auto;mso-width-percent:1000;';

/** Колонка со схемой — ровно 2/5 ширины таблицы; остальные колонки добирают 100%. */
const OFF_B2_DIAGRAM_COL_PCT = 40;
const OFF_B2_SIDE_COL_PCT = 12;
/** 4 колонки: бок | наименование | значение | схема (12 + 33 + 15 + 40 = 100). */
const OFF_B2_NAME_4COL_PCT = 33;
const OFF_B2_VAL_4COL_PCT = 15;
/** 3 колонки «объект контроля»: бок | наименование | значение (без схемы), сумма 100%. */
const OFF_B2_NAME_OC_PCT = 62;
const OFF_B2_VAL_OC_PCT = 26;
/** 3 колонки зоны диаграммы: наименование | значение | схема. */
const OFF_B2_NAME_DZ_PCT = 35;
const OFF_B2_VAL_DZ_PCT = 25;

const OFF_B3_DIAGRAM_COL_PCT = 40;
const OFF_B3_PNAME_PCT = 38;
const OFF_B3_PVAL_PCT = 22;

/** Атрибуты ячейки со схемой для Word (фиксированная доля таблицы). */
const offB2DiagramTdAttrs = () => ` width="${OFF_B2_DIAGRAM_COL_PCT}%" style="width:${OFF_B2_DIAGRAM_COL_PCT}%;max-width:${OFF_B2_DIAGRAM_COL_PCT}%;overflow:hidden;vertical-align:top;"`;

const offB3DiagramTdAttrs = () => ` width="${OFF_B3_DIAGRAM_COL_PCT}%" style="width:${OFF_B3_DIAGRAM_COL_PCT}%;max-width:${OFF_B3_DIAGRAM_COL_PCT}%;overflow:hidden;vertical-align:top;"`;

const OFF_B2_DIAGRAM_SPACER_PCT = 100 - OFF_B2_SIDE_COL_PCT - OFF_B2_DIAGRAM_COL_PCT;

const wordImg = (src, alt, style, opts = {}) => {
  const safeSrc = escapeHtml(String(src || ''));
  const safeAlt = escapeHtml(alt || '');
  const { widthPx, heightPx } = opts;
  const dimAttr = widthPx != null && heightPx != null
    ? ` width="${widthPx}" height="${heightPx}"`
    : widthPx != null
      ? ` width="${widthPx}"`
      : '';
  return `<img src="${safeSrc}" alt="${safeAlt}"${dimAttr} style="${style}" />`;
};

const buildDiagramImgStyle = (w, h) => (
  `width:${w}px;max-width:100%;height:${h}px;max-height:100%;object-fit:contain;display:block;margin:0 auto;mso-width-percent:1000;`
);

const wordDiagramWrapB2 = (src, size) => {
  if (size?.w != null && size?.h != null) {
    const { w, h } = size;
    return `
  <div class="off-diagram-wrap" style="width:100%;max-width:100%;overflow:hidden;text-align:center;line-height:0;">
    ${wordImg(src, '', buildDiagramImgStyle(w, h), { widthPx: w, heightPx: h })}
  </div>`;
  }
  return `
  <div class="off-diagram-wrap" style="width:100%;max-width:100%;overflow:hidden;text-align:center;line-height:0;">
    ${wordImg(src, '', WORD_DIAGRAM_IMG_STYLE)}
  </div>`;
};

const wordDiagramWrapB3 = (src, caption, size) => {
  if (size?.w != null && size?.h != null) {
    const { w, h } = size;
    return `
  <div class="off-diagram-wrap off-b3-img" style="width:100%;max-width:100%;overflow:hidden;text-align:center;line-height:0;">
    ${wordImg(src, caption, buildDiagramImgStyle(w, h), { widthPx: w, heightPx: h })}
  </div>`;
  }
  return `
  <div class="off-diagram-wrap off-b3-img" style="width:100%;max-width:100%;overflow:hidden;text-align:center;line-height:0;">
    ${wordImg(src, caption, WORD_DIAGRAM_IMG_STYLE)}
  </div>`;
};

const wordImgWithMeta = (src, alt, baseStyle, meta) => {
  if (meta && meta.w != null && meta.h != null) {
    const style = `${baseStyle};width:${meta.w}px;max-width:100%;height:${meta.h}px;max-height:100%;object-fit:contain;display:block;margin:0 auto;mso-width-percent:1000;`;
    return wordImg(src, alt, style, { widthPx: meta.w, heightPx: meta.h });
  }
  return wordImg(src, alt, baseStyle);
};

const resolveImageSrc = (imageSrc) => {
  if (!imageSrc) {
    return '';
  }

  const normalizedSrc = String(imageSrc).trim();

  if (
    normalizedSrc.startsWith('data:')
    || normalizedSrc.startsWith('http://')
    || normalizedSrc.startsWith('https://')
    || normalizedSrc.startsWith('blob:')
  ) {
    return normalizedSrc;
  }

  if (normalizedSrc.startsWith('/')) {
    return normalizedSrc;
  }

  if (normalizedSrc.startsWith('res/')) {
    return `/${normalizedSrc}`;
  }

  const looksLikeBase64 = (
    !normalizedSrc.includes('/')
    && !normalizedSrc.includes('\\')
    && !normalizedSrc.includes(' ')
    && /^[A-Za-z0-9+/=]+$/.test(normalizedSrc)
    && normalizedSrc.length > 64
  );

  if (looksLikeBase64) {
    return `data:image/png;base64,${normalizedSrc}`;
  }

  return normalizedSrc;
};

const isNamedValueObject = (value) => (
  typeof value === 'object'
  && value !== null
  && !Array.isArray(value)
  && (value.name !== undefined || value.id !== undefined || value.value !== undefined)
);

const normalizeValueText = (value) => {
  if (value === null || value === undefined) {
    return '';
  }

  if (typeof value === 'string') {
    return value.trim();
  }

  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }

  if (Array.isArray(value)) {
    return value.map(normalizeValueText).filter(Boolean).join(', ');
  }

  if (typeof value === 'object') {
    if (value.image) {
      return '';
    }

    if (value.name !== undefined && value.name !== null) {
      return String(value.name).trim();
    }

    if (value.value !== undefined && value.value !== null && typeof value.value !== 'object') {
      return String(value.value).trim();
    }

    return Object.entries(value)
      .filter(([key]) => key !== 'image')
      .map(([key, nestedValue]) => {
        const text = normalizeValueText(nestedValue);
        return text ? `${key}: ${text}` : '';
      })
      .filter(Boolean)
      .join('\n');
  }

  return String(value).trim();
};

const getParamTextValue = (param, compositeKey, paramValues) => {
  if (Object.prototype.hasOwnProperty.call(paramValues, compositeKey)) {
    const rawValue = paramValues[compositeKey];
    return rawValue !== undefined && rawValue !== null ? String(rawValue).trim() : '';
  }

  if (Array.isArray(param.value)) {
    return '';
  }

  if (isNamedValueObject(param.value)) {
    return normalizeValueText(param.value);
  }

  return normalizeValueText(param.value);
};

const getParamText2Value = (param, compositeKey, paramValues2 = {}) => {
  if (Object.prototype.hasOwnProperty.call(paramValues2, compositeKey)) {
    const rawValue = paramValues2[compositeKey];
    return rawValue !== undefined && rawValue !== null ? String(rawValue).trim() : '';
  }

  if (Array.isArray(param.value2)) {
    return '';
  }

  if (isNamedValueObject(param.value2)) {
    return normalizeValueText(param.value2);
  }

  return normalizeValueText(param.value2);
};

const getParamExportCellText = (param, compositeKey, paramValues, paramValues2 = {}) => {
  const primary = getParamTextValue(param, compositeKey, paramValues);
  if (!param.hasVal2) {
    return primary;
  }
  const secondary = getParamText2Value(param, compositeKey, paramValues2);
  if (!secondary) {
    return primary;
  }
  if (!primary) {
    return secondary;
  }
  return `${primary} – ${secondary}`;
};

const getParamImageSrc = (param) => {
  if (param.image) {
    return resolveImageSrc(param.image);
  }

  if (param.value && typeof param.value === 'object' && !Array.isArray(param.value) && param.value.image) {
    return resolveImageSrc(param.value.image);
  }

  return '';
};

const isOperationsRowParam = (param) => param?.displayMode === DISPLAY_MODE_OPERATIONS_ROW;

/**
 * Строка операции в техкарте:
 * — displayMode operations_row;
 * — объект value с полями content + equipment;
 * — пара val/val2 с бэка → на фронте hasVal2 + value + value2 (иначе number_only даёт пустые «Пункт»/«Наименование»).
 */
const isOperationsLikeParam = (param) => {
  if (param?.displayMode === DISPLAY_MODE_OPERATIONS_ROW) {
    return true;
  }
  if (param?.hasVal2) {
    return true;
  }
  const v = param?.value;
  if (!v || typeof v !== 'object' || Array.isArray(v)) {
    return false;
  }
  return Object.prototype.hasOwnProperty.call(v, 'content')
    && Object.prototype.hasOwnProperty.call(v, 'equipment');
};

const isSectionHeaderParam = (param) => param?.displayMode === DISPLAY_MODE_SECTION_HEADER;

const paramHasImage = (param, compositeKey, imageSrcMap) => Boolean(
  imageSrcMap[compositeKey]
  || getParamImageSrc(param),
);

const normalizeBlockId = (block) => String(block?.id ?? '');

/** Экспорт блока «Перечень операций РК» — три колонки по ГОСТ (как на макете). */
const isOperationsRcBlock = (block) => {
  const id = normalizeBlockId(block);
  if (id === '4') {
    return true;
  }
  const n = String(block?.name ?? '').toUpperCase().replace(/\s+/g, ' ').trim();
  return n.includes('ПЕРЕЧЕНЬ') && n.includes('ОПЕРАЦ') && n.includes('РК');
};

const trimBlock2Subtitle = (s) => (s == null ? '' : String(s).trim());

const isBlock2ObjectControlSubtitle = (subtitle) => {
  const t = trimBlock2Subtitle(subtitle).toLowerCase();
  if (!t) {
    return false;
  }
  if (t === String(PARAM_SUBTITLE_BLOCK2.GENERAL).toLowerCase()) {
    return true;
  }
  return t.includes('объект') && t.includes('контрол');
};

const isBlock2WeldDiagramSubtitle = (subtitle) => {
  const t = trimBlock2Subtitle(subtitle).toLowerCase();
  if (!t) {
    return false;
  }
  if (t === String(PARAM_SUBTITLE_BLOCK2.WELD_PARAMETERS).toLowerCase()) {
    return true;
  }
  if (t.includes('параметр') && t.includes('сварн')) {
    return true;
  }
  return false;
};

const isBlock2RequirementsSubtitle = (subtitle) => {
  const t = trimBlock2Subtitle(subtitle).toLowerCase();
  if (!t) {
    return false;
  }
  if (t === String(PARAM_SUBTITLE_BLOCK2.REQUIREMENTS).toLowerCase()) {
    return true;
  }
  return t.includes('требован') && (t.includes('проведен') || t.includes('контрол'));
};

const isBlock2DiagramZoneSubtitle = (subtitle) => isBlock2WeldDiagramSubtitle(subtitle)
  || isBlock2RequirementsSubtitle(subtitle);

const block2SubtitleModeEnabled = (params) => params.some(
  (p) => trimBlock2Subtitle(p?.subtitle) !== '',
);

const effectiveBlock2Subtitle = (param) => {
  const t = trimBlock2Subtitle(param?.subtitle);
  return t || '__default__';
};

const readBlobAsDataUrl = (blob) => new Promise((resolve, reject) => {
  const reader = new FileReader();
  reader.onload = () => resolve(reader.result);
  reader.onerror = () => reject(new Error('Не удалось прочитать изображение для экспорта.'));
  reader.readAsDataURL(blob);
});

const embedImageSource = async (imageSrc, cache) => {
  const resolvedSrc = resolveImageSrc(imageSrc);
  if (!resolvedSrc) {
    return '';
  }

  if (resolvedSrc.startsWith('data:')) {
    return resolvedSrc;
  }

  if (cache.has(resolvedSrc)) {
    return cache.get(resolvedSrc);
  }

  try {
    const response = await fetch(resolvedSrc);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const dataUrl = await readBlobAsDataUrl(await response.blob());
    cache.set(resolvedSrc, dataUrl);
    return dataUrl;
  } catch {
    cache.set(resolvedSrc, resolvedSrc);
    return resolvedSrc;
  }
};

const downscaleDataUrlToFitBox = (dataUrl, maxW, maxH) => new Promise((resolve) => {
  if (
    typeof document === 'undefined'
    || !dataUrl
    || typeof dataUrl !== 'string'
    || !dataUrl.startsWith('data:')
  ) {
    resolve({ dataUrl, width: null, height: null });
    return;
  }

  const img = new Image();
  img.onload = () => {
    const w0 = img.naturalWidth || img.width;
    const h0 = img.naturalHeight || img.height;
    if (!w0 || !h0) {
      resolve({ dataUrl, width: null, height: null });
      return;
    }

    const scale = Math.min(maxW / w0, maxH / h0, 1);
    const w = Math.max(1, Math.round(w0 * scale));
    const h = Math.max(1, Math.round(h0 * scale));

    if (scale >= 1) {
      resolve({ dataUrl, width: w0, height: h0 });
      return;
    }

    let canvas;
    try {
      canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
    } catch {
      resolve({ dataUrl, width: w0, height: h0 });
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      resolve({ dataUrl, width: w0, height: h0 });
      return;
    }

    try {
      ctx.drawImage(img, 0, 0, w, h);
      const out = canvas.toDataURL('image/png');
      resolve({ dataUrl: out || dataUrl, width: w, height: h });
    } catch {
      resolve({ dataUrl, width: w0, height: h0 });
    }
  };
  img.onerror = () => resolve({ dataUrl, width: null, height: null });
  img.src = dataUrl;
});

const processDataUrlForWordExport = async (dataUrl, { maxW, maxH }) => {
  if (!dataUrl || typeof dataUrl !== 'string') {
    return { dataUrl: '', width: undefined, height: undefined };
  }
  if (!dataUrl.startsWith('data:')) {
    return { dataUrl, width: undefined, height: undefined };
  }
  const { dataUrl: out, width, height } = await downscaleDataUrlToFitBox(dataUrl, maxW, maxH);
  return {
    dataUrl: out,
    width: width ?? undefined,
    height: height ?? undefined,
  };
};

const prepareExportImages = async (blocks, uploadedImages) => {
  const cache = new Map();
  const blockImages = {};
  const blockImageMeta = {};
  const extraImages = {};

  for (const block of blocks) {
    const bid = String(block.id);
    const box = (bid === '2' || bid === '3') ? EXPORT_IMG_DIAGRAM : EXPORT_IMG_GENERIC;

    for (const param of block.params || []) {
      const compositeKey = `${block.id}.${param.id}`;
      const imageSrc = getParamImageSrc(param);
      if (!imageSrc) {
        continue;
      }

      const embedded = await embedImageSource(imageSrc, cache);
      const processed = await processDataUrlForWordExport(embedded, box);
      blockImages[compositeKey] = processed.dataUrl;
      if (processed.width != null && processed.height != null) {
        blockImageMeta[compositeKey] = { w: processed.width, h: processed.height };
      }
    }
  }

  for (const [blockId, images] of Object.entries(uploadedImages || {})) {
    if (!Array.isArray(images) || images.length === 0) {
      continue;
    }

    extraImages[blockId] = await Promise.all(
      images
        .filter((image) => image && image.preview)
        .map(async (image) => {
          const embedded = await embedImageSource(image.preview, cache);
          const processed = await processDataUrlForWordExport(embedded, EXPORT_IMG_EXTRA);
          return {
            ...image,
            exportSrc: processed.dataUrl,
            exportW: processed.width,
            exportH: processed.height,
          };
        }),
    );
  }

  return {
    blockImages,
    blockImageMeta,
    extraImages,
  };
};

/** Шапка: заголовок слева, шифр/ТК/уровень справа, затем строки параметров */
const buildOfficialBlock1Html = (block, paramValues, imageSrcMap, paramValues2 = {}) => {
  const params = (block.params || []).filter((p) => !isOperationsRowParam(p));
  const textParams = params.filter((p) => !paramHasImage(p, `${block.id}.${p.id}`, imageSrcMap));

  const findVal = (predicate) => {
    const found = textParams.find((p) => predicate(p.name || ''));
    if (!found) {
      return '';
    }
    const key = `${block.id}.${found.id}`;
    return getParamExportCellText(found, key, paramValues, paramValues2);
  };

  const tkLine = findVal((name) => /шифр|тк[-\s]|код\s*тк/i.test(name))
    || findVal((name) => /^тк\b/i.test(name));
  const qualityVal = findVal((name) => /уровень\s+качеств/i.test(name)) || 'А';

  const usedForMeta = new Set();
  textParams.forEach((p) => {
    const n = p.name || '';
    if (/шифр|тк[-\s]|код\s*тк|^тк\b|уровень\s+качеств/i.test(n)) {
      usedForMeta.add(p.id);
    }
  });

  const rowParams = textParams.filter((p) => !usedForMeta.has(p.id));
  const title = escapeHtml(block.name || 'Технологическая карта');

  const dataRows = rowParams.map((p) => {
    const key = `${block.id}.${p.id}`;
    const val = getParamExportCellText(p, key, paramValues, paramValues2);
    return `
      <tr>
        <td class="off-b1-label">${escapeHtml(p.name || '')}</td>
        <td class="off-b1-value" colspan="2">${escapeHtml(val || '')}</td>
      </tr>`;
  }).join('');

  return `
    <table class="official-table official-b1" width="100%" border="1">
      <tr>
        <td class="off-b1-title" rowspan="3" width="70%">${title}</td>
        <td class="off-b1-meta-head" colspan="2" align="center" width="30%">ШИФР</td>
      </tr>
      <tr>
        <td class="off-b1-meta-val" colspan="2" align="center">${escapeHtml(tkLine || '')}</td>
      </tr>
      <tr>
        <td class="off-b1-meta-label" width="15%">УРОВЕНЬ КАЧЕСТВА</td>
        <td class="off-b1-meta-q" width="15%" align="center">${escapeHtml(qualityVal)}</td>
      </tr>
      ${dataRows}
    </table>`;
};

/**
 * Блок «Объект контроля» с subtitle: левая подпись только на группе «ОБЪЕКТ КОНТРОЛЯ»;
 * зона «Параметры сварного соединения» + «Требования…» — 3 колонки (имя | значение | схема);
 * при отсутствии section_header сверху группы подставляется строка с текстом subtitle.
 */
const buildOfficialBlock2GroupedHtml = (
  block,
  paramValues,
  imageSrcMap,
  paramValues2,
  params,
  imageParams,
  imageMetaMap = {},
) => {
  const blockId = block.id;
  const leftRows = [];
  for (const p of params) {
    if (paramHasImage(p, `${blockId}.${p.id}`, imageSrcMap)) {
      continue;
    }
    const subtitle = effectiveBlock2Subtitle(p);
    if (isSectionHeaderParam(p)) {
      leftRows.push({ kind: 'section', title: p.name || '', subtitle });
    } else {
      leftRows.push({ kind: 'kv', param: p, subtitle });
    }
  }

  const groups = [];
  for (const row of leftRows) {
    const last = groups[groups.length - 1];
    if (!last || last.subtitle !== row.subtitle) {
      groups.push({ subtitle: row.subtitle, rows: [row] });
    } else {
      last.rows.push(row);
    }
  }

  const diagramImageParam = imageParams.find(
    (p) => isBlock2DiagramZoneSubtitle(p.subtitle),
  ) || imageParams[0];
  const diagramKey = diagramImageParam ? `${blockId}.${diagramImageParam.id}` : '';
  const diagramSrc = diagramImageParam
    ? (imageSrcMap[diagramKey] || '')
    : '';
  const diagramSize = diagramKey ? imageMetaMap[diagramKey] : undefined;

  const countRowsInGroup = (g) => g.rows.length;

  const totalRows = groups.reduce((acc, g) => acc + countRowsInGroup(g), 0);

  const sideLabel = `${escapeHtml(String(block.id))}. ${escapeHtml((block.name || 'ОБЪЕКТ КОНТРОЛЯ').toUpperCase())}`;

  if (totalRows === 0 && !diagramSrc) {
    return `
      <table class="official-table" width="100%" border="1">
        <tr><td class="off-empty">Нет данных для экспорта в этом разделе.</td></tr>
      </table>`;
  }

  if (totalRows === 0 && diagramSrc) {
    return `
      <table class="official-table official-b2 official-b2-grouped" width="100%" border="1">
        <tr>
          <td class="off-b2-side">${sideLabel}</td>
          <td class="off-b2-diagram-spacer">&#160;</td>
          <td class="off-b2-diagram" align="center"${offB2DiagramTdAttrs()}>
            ${wordDiagramWrapB2(diagramSrc, diagramSize)}
          </td>
        </tr>
      </table>`;
  }

  const trs = [];

  let groupIndex = 0;
  while (groupIndex < groups.length) {
    const g = groups[groupIndex];

    if (isBlock2ObjectControlSubtitle(g.subtitle)) {
      const n = countRowsInGroup(g);
      const ocSide = `<td class="off-b2-side" rowspan="${n}">${sideLabel}</td>`;
      let first = true;
      for (const row of g.rows) {
        const sideCell = first ? ocSide : '';
        first = false;
        if (row.kind === 'section') {
          trs.push(`
        <tr>
          ${sideCell}
          <td class="off-b2-section off-b2-section-oc" colspan="2">${escapeHtml(row.title)}</td>
        </tr>`);
        } else {
          const p = row.param;
          const val = getParamExportCellText(
            p,
            `${blockId}.${p.id}`,
            paramValues,
            paramValues2,
          );
          trs.push(`
        <tr>
          ${sideCell}
          <td class="off-b2-name off-b2-name-oc">${escapeHtml(p.name || '')}</td>
          <td class="off-b2-val off-b2-val-oc" align="center">${escapeHtml(val || '')}</td>
        </tr>`);
        }
      }
      groupIndex += 1;
      continue;
    }

    if (isBlock2DiagramZoneSubtitle(g.subtitle)) {
      let end = groupIndex;
      while (
        end < groups.length
        && isBlock2DiagramZoneSubtitle(groups[end].subtitle)
      ) {
        end += 1;
      }
      const zoneGroups = groups.slice(groupIndex, end);

      const getDiagramZoneDisplayRows = (zg) => {
        const rows = zg.rows;
        if (rows.length === 0) {
          return rows;
        }
        if (rows[0].kind === 'section') {
          return rows;
        }
        if (zg.subtitle === '__default__') {
          return rows;
        }
        return [
          { kind: 'section', title: zg.subtitle, synthetic: true },
          ...rows,
        ];
      };

      const zoneRowCount = zoneGroups.reduce(
        (acc, zg) => acc + getDiagramZoneDisplayRows(zg).length,
        0,
      );

      const diagramTd = diagramSrc
        ? `<td class="off-b2-diagram" rowspan="${zoneRowCount}" align="center" valign="top"${offB2DiagramTdAttrs()}>
        ${wordDiagramWrapB2(diagramSrc, diagramSize)}
      </td>`
        : '';

      let firstPhysical = true;
      for (const zg of zoneGroups) {
        const displayRows = getDiagramZoneDisplayRows(zg);
        for (const row of displayRows) {
          if (diagramSrc) {
            if (row.kind === 'section') {
              trs.push(`
        <tr>
          <td class="off-b2-section off-b2-section-dz" colspan="2">${escapeHtml(row.title)}</td>
          ${firstPhysical ? diagramTd : ''}
        </tr>`);
            } else {
              const p = row.param;
              const key = `${blockId}.${p.id}`;
              const val = getParamExportCellText(p, key, paramValues, paramValues2);
              trs.push(`
        <tr>
          <td class="off-b2-name off-b2-name-dz">${escapeHtml(p.name || '')}</td>
          <td class="off-b2-val off-b2-val-dz" align="center">${escapeHtml(val || '')}</td>
          ${firstPhysical ? diagramTd : ''}
        </tr>`);
            }
          } else if (row.kind === 'section') {
            trs.push(`
        <tr>
          <td class="off-b2-section off-b2-section-full" colspan="3">${escapeHtml(row.title)}</td>
        </tr>`);
          } else {
            const p = row.param;
            const key = `${blockId}.${p.id}`;
            const val = getParamExportCellText(p, key, paramValues, paramValues2);
            trs.push(`
        <tr>
          <td class="off-b2-name off-b2-name-dz">${escapeHtml(p.name || '')}</td>
          <td class="off-b2-val off-b2-val-wide" align="center" colspan="2">${escapeHtml(val || '')}</td>
        </tr>`);
          }
          firstPhysical = false;
        }
      }
      groupIndex = end;
      continue;
    }

    for (const row of g.rows) {
      if (row.kind === 'section') {
        trs.push(`
        <tr>
          <td class="off-b2-section off-b2-section-full" colspan="3">${escapeHtml(row.title)}</td>
        </tr>`);
      } else {
        const p = row.param;
        const key = `${blockId}.${p.id}`;
        const val = getParamExportCellText(p, key, paramValues, paramValues2);
        trs.push(`
        <tr>
          <td class="off-b2-name off-b2-name-dz">${escapeHtml(p.name || '')}</td>
          <td class="off-b2-val off-b2-val-wide" align="center" colspan="2">${escapeHtml(val || '')}</td>
        </tr>`);
      }
    }
    groupIndex += 1;
  }

  return `
    <table class="official-table official-b2 official-b2-grouped" width="100%" border="1">
      ${trs.join('')}
    </table>`;
};

/**
 * Блок «Объект контроля»: без subtitle — схема справа на всю высоту текстовой части;
 * с subtitle — см. buildOfficialBlock2GroupedHtml.
 */
const buildOfficialBlock2Html = (block, paramValues, imageSrcMap, paramValues2 = {}, imageMetaMap = {}) => {
  const params = (block.params || []).filter((p) => !isOperationsRowParam(p));
  const imageParams = params.filter((p) => paramHasImage(p, `${block.id}.${p.id}`, imageSrcMap));
  const diagramKey = imageParams.length > 0 ? `${block.id}.${imageParams[0].id}` : '';
  const diagramSrc = imageParams.length > 0
    ? (imageSrcMap[diagramKey] || '')
    : '';
  const diagramSize = diagramKey ? imageMetaMap[diagramKey] : undefined;

  if (block2SubtitleModeEnabled(params)) {
    return buildOfficialBlock2GroupedHtml(
      block,
      paramValues,
      imageSrcMap,
      paramValues2,
      params,
      imageParams,
      imageMetaMap,
    );
  }

  const leftRows = [];
  for (const p of params) {
    if (paramHasImage(p, `${block.id}.${p.id}`, imageSrcMap)) {
      continue;
    }
    if (isSectionHeaderParam(p)) {
      leftRows.push({ kind: 'section', title: p.name || '' });
    } else {
      leftRows.push({ kind: 'kv', param: p });
    }
  }

  const sideLabel = `${escapeHtml(String(block.id))}. ${escapeHtml((block.name || 'ОБЪЕКТ КОНТРОЛЯ').toUpperCase())}`;
  const rowspanMain = Math.max(1, leftRows.length);

  if (leftRows.length === 0 && !diagramSrc) {
    return `
      <table class="official-table" width="100%" border="1">
        <tr><td class="off-empty">Нет данных для экспорта в этом разделе.</td></tr>
      </table>`;
  }

  if (leftRows.length === 0 && diagramSrc) {
    return `
      <table class="official-table official-b2 official-b2-grouped" width="100%" border="1">
        <tr>
          <td class="off-b2-side">${sideLabel}</td>
          <td class="off-b2-diagram-spacer">&#160;</td>
          <td class="off-b2-diagram" align="center"${offB2DiagramTdAttrs()}>
            ${wordDiagramWrapB2(diagramSrc, diagramSize)}
          </td>
        </tr>
      </table>`;
  }

  const diagramCell = diagramSrc
    ? `<td class="off-b2-diagram" rowspan="${rowspanMain}" align="center" valign="top"${offB2DiagramTdAttrs()}>
        ${wordDiagramWrapB2(diagramSrc, diagramSize)}
      </td>`
    : '';

  const body = leftRows.map((row, index) => {
    const isFirst = index === 0;
    const sideCell = isFirst
      ? `<td class="off-b2-side" rowspan="${rowspanMain}">${sideLabel}</td>`
      : '';

    if (row.kind === 'section') {
      return `
        <tr>
          ${sideCell}
          <td class="off-b2-section off-b2-section-4col" colspan="2">${escapeHtml(row.title)}</td>
          ${isFirst ? diagramCell : ''}
        </tr>`;
    }

    const p = row.param;
    const key = `${block.id}.${p.id}`;
    const val = getParamExportCellText(p, key, paramValues, paramValues2);
    return `
      <tr>
        ${sideCell}
        <td class="off-b2-name">${escapeHtml(p.name || '')}</td>
        <td class="off-b2-val" align="center">${escapeHtml(val || '')}</td>
        ${isFirst ? diagramCell : ''}
      </tr>`;
  }).join('');

  return `
    <table class="official-table official-b2" width="100%" border="1">
      <colgroup>
        <col style="width:${OFF_B2_SIDE_COL_PCT}%;" />
        <col style="width:${OFF_B2_NAME_4COL_PCT}%;" />
        <col style="width:${OFF_B2_VAL_4COL_PCT}%;" />
        <col style="width:${OFF_B2_DIAGRAM_COL_PCT}%;" />
      </colgroup>
      ${body}
    </table>`;
};

const BLOCK3_FOOTNOTE = (
  '* Допускается использовать усиливающие экраны, поставляемые в одной упаковке с пленкой.'
);

const buildOfficialBlock3Html = (block, paramValues, imageSrcMap, paramValues2 = {}, imageMetaMap = {}) => {
  const params = (block.params || []).filter((p) => !isOperationsRowParam(p));
  const imageParams = params.filter((p) => paramHasImage(p, `${block.id}.${p.id}`, imageSrcMap));
  const textParams = params.filter((p) => !paramHasImage(p, `${block.id}.${p.id}`, imageSrcMap));

  const diagramParts = imageParams.map((p) => {
    const key = `${block.id}.${p.id}`;
    const src = imageSrcMap[key] || '';
    if (!src) {
      return '';
    }
    const caption = p.name || 'Схема';
    return wordDiagramWrapB3(src, caption, imageMetaMap[key]);
  }).join('');

  const diagramBody = diagramParts || '&#160;';

  const diagramCell = `
    <td class="off-b3-diagram" rowspan="__ROWSPAN__" align="center" valign="top"${offB3DiagramTdAttrs()}>
      ${diagramBody}
    </td>`;

  const nDataRows = Math.max(textParams.length, 1);
  const diagramRowspan = 1 + nDataRows;

  const titleRow = `
    <tr>
      <td colspan="3" class="off-b3-banner" align="center">
        <b>${escapeHtml(String(block.id))}. ${escapeHtml((block.name || '').toUpperCase())}</b>
      </td>
    </tr>`;

  const subHeadRow = `
    <tr>
      <td colspan="2" class="off-b3-subhead" align="center"><b>ПАРАМЕТРЫ КОНТРОЛЯ</b></td>
      ${diagramCell.replace('__ROWSPAN__', String(diagramRowspan))}
    </tr>`;

  const dataRows = textParams.length > 0
    ? textParams.map((p) => {
      const key = `${block.id}.${p.id}`;
      const val = getParamExportCellText(p, key, paramValues, paramValues2);
      return `
        <tr>
          <td class="off-b3-pname">${escapeHtml(p.name || '')}</td>
          <td class="off-b3-pval" align="center">${escapeHtml(val || '')}</td>
        </tr>`;
    }).join('')
    : `
      <tr>
        <td class="off-b3-pname">&#160;</td>
        <td class="off-b3-pval" align="center">&#160;</td>
      </tr>`;

  const footnoteRow = `
    <tr>
      <td colspan="3" class="off-b3-footnote">${escapeHtml(BLOCK3_FOOTNOTE)}</td>
    </tr>`;

  return `
    <table class="official-table official-b3" width="100%" border="1">
      <colgroup>
        <col style="width:${OFF_B3_PNAME_PCT}%;" />
        <col style="width:${OFF_B3_PVAL_PCT}%;" />
        <col style="width:${OFF_B3_DIAGRAM_COL_PCT}%;" />
      </colgroup>
      ${titleRow}
      ${subHeadRow}
      ${dataRows}
      ${footnoteRow}
    </table>`;
};

const buildParamRowHtml = (blockId, param, paramValues, imageSrcMap, paramValues2 = {}, options = {}) => {
  const { operationsGost = false, imageMetaMap = {} } = options;
  const compositeKey = `${blockId}.${param.id}`;
  const paramNumber = `${blockId}.${param.id}`;
  const imageSrc = imageSrcMap[compositeKey] || '';

  if (isOperationsLikeParam(param)) {
    const value = getOperationsValueObject(param);
    const rawContent = typeof value.content === 'string'
      ? value.content
      : normalizeValueText(value.content);
    const rawEquipment = typeof value.equipment === 'string'
      ? value.equipment.trim()
      : normalizeValueText(value.equipment);

    const contentProcessed = applyOperationPlaceholders(
      rawContent,
      param,
      compositeKey,
      paramValues,
      paramValues2,
    );
    const equipmentProcessed = applyOperationPlaceholders(
      rawEquipment,
      param,
      compositeKey,
      paramValues,
      paramValues2,
    );
    const fullContent = resolveOperationFullContent(value, contentProcessed);
    const nameHtml = buildOperationsNameCellHtml(param, { id: blockId });

    if (operationsGost) {
      return `
      <tr class="ops-gost-row">
        <td class="ops-gost-name"><b>${nameHtml}</b></td>
        <td class="ops-gost-content">${formatOpsCellHtml(fullContent)}</td>
        <td class="ops-gost-equipment">${formatOpsCellHtml(equipmentProcessed)}</td>
      </tr>`;
    }

    const punctHtml = escapeHtml(paramNumber);
    let valueHtml = formatOpsCellHtml(fullContent);
    const eqTrim = equipmentProcessed.trim();
    if (valueHtml === '–' && eqTrim) {
      valueHtml = formatOpsCellHtml(equipmentProcessed);
    } else if (eqTrim && eqTrim !== '–') {
      valueHtml = `${valueHtml}<br/><br/><b>Оборудование и инструмент:</b><br/>${formatOpsCellHtml(equipmentProcessed)}`;
    }

    return `
      <tr class="param-operation-row">
        <td class="cell-number"><b>${punctHtml}</b></td>
        <td class="cell-name"><b>${nameHtml}</b></td>
        <td class="cell-value">${valueHtml}</td>
      </tr>`;
  }

  if (param.displayMode === DISPLAY_MODE_SECTION_HEADER) {
    return `
      <tr class="section-row">
        <td colspan="3">${escapeHtml(param.name || '')}</td>
      </tr>
    `;
  }

  if (imageSrc) {
    const isFullImage = param.displayMode === DISPLAY_MODE_IMAGE_FULL;
    const caption = escapeHtml(param.name || paramNumber);

    if (isFullImage) {
      return `
        <tr class="image-row image-row-full">
          <td colspan="3">
            <div class="image-wrapper image-wrapper-full">
              ${wordImgWithMeta(imageSrc, param.name || paramNumber, WORD_IMG_TABLE_CELL_FULL, imageMetaMap[compositeKey])}
            </div>
          </td>
        </tr>
      `;
    }

    if (operationsGost) {
      return `
      <tr class="image-row">
        <td colspan="3">
          <div class="image-wrapper">
            <div class="image-caption">${caption}</div>
            ${wordImgWithMeta(imageSrc, param.name || paramNumber, WORD_IMG_TABLE_CELL, imageMetaMap[compositeKey])}
          </div>
        </td>
      </tr>`;
    }

    return `
      <tr class="image-row">
        <td class="cell-number">${escapeHtml(paramNumber)}</td>
        <td colspan="2">
          <div class="image-wrapper">
            <div class="image-caption">${caption}</div>
            ${wordImgWithMeta(imageSrc, param.name || paramNumber, WORD_IMG_TABLE_CELL, imageMetaMap[compositeKey])}
          </div>
        </td>
      </tr>
    `;
  }

  const textValue = getParamExportCellText(param, compositeKey, paramValues, paramValues2);
  if (!textValue) {
    return '';
  }

  if (operationsGost) {
    if (param.displayMode === DISPLAY_MODE_NUMBER_ONLY) {
      return `
      <tr class="row-number-only">
        <td class="ops-gost-name">${escapeHtml(paramNumber)}</td>
        <td class="ops-gost-content">${escapeHtml(textValue)}</td>
        <td class="ops-gost-equipment">–</td>
      </tr>`;
    }
    return `
    <tr>
      <td class="ops-gost-name">${escapeHtml(param.name || paramNumber)}</td>
      <td class="ops-gost-content">${escapeHtml(textValue)}</td>
      <td class="ops-gost-equipment">–</td>
    </tr>`;
  }

  if (param.displayMode === DISPLAY_MODE_NUMBER_ONLY) {
    return `
      <tr class="row-number-only">
        <td class="cell-number">${escapeHtml(paramNumber)}</td>
        <td colspan="2" class="cell-value cell-value-wide">${escapeHtml(textValue)}</td>
      </tr>
    `;
  }

  return `
    <tr>
      <td class="cell-number">${escapeHtml(paramNumber)}</td>
      <td class="cell-name">${escapeHtml(param.name || '')}</td>
      <td class="cell-value">${escapeHtml(textValue)}</td>
    </tr>
  `;
};

const getOperationsValueObject = (param) => {
  const v = param?.value;
  if (v && typeof v === 'object' && !Array.isArray(v)) {
    return v;
  }
  if (param?.hasVal2) {
    const contentStr = v != null && typeof v !== 'object'
      ? String(v)
      : normalizeValueText(v);
    const eq = param.value2 != null ? String(param.value2).trim() : '';
    const primary = v != null && typeof v !== 'object' ? String(v) : String(v ?? '');
    return {
      content: contentStr,
      equipment: eq,
      val: primary,
      val2: param.value2 != null ? String(param.value2) : '',
    };
  }
  return {};
};

/**
 * Полный текст колонки «Содержание»: одна ячейка (подпункты 3.1.1, 3.1.2 … через переносы).
 * При наличии value.steps — склеиваем в один блок.
 */
const resolveOperationFullContent = (value, contentAfterPlaceholders) => {
  if (Array.isArray(value.steps) && value.steps.length > 0) {
    const mapped = value.steps.map((item) => {
      if (typeof item === 'string') {
        return item;
      }
      if (item && typeof item === 'object') {
        return String(item.content ?? item.text ?? '');
      }
      return '';
    }).filter((s) => String(s).trim() !== '');
    if (mapped.length > 0) {
      return mapped.join('\n');
    }
  }
  return String(contentAfterPlaceholders ?? '').replace(/\r\n/g, '\n').trim();
};

/** Номер операции (3.1) и наименование — в одной ячейке первой колонки; подпункты 3.1.1 только в «Содержании». */
const buildOperationsNameCellHtml = (param, block) => {
  const name = (param.name || '').trim();
  const autoPrefix = `${block.id}.${param.id}`;
  if (!name) {
    return escapeHtml(autoPrefix);
  }
  if (/^\s*\d+(?:\.\d+)+\s/.test(name)) {
    return escapeHtml(name);
  }
  return escapeHtml(`${autoPrefix} ${name}`.trim());
};

const applyOperationPlaceholders = (text, param, compositeKey, paramValues, paramValues2 = {}) => {
  let s = String(text ?? '');
  let v1 = '';
  let v2 = '';
  if (isOperationsLikeParam(param)) {
    const ov = getOperationsValueObject(param);
    if (Object.prototype.hasOwnProperty.call(paramValues, compositeKey)) {
      v1 = String(paramValues[compositeKey] ?? '').trim();
    } else if (ov.val !== undefined && ov.val !== null) {
      v1 = String(ov.val).trim();
    }
    if (Object.prototype.hasOwnProperty.call(paramValues2, compositeKey)) {
      v2 = String(paramValues2[compositeKey] ?? '').trim();
    } else if (ov.val2 !== undefined && ov.val2 !== null) {
      v2 = String(ov.val2).trim();
    }
  } else {
    v1 = getParamTextValue(param, compositeKey, paramValues);
    v2 = getParamText2Value(param, compositeKey, paramValues2);
  }
  s = s.replace(/\{\{val2\}\}/g, v2).replace(/\{\{val\}\}/g, v1);
  s = s.replace(/\{val2\}/g, v2).replace(/\{val\}/g, v1);
  return s;
};

const formatOpsCellHtml = (text) => {
  const s = String(text ?? '').trim();
  if (!s) {
    return '–';
  }
  return escapeHtml(s).replace(/\n/g, '<br/>');
};

const buildCustomRowsHtml = (fields = [], options = {}) => {
  const { operationsGost = false } = options;
  const normalizedFields = Array.isArray(fields)
    ? fields.filter((field) => field && ((field.name || '').trim() || (field.value || '').trim()))
    : [];

  if (normalizedFields.length === 0) {
    return '';
  }

  const rows = normalizedFields.map((field) => (operationsGost
    ? `
    <tr class="custom-row">
      <td class="ops-gost-name">${escapeHtml(field.name || 'Дополнительное поле')}</td>
      <td class="ops-gost-content">${escapeHtml(field.value || '')}</td>
      <td class="ops-gost-equipment">&#160;</td>
    </tr>`
    : `
    <tr class="custom-row">
      <td class="cell-number"></td>
      <td class="cell-name">${escapeHtml(field.name || 'Дополнительное поле')}</td>
      <td class="cell-value">${escapeHtml(field.value || '')}</td>
    </tr>
  `)).join('');

  return `
    <tr class="section-row">
      <td colspan="3">Дополнительные поля</td>
    </tr>
    ${rows}
  `;
};

const buildUploadedImagesHtml = (images = []) => {
  const normalizedImages = Array.isArray(images)
    ? images.filter((image) => image && (image.exportSrc || image.preview))
    : [];

  if (normalizedImages.length === 0) {
    return '';
  }

  const cards = normalizedImages.map((image) => {
    const meta = image.exportW != null && image.exportH != null
      ? { w: image.exportW, h: image.exportH }
      : undefined;
    return `
    <figure class="extra-image-card">
      ${wordImgWithMeta(image.exportSrc || resolveImageSrc(image.preview), image.name || 'Изображение', WORD_IMG_EXTRA, meta)}
      <figcaption>${escapeHtml(image.name || 'Изображение')}</figcaption>
    </figure>`;
  }).join('');

  return `
    <div class="extra-images-section">
      <div class="extra-images-title">Дополнительные изображения</div>
      <div class="extra-images-grid">
        ${cards}
      </div>
    </div>
  `;
};

const buildGenericBlockHtml = (block, paramValues, customFields, uploadedImages, imageSrcMap, paramValues2 = {}, imageMetaMap = {}) => {
  const operationsGost = isOperationsRcBlock(block);
  const rowOptions = { operationsGost, imageMetaMap };
  const paramRows = (block.params || [])
    .map((param) => buildParamRowHtml(block.id, param, paramValues, imageSrcMap, paramValues2, rowOptions))
    .filter(Boolean)
    .join('');
  const customRows = buildCustomRowsHtml(customFields[block.id] || [], rowOptions);
  const imagesSection = buildUploadedImagesHtml(uploadedImages[block.id] || []);

  const tableHtml = (paramRows || customRows)
    ? (operationsGost
      ? `
      <table class="block-table block-table-ops-gost" width="100%" border="1">
        <thead>
          <tr>
            <th class="ops-gost-name">Наименование<br/>операции</th>
            <th class="ops-gost-content">Содержание операции, основные требования</th>
            <th class="ops-gost-equipment">Оборудование и инструмент</th>
          </tr>
        </thead>
        <tbody>
          ${paramRows}
          ${customRows}
        </tbody>
      </table>
    `
      : `
      <table class="block-table">
        <thead>
          <tr>
            <th class="col-number">Пункт</th>
            <th class="col-name">Наименование</th>
            <th class="col-value">Значение</th>
          </tr>
        </thead>
        <tbody>
          ${paramRows}
          ${customRows}
        </tbody>
      </table>
    `)
    : '';

  const hasAnyContent = Boolean(tableHtml || imagesSection);

  return `
    <section class="techcard-block">
      <h2 class="block-title">${escapeHtml(`${block.id}. ${block.name}`)}</h2>
      ${hasAnyContent ? `
        ${tableHtml}
        ${imagesSection}
      ` : `
        <div class="empty-block">Нет заполненных данных.</div>
      `}
    </section>
  `;
};

const buildBlockExportSection = (block, paramValues, customFields, uploadedImages, imageSrcMap, paramValues2 = {}, imageMetaMap = {}) => {
  const id = normalizeBlockId(block);
  if (id === '1') {
    return `<section class="techcard-block techcard-official">${buildOfficialBlock1Html(block, paramValues, imageSrcMap, paramValues2)}</section>`;
  }
  if (id === '2') {
    return `<section class="techcard-block techcard-official">${buildOfficialBlock2Html(block, paramValues, imageSrcMap, paramValues2, imageMetaMap)}</section>`;
  }
  if (id === '3') {
    return `<section class="techcard-block techcard-official">${buildOfficialBlock3Html(block, paramValues, imageSrcMap, paramValues2, imageMetaMap)}</section>`;
  }
  return buildGenericBlockHtml(block, paramValues, customFields, uploadedImages, imageSrcMap, paramValues2, imageMetaMap);
};

const buildWordHtml = ({
  methodologyName,
  objectName,
  elementName,
  blocks,
  paramValues,
  paramValues2 = {},
  customFields,
  uploadedImages,
  imageSrcMap,
  imageMetaMap = {},
  title,
}) => {
  const metadataRows = [
    methodologyName ? `<div><span>Методика:</span> ${escapeHtml(methodologyName)}</div>` : '',
    objectName ? `<div><span>Объект контроля:</span> ${escapeHtml(objectName)}</div>` : '',
    elementName ? `<div><span>Элемент контроля:</span> ${escapeHtml(elementName)}</div>` : '',
    `<div><span>Дата экспорта:</span> ${escapeHtml(new Date().toLocaleString('ru-RU'))}</div>`,
  ].filter(Boolean).join('');

  const blocksHtml = blocks
    .map((block) => buildBlockExportSection(block, paramValues, customFields, uploadedImages, imageSrcMap, paramValues2, imageMetaMap))
    .join('');
  const documentTitle = escapeHtml(title || 'Технологическая карта');

  return `<!doctype html>
  <html lang="ru" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40">
    <head>
      <meta charset="utf-8" />
      <title>${documentTitle}</title>
      <!--[if gte mso 9]>
      <xml>
        <w:WordDocument>
          <w:View>Print</w:View>
          <w:Zoom>100</w:Zoom>
          <w:DoNotOptimizeForBrowser/>
        </w:WordDocument>
      </xml>
      <![endif]-->
      <style>
        /* Альбомная ориентация A4 для Word (HTML → .doc) */
        @page WordSection1 {
          size: 297mm 210mm;
          mso-page-orientation: landscape;
        }
        div.WordSection1 {
          page: WordSection1;
          mso-page-orientation: landscape;
        }
        * { box-sizing: border-box; }
        html, body {
          margin: 0;
          padding: 0;
          background: #ffffff;
          color: #000000;
          font-family: "Times New Roman", Times, serif;
          font-size: 11pt;
          line-height: 1.25;
        }
        body { padding: 8mm 10mm; }
        .page { width: 100%; max-width: 277mm; margin: 0 auto; }
        .document-title {
          margin: 0 0 4mm;
          font-size: 14pt;
          text-align: center;
        }
        .document-meta {
          margin-bottom: 5mm;
          padding-bottom: 3mm;
          border-bottom: 1px solid #000000;
          font-size: 10pt;
        }
        .document-meta span { font-weight: 700; }
        .techcard-block { margin-bottom: 6mm; page-break-inside: avoid; }
        .block-title {
          margin: 0 0 2mm;
          font-size: 12pt;
        }
        .official-table {
          width: 100%;
          border-collapse: collapse;
          table-layout: fixed;
          mso-table-layout-alt: fixed;
        }
        .official-table td, .official-table th {
          border: 1px solid #000000;
          padding: 3pt 4pt;
          vertical-align: middle;
        }
        .off-b1-title {
          font-weight: bold;
          font-size: 11pt;
          text-align: center;
          vertical-align: middle;
          line-height: 1.2;
        }
        .off-b1-label { font-weight: 600; width: 38%; vertical-align: top; }
        .off-b1-value { vertical-align: top; }
        .off-b1-meta-head, .off-b1-meta-val, .off-b1-meta-label, .off-b1-meta-q {
          font-size: 10pt;
        }
        .off-b2-side {
          font-weight: bold;
          text-align: center;
          vertical-align: middle;
          width: ${OFF_B2_SIDE_COL_PCT}%;
          max-width: ${OFF_B2_SIDE_COL_PCT}%;
          font-size: 9pt;
          line-height: 1.15;
        }
        .off-b2-name { width: ${OFF_B2_NAME_4COL_PCT}%; vertical-align: top; word-wrap: break-word; }
        .off-b2-val { width: ${OFF_B2_VAL_4COL_PCT}%; vertical-align: top; word-wrap: break-word; }
        .official-b2-grouped .off-b2-name-oc { width: ${OFF_B2_NAME_OC_PCT}%; max-width: ${OFF_B2_NAME_OC_PCT}%; }
        .official-b2-grouped .off-b2-val-oc { width: ${OFF_B2_VAL_OC_PCT}%; max-width: ${OFF_B2_VAL_OC_PCT}%; }
        .official-b2-grouped .off-b2-name-dz { width: ${OFF_B2_NAME_DZ_PCT}%; max-width: ${OFF_B2_NAME_DZ_PCT}%; }
        .official-b2-grouped .off-b2-val-dz { width: ${OFF_B2_VAL_DZ_PCT}%; max-width: ${OFF_B2_VAL_DZ_PCT}%; }
        .off-b2-diagram-spacer {
          width: ${OFF_B2_DIAGRAM_SPACER_PCT}%;
          max-width: ${OFF_B2_DIAGRAM_SPACER_PCT}%;
          vertical-align: top;
          padding: 2pt;
        }
        .off-b2-diagram {
          width: ${OFF_B2_DIAGRAM_COL_PCT}%;
          max-width: ${OFF_B2_DIAGRAM_COL_PCT}%;
          vertical-align: top;
          padding: 4pt;
          overflow: hidden;
          word-wrap: break-word;
        }
        .off-b2-section {
          font-weight: bold;
          text-align: center;
          background: #f0f0f0;
        }
        .official-b2-grouped .off-b2-section-oc { width: 88%; max-width: 88%; }
        .official-b2-grouped .off-b2-section-dz { width: 60%; max-width: 60%; }
        .official-b2-grouped .off-b2-section-full { width: 100%; max-width: 100%; }
        .official-b2:not(.official-b2-grouped) .off-b2-section-4col { width: 48%; max-width: 48%; }
        .official-b2-grouped .off-b2-val-wide { width: 65%; max-width: 65%; }
        .off-b3-banner { font-size: 11pt; padding: 4pt; }
        .off-b3-subhead { padding: 3pt; background: #f0f0f0; }
        .off-b3-pname { width: ${OFF_B3_PNAME_PCT}%; vertical-align: top; word-wrap: break-word; }
        .off-b3-pval { width: ${OFF_B3_PVAL_PCT}%; vertical-align: top; word-wrap: break-word; }
        .off-b3-diagram {
          width: ${OFF_B3_DIAGRAM_COL_PCT}%;
          max-width: ${OFF_B3_DIAGRAM_COL_PCT}%;
          vertical-align: top;
          padding: 4pt;
          overflow: hidden;
          word-wrap: break-word;
        }
        .off-b3-footnote { font-size: 9pt; vertical-align: top; padding: 4pt; }
        .off-diagram-wrap {
          text-align: center;
          overflow: hidden;
          max-width: 100%;
          box-sizing: border-box;
          line-height: 0;
          border: 2.5pt solid ${IMAGE_FRAME_COLOR};
          border-radius: 10pt;
          padding: 2pt;
        }
        .off-diagram-wrap img {
          display: block;
          margin: 0 auto;
          width: 100%;
          max-width: 100%;
          height: auto;
          max-height: 68mm;
          object-fit: contain;
        }
        .off-b3-img img { max-height: 68mm; }
        .off-empty { padding: 6pt; color: #444; font-style: italic; }
        .block-table {
          width: 100%;
          border-collapse: collapse;
          table-layout: fixed;
        }
        .block-table th, .block-table td {
          border: 1px solid #000000;
          padding: 3mm 3.2mm;
          vertical-align: top;
        }
        .block-table th {
          background: #f2f2f2;
          font-size: 10pt;
          text-align: left;
        }
        .col-number { width: 18%; }
        .col-name { width: 30%; }
        .col-value { width: 52%; }
        .block-table-ops-gost thead th {
          text-align: center;
          vertical-align: middle;
          font-size: 10pt;
        }
        .block-table-ops-gost td {
          vertical-align: top;
        }
        .ops-gost-name {
          width: 24%;
          vertical-align: top;
          word-wrap: break-word;
        }
        .ops-gost-content {
          width: 50%;
          vertical-align: top;
          word-wrap: break-word;
        }
        .ops-gost-equipment {
          width: 26%;
          vertical-align: top;
          word-wrap: break-word;
        }
        .cell-number { font-weight: 700; white-space: nowrap; }
        .cell-name { font-weight: 600; }
        .cell-value, .cell-value-wide {
          white-space: pre-wrap;
          word-break: break-word;
        }
        .section-row td {
          background: #f8f8f8;
          font-weight: 700;
        }
        .image-row td { padding: 4mm; overflow: hidden; max-width: 100%; }
        .image-wrapper {
          text-align: center;
          overflow: hidden;
          max-width: 100%;
          box-sizing: border-box;
          border: 2.5pt solid ${IMAGE_FRAME_COLOR};
          border-radius: 10pt;
          padding: 1.2mm;
        }
        .image-caption { margin-bottom: 2mm; font-weight: 600; }
        .image-wrapper img {
          display: block;
          margin: 0 auto;
          width: 100%;
          max-width: 100%;
          height: auto;
          max-height: 95mm;
          object-fit: contain;
        }
        .image-wrapper-full img { max-height: 130mm; }
        .extra-images-section { margin-top: 4mm; }
        .extra-images-title { margin-bottom: 2mm; font-weight: 700; }
        .extra-images-grid {
          display: table;
          width: 100%;
        }
        .extra-image-card {
          display: inline-block;
          width: 48%;
          margin: 1%;
          vertical-align: top;
          border: 2.5pt solid ${IMAGE_FRAME_COLOR};
          border-radius: 10pt;
          padding: 3mm;
          page-break-inside: avoid;
        }
        .extra-image-card img {
          display: block;
          width: 100%;
          max-height: 60mm;
          object-fit: contain;
        }
        .extra-image-card figcaption {
          margin-top: 2mm;
          font-size: 10pt;
          word-break: break-word;
        }
        .empty-block {
          padding: 4mm;
          border: 1px dashed #000;
          color: #444;
          font-style: italic;
        }
        .export-note {
          margin-top: 6mm;
          color: #444;
          font-size: 9pt;
        }
      </style>
    </head>
    <body>
      <div class="WordSection1">
        <main class="page">
          <h1 class="document-title">${documentTitle}</h1>
          <section class="document-meta">
            ${metadataRows}
          </section>
          ${blocksHtml}
          <div class="export-note">Документ сформирован из текущего состояния техкарты.</div>
        </main>
      </div>
    </body>
  </html>`;
};

const slugify = (value) => String(value || '')
  .trim()
  .toLowerCase()
  .replace(/\s+/g, '-')
  .replace(/[^a-z0-9а-яё_-]+/gi, '')
  .replace(/^-+|-+$/g, '');

const buildExportFileName = ({ title, methodologyName, objectName, elementName }) => {
  const parts = [title, methodologyName, objectName, elementName]
    .map(slugify)
    .filter(Boolean)
    .slice(0, 4);

  return `${parts.length > 0 ? parts.join('-') : 'tech-card'}.doc`;
};

const downloadBlob = (blob, fileName) => {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};

export const exportTechCardToWord = async ({
  methodologyName = '',
  objectName = '',
  elementName = '',
  blocks = [],
  paramValues = {},
  paramValues2 = {},
  customFields = {},
  uploadedImages = {},
  title = 'Технологическая карта',
}) => {
  const { blockImages, blockImageMeta, extraImages } = await prepareExportImages(blocks, uploadedImages);

  const html = buildWordHtml({
    methodologyName,
    objectName,
    elementName,
    blocks,
    paramValues,
    paramValues2,
    customFields,
    uploadedImages: extraImages,
    imageSrcMap: blockImages,
    imageMetaMap: blockImageMeta,
    title,
  });

  const blob = new Blob(['\ufeff', html], {
    type: 'application/msword;charset=utf-8',
  });

  downloadBlob(blob, buildExportFileName({
    title,
    methodologyName,
    objectName,
    elementName,
  }));
};
