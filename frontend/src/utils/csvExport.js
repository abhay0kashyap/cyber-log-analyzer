/**
 * @typedef {Object} ExportLogRow
 * @property {string} timestamp
 * @property {string} ip
 * @property {"Critical"|"High"|"Medium"|"Low"} severity
 * @property {string} message
 */

/** @type {Array<keyof ExportLogRow>} */
const CSV_COLUMNS = ['timestamp', 'ip', 'severity', 'message'];

/**
 * Escape a single value for CSV format.
 * @param {unknown} value
 * @returns {string}
 */
function escapeCsvValue(value) {
  const raw = value == null ? '' : String(value);
  const escaped = raw.replace(/"/g, '""');
  return /[",\r\n]/.test(raw) ? `"${escaped}"` : escaped;
}

/**
 * Convert JSON rows to CSV, including a header row.
 * @param {ExportLogRow[]} rows
 * @returns {string}
 */
export function logsToCsv(rows) {
  const header = CSV_COLUMNS.join(',');
  const body = rows.map((row) => CSV_COLUMNS.map((key) => escapeCsvValue(row[key])).join(','));
  return [header, ...body].join('\r\n');
}

/**
 * Create a CSV filename using local timestamp.
 * Format: logs-YYYY-MM-DDTHH_MM_SS.csv
 * @param {Date} [date]
 * @returns {string}
 */
export function buildCsvFilename(date = new Date()) {
  const pad2 = (value) => String(value).padStart(2, '0');
  const yyyy = date.getFullYear();
  const mm = pad2(date.getMonth() + 1);
  const dd = pad2(date.getDate());
  const hh = pad2(date.getHours());
  const min = pad2(date.getMinutes());
  const ss = pad2(date.getSeconds());
  return `logs-${yyyy}-${mm}-${dd}T${hh}_${min}_${ss}.csv`;
}

/**
 * Trigger browser download from text content.
 * @param {string} content
 * @param {string} filename
 * @param {string} [mimeType]
 */
export function downloadTextFile(content, filename, mimeType = 'text/csv;charset=utf-8;') {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

