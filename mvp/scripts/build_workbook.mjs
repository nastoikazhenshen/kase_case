// Local contest workbook. Uses the bundled @oai/artifact-tool runtime.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const demo = process.argv.includes('--demo');
const outputDir = path.join(root, demo ? 'outputs/final/demo' : 'outputs');
const report = JSON.parse(await fs.readFile(path.join(outputDir, 'report.json'), 'utf8'));
const snapshot = JSON.parse(await fs.readFile(path.join(root, 'data/processed/snapshot.json'), 'utf8'));
const wb = Workbook.create();
const summary = wb.worksheets.add('Наблюдения');
const rules = wb.worksheets.add('Правила');
const context = wb.worksheets.add('Оценки и события');
const inputs = wb.worksheets.add('Источники');
const literal = v => typeof v === 'string' && /^[\s]*[=+@-]/.test(v) ? "'" + v : v;
const number = v => v === '' || v === null || v === undefined ? null : Number(v);
// This workbook is a rendered evidence report, not a date-calculation model.  Text
// avoids renderer serial dates while preserving the full offset on instants.
const dateText = v => {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(v ?? ''));
  return match ? `${match[3]}.${match[2]}.${match[1]}` : 'не записано';
};
const instantText = v => {
  const text = String(v ?? '').trim();
  return text ? text.replace('T', ' ') : 'не записано';
};
const columnName = n => { let s=''; for (;n;n=Math.floor((n-1)/26)) s=String.fromCharCode(65+(n-1)%26)+s; return s; };
// Explicit values preserve ISO instants and timezone offsets as text; write() auto-parses them.
const write = (sheet, cell, rows) => {
  const [, col, row] = /^([A-Z]+)(\d+)$/.exec(cell);
  const start = [...col].reduce((n,c)=>n*26+c.charCodeAt(0)-64,0);
  const width = Math.max(...rows.map(r=>r.length));
  sheet.getRange(`${cell}:${columnName(start+width-1)}${Number(row)+rows.length-1}`).values = rows.map(r=>Array.from({length:width},(_,i)=>literal(r[i]??null)));
};
function style(sheet, region, header, widths) {
  sheet.showGridLines = false;
  sheet.getRange(region).format.font = {name: 'Arial', size: 10, color: '#45464F'};
  sheet.getRange(region).format.rowHeight = 24;
  sheet.getRange(header).format = {fill: '#45464F', font: {name:'Arial', size:10, bold:true, color:'#FFFFFF'}, rowHeight:40, wrapText:true};
  for (const [column, width] of Object.entries(widths)) sheet.getRange(`${column}:${column}`).format.columnWidth = width;
}
write(summary, 'A2', [['KASE BondScope 3.0 · наблюдения за 21 октября 2026']]);
summary.getRange('A2').format.font = {name:'Arial',size:16,bold:true,color:'#038726'};
write(summary, 'A3', [['Конкурсный прототип. Снимок не сертифицирован как окончательные итоги дня.']]);
write(summary, 'A4', [['Сумма, KZT', report.planned_amount_kzt, demo ? 'Условный ввод для демонстрации, не реальная заявка и не рыночное наблюдение.' : 'Необязательный ввод пользователя, не рыночное наблюдение.']]);
summary.getRange('B4').format.fill = '#FFF4CC';
summary.getRange('B4').setNumberFormat('#,##0');
write(summary, 'A5', [['Отчёт', report.report_id]]);
write(summary, 'A6', [['Контекст событий', dateText(report.as_of)]]);
write(summary, 'A8', [['Тикер', 'Дата', 'Режим', 'Оборот, KZT', 'Сделки', 'Средний размер, KZT', 'Разница Last/Wavg', 'Диапазон / Wavg', 'Сумма / оборот дня', 'Ограничение']]);

const inputHeader = ['row_id','ISIN','Тикер','Дата торгов','Режим','Режим подтверждён','Оборот KZT','Число сделок','Last','Wavg','High','Low','Вкладка доказана','URL','Получено','SHA-256','Исходная точность KZT'];
write(inputs, 'A1', [inputHeader]);
const inputRows = report.observations.map(r => [r.row_id,r.instrument_id,r.ticker,dateText(r.trade_date),r.trading_mode,r.mode_status,
  number(r.turnover_kzt),number(r.trades_count),number(r.last_price),number(r.weighted_avg_price),number(r.high_price),number(r.low_price),
  r.price_view_status,r.source_url,instantText(r.retrieved_at),r.evidence_sha256,number(r.turnover_precision_kzt)]);
