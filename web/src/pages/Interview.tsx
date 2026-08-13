import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { Field } from "../components/Field";
import { LoadingStage } from "../components/LoadingStage";
import { PageHeader } from "../components/PageHeader";
import { ProgressBar } from "../components/ProgressBar";
import { api } from "../lib/api";
import { saveLocalReport } from "../lib/localReports";
import { useApp } from "../state/AppContext";
import type { InterviewState } from "../types";

const START_STAGES = ["正在读取岗位信息…", "正在结合简历出题…", "正在排版面试问题…"];
const FOLLOWUP_STAGES = ["正在回顾你的回答…", "正在找出可深挖的细节…", "正在生成追问…"];
const REPORT_STAGES = [
  "面试官正在翻看全部问答记录…",
  "正在逐题打分与点评…",
  "正在起草面试官手记…",
  "正在生成成长建议…",
  "正在排版复盘报告…",
];

export function Interview() {
  const { resumeText, interviewState, setInterviewState, setCurrentReport } = useApp();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [loadingStages, setLoadingStages] = useState<string[]>([]);
  const [loadingStep, setLoadingStep] = useState(0);
  const [loadingDone, setLoadingDone] = useState(false);
  const [error, setError] = useState("");
  const [answers, setAnswers] = useState({ main: "", followup: "" });
  const intervalRef = useRef<number | null>(null);
  const doneTimerRef = useRef<number | null>(null);

  useEffect(() => {
    setAnswers({ main: "", followup: "" });
  }, [interviewState?.current_index, interviewState?.phase]);

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

  async function run<T>(fn: () => Promise<T>, stages: string[]) {
    startLoading(stages);
    try {
      return await fn();
    } catch (err) {
      setError(err instanceof Error ? err.message : "请求失败，请重试。");
      return null;
    } finally {
      finishLoading();
    }
  }

  async function submitMain() {
    if (!interviewState) return;
    if (!answers.main.trim()) {
      setError("请先输入回答内容再提交。");
      return;
    }
    const next = await run(() => api.answer(interviewState, answers.main), START_STAGES);
    if (next) setInterviewState(next);
  }

  async function requestFollowUp() {
    if (!interviewState) return;
    const next = await run(() => api.followup(interviewState), FOLLOWUP_STAGES);
    if (next) setInterviewState(next);
  }

  async function submitFollowUp() {
    if (!interviewState) return;
    if (!answers.followup.trim()) {
      setError("请先输入追问的回答内容。");
      return;
    }
    const next = await run(
      () => api.followupAnswer(interviewState, answers.followup),
      START_STAGES,
    );
    if (next) setInterviewState(next);
  }

  async function goNext() {
    if (!interviewState) return;
    const next = await run(() => api.next(interviewState), START_STAGES);
    if (next) setInterviewState(next);
  }

  async function finishEarly() {
    if (!interviewState) return;
    const next = await run(() => api.finish(interviewState), START_STAGES);
    if (next) setInterviewState(next);
  }

  async function generateReport() {
    if (!interviewState) return;
    const report = await run(() => api.generateReport(interviewState), REPORT_STAGES);
    if (report) {
      saveLocalReport(report);
      setCurrentReport(report);
      setInterviewState(null);
      navigate("/review");
    }
  }

  const state = interviewState;
  const inProgress = state && state.status === "in_progress";

  return (
    <div>
      <PageHeader
        title="模拟面试"
        caption="选择岗位方向，像真实面试官一样逐题问答；答完还可以被追问细节。"
      />

      {loading ? (
        <LoadingStage stages={loadingStages} current={loadingStep} done={loadingDone} />
      ) : null}

      {error ? (
        <div
          role="alert"
          className="mt-6 rounded-control border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {error}
        </div>
      ) : null}

      {!loading && !state ? <Setup onStart={setInterviewState} resumeAvailable={resumeText.length > 0} /> : null}
      {!loading && inProgress ? (
        <QuestionView
          state={state}
          answers={answers}
          setAnswers={setAnswers}
          onSubmitMain={() => void submitMain()}
          onFollowUp={() => void requestFollowUp()}
          onSubmitFollowUp={() => void submitFollowUp()}
          onNext={() => void goNext()}
          onFinish={() => void finishEarly()}
        />
      ) : null}
      {!loading && state && state.status === "finished" ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="mt-8 max-w-2xl space-y-5"
        >
          <Card>
            <h2 className="text-xl font-bold text-ink">面试已结束</h2>
            <p className="mt-2 text-sm text-muted">
              岗位：{state.job_label} · 共 {state.total} 题 · 回答 {state.answered_count} 题
            </p>
          </Card>
          <div className="flex flex-wrap gap-3">
            <Button onClick={() => void generateReport()}>生成面试复盘</Button>
            <Button variant="secondary" onClick={() => setInterviewState(null)}>
              重新开始
            </Button>
          </div>
        </motion.div>
      ) : null}
    </div>
  );
}

