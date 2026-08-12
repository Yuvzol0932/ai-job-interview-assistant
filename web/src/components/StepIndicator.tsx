interface StepIndicatorProps {
  steps: string[];
  current: number;
}

export function StepIndicator({ steps, current }: StepIndicatorProps) {
  return (
    <ol className="flex flex-wrap items-center gap-2 sm:gap-3" aria-label="流程步骤">
      {steps.map((step, index) => {
        const done = index < current;
        const active = index === current;
        return (
          <li key={step} className="flex items-center gap-2 sm:gap-3">
            <span
              className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-semibold transition-colors duration-150 ${
                active
                  ? "bg-fog text-blue-deep"
                  : done
                    ? "bg-gold-soft text-gold"
                    : "text-muted"
              }`}
            >
              <span
                className={`flex size-5 items-center justify-center rounded-full border text-xs ${
                  active
                    ? "border-blue bg-blue text-white"
                    : done
                      ? "border-gold/40 bg-surface text-gold"
                      : "border-line bg-surface text-muted"
                }`}
              >
                {done ? "✓" : index + 1}
              </span>
              {step}
            </span>
            {index < steps.length - 1 ? (
              <span
                className={`h-px w-6 sm:w-10 ${
                  done ? "bg-gold/40" : "bg-line"
                }`}
                aria-hidden="true"
              />
            ) : null}
          </li>
        );
      })}
    </ol>
  );
}