write(inputs, 'A2', inputRows);
inputs.getRange(`G2:H${inputRows.length+1}`).setNumberFormat('#,##0');
inputs.getRange(`I2:L${inputRows.length+1}`).setNumberFormat('0.0000');

for (let i=0; i<report.observations.length; i++) {
  const r=9+i, s=2+i;
  summary.getRange(`A${r}:I${r}`).formulas = [[
    `='Источники'!C${s}`, `='Источники'!D${s}`, `=IF('Источники'!E${s}="","не подтверждён",'Источники'!E${s})`,
    `=IF(ISNUMBER('Источники'!G${s}),'Источники'!G${s},"")`, `=IF(ISNUMBER('Источники'!H${s}),'Источники'!H${s},"")`,
    `=IF(AND('Источники'!F${s}="VERIFIED",ISNUMBER(D${r}),E${r}>0),D${r}/E${r},"")`,
    `=IF(AND('Источники'!M${s}="VERIFIED",'Источники'!F${s}="VERIFIED",'Источники'!J${s}>0),'Источники'!I${s}/'Источники'!J${s}-1,"")`,
    `=IF(AND('Источники'!M${s}="VERIFIED",'Источники'!F${s}="VERIFIED",'Источники'!J${s}>0),('Источники'!K${s}-'Источники'!L${s})/'Источники'!J${s},"")`,
    `=IF(AND(ISNUMBER($B$4),$B$4>=0,'Источники'!F${s}="VERIFIED",ISNUMBER(D${r}),D${r}>0),$B$4/D${r},"")`
  ]];
  write(summary, `J${r}`, [['Вкладка цены не доказана; история недостаточна']]);
}
summary.getRange('D9:F13').setNumberFormat('#,##0.00');
summary.getRange('E9:E13').setNumberFormat('#,##0');
summary.getRange('G9:H13').setNumberFormat('0.00%');
summary.getRange('I9:I13').setNumberFormat('0.0000" ×"');
write(summary,'A16', [['Средний размер = округлённый дневной оборот / число сделок. Это описательная величина, не историческая норма.'],
  ['Сумма / оборот дня не равна сумме / исторической медиане. Не является прогнозом исполнения.'],
  ['Пустые ценовые метрики заблокированы до доказательства активной вкладки, даты и режима.'],
  ['Канонический *_pct: 0,5 означает 0,5%; Excel хранит 0,005 с форматом процента.']]);
summary.tabColor='#038726';

write(rules,'A1',[['Тикер','Дата','Правило','Значение','Единицы','Статус','База','n','Порог-гипотеза','Версия','Строки входа','Источник']]);
write(rules,'A2',report.evaluations.map(r=>[r.ticker,dateText(r.trade_date),r.rule,r.value,r.units,r.status,r.baseline,r.n,r.threshold,r.method_version,r.input_row_ids.join(';'),r.source_ids.join(';')]));
write(context,'A1',[['Тикер','Дата оценки','Официальная рыночная цена','Единицы','Тип','Источник','Получено']]);
write(context,'A2',report.valuations.map(v=>[v.ticker,dateText(v.valuation_date),v.market_price,v.unit,v.valuation_type,v.source_url,instantText(v.retrieved_at)]));
write(context,'A8',[['Опубликованное сообщение CLSGb11 (контекст полного локального пакета)']]);
const event = snapshot.events[0];
write(context,'A10',[['Дата события','Дата/время публикации','Сумма KZT','Доступно по политике','Доказательство','Источник','Получено'],
  [dateText(event.event_date),instantText(event.event_published_at),number(event.payment_amount_kzt),instantText(event.availability?.effective_from || '2026-10-22T00:00:00+05:00'),event.evidence_status,event.source_url,instantText(event.retrieved_at)]]);
context.getRange('C11').setNumberFormat('#,##0');
write(context,'A14',[['Часовой пояс публикации не напечатан: доступность со следующего дня +05:00. На срезе 21 октября событие исключено из отчёта.'],
 ['Рыночная оценка не является последней сделкой или отдельной расчётной ценой для риск-процессов.'],
 ['Внутреннее API-поле settlement_price здесь принадлежит странице «Рыночная оценка»; назначение определяется страницей.'],
 ['Расчётные цены для риск-процессов не получены; отсутствие данных не подменено нулём.']]);

