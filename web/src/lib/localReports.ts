import type { Report, ReportMeta } from "../types";

const KEY = "ai_interview_reports_v1";
const MAX_LOCAL_REPORTS = 50;

function readAll(): Report[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    return Array.isArray(parsed) ? (parsed as Report[]) : [];
  } catch {
    return [];
  }
}

function writeAll(reports: Report[]): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(reports));
  } catch {
    /* 存储已满或隐私模式：静默失败，不阻塞主流程 */
  }
}

/** 本机历史记录（元信息，按时间倒序） */
export function listLocalReportsMeta(): ReportMeta[] {
  return readAll()
    .map((report) => ({
      report_id: report.report_id,
      created_at: report.created_at,
      job_label: report.job_label,
      total_score: report.total_score,
    }))
    .sort((a, b) => b.created_at.localeCompare(a.created_at));
}

/** 生成复盘成功后同步存一份到本机，云端重置也不丢失 */
export function saveLocalReport(report: Report): void {
  const reports = readAll().filter((item) => item.report_id !== report.report_id);
  reports.unshift(report);
  writeAll(reports.slice(0, MAX_LOCAL_REPORTS));
}

export function loadLocalReport(reportId: string): Report | null {
  return readAll().find((item) => item.report_id === reportId) ?? null;
}

export function deleteLocalReport(reportId: string): void {
  writeAll(readAll().filter((item) => item.report_id !== reportId));
}
