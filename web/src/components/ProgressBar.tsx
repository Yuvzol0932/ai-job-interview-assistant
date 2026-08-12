import { motion } from "framer-motion";

export function ProgressBar({ value, label }: { value: number; label?: string }) {
  const safe = Math.min(Math.max(value, 0), 1);
  return (
    <div>
      {label ? (
        <div className="mb-1.5 flex items-center justify-between text-sm">
          <span className="text-ink">{label}</span>
          <span className="tabular-nums text-muted">{Math.round(safe * 100)}%</span>
        </div>
      ) : null}
      <div className="h-2 overflow-hidden rounded-full bg-fog">
        <motion.div
          className="h-full rounded-full bg-linear-to-r from-blue to-[#6FA3F0]"
          initial={false}
          animate={{ width: `${safe * 100}%` }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
    </div>
  );
}