function Setup({
  onStart,
  resumeAvailable,
}: {
  onStart: (state: InterviewState) => void;
  resumeAvailable: boolean;
}) {
  const [jobs, setJobs] = useState<string[]>([]);
  const [job, setJob] = useState("");
  const [custom, setCustom] = useState("");
  const [numQuestions, setNumQuestions] = useState(5);
  const [useResume, setUseResume] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { resumeText } = useApp();

  useEffect(() => {
    api
      .jobs()
      .then((res) => {
        setJobs(res.labels);
        setJob(res.labels[0] ?? "");
      })
      .catch(() => setJobs(["产品经理", "市场营销", "运营", "财务", "人力资源", "行政文秘", "通用管培生", "自定义岗位"]));
  }, []);

  async function start() {
    const label = job === "自定义岗位" ? custom.trim() : job;
    if (!label) {
      setError("请先填写自定义岗位名称。");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const state = await api.startInterview({
        job_label: label,
        num_questions: numQuestions,
        resume_text: resumeAvailable && useResume ? resumeText : "",
      });
      onStart(state);
    } catch (err) {
      setError(err instanceof Error ? err.message : "出题失败，请重试。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="mt-8 max-w-2xl space-y-5"
    >
      <Card>
        <h2 className="text-lg font-bold text-ink">面试设置</h2>
        <div className="mt-5 space-y-5">
          <Field label="岗位方向">
            <select
              value={job}
              onChange={(event) => setJob(event.target.value)}
              className="w-full rounded-control border border-line bg-surface px-4 py-2.5 text-sm text-ink transition-colors duration-150 focus:border-blue focus:ring-2 focus:ring-blue/20"
            >
              {jobs.map((label) => (
                <option key={label} value={label}>
                  {label}
                </option>
              ))}
            </select>
          </Field>
          {job === "自定义岗位" ? (
            <Field label="自定义岗位名称">
              <input
                value={custom}
                onChange={(event) => setCustom(event.target.value)}
                placeholder="例如：跨境电商运营"
                className="w-full rounded-control border border-line bg-surface px-4 py-2.5 text-sm text-ink transition-colors duration-150 focus:border-blue focus:ring-2 focus:ring-blue/20"
              />
            </Field>
          ) : null}
          <Field label={`题目数量：${numQuestions} 题`}>
            <input
              type="range"
              min={3}
              max={8}
              value={numQuestions}
              onChange={(event) => setNumQuestions(Number(event.target.value))}
              className="w-full accent-blue"
            />
            <div className="mt-1 flex justify-between text-xs text-muted">
              <span>3</span>
              <span>8</span>
            </div>
          </Field>
          {resumeAvailable ? (
            <label className="flex cursor-pointer items-center gap-2 text-sm text-ink">
              <input
                type="checkbox"
                checked={useResume}
                onChange={(event) => setUseResume(event.target.checked)}
                className="size-4 accent-blue"
              />
              带入简历诊断页的简历内容辅助出题（推荐）
            </label>
          ) : null}
        </div>
      </Card>

      {error ? (
        <div role="alert" className="rounded-control border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <Button onClick={() => void start()} loading={loading}>
        开始面试
      </Button>
    </motion.div>
  );
}

interface QuestionViewProps {
  state: InterviewState;
  answers: { main: string; followup: string };
  setAnswers: (value: { main: string; followup: string }) => void;
  onSubmitMain: () => void;
  onFollowUp: () => void;
  onSubmitFollowUp: () => void;
  onNext: () => void;
  onFinish: () => void;
}

function QuestionView({
  state,
  answers,
  setAnswers,
  onSubmitMain,
  onFollowUp,
  onSubmitFollowUp,
  onNext,
  onFinish,
}: QuestionViewProps) {
  const questionNumber = state.current_index + 1;
  const isFollowUp = state.phase === "followup" || state.phase === "answered_followup";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="mt-8 max-w-3xl space-y-6"
    >
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-muted">岗位：{state.job_label}</p>
        <button
          type="button"
          onClick={onFinish}
          className="text-sm font-semibold text-muted underline-offset-4 transition-colors hover:text-blue hover:underline"
        >
          提前结束
        </button>
      </div>
      <ProgressBar
        value={state.total ? state.answered_count / state.total : 0}
        label={`已完成 ${state.answered_count} / ${state.total} 题`}
      />

      <Card>
        <p className="text-sm font-semibold text-muted">
          {isFollowUp
            ? `第 ${questionNumber} 题 · 面试官追问`
            : `第 ${questionNumber} 题 / 共 ${state.total} 题`}
        </p>
        <p className="mt-3 text-lg font-medium leading-relaxed text-ink">
          {isFollowUp ? state.current_follow_up_question : state.current_question}
        </p>
      </Card>

      {state.phase === "main" ? (
        <>
          <Field label="你的回答">
            <textarea
              value={answers.main}
              onChange={(event) => setAnswers({ ...answers, main: event.target.value })}
              rows={6}
              placeholder="请像在真实面试中一样完整作答…"
              className="w-full rounded-control border border-line bg-surface px-4 py-3 text-sm leading-relaxed text-ink transition-colors duration-150 focus:border-blue focus:ring-2 focus:ring-blue/20"
            />
          </Field>
          <Button onClick={onSubmitMain}>提交答案</Button>
        </>
      ) : null}

      {state.phase === "answered_main" ? (
        <div className="flex flex-wrap gap-3">
          <Button onClick={onFollowUp}>让 AI 追问</Button>
          <Button variant="secondary" onClick={onNext}>
            下一题
          </Button>
        </div>
      ) : null}

      {state.phase === "followup" ? (
        <>
          <Field label="你的回答">
            <textarea
              value={answers.followup}
              onChange={(event) => setAnswers({ ...answers, followup: event.target.value })}
              rows={5}
              placeholder="针对追问作答…"
              className="w-full rounded-control border border-line bg-surface px-4 py-3 text-sm leading-relaxed text-ink transition-colors duration-150 focus:border-blue focus:ring-2 focus:ring-blue/20"
            />
          </Field>
          <Button onClick={onSubmitFollowUp}>提交追问回答</Button>
        </>
      ) : null}

      {state.phase === "answered_followup" ? (
        <div className="flex flex-wrap gap-3">
          <Button onClick={onNext}>下一题</Button>
        </div>
      ) : null}
    </motion.div>
  );
}
