import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { PageHeader } from "../components/PageHeader";
import { ProgressBar } from "../components/ProgressBar";
import { api } from "../lib/api";
import {
  deleteLocalReport,
  listLocalReportsMeta,
  loadLocalReport,
} from "../lib/localReports";
import { useApp } from "../state/AppContext";
import type { Report, ReportMeta } from "../types";

export function Review() {
  const { currentReport } = useApp();
  const [reports, setReports] = useState<ReportMeta[]>([]);
  const [viewing, setViewing] = useState<Report | null>(null);

  const refresh = useCallback(() => {
    const local = listLocalReportsMeta();
    api
      .listReports()
      .then((res) => {
        const seen = new Set<string>();
        setReports(
          [...res.reports, ...local].filter((item) => {
            if (seen.has(item.report_id)) return false;
            seen.add(item.report_id);
            return true;
          }),
        );
      })
      .catch(() => setReports(local));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh, currentReport]);

  async function viewReport(id: string) {
    try {
      setViewing(await api.loadReport(id));
    } catch {
      setViewing(loadLocalReport(id));
    }
  }

  async function removeReport(id: string) {
    if (!window.confirm("确定删除这份复盘吗？删除后无法恢复。")) return;
    try {
      await api.deleteReport(id);
    } catch {
      /* 云端记录已失效时，仍允许删除本地副本 */
    }
    deleteLocalReport(id);
    if (viewing?.report_id === id) setViewing(null);
    refresh();
  }

  return (
    <div>
      <PageHeader
        title="面试复盘"
        caption="五维评分 · 面试官手记 · 历史记录随时回看"
      />

      {currentReport ? (
        <section className="mb-10">
          <h2 className="mb-4 text-lg font-bold text-ink">本次复盘</h2>
          <ReportDetail report={currentReport} />
        </section>
      ) : null}

      <section>
        <h2 className="mb-1 text-lg font-bold text-ink">历史复盘</h2>
        <p className="mb-4 text-xs text-muted">记录同时保存在本机浏览器，云端重置也不会丢失。</p>
        {reports.length === 0 ? (
          <Card className="text-center">
            <p className="text-muted">完成一次模拟面试并生成复盘后，这里会出现你的历史记录。</p>
          </Card>
        ) : (
          <div className="space-y-3">
            {reports.map((item) => (
              <Card key={item.report_id} className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-semibold text-ink">{item.job_label}</p>
                  <p className="text-xs text-muted">
                    {item.created_at} · 总分 {item.total_score} / 100
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button variant="secondary" onClick={() => void viewReport(item.report_id)}>
                    查看
                  </Button>
                  <Button variant="ghost" onClick={() => void removeReport(item.report_id)}>
                    删除
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>

      {viewing ? (
        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="mt-10"
        >
          <h2 className="mb-4 text-lg font-bold text-ink">这份复盘</h2>
          <ReportDetail report={viewing} />
        </motion.section>
      ) : null}
    </div>
  );
}

function ReportDetail({ report }: { report: Report }) {
  return (
    <div className="space-y-5">
      <div className="grid gap-5 md:grid-cols-[1fr_2fr]">
        <Card className="flex flex-col items-center justify-center text-center">
          <span className="text-sm text-muted">总分</span>
          <span className="mt-1 text-5xl font-extrabold tabular-nums text-ink">
            {report.total_score}
          </span>
          <span className="text-sm text-muted">/ 100</span>
        </Card>
        <Card>
          <h3 className="font-bold text-ink">五维表现</h3>
          <div className="mt-4 space-y-3">
            {Object.entries(report.dimensions).map(([name, score]) => (
              <ProgressBar key={name} value={score / 10} label={`${name} ${score}/10`} />
            ))}
          </div>
        </Card>
      </div>

      {report.overall_impression ? (
        <Card className="border-gold/30 bg-[#FCFAF3]">
          <p className="leading-relaxed text-ink">
            这轮面试看下来，我的第一印象是——{report.overall_impression}
          </p>
        </Card>
      ) : null}

      {report.question_comments.length ? (
        <Card>
          <h3 className="font-bold text-ink">逐题点评</h3>
          <div className="mt-4 space-y-4">
            {report.question_comments.map((item, index) => (
              <div key={index}>
                <p className="font-semibold text-ink">
                  第 {index + 1} 题：{item.question}
                </p>
                <p className="mt-1.5 text-sm leading-relaxed text-muted">{item.comment}</p>
              </div>
            ))}
          </div>
        </Card>
      ) : null}

      {report.growth_advice.length ? (
        <Card>
          <h3 className="font-bold text-ink">接下来可以这样练</h3>
          <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-ink">
            {report.growth_advice.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
        </Card>
      ) : null}

      {report.closing ? (
        <Card>
          <p className="leading-relaxed text-ink">{report.closing}</p>
        </Card>
      ) : null}
    </div>
  );
}
