import { motion } from "framer-motion";

interface LoadingStageProps {
  stages: string[];
  current: number;
}

export function LoadingStage({ stages, current }: LoadingStageProps) {
  const safeCurrent = Math.min(Math.max(current, 0), stages.length - 1);
  const progress = (safeCurrent + 1) / stages.length;

  return (
    <div
      role="status"
      aria-live="polite"
      className="mx-auto max-w-xl rounded-card border border-line bg-surface p-6 shadow-card"
    >
      <div className="flex items-center gap-3">
        <span
          aria-hidden="true"
          className="size-4 animate-spin rounded-full border-2 border-blue border-t-transparent"
        />
        <p className="text-sm font-semibold text-ink">{stages[safeCurrent]}</p>
      </div>
      <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-fog">
        <motion.div
          className="h-full rounded-full bg-linear-to-r from-blue to-[#6FA3F0]"
          initial={{ width: "8%" }}
          animate={{ width: `${Math.max(progress * 100, 12)}%` }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
      <p className="mt-2 text-right text-xs tabular-nums text-muted">
        {Math.round(progress * 100)}%
      </p>
    </div>
  );
}
