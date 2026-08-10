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
                  ? "bg-blue text-white shadow-btn"
                  : done
                    ? "bg-fog text-blue-deep"
                    : "bg-surface text-muted border border-line"
              }`}
            >
              <span
                className={`flex size-5 items-center justify-center rounded-full text-xs ${
                  active ? "bg-white/20" : done ? "bg-blue/15" : "bg-canvas"
                }`}
              >
                {done ? "✓" : index + 1}
              </span>
              {step}
            </span>
            {index < steps.length - 1 ? (
              <span className="h-px w-6 bg-line sm:w-10" aria-hidden="true" />
            ) : null}
          </li>
        );
      })}
    </ol>
  );
}
