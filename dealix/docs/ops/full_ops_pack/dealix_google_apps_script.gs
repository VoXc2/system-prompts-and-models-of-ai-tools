/**
 * Dealix — Google Apps Script template (paste into Spreadsheet-bound project).
 * Rename file in editor if you like (e.g. dealix_apps_script.gs).
 *
 * After paste: Run setupDealixTrigger() once, then testInsertRow(), then a real Form submit.
 */

var CONFIG = {
  SPREADSHEET_ID: '', // optional if bound; leave empty when script is container-bound
  SHEET_FORM: 'Form Responses 1',
  SHEET_BOARD: '02_Operating_Board',
  /** 1-based column indices on BOARD row (extend to match LEVEL1_OPS_STRUCTURE_AR.md) */
  COL: {
    TIMESTAMP: 1,
    NAME: 2,
    COMPANY: 3,
    SOURCE: 10,
    CONSENT_SOURCE: 11,
    RECOMMENDED_SERVICE: 12,
    NEXT_STEP: 16,
    DIAGNOSTIC_STATUS: 17,
    DIAGNOSTIC_CARD: 18
  },
  /** If true, append one board row per form row using mapped indices below */
  USE_SCRIPT_FORM_TO_BOARD_APPEND: true,
  /** Must equal last column index you use on 02_Operating_Board (default 26). */
  BOARD_COL_COUNT: 26
};

/**
 * Installable onFormSubmit → set handler to this function name in the trigger UI,
 * or run setupDealixTrigger() to bind programmatically.
 */
function onDealixFormSubmit(e) {
  return handleDealixFormSubmit_(e);
}

/** Alternate name — same handler (repo-compatible alias). */
function onFormSubmitDealix(e) {
  return onDealixFormSubmit(e);
}

function handleDealixFormSubmit_(e) {
  if (!e || !e.range) {
    Logger.log('onDealixFormSubmit: no event/range');
    return;
  }
  var sh = e.range.getSheet();
  if (sh.getName() !== CONFIG.SHEET_FORM) {
    return;
  }
  var row = e.range.getRow();
  if (row < 2) return;

  var ss = sh.getParent();
  var board = ss.getSheetByName(CONFIG.SHEET_BOARD);
  if (!board) {
    throw new Error('Missing sheet: ' + CONFIG.SHEET_BOARD);
  }

  var formRow = sh.getRange(row, 1, row, sh.getLastColumn()).getValues()[0];
  var mapped = mapFormRowToBoard_(formRow, sh);

  if (CONFIG.USE_SCRIPT_FORM_TO_BOARD_APPEND) {
    board.appendRow(mapped);
  }
}

/** Map Form Responses row → array matching BOARD column order (adjust to your headers). */
function mapFormRowToBoard_(formRow, formSheet) {
  var headers = formSheet.getRange(1, 1, 1, formSheet.getLastColumn()).getValues()[0];
  var idx = {};
  for (var i = 0; i < headers.length; i++) {
    idx[String(headers[i]).trim()] = i;
  }
  function pick(name, fallback) {
    var j = idx[name];
    return (j === undefined) ? fallback : formRow[j];
  }

  var ts = pick('Timestamp', new Date());
  var name = pick('Name', pick('الاسم', ''));
  var company = pick('Company', pick('الشركة', ''));
  var consent = pick('Consent', pick('موافقة', ''));
  var source = pick('Source', 'form');
  var consentSource = consent ? 'form_opt_in' : 'missing';
  var goal = pick('Goal', pick('الهدف', ''));
  var rec = recommendService_(goal);
  var nextStep = 'جهّز Mini Diagnostic';
  var diagStatus = 'new';
  var card = buildDiagnosticCardStub_(company, goal, rec);

  // Pad/truncate to BOARD_COL_COUNT columns on 02_Operating_Board (see LEVEL1_OPS_STRUCTURE_AR.md).
  var row = [
    ts, name, company,
    pick('Website', ''), pick('Sector', ''), pick('City', ''),
    goal, pick('Ideal customer', ''), pick('Offer', ''),
    pick('Contact method', ''), pick('WhatsApp', ''), pick('Email', ''),
    consent, source, consentSource,
    rec, '', '', nextStep, diagStatus, card,
    '', '', '', '', '', ''
  ];
  while (row.length < CONFIG.BOARD_COL_COUNT) row.push('');
  return row.slice(0, CONFIG.BOARD_COL_COUNT);
}

function recommendService_(goal) {
  var g = String(goal || '').toLowerCase();
  if (/شراكة|partnership/i.test(g)) return 'Partnership Growth';
  if (/اجتماع|meeting/i.test(g)) return 'Meeting Sprint';
  if (/قائمة|list|data/i.test(g)) return 'Data to Revenue';
  if (/وكالة|agency|مسوق/i.test(g)) return 'Agency Partner Pilot';
  if (/متجر|retail|local/i.test(g)) return 'Local Growth / Reactivation';
  if (/عملاء|leads|growth/i.test(g)) return 'Growth Starter';
  return 'Growth Starter';
}

function buildDiagnosticCardStub_(company, goal, service) {
  return JSON.stringify({
    company: company,
    goal: goal,
    recommended_service: service,
    opportunities: ['فرصة 1', 'فرصة 2', 'فرصة 3'],
    risk_note: 'راجع قبل الإرسال — لا وعود مبالغ فيها.',
    next_step: 'Pilot 499'
  });
}

/** Create installable trigger: Form submit → onDealixFormSubmit */
function setupDealixTrigger() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'onDealixFormSubmit') {
      ScriptApp.deleteTrigger(t);
    }
  });
  ScriptApp.newTrigger('onDealixFormSubmit')
    .forSpreadsheet(ss)
    .onFormSubmit()
    .create();
}

/** Append one test row to BOARD (no Form). */
function testInsertRow() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var board = ss.getSheetByName(CONFIG.SHEET_BOARD);
  if (!board) throw new Error('Missing sheet: ' + CONFIG.SHEET_BOARD);
  var testRow = [
    new Date(), 'Test User', 'Test Co', '', 'Tech', 'Riyadh',
    'أبغى عملاء', 'B2B', 'SaaS',
    'whatsapp', '966500000000', 'test@example.com',
    'yes', 'manual_test', 'form_opt_in',
    'Growth Starter', 'warm', '', 'جهّز Mini Diagnostic', 'new',
    buildDiagnosticCardStub_('Test Co', 'أبغى عملاء', 'Growth Starter'),
    '', '', '', '', '', ''
  ];
  while (testRow.length < CONFIG.BOARD_COL_COUNT) testRow.push('');
  board.appendRow(testRow.slice(0, CONFIG.BOARD_COL_COUNT));
}
