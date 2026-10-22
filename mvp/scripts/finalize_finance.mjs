// Narrow artifact-tool edit of a local copy. The archive workbook is never written.
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = path.join(root, 'data/raw/archive/verification/inputs/BondScope_Dashboard_Corrected_M12_8_M24_10.xlsx');
const outputDir = path.join(root, 'outputs/final/finance');
const outputPath = path.join(outputDir, 'BondScope_Dashboard_Finalized_Base_M12_8_M24_10.xlsx');
const recordPath = path.join(root, 'implementation/finalization/finance_workbook_run.json');
const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const changes = [
  {sheet: '14 Decision Gate', cell: 'B31', kind: 'value', value: 'Условная рекомендация: согласовать узкий шестимесячный MVP и ограничить коммерческое расширение до подтверждения данных, 2 платных пилотов и обоснованной модели окупаемости. В базовом сценарии 600 000 ₸ / мес. модельно достигается окупаемость в M20 и кумулятивный результат M24 12 602 000 ₸; это сценарный расчёт, не подтверждённая продажа или полная финансовая модель.'},
  {sheet: '14 Decision Gate', cell: 'F16', kind: 'value', value: 'Учитывает заявленные CAPEX, OPEX и CAC; VAT и налог на прибыль не моделируются'},
  {sheet: '13 Buyer Pilot', cell: 'C31', kind: 'formula', value: "='08 Scenarios'!D9"},
  {sheet: '13 Buyer Pilot', cell: 'C32', kind: 'formula', value: "='08 Scenarios'!E9"},
  {sheet: '13 Buyer Pilot', cell: 'F33', kind: 'value', value: 'КОНФЛИКТ: 8–12 здесь vs 12–18 в 04 Inputs; нужен выбор участников 1/3, ни один диапазон не принят.'},
  {sheet: '09 KPI Risks', cell: 'B13', kind: 'value', value: 'Доля сигналов с обязательными раскрытыми основаниями'},
  {sheet: '09 KPI Risks', cell: 'C13', kind: 'value', value: 1},  {sheet: '09 KPI Risks', cell: 'H13', kind: 'value', value: 'Обязательное требование: 100% сигналов имеют источник и объяснение. Воспроизводимость ≥95%: доля согласованного набора контрольных случаев, где повторный запуск на тех же входах, версии правил и источниках даёт совпадающий результат; до пилота Data фиксирует знаменатель и правило совпадения.'}
];
const formatAdjustments = [
  {sheet: '13 Buyer Pilot', range: 'B33:H33', rowHeight: 48, wrapText: true},
  {sheet: '09 KPI Risks', range: 'B13:H13', rowHeight: 78, wrapText: true},
];

const sourceBytes = await fs.readFile(source);
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const sheetsBefore = await workbook.inspect({kind: 'sheet', include: 'id,name', maxChars: 4000});
for (const change of changes) {
  const range = workbook.worksheets.getItem(change.sheet).getRange(change.cell);
  if (change.kind === 'formula') range.formulas = [[change.value]];
  else range.values = [[change.value]];
}
for (const adjustment of formatAdjustments) {
  const range = workbook.worksheets.getItem(adjustment.sheet).getRange(adjustment.range);
  range.format.wrapText = adjustment.wrapText;
  range.format.rowHeight = adjustment.rowHeight;
}
workbook.recalculate();
const changedRanges = await Promise.all(['14 Decision Gate!B12:H31', '13 Buyer Pilot!B29:H35', '09 KPI Risks!B8:H14'].map(async address => {
  const [sheetName, range] = address.split('!');
  return {address, inspection: (await workbook.inspect({kind: 'table', sheetId: sheetName, range, include: 'values,formulas', tableMaxRows: 24, tableMaxCols: 8, maxChars: 6000})).ndjson};
}));
const errors = await workbook.inspect({kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!', options: {useRegex: true, maxResults: 300}, maxChars: 4000});
await fs.mkdir(outputDir, {recursive: true});
for (const [sheetName, range, name] of [['14 Decision Gate', 'B12:H32', 'decision-gate.png'], ['13 Buyer Pilot', 'B29:H35', 'buyer-pilot.png'], ['09 KPI Risks', 'B8:H14', 'kpi-risks.png']]) {
  const preview = await workbook.render({sheetName, range, scale: 1, format: 'png'});
  await fs.writeFile(path.join(outputDir, name), new Uint8Array(await preview.arrayBuffer()));
}
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
const outputBytes = await fs.readFile(outputPath);
const sheetsAfter = await workbook.inspect({kind: 'sheet', include: 'id,name', maxChars: 4000});
await fs.writeFile(recordPath, JSON.stringify({source_workbook: path.relative(root, source).replaceAll('\\', '/'), source_sha256: sha256(sourceBytes), output_workbook: path.relative(root, outputPath).replaceAll('\\', '/'), output_sha256: sha256(outputBytes), changes, format_adjustments: formatAdjustments, sheets_before: sheetsBefore.ndjson, sheets_after: sheetsAfter.ndjson, changed_ranges: changedRanges, formula_error_scan: errors.ndjson, recalculation: 'artifact-tool workbook.recalculate() called; validate formulas in a native spreadsheet application before external use'}, null, 2) + '\n', 'utf8');
console.log(JSON.stringify({output: outputPath, changes: changes.length, source_sha256: sha256(sourceBytes), output_sha256: sha256(outputBytes)}));
