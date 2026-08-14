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

interface QuestionType {
  label: string;
  hint: string;
}

const QUESTION_TYPES: Record<string, QuestionType> = {
  selfIntro: { label: "自我介绍", hint: "介绍背景、经历与岗位匹配点" },
  jobCognition: { label: "岗位认知", hint: "考察你对岗位和公司的理解" },
  behavioral: { label: "行为经历", hint: "用 STAR 讲一件具体经历" },
  strengthsWeaknesses: { label: "优缺点", hint: "评价自己并举例说明" },
  situational: { label: "情景应变", hint: "给出假设场景下的处理方式" },
  career: { label: "职业规划", hint: "聊个人发展方向与稳定性" },
  opinion: { label: "观点认知", hint: "表达对某个话题的看法" },
  comprehensive: { label: "综合问答", hint: "综合考察表达能力与临场反应" },
};

function classifyQuestion(question: string, index: number): QuestionType {
  const q = question.replace(/\s+/g, "");

  if (/自我介绍|介绍.*自己/.test(q)) {
    return QUESTION_TYPES.selfIntro;
  }
  if (/为什么选择|为什么想|应聘动机|选择我们|了解.*岗位|岗位.*理解|对这个岗位|工作内容|岗位职责|核心职责|核心能力|岗位要求|胜任|入职后/.test(q)) {
    return QUESTION_TYPES.jobCognition;
  }
  if (/如果|假设|遇到.*怎么办|如何应对|怎么应对|如何处理|你会怎么|压力|加班|冲突|临时|紧急|突然/.test(q)) {
    return QUESTION_TYPES.situational;
  }
  if (/你的?[^，。]{0,12}(优点|缺点|不足|短板|优势)|(优点|缺点|不足|短板).{0,8}(自己|你)|评价自己|性格/.test(q)) {
    return QUESTION_TYPES.strengthsWeaknesses;
  }
  if (/分享一次|举例|经历|项目|实习|团队|做过|完成过|遇到.*困难|解决.*分歧|最难忘|最有成就感|失败/.test(q)) {
    return QUESTION_TYPES.behavioral;
  }
  if (/职业规划|未来.*年|发展目标|长期规划|期望薪资|薪资/.test(q)) {
    return QUESTION_TYPES.career;
  }
  if (/如何看待|你怎么看|怎么看|你的理解|你如何理解|谈谈.*看法|对.*认识/.test(q)) {
    return QUESTION_TYPES.opinion;
  }

  return index === 0 ? QUESTION_TYPES.selfIntro : QUESTION_TYPES.comprehensive;
}

function QuestionRoadmap({ state }: { state: InterviewState }) {
  const futureQuestions = state.questions.slice(state.current_index + 1);
  const remainingCount = futureQuestions.length;

  if (remainingCount === 0) {
    return (
      <motion.p
        key={`last-${state.current_index}`}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="mt-6 text-xs text-muted"
      >
        这是最后一题，答完即可结束。
      </motion.p>
    );
  }

  return (
    <section aria-label="后续题型预览" className="mt-8">
      <div className="hairline-gold" />
      <div className="mt-4 flex items-baseline gap-3">
        <p className="shrink-0 text-xs font-medium text-muted">后续 {remainingCount} 题</p>
        <div className="flex min-w-0 flex-1 flex-wrap gap-2">
          {futureQuestions.map((question, offset) => {
            const type = classifyQuestion(
              question,
              state.current_index + offset + 1,
            );
            return (
              <motion.span
                key={`${state.current_index}-${offset}-${type.label}`}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  duration: 0.35,
                  delay: offset * 0.06,
                  ease: [0.16, 1, 0.3, 1],
                }}
                title={type.hint}
                className="rounded-full border border-line bg-porcelain px-2.5 py-0.5 text-xs text-muted"
              >
                {offset + 1} · {type.label}
              </motion.span>
            );
          })}
        </div>
      </div>
    </section>
  );
}

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
      .jobLabels()
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
  const currentType = isFollowUp
    ? { label: "面试官追问", hint: "围绕当前回答深挖细节" }
    : classifyQuestion(state.current_question, state.current_index);

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
        <div className="flex flex-wrap items-center gap-2">
          <p className="text-sm font-semibold text-muted">
            {isFollowUp
              ? `第 ${questionNumber} 题 · 面试官追问`
              : `第 ${questionNumber} 题 / 共 ${state.total} 题`}
          </p>
          <span
            title={currentType.hint}
            className="rounded-full bg-fog px-2.5 py-0.5 text-xs font-semibold text-blue-deep"
          >
            {currentType.label}
          </span>
        </div>
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

      <QuestionRoadmap state={state} />
    </motion.div>
  );
}
