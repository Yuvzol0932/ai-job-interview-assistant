import { useEffect, useState } from "react";
import { motion } from "framer-motion";

interface LoadingStageProps {
  stages: string[];
  current: number;
  /** 后台请求真正结束时置为 true，全部步骤打勾并显示完成态 */
  done?: boolean;
}

const TIPS = [
  "回答行为面试题时，试试 STAR 法则：情境 → 任务 → 行动 → 结果。",
  "简历控制在一页左右，把与目标岗位最相关的经历放在最前面。",
  "面试前把岗位 JD 里的关键词记下来，回答时自然带出。",
  "说到项目经历时，用数字量化成果，比形容词更有说服力。",
  "回答“你最大的缺点”时，说一个正在改进的真实缺点，并给出方法。",
  "模拟面试别追求“完美答案”，练表达流畅度比背稿更重要。",
];

function formatElapsed(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60)
    .toString()
    .padStart(2, "0");
  const seconds = (totalSeconds % 60).toString().padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function CheckIcon() {
  return (
    <svg
      viewBox="0 0 16 16"
      className="size-3"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M3.5 8.5 6.5 11.5 12.5 4.5" />
    </svg>
  );
}

export function LoadingStage({ stages, current, done = false }: LoadingStageProps) {
  const safeCurrent = Math.min(Math.max(current, 0), Math.max(stages.length - 1, 0));
  const [elapsed, setElapsed] = useState(0);
  const [tipIndex, setTipIndex] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => setElapsed((seconds) => seconds + 1), 1000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    const timer = window.setInterval(
      () => setTipIndex((index) => (index + 1) % TIPS.length),
      7000,
    );
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div
      role="status"
      aria-live="polite"
      className="mx-auto max-w-xl rounded-card border border-line bg-surface p-6 shadow-card"
    >
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span
            aria-hidden="true"
            className={`flex size-4 shrink-0 items-center justify-center rounded-full border-2 ${
              done
                ? "border-blue-deep bg-blue-deep text-white"
                : "animate-spin border-blue border-t-transparent"
            }`}
          >
            {done ? <CheckIcon /> : null}
          </span>
          <p className="text-sm font-semibold text-ink">
            {done ? "已完成" : stages[safeCurrent] ?? "正在准备…"}
          </p>
        </div>
        <p className="text-xs tabular-nums text-muted">已用时 {formatElapsed(elapsed)}</p>
      </div>

      <ol className="mt-6 space-y-3">
        {stages.map((stage, index) => {
          const isDone = done || index < safeCurrent;
          const isActive = !done && index === safeCurrent;
          return (
            <li key={stage} className="flex items-center gap-3">
              <span
                aria-hidden="true"
                className={`flex size-5 shrink-0 items-center justify-center rounded-full border transition-colors duration-300 ${
                  isDone
                    ? "border-blue bg-blue text-white"
                    : isActive
                      ? "border-blue bg-fog text-blue"
                      : "border-line bg-surface text-muted"
                }`}
              >
                {isDone ? (
                  <CheckIcon />
                ) : isActive ? (
                  <span className="size-2 animate-pulse rounded-full bg-blue" />
                ) : (
                  <span className="size-1.5 rounded-full bg-[#C9D4E3]" />
                )}
              </span>
              <span
                className={`text-sm transition-colors duration-300 ${
                  isDone
                    ? "font-medium text-ink"
                    : isActive
                      ? "font-semibold text-blue"
                      : "text-muted"
                }`}
              >
                {stage}
              </span>
            </li>
          );
        })}
      </ol>

      {!done ? (
        <div className="mt-6 rounded-control border-l-2 border-gold bg-gold-soft px-4 py-3">
          <motion.p
            key={tipIndex}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="text-xs leading-relaxed text-muted"
          >
            求职小贴士 · {TIPS[tipIndex]}
          </motion.p>
        </div>
      ) : null}

      <p className="mt-4 text-xs text-muted">
        {done ? "正在整理结果…" : "通常需要 1–2 分钟，请稍候…"}
      </p>
    </div>
  );
}
