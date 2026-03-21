const DISPLAY_MODE_NUMBER_ONLY = 'number_only';
const DISPLAY_MODE_IMAGE_FULL = 'image_full';
const DISPLAY_MODE_SECTION_HEADER = 'section_header';
const DISPLAY_MODE_OPERATIONS_ROW = 'operations_row';

const escapeHtml = (value = '') => String(value)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;');

const resolveImageSrc = (imageSrc) => {
  if (!imageSrc) {
    return '';
  }

  const normalizedSrc = String(imageSrc).trim();

  if (
    normalizedSrc.startsWith('data:') ||
    normalizedSrc.startsWith('http://') ||
    normalizedSrc.startsWith('https://') ||
    normalizedSrc.startsWith('blob:')
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

const prepareExportImages = async (blocks, uploadedImages) => {
  const cache = new Map();
  const blockImages = {};
  const extraImages = {};

  for (const block of blocks) {
    for (const param of block.params || []) {
      const compositeKey = `${block.id}.${param.id}`;
      const imageSrc = getParamImageSrc(param);
      if (!imageSrc) {
        continue;
      }

      blockImages[compositeKey] = await embedImageSource(imageSrc, cache);
    }
  }

  for (const [blockId, images] of Object.entries(uploadedImages || {})) {
    if (!Array.isArray(images) || images.length === 0) {
      continue;
    }

    extraImages[blockId] = await Promise.all(
      images
        .filter((image) => image && image.preview)
        .map(async (image) => ({
          ...image,
          exportSrc: await embedImageSource(image.preview, cache),
        }))
    );
  }

  return {
    blockImages,
    extraImages,
  };
};

const buildParamRowHtml = (blockId, param, paramValues, imageSrcMap) => {
  const compositeKey = `${blockId}.${param.id}`;
  const paramNumber = `${blockId}.${param.id}`;
  const imageSrc = imageSrcMap[compositeKey] || '';

  if (param.displayMode === DISPLAY_MODE_OPERATIONS_ROW) {
    return '';
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
              <img src="${imageSrc}" alt="${caption}" />
            </div>
          </td>
        </tr>
      `;
    }

    return `
      <tr class="image-row">
        <td class="cell-number">${escapeHtml(paramNumber)}</td>
        <td colspan="2">
          <div class="image-wrapper">
            <div class="image-caption">${caption}</div>
            <img src="${imageSrc}" alt="${caption}" />
          </div>
        </td>
      </tr>
    `;
  }

  const textValue = getParamTextValue(param, compositeKey, paramValues);
  if (!textValue) {
    return '';
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

const buildCustomRowsHtml = (fields = []) => {
  const normalizedFields = Array.isArray(fields)
    ? fields.filter((field) => field && ((field.name || '').trim() || (field.value || '').trim()))
    : [];

  if (normalizedFields.length === 0) {
    return '';
  }

  const rows = normalizedFields.map((field) => `
    <tr class="custom-row">
      <td class="cell-number"></td>
      <td class="cell-name">${escapeHtml(field.name || 'Дополнительное поле')}</td>
      <td class="cell-value">${escapeHtml(field.value || '')}</td>
    </tr>
  `).join('');

  return `
    <tr class="section-row">
      <td colspan="3">Дополнительные поля</td>
    </tr>
    ${rows}
  `;
};

const buildOperationsTableHtml = (params = []) => {
  const operationRows = Array.isArray(params)
    ? params.filter(isOperationsRowParam)
    : [];

  if (operationRows.length === 0) {
    return '';
  }

  const rowsHtml = operationRows.map((param) => {
    const value = (param?.value && typeof param.value === 'object' && !Array.isArray(param.value))
      ? param.value
      : {};

    const content = normalizeValueText(value.content) || '-';
    const equipment = normalizeValueText(value.equipment) || '-';

    return `
      <tr>
        <td class="cell-name">${escapeHtml(param.name || '')}</td>
        <td class="cell-value">${escapeHtml(content)}</td>
        <td class="cell-value">${escapeHtml(equipment)}</td>
      </tr>
    `;
  }).join('');

  return `
    <table class="block-table operations-table">
      <thead>
        <tr>
          <th class="operations-col-name">Наименование операции</th>
          <th class="operations-col-content">Содержание операции, основные требования</th>
          <th class="operations-col-equipment">Оборудование и инструмент</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHtml}
      </tbody>
    </table>
  `;
};

const buildUploadedImagesHtml = (images = []) => {
  const normalizedImages = Array.isArray(images)
    ? images.filter((image) => image && (image.exportSrc || image.preview))
    : [];

  if (normalizedImages.length === 0) {
    return '';
  }

  const cards = normalizedImages.map((image) => `
    <figure class="extra-image-card">
      <img src="${image.exportSrc || resolveImageSrc(image.preview)}" alt="${escapeHtml(image.name || 'Изображение')}" />
      <figcaption>${escapeHtml(image.name || 'Изображение')}</figcaption>
    </figure>
  `).join('');

  return `
    <div class="extra-images-section">
      <div class="extra-images-title">Дополнительные изображения</div>
      <div class="extra-images-grid">
        ${cards}
      </div>
    </div>
  `;
};

const buildBlockHtml = (block, paramValues, customFields, uploadedImages, imageSrcMap) => {
  const regularParams = (block.params || []).filter((param) => !isOperationsRowParam(param));
  const paramRows = regularParams
    .map((param) => buildParamRowHtml(block.id, param, paramValues, imageSrcMap))
    .filter(Boolean)
    .join('');
  const operationsTableHtml = buildOperationsTableHtml(block.params);
  const customRows = buildCustomRowsHtml(customFields[block.id] || []);
  const imagesSection = buildUploadedImagesHtml(uploadedImages[block.id] || []);

  const tableHtml = (paramRows || customRows)
    ? `
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
    `
    : '';

  const hasAnyContent = Boolean(tableHtml || operationsTableHtml || imagesSection);

  return `
    <section class="techcard-block">
      <h2 class="block-title">${escapeHtml(`${block.id}. ${block.name}`)}</h2>
      ${hasAnyContent ? `
        ${tableHtml}
        ${operationsTableHtml}
        ${imagesSection}
      ` : `
        <div class="empty-block">Нет заполненных данных.</div>
      `}
    </section>
  `;
};

const buildWordHtml = ({
  methodologyName,
  objectName,
  elementName,
  blocks,
  paramValues,
  customFields,
  uploadedImages,
  imageSrcMap,
  title,
}) => {
  const metadataRows = [
    methodologyName ? `<div><span>Методика:</span> ${escapeHtml(methodologyName)}</div>` : '',
    objectName ? `<div><span>Объект контроля:</span> ${escapeHtml(objectName)}</div>` : '',
    elementName ? `<div><span>Элемент контроля:</span> ${escapeHtml(elementName)}</div>` : '',
    `<div><span>Дата экспорта:</span> ${escapeHtml(new Date().toLocaleString('ru-RU'))}</div>`,
  ].filter(Boolean).join('');

  const blocksHtml = blocks
    .map((block) => buildBlockHtml(block, paramValues, customFields, uploadedImages, imageSrcMap))
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
        * {
          box-sizing: border-box;
        }

        html, body {
          margin: 0;
          padding: 0;
          background: #ffffff;
          color: #202020;
          font-family: "Times New Roman", Georgia, serif;
          font-size: 12pt;
          line-height: 1.35;
        }

        body {
          padding: 10mm 0;
        }

        .page {
          width: 182mm;
          margin: 0 auto;
        }

        .document-title {
          margin: 0 0 6mm;
          font-size: 18pt;
          line-height: 1.2;
        }

        .document-meta {
          display: grid;
          gap: 2mm;
          margin-bottom: 7mm;
          padding-bottom: 4mm;
          border-bottom: 1px solid #7b7b7b;
          font-size: 10.5pt;
        }

        .document-meta span {
          font-weight: 700;
        }

        .techcard-block {
          margin-bottom: 8mm;
          page-break-inside: avoid;
        }

        .block-title {
          margin: 0 0 3mm;
          font-size: 13.5pt;
          line-height: 1.25;
        }

        .block-table {
          width: 100%;
          border-collapse: collapse;
          table-layout: fixed;
        }

        .block-table th,
        .block-table td {
          border: 1px solid #8b8b8b;
          padding: 3mm 3.2mm;
          vertical-align: top;
        }

        .block-table th {
          background: #f2f2f2;
          font-size: 10pt;
          text-align: left;
        }

        .col-number {
          width: 18%;
        }

        .col-name {
          width: 30%;
        }

        .col-value {
          width: 52%;
        }

        .operations-col-name {
          width: 24%;
        }

        .operations-col-content {
          width: 50%;
        }

        .operations-col-equipment {
          width: 26%;
        }

        .cell-number {
          font-weight: 700;
          white-space: nowrap;
        }

        .cell-name {
          font-weight: 600;
        }

        .cell-value,
        .cell-value-wide {
          white-space: pre-wrap;
          word-break: break-word;
        }

        .section-row td {
          background: #f8f8f8;
          font-weight: 700;
        }

        .image-row td {
          padding: 4mm;
        }

        .image-wrapper {
          text-align: center;
        }

        .image-caption {
          margin-bottom: 2mm;
          font-weight: 600;
        }

        .image-wrapper img {
          max-width: 100%;
          max-height: 110mm;
          object-fit: contain;
        }

        .image-wrapper-full img {
          max-height: 175mm;
        }

        .extra-images-section {
          margin-top: 4mm;
        }

        .extra-images-title {
          margin-bottom: 2mm;
          font-weight: 700;
        }

        .extra-images-grid {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 4mm;
        }

        .extra-image-card {
          margin: 0;
          border: 1px solid #8b8b8b;
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
          border: 1px dashed #9b9b9b;
          color: #5f5f5f;
          font-style: italic;
        }

        .export-note {
          margin-top: 8mm;
          color: #5f5f5f;
          font-size: 9pt;
        }
      </style>
    </head>
    <body>
      <main class="page">
        <h1 class="document-title">${documentTitle}</h1>
        <section class="document-meta">
          ${metadataRows}
        </section>
        ${blocksHtml}
        <div class="export-note">Документ сформирован из текущего состояния техкарты на frontend.</div>
      </main>
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
  customFields = {},
  uploadedImages = {},
  title = 'Технологическая карта',
}) => {
  const { blockImages, extraImages } = await prepareExportImages(blocks, uploadedImages);

  const html = buildWordHtml({
    methodologyName,
    objectName,
    elementName,
    blocks,
    paramValues,
    customFields,
    uploadedImages: extraImages,
    imageSrcMap: blockImages,
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