style(summary,'A1:J20','A8:J8',{A:18,B:16,C:19,D:19,E:10,F:21,G:19,H:19,I:21,J:38});
summary.getRange('J9:J13').format.wrapText=true;
summary.getRange('A9:J13').format.rowHeight=38;
style(inputs,`A1:Q${inputRows.length+1}`,'A1:Q1',{A:34,B:20,C:15,D:16,E:15,F:18,G:18,H:14,I:14,J:14,K:14,L:14,M:27,N:65,O:29,P:66,Q:20});
style(rules,`A1:L${report.evaluations.length+1}`,'A1:L1',{A:14,B:16,C:45,D:16,E:12,F:30,G:16,H:8,I:20,J:16,K:40,L:38});
style(context,'A1:G18','A1:G1',{A:21,B:31,C:26,D:33,E:35,F:68,G:31});
context.getRange('A10:G10').format={fill:'#45464F',font:{color:'#FFFFFF',bold:true},rowHeight:38,wrapText:true};
inputs.freezePanes.freezeRows(1); rules.freezePanes.freezeRows(1);
// Apply number formats after overall styles so renderer and XLSX agree.
summary.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:'#038726'};
summary.getRange('D9:F13').setNumberFormat('#,##0.00');
summary.getRange('E9:E13').setNumberFormat('#,##0');
summary.getRange('G9:H13').setNumberFormat('0.00%');
summary.getRange('I9:I13').setNumberFormat('0.0000" ×"');
inputs.getRange(`G2:H${inputRows.length+1}`).setNumberFormat('#,##0');
inputs.getRange(`I2:L${inputRows.length+1}`).setNumberFormat('0.0000');
context.getRange('C2:C4').setNumberFormat('0.00000');
context.getRange('C11').setNumberFormat('#,##0');
wb.recalculate();
// Independent computation check, plus live input test in a disposable in-memory state.
const expectedMean=Number(report.observations[0].turnover_kzt)/Number(report.observations[0].trades_count);
if (Math.abs(Number(summary.getRange('F9').values[0][0])-expectedMean)>1e-8) throw new Error('Mean formula mismatch');
summary.getRange('B4').values=[[100000]];
wb.recalculate();
const expectedRatio=100000/Number(report.observations[0].turnover_kzt);
if (Math.abs(Number(summary.getRange('I9').values[0][0])-expectedRatio)>1e-10) throw new Error('Ratio formula does not recalculate');
summary.getRange('B4').clear({applyTo:'contents'});
wb.recalculate();
if (summary.getRange('I9').values[0][0] !== '') throw new Error('Blank planned input became zero');
if (!demo && summary.getRange('E12').values[0][0] !== 0) throw new Error('Zero trades became missing');
if (summary.getRange('B9').values[0][0] !== '21.10.2026') throw new Error('Date is not human-readable text');
if (demo) {
  summary.getRange('B4').values=[[report.planned_amount_kzt]];
  wb.recalculate();
  const formal = report.evaluations.find(r => r.rule === 'planned_amount_to_observed_daily_turnover');
  if (Math.abs(Number(summary.getRange('I9').values[0][0])-formal.value)>1e-12) throw new Error('Workbook/report example mismatch');
}
const check=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},maxChars:1800});
await fs.writeFile(path.join(outputDir,'workbook_checks.json'),JSON.stringify({report_id:report.report_id,live_input_recalculated:true,blank_input_tested:true,delivered_planned_amount_kzt:report.planned_amount_kzt,inspection:check.ndjson},null,2));
const output=await SpreadsheetFile.exportXlsx(wb);
await output.save(path.join(outputDir,'mvp_results.xlsx'));
for (const [sheetName,range,index] of [['Наблюдения','A2:J19',0],['Правила','A1:J14',1],['Оценки и события','A1:G17',2],['Источники','A1:Q6',3]]) {
  const preview=await wb.render({sheetName,range,scale:1,format:'png'});
  await fs.writeFile(path.join(outputDir,`workbook_preview${index}.png`),new Uint8Array(await preview.arrayBuffer()));
}
console.log(JSON.stringify({file:path.join(outputDir,'mvp_results.xlsx'),report_id:report.report_id,formula_input_check:'PASS'}));
