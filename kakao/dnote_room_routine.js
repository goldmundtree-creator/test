/**
 * dNote방 확인 카카오톡 루틴 (메신저봇R 스크립트)
 *
 * 동작 방식
 *  - "dNote" 방에 올라오는 모든 메시지를 로컬 파일에 기록한다.
 *  - 아무 방에서나 "dNote방 확인해줘"라고 보내면,
 *    마지막 확인 이후 쌓인 새 메시지 개수와 최근 메시지를 답장한다.
 *
 * 설치: 메신저봇R 앱에서 새 봇 생성 후 이 파일 내용을 붙여넣고 컴파일.
 *       메신저봇R의 카카오톡 알림 읽기 권한이 켜져 있어야 한다.
 */

var TARGET_ROOM = "dNote";               // 감시할 방 이름
var TRIGGER = "dNote방 확인해줘";          // 확인 명령어
var MAX_RECENT = 10;                      // 답장에 보여줄 최근 메시지 수
var MAX_STORED = 200;                     // 파일에 보관할 최대 메시지 수

var DATA_DIR = "sdcard/msgbot/dnote";
var LOG_FILE = DATA_DIR + "/messages.json";
var STATE_FILE = DATA_DIR + "/state.json";

function loadJson(path, fallback) {
    var raw = FileStream.read(path);
    if (raw === null || raw === "") return fallback;
    try {
        return JSON.parse(raw);
    } catch (e) {
        return fallback;
    }
}

function saveJson(path, obj) {
    FileStream.write(path, JSON.stringify(obj));
}

function formatTime(ts) {
    var d = new Date(ts);
    function pad(n) { return (n < 10 ? "0" : "") + n; }
    return pad(d.getMonth() + 1) + "/" + pad(d.getDate()) + " " +
        pad(d.getHours()) + ":" + pad(d.getMinutes());
}

function recordMessage(sender, msg) {
    var messages = loadJson(LOG_FILE, []);
    messages.push({ time: Date.now(), sender: sender, msg: msg });
    if (messages.length > MAX_STORED) {
        messages = messages.slice(messages.length - MAX_STORED);
    }
    saveJson(LOG_FILE, messages);
}

function buildReport() {
    var messages = loadJson(LOG_FILE, []);
    var state = loadJson(STATE_FILE, { lastChecked: 0 });

    if (messages.length === 0) {
        return "[" + TARGET_ROOM + "방 확인]\n기록된 메시지가 없습니다.";
    }

    var newCount = 0;
    for (var i = 0; i < messages.length; i++) {
        if (messages[i].time > state.lastChecked) newCount++;
    }

    var recent = messages.slice(-MAX_RECENT);
    var lines = ["[" + TARGET_ROOM + "방 확인]"];
    lines.push(state.lastChecked === 0
        ? "총 " + messages.length + "개의 메시지가 기록되어 있습니다."
        : "마지막 확인(" + formatTime(state.lastChecked) + ") 이후 새 메시지 " + newCount + "개");
    lines.push("");
    lines.push("최근 메시지 " + recent.length + "개:");
    for (var j = 0; j < recent.length; j++) {
        var m = recent[j];
        var mark = m.time > state.lastChecked ? "🆕 " : "";
        lines.push(mark + formatTime(m.time) + " " + m.sender + ": " + m.msg);
    }

    state.lastChecked = Date.now();
    saveJson(STATE_FILE, state);

    return lines.join("\n");
}

function response(room, msg, sender, isGroupChat, replier, imageDB, packageName) {
    // dNote방 메시지는 전부 기록 (명령어 자체는 기록하지 않음)
    if (room === TARGET_ROOM && msg !== TRIGGER) {
        recordMessage(sender, msg);
    }

    // 어느 방에서든 확인 명령에 응답
    if (msg.trim() === TRIGGER) {
        replier.reply(buildReport());
    }
}
