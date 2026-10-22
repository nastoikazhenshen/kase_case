import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import crypto from "node:crypto";
import { execFileSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = process.cwd();
const skillDir = process.env.PRESENTATIONS_SKILL_DIR || path.join(os.homedir(), '.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11348/skills/presentations');
const runtimePython = process.env.RUNTIME_PYTHON || path.resolve(path.dirname(process.execPath), '../../python/python.exe');
process.env.RUNTIME_NODE ||= process.execPath;
process.env.RUNTIME_NODE_MODULES ||= path.resolve(path.dirname(process.execPath), '../node_modules');
process.env.RUNTIME_PYTHON ||= runtimePython;
const finalDir = path.join(workspaceDir, "mvp", "outputs", "final");
const stagingDir = path.join(workspaceDir, "mvp", "local_validation", "slides6_7");
const version = process.env.BONDSCOPE_SLIDE_VERSION || "v5";
if (!/^v[0-9]+$/.test(version)) throw new Error("Invalid slide version");
const candidatePath = path.join(stagingDir, `slides6_7_candidate_${version}.pptx`);
const finalPath = path.join(finalDir, `slides6_7_kase_bondscope_mvp_${version}.pptx`);
const screenshotPath = path.join(finalDir, "app", "demo-example-1440.png");
const frozenScreenshotPath = path.join(finalDir, `slides6_7_source_app_${version}.png`);

const report = JSON.parse(await fs.readFile(path.join(finalDir, 'demo/report.json'), 'utf8'));
const observation = report.observations[0];
const formal = report.evaluations.find(r => r.rule === 'planned_amount_to_observed_daily_turnover');
if (report.observations.length !== 1 || observation.ticker !== 'BIGDb5' || observation.trade_date !== '2026-10-21' || !['EVALUATED','TRIGGERED'].includes(formal?.status)) throw new Error('Wrong or gated demonstration report');
const money = n => Number(n).toLocaleString('en-US', {maximumFractionDigits: 0}).replaceAll(',', ' ');
const numerator = money(report.planned_amount_kzt);
const denominator = money(observation.turnover_kzt);
const ratio = Number(report.planned_amount_kzt) / Number(observation.turnover_kzt);
if (Math.abs(ratio - formal.value) > 1e-12) throw new Error('Slide arithmetic differs from the report');
const identity = `снимок ${report.snapshot_id}; отчёт ${report.report_id}`;

const C = {
  graphite: "#45464F",
  green: "#038726",
  greenLight: "#3CBD0D",
  lime: "#9ED110",
  yellow: "#FECC00",
  paper: "#F7F9F7",
  mist: "#E8EEE9",
  muted: "#66706A",
  white: "#FFFFFF",
};

async function writeBlob(target, blob) {
  await fs.writeFile(target, new Uint8Array(await blob.arrayBuffer()));
}

async function readImageBlob(source) {
  const bytes = await fs.readFile(source);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

function box(slide, left, top, width, height, options = {}) {
  return slide.shapes.add({
    geometry: options.geometry ?? "rect",
    position: { left, top, width, height },
    fill: options.fill ?? "none",
    line: options.line ?? { style: "solid", fill: "none", width: 0 },
  });
}

function text(slide, value, left, top, width, height, style = {}) {
  const shape = box(slide, left, top, width, height);
  shape.text = value;
  shape.text.style = {
    typeface: "Arial",
    fontSize: 18,
    color: C.graphite,
    ...style,
  };
  return shape;
}

function footer(slide, label) {
  box(slide, 72, 674, 1136, 1, { fill: C.mist, line: { style: "solid", fill: C.mist, width: 1 } });
  text(slide, label, 72, 686, 930, 18, { fontSize: 10, color: C.muted });
  text(slide, "KASE BondScope 3.0", 1034, 686, 174, 18, { fontSize: 10, color: C.green, bold: true, align: "right" });
}

async function addSlide6(presentation) {
  const slide = presentation.slides.add();
  slide.background.fill = C.paper;
  text(slide, "06", 72, 52, 80, 44, { fontSize: 31, color: C.green, bold: true });
  text(slide, "Проверка дневного оборота BIGDb5", 72, 106, 800, 52, { fontSize: 32, color: C.graphite, bold: true });
  text(slide, "21 октября 2026", 74, 164, 300, 24, { fontSize: 16, color: C.muted });

  text(slide, "Планируемая сумма", 72, 228, 310, 24, { fontSize: 16, color: C.muted });
  text(slide, `${numerator} ₸`, 72, 257, 330, 63, { fontSize: 44, color: C.green, bold: true });
  text(slide, "ввод аналитика, гипотетический", 72, 325, 360, 23, { fontSize: 15, color: C.graphite, italic: true });

  text(slide, "наблюдаемый дневной оборот", 72, 387, 390, 24, { fontSize: 16, color: C.muted });
  text(slide, `${denominator} ₸`, 72, 416, 340, 56, { fontSize: 36, color: C.graphite, bold: true });
  text(slide, "округлённое отображение KASE", 72, 476, 360, 23, { fontSize: 14, color: C.muted });

  box(slide, 478, 235, 2, 252, { fill: C.mist, line: { style: "solid", fill: C.mist, width: 1 } });
  text(slide, `${numerator} / ${denominator} =`, 528, 245, 220, 31, { fontSize: 19, color: C.graphite, bold: true });
  text(slide, ratio.toFixed(7).replace(".", ","), 528, 280, 220, 38, { fontSize: 27, color: C.graphite, bold: true });
  text(slide, `≈ ${(ratio * 100).toFixed(2).replace(".", ",")}%`, 528, 328, 220, 43, { fontSize: 31, color: C.green, bold: true });
  text(slide, "доля наблюдаемого оборота", 528, 374, 220, 22, { fontSize: 14, color: C.muted });
  text(slide, `Порог ${Number(formal.threshold) * 100}% — гипотеза правила. Расчёт не подтверждает исполнение сделки.`, 528, 421, 218, 66, { fontSize: 15, color: C.graphite });

  const screenshot = await readImageBlob(frozenScreenshotPath);
  slide.images.add({
    blob: screenshot,
    contentType: "image/png",
    alt: "Проверенный экран KASE BondScope с расчётом BIGDb5",
    fit: "contain",
    position: { left: 775, top: 218, width: 433, height: 272 },
    geometry: "rect",
  });
  text(slide, "Проверенный экран MVP", 775, 499, 280, 21, { fontSize: 14, color: C.green, bold: true });
  text(slide, "Снимок 1440 px, офлайн-проверка пройдена", 775, 521, 390, 20, { fontSize: 13, color: C.muted });

  text(slide, "Покрытие текущего среза", 72, 536, 360, 24, { fontSize: 17, color: C.graphite, bold: true });
  text(slide, "6 правил реализованы   ·   1 формально вычислимо на 4 строках   ·   5 заблокированы условиями набора данных", 72, 566, 1130, 28, { fontSize: 16, color: C.graphite });
  text(slide, "Ценовой вид, режим торгов и сопоставимая история остаются неполными для заблокированных правил.", 72, 602, 1040, 22, { fontSize: 13, color: C.muted });
  footer(slide, `Источник: KASE, карточка ${observation.ticker}; локальный ${identity}`);
  slide.speakerNotes.text = `Проверка масштаба предполагаемой сделки. ${numerator} KZT — гипотетический ввод аналитика; ${denominator} KZT — опубликованный округлённый оборот ${observation.trade_date}. Порог ${Number(formal.threshold)*100}% — гипотеза, не гарантия исполнения. Источник: https://kase.kz/ru/investors/bonds/${observation.ticker}; ${identity}.`;
  slide.speakerNotes.setVisible(true);
  return slide;
}

function addSlide7(presentation) {
  const slide = presentation.slides.add();
  slide.background.fill = C.paper;
  text(slide, "07", 72, 52, 80, 44, { fontSize: 31, color: C.green, bold: true });
  text(slide, "Концепция продукта и шесть месяцев до готовности", 72, 106, 950, 52, { fontSize: 31, color: C.graphite, bold: true });
  text(slide, "Концепция. Интеграция KASE / IRIS / API в MVP не реализована.", 74, 164, 900, 24, { fontSize: 16, color: C.muted });

  text(slide, "A", 72, 232, 46, 44, { fontSize: 33, color: C.green, bold: true });
  text(slide, "Монитор\nисключений", 132, 237, 220, 52, { fontSize: 19, color: C.graphite, bold: true });
  text(slide, "Правило, статус и основание", 132, 307, 252, 44, { fontSize: 15, color: C.muted });
  box(slide, 398, 230, 1, 118, { fill: C.mist, line: { style: "solid", fill: C.mist, width: 1 } });
  text(slide, "B", 438, 232, 46, 44, { fontSize: 33, color: C.green, bold: true });
  text(slide, "Контекст ликвидности\nдо сделки", 498, 237, 286, 52, { fontSize: 19, color: C.graphite, bold: true });
  text(slide, "Оборот, число сделок и ограничение", 498, 307, 258, 44, { fontSize: 15, color: C.muted });
  box(slide, 770, 230, 1, 118, { fill: C.mist, line: { style: "solid", fill: C.mist, width: 1 } });
  text(slide, "C", 810, 232, 46, 44, { fontSize: 33, color: C.green, bold: true });
  text(slide, "События эмитента", 870, 237, 240, 25, { fontSize: 19, color: C.graphite, bold: true });
  text(slide, "Дата, источник и момент доступности", 870, 272, 258, 44, { fontSize: 15, color: C.muted });

  text(slide, "Цепочка работы: Watchlist, очередь исключений, аудит-отчёт", 72, 343, 700, 24, { fontSize: 15, color: C.graphite, bold: true });

  box(slide, 72, 382, 1136, 2, { fill: C.green, line: { style: "solid", fill: C.green, width: 1 } });
  const months = [
    ["M1", "Спецификация\nи права", "доступ к данным согласован"],
    ["M2", "ETL и\nкачество", "поля и происхождение проверены"],
    ["M3", "Объяснимые\nправила", "пороги и проверки согласованы"],
    ["M4", "UI и\nинтеграция", "очередь и контракт интеграции"],
    ["M5", "Пилот и\nтесты", "принятие и воспроизводимость"],
    ["M6", "Готовность\nк запуску", "решение о запуске владельцем"],
  ];
  months.forEach(([month, title, exit], index) => {
    const left = 72 + index * 189;
    text(slide, month, left, 411, 58, 25, { fontSize: 17, color: C.green, bold: true });
    text(slide, title, left, 447, 166, 50, { fontSize: 17, color: C.graphite, bold: true });
    text(slide, exit, left, 513, 164, 47, { fontSize: 13, color: C.muted });
    if (index < 5) box(slide, left + 174, 420, 1, 144, { fill: C.mist, line: { style: "solid", fill: C.mist, width: 1 } });
  });
  text(slide, "Демо использует локально сохранённые публичные наблюдения. Будущий контур требует лицензированных данных и согласованных прав.", 72, 606, 1100, 24, { fontSize: 14, color: C.graphite });
  footer(slide, `Концепция продукта: будущая интеграция не реализована; ${identity}`);
  slide.speakerNotes.text = "Поясните границу MVP: сейчас доступны локально сохранённые публичные наблюдения и воспроизводимый отчёт. A, B и C — концепция целевого продукта. Интеграция KASE, IRIS и API не реализована. План: M1 спецификация и права, M2 ETL и качество, M3 правила, M4 UI и интеграция, M5 пилот и тесты, M6 готовность к промышленной работе. Источник ограничений — локальный отчёт, указанный в нижней строке слайда.";
  slide.speakerNotes.setVisible(true);
  return slide;
}

async function main() {
  await fs.mkdir(finalDir, { recursive: true });
  await fs.mkdir(stagingDir, { recursive: true });
  // The browser smoke runner may refresh its captures. Freeze the exact input to
  // this version before embedding it, so subsequent tests cannot alter provenance.
  await fs.copyFile(screenshotPath, frozenScreenshotPath, (await import('node:fs')).constants.COPYFILE_EXCL);
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  await addSlide6(presentation);
  addSlide7(presentation);
  await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

  const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir, "container_tools", "artifact_tool_utils.mjs")).href);
  await finalizePresentation({
    explicitTotalSlideCount: 2,
    requiredNativeTableOwnerSlides: [],
    requiredNativeChartOwnerSlides: [],
    workspaceDir,
    candidatePath,
    finalPath,
    pythonExecutable: runtimePython,
    integrityValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_layout_geometry.py"),
    layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-bullet-geometry", "--validate-heading-fit"],
    fontPolicy: { basis: "user_request", families: ["Arial"] },
    verifyArtifactToolImport: true,
    receiptPath: path.join(stagingDir, `slides6_7_${version}.validation.json`),
  });
  const renderDir = path.join(stagingDir, 'final-render');
  execFileSync(runtimePython, [path.join(skillDir, 'container_tools/render_slides.py'), finalPath, '--output_dir', renderDir], {stdio:'inherit', env:process.env});
  for (let i=1;i<=2;i++) await fs.copyFile(path.join(renderDir, `slide-${i}.png`), path.join(finalDir, `slides6_7_0${i+5}_${version}.png`));
  const pdfPath = finalPath.replace(/\.pptx$/, '.pdf');
  execFileSync(runtimePython, ['-c', 'from PIL import Image; import sys; from pathlib import Path; p=Path(sys.argv[1]); a=Image.open(p/"slide-1.png").convert("RGB"); b=Image.open(p/"slide-2.png").convert("RGB"); a.save(sys.argv[2],"PDF",save_all=True,append_images=[b],resolution=120.0)', renderDir, pdfPath], {stdio:'inherit'});
  const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
  const artifacts = [];
  for (const output of [finalPath, pdfPath, path.join(finalDir,`slides6_7_06_${version}.png`),path.join(finalDir,`slides6_7_07_${version}.png`)]) {
    const bytes=await fs.readFile(output); artifacts.push({path:path.relative(workspaceDir,output).replaceAll('\\','/'),bytes:bytes.length,sha256:sha256(bytes)});
  }
  const record = {snapshot_id:report.snapshot_id,report_id:report.report_id,screenshot_path:path.relative(workspaceDir,frozenScreenshotPath).replaceAll('\\','/'),screenshot_sha256:sha256(await fs.readFile(frozenScreenshotPath)),editable_slides:2,pdf_type:'Raster preview of actual final PPTX renders; editable objects remain in PPTX',artifacts};
  await fs.writeFile(path.join(workspaceDir,'mvp/implementation/finalization/slides_manifest.json'),JSON.stringify(record,null,2)+'\n');
  console.log(JSON.stringify({slides:2,rendered:true,report_id:report.report_id,artifacts}));

}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
