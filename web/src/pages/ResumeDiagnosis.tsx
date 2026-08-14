import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { Field } from "../components/Field";
import { JobCard } from "../components/JobCard";
import { LoadingStage } from "../components/LoadingStage";
import { PageHeader } from "../components/PageHeader";
import { StepIndicator } from "../components/StepIndicator";
import { api } from "../lib/api";
import { useApp } from "../state/AppContext";
import type { ClarificationItem, DiagnosisResult, MatchedJob } from "../types";

type Phase = "input" | "clarify" | "result";

const STEPS = ["提交简历", "补充信息", "专属方案"];
const CLARIFY_STAGES = [
  "正在读取简历…",
  "正在提取缺失的信息…",
  "正在生成待确认清单…",
];
const DIAGNOSE_STAGES = [
  "正在整理你的简历与补充信息…",
  "正在逐项对照岗位要求…",
  "正在起草最优先修改建议…",
  "正在生成当地市场提示…",
  "正在排版专属优化方案…",
];

export function ResumeDiagnosis() {
  const { setResumeText } = useApp();
  const [phase, setPhase] = useState<Phase>("input");
  const [source, setSource] = useState<"paste" | "file">("paste");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [resumeContent, setResumeContent] = useState("");
  const [targetJob, setTargetJob] = useState("");
  const [targetLocation, setTargetLocation] = useState("");
  const [marketNotes, setMarketNotes] = useState("");
  const [items, setItems] = useState<ClarificationItem[]>([]);
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const [matchedJobs, setMatchedJobs] = useState<MatchedJob[]>([]);
  const [matchLoading, setMatchLoading] = useState(false);
  const [matchError, setMatchError] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingStages, setLoadingStages] = useState<string[]>([]);
  const [loadingStep, setLoadingStep] = useState(0);
  const [loadingDone, setLoadingDone] = useState(false);
  const intervalRef = useRef<number | null>(null);
  const doneTimerRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (intervalRef.current) window.clearInterval(intervalRef.current);
      if (doneTimerRef.current) window.clearTimeout(doneTimerRef.current);
    };
  }, []);

  function startLoading(stages: string[]) {
    setError("");
    setLoading(true);
    setLoadingDone(false);
    setLoadingStages(stages);
    setLoadingStep(0);
    if (intervalRef.current) window.clearInterval(intervalRef.current);
    if (doneTimerRef.current) window.clearTimeout(doneTimerRef.current);
    intervalRef.current = window.setInterval(() => {
      setLoadingStep((step) => Math.min(step + 1, stages.length - 1));
    }, 3500);
  }

  function finishLoading() {
    if (intervalRef.current) window.clearInterval(intervalRef.current);
    intervalRef.current = null;
    setLoadingDone(true);
    doneTimerRef.current = window.setTimeout(() => {
      setLoading(false);
    }, 650);
  }

  async function parseCurrent(): Promise<string> {
    if (source === "paste") {
      if (!text.trim()) throw new Error("请先粘贴简历内容。");
      const parsed = await api.parseText(text);
      return parsed.content;
    }
    if (!file) throw new Error("请先选择简历文件。");
    const parsed = await api.parseFile(file);
    return parsed.content;
  }

  async function runDiagnose(resumeText: string, clarifyItems: ClarificationItem[]) {
    const res = await api.diagnose({
      resume_text: resumeText,
      items: clarifyItems,
      market_notes: marketNotes,
      target_job: targetJob,
      target_location: targetLocation,
    });
    setResult(res);
    setPhase("result");
    setMatchedJobs([]);
    setMatchError("");
    setMatchLoading(true);
    try {
      const matched = await api.matchJobs({
        resume_text: resumeText,
        target_job: targetJob,
        target_location: targetLocation,
        limit: 6,
      });
      setMatchedJobs(matched.jobs);
    } catch (err) {
      setMatchError(err instanceof Error ? err.message : "岗位匹配失败，请稍后重试。");
    } finally {
      setMatchLoading(false);
    }
  }

  async function handleAnalyze() {
    startLoading(CLARIFY_STAGES);
    try {
      const content = await parseCurrent();
      setResumeText(content);
      setResumeContent(content);
      const res = await api.clarify(content);
      setItems(res.items.map((item) => ({ ...item, answer: "" })));
      setPhase("clarify");
    } catch (err) {
      setError(err instanceof Error ? err.message : "分析失败，请重试。");
    } finally {
      finishLoading();
    }
  }

  async function handleSkip() {
    startLoading(DIAGNOSE_STAGES);
    try {
      const content = await parseCurrent();
      setResumeText(content);
      setResumeContent(content);
      await runDiagnose(content, []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "诊断失败，请重试。");
    } finally {
      finishLoading();
    }
  }

  async function handleDiagnoseConfirm(skip: boolean) {
    startLoading(DIAGNOSE_STAGES);
    try {
      const clarifyItems = skip ? items.map((i) => ({ ...i, answer: "" })) : items;
      await runDiagnose(resumeContent, clarifyItems);
    } catch (err) {
      setError(err instanceof Error ? err.message : "诊断失败，请重试。");
    } finally {
      finishLoading();
    }
  }

  function reset() {
    setPhase("input");
    setText("");
    setFile(null);
    setResumeContent("");
    setItems([]);
    setResult(null);
    setMatchedJobs([]);
    setMatchLoading(false);
    setMatchError("");
    setError("");
  }

  return (
    <div>
      <PageHeader
        title="简历诊断"
        caption="粘贴或上传简历 → AI 先找出没写清楚的地方 → 你补充后生成专属优化方案。"
      />
      <StepIndicator steps={STEPS} current={phase === "input" ? 0 : phase === "clarify" ? 1 : 2} />

      {loading ? (
        <div className="mt-10">
          <LoadingStage stages={loadingStages} current={loadingStep} done={loadingDone} />
        </div>
      ) : null}

      {error ? (
        <div
          role="alert"
          className="mt-6 rounded-control border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {error}
        </div>
      ) : null}

      {!loading && phase === "input" ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="mt-8 space-y-6"
        >
          <Card>
            <div className="mb-4 inline-flex rounded-full border border-line bg-canvas p-1">
              {(["paste", "file"] as const).map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setSource(option)}
                  className={`rounded-full px-4 py-1.5 text-sm font-semibold transition-colors duration-150 ${
                    source === option
                      ? "bg-blue text-white shadow-btn"
                      : "text-muted hover:text-blue"
                  }`}
                >
                  {option === "paste" ? "粘贴文本" : "上传文件"}
                </button>
              ))}
            </div>

            {source === "paste" ? (
              <Field label="简历内容">
                <textarea
                  value={text}
                  onChange={(event) => setText(event.target.value)}
                  rows={9}
                  placeholder="把简历全文粘贴到这里…"
                  className="w-full rounded-control border border-line bg-surface px-4 py-3 text-sm leading-relaxed text-ink transition-colors duration-150 focus:border-blue focus:ring-2 focus:ring-blue/20"
                />
              </Field>
            ) : (
              <label className="block cursor-pointer rounded-control border border-dashed border-[#A9C7F2] bg-[#FBFDFF] p-6 text-center transition-colors duration-150 hover:border-blue hover:bg-fog">
                <input
                  type="file"
                  accept=".pdf,.docx"
                  className="sr-only"
                  onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                />
                <span className="block text-sm font-semibold text-ink">
                  {file ? file.name : "点击选择简历文件"}
                </span>
                <span className="mt-1 block text-xs text-muted">支持 PDF 或 Word .docx</span>
              </label>
            )}
          </Card>

          <Card>
            <div className="grid gap-4 md:grid-cols-2">
              <Field label="目标岗位（选填）" hint="例如：产品经理、市场营销…">
                <input
                  value={targetJob}
                  onChange={(event) => setTargetJob(event.target.value)}
                  className="w-full rounded-control border border-line bg-surface px-4 py-2.5 text-sm text-ink transition-colors duration-150 focus:border-blue focus:ring-2 focus:ring-blue/20"
                />
              </Field>
              <Field label="期望工作地点（选填）" hint="例如：青岛、杭州…">
                <input
                  value={targetLocation}
                  onChange={(event) => setTargetLocation(event.target.value)}
                  className="w-full rounded-control border border-line bg-surface px-4 py-2.5 text-sm text-ink transition-colors duration-150 focus:border-blue focus:ring-2 focus:ring-blue/20"
                />
              </Field>
            </div>
            <div className="mt-4">
              <Field label="当地市场补充说明（选填）" hint="例如：了解到本地该岗位普遍要求会数据分析…">
                <textarea
                  value={marketNotes}
                  onChange={(event) => setMarketNotes(event.target.value)}
                  rows={3}
                  className="w-full rounded-control border border-line bg-surface px-4 py-3 text-sm text-ink transition-colors duration-150 focus:border-blue focus:ring-2 focus:ring-blue/20"
                />
              </Field>
            </div>
          </Card>

          <div className="flex flex-wrap gap-3">
            <Button onClick={handleAnalyze}>分析简历缺失信息</Button>
            <Button variant="secondary" onClick={handleSkip}>
              跳过询问，直接诊断
            </Button>
          </div>
        </motion.div>
      ) : null}

      {!loading && phase === "clarify" ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="mt-8 space-y-5"
        >
          <Card>
            <h2 className="text-lg font-bold text-ink">简历里还差这些信息</h2>
            <p className="mt-1 text-sm text-muted">
              能填的填一下，不确定的可以留空跳过；填写内容只用于本次简历优化。
            </p>
            <div className="mt-5 grid gap-4 md:grid-cols-2">
              {items.map((item, index) => (
                <Field key={`${item.field}-${index}`} label={item.question} hint={item.hint || "可不填"}>
                  <input
                    value={item.answer}
                    onChange={(event) => {
                      const next = [...items];
                      next[index] = { ...item, answer: event.target.value };
                      setItems(next);
                    }}
                    className="w-full rounded-control border border-line bg-surface px-4 py-2.5 text-sm text-ink transition-colors duration-150 focus:border-blue focus:ring-2 focus:ring-blue/20"
                  />
                </Field>
              ))}
            </div>
            <div className="mt-5">
              <Field label="当地市场补充说明（选填）">
                <textarea
                  value={marketNotes}
                  onChange={(event) => setMarketNotes(event.target.value)}
                  rows={3}
                  className="w-full rounded-control border border-line bg-surface px-4 py-3 text-sm text-ink transition-colors duration-150 focus:border-blue focus:ring-2 focus:ring-blue/20"
                />
              </Field>
            </div>
          </Card>
          <div className="flex flex-wrap gap-3">
            <Button onClick={() => void handleDiagnoseConfirm(false)}>确认并生成优化方案</Button>
            <Button variant="secondary" onClick={() => void handleDiagnoseConfirm(true)}>
              全部跳过，直接诊断
            </Button>
            <Button variant="ghost" onClick={reset}>
              重新上传简历
            </Button>
          </div>
        </motion.div>
      ) : null}

      {!loading && phase === "result" && result ? (
        <ResultView
          result={result}
          onReset={reset}
          matchedJobs={matchedJobs}
          matchLoading={matchLoading}
          matchError={matchError}
        />
      ) : null}
    </div>
  );
}

