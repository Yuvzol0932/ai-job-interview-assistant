import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

interface LoadingStageProps {
  stages: string[];
  current: number;
  /** 后台请求真正结束时置为 true，进度条才跳到 100% */
  done?: boolean;
}

/** 运行中最高逼近 90%，拿到结果前绝不“满格”，避免用户误以为卡死 */
const TARGET = 0.9;

export function LoadingStage({ stages, current, done = false }: LoadingStageProps) {
  const safeCurrent = Math.min(Math.max(current, 0), stages.length - 1);
  const [progress, setProgress] = useState(0.08);
  const frameRef = useRef<number | null>(null);

  useEffect(() => {
    if (done) {
      setProgress(1);
      return;
    }
    const tick = () => {
      setProgress((prev) => Math.min(prev + (TARGET - prev) * 0.02, TARGET));
      frameRef.current = window.requestAnimationFrame(tick);
    };
    frameRef.current = window.requestAnimationFrame(tick);
    return () => {
      if (frameRef.current !== null) window.cancelAnimationFrame(frameRef.current);
    };
  }, [done]);

  const percent = Math.round(progress * 100);

  return (
    <div
      role="status"
      aria-live="polite"
      className="mx-auto max-w-xl rounded-card border border-line bg-surface p-6 shadow-card"
    >
      <div className="flex items-center gap-3">
        <span
          aria-hidden="true"
          className={`size-4 rounded-full border-2 border-blue border-t-transparent ${
            done ? "border-blue-deep" : "animate-spin"
          }`}
        />
        <p className="text-sm font-semibold text-ink">
          {done ? "已完成" : stages[safeCurrent]}
        </p>
      </div>
      <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-fog">
        <motion.div
          className={`h-full rounded-full bg-linear-to-r from-blue to-[#6FA3F0] ${
            done ? "" : "loading-shimmer"
          }`}
          initial={{ width: "8%" }}
          animate={{ width: `${percent}%` }}
          transition={{ duration: 0.25, ease: "easeOut" }}
        />
      </div>
      <div className="mt-2 flex items-center justify-between gap-4">
        <p className="text-xs text-muted">
          {done ? "正在整理结果…" : "AI 生成中，通常需要 1–2 分钟，请稍候…"}
        </p>
        <p className="text-xs tabular-nums text-muted">{percent}%</p>
      </div>
    </div>
  );
}