function ResultView({
  result,
  onReset,
  matchedJobs,
  matchLoading,
  matchError,
}: {
  result: DiagnosisResult;
  onReset: () => void;
  matchedJobs: MatchedJob[];
  matchLoading: boolean;
  matchError: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="mt-8 space-y-6"
    >
      <div className="grid gap-5 md:grid-cols-[1fr_2fr]">
        <Card className="flex flex-col items-center justify-center text-center">
          <span className="text-sm text-muted">简历综合评分</span>
          <span className="mt-1 text-5xl font-extrabold tabular-nums text-ink">
            {result.score}
          </span>
          <span className="text-sm text-muted">/ 100</span>
        </Card>
        <Card>
          <h2 className="font-bold text-ink">整体评价</h2>
          <p className="mt-2 text-sm leading-relaxed text-ink">{result.overall_evaluation}</p>
        </Card>
      </div>

      {result.top_priorities.length ? (
        <Card>
          <h2 className="font-bold text-ink">最优先修改建议</h2>
          <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-ink">
            {result.top_priorities.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
        </Card>
      ) : null}

      {result.requirement_table.length ? (
        <Card>
          <h2 className="font-bold text-ink">岗位要求对照表</h2>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[560px] border-collapse text-left text-sm">
              <thead>
                <tr className="border-b border-line text-muted">
                  <th className="px-3 py-2 font-semibold">岗位要求</th>
                  <th className="px-3 py-2 font-semibold">简历证据</th>
                  <th className="px-3 py-2 font-semibold">证据强度</th>
                  <th className="px-3 py-2 font-semibold">差距说明</th>
                </tr>
              </thead>
              <tbody>
                {result.requirement_table.map((row, index) => (
                  <tr key={index} className="border-b border-line/70 align-top">
                    <td className="px-3 py-2.5 text-ink">{row.requirement}</td>
                    <td className="px-3 py-2.5 text-ink">{row.evidence}</td>
                    <td className="px-3 py-2.5 text-ink">{row.strength}</td>
                    <td className="px-3 py-2.5 text-ink">{row.gap}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : null}

      {result.market_notes ? (
        <Card className="border-gold/30 bg-[#FCFAF3]">
          <h2 className="font-bold text-ink">当地市场提示</h2>
          <p className="mt-2 text-sm leading-relaxed text-ink">{result.market_notes}</p>
          <p className="mt-2 text-xs text-muted">以上为 AI 参考信息，具体以官方招聘信息为准。</p>
        </Card>
      ) : null}

      <MatchedJobsSection
        jobs={matchedJobs}
        loading={matchLoading}
        error={matchError}
      />

      <div className="grid gap-5 md:grid-cols-2">
        <Card>
          <h2 className="font-bold text-ink">优势</h2>
          <ul className="mt-3 space-y-2 text-sm text-ink">
            {result.strengths.map((item) => (
              <li key={item}>· {item}</li>
            ))}
          </ul>
        </Card>
        <Card>
          <h2 className="font-bold text-ink">不足</h2>
          <ul className="mt-3 space-y-2 text-sm text-ink">
            {result.weaknesses.map((item) => (
              <li key={item}>· {item}</li>
            ))}
          </ul>
        </Card>
      </div>

      <Card>
        <h2 className="font-bold text-ink">修改建议</h2>
        <ul className="mt-3 space-y-2 text-sm text-ink">
          {result.suggestions.map((item) => (
            <li key={item}>· {item}</li>
          ))}
        </ul>
      </Card>

      {result.optimized_examples.length ? (
        <Card>
          <h2 className="font-bold text-ink">优化示例（改写后的片段）</h2>
          <div className="mt-3 space-y-4">
            {result.optimized_examples.map((example, index) => (
              <div key={index}>
                <p className="text-xs font-semibold text-muted">示例 {index + 1}</p>
                <p className="mt-1 rounded-control bg-canvas px-4 py-3 text-sm leading-relaxed text-ink">
                  {example}
                </p>
              </div>
            ))}
          </div>
        </Card>
      ) : null}

      <Button onClick={onReset}>再来一份</Button>
    </motion.div>
  );
}

function MatchedJobsSection({
  jobs,
  loading,
  error,
}: {
  jobs: MatchedJob[];
  loading: boolean;
  error: string;
}) {
  return (
    <Card>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="font-bold text-ink">可投递岗位</h2>
        {loading ? <span className="text-xs text-muted">正在匹配岗位…</span> : null}
      </div>
      {error ? (
        <p role="alert" className="mt-2 text-sm text-red-700">
          {error}
        </p>
      ) : null}
      {!loading && jobs.length ? (
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      ) : null}
      {!loading && !error && !jobs.length ? (
        <p className="mt-2 text-sm text-muted">暂无匹配岗位，可稍后在企业招聘页浏览。</p>
      ) : null}
    </Card>
  );
}
