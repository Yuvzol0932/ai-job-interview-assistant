import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  loading?: boolean;
  children: ReactNode;
}

const variantClass: Record<Variant, string> = {
  primary:
    "bg-blue text-white shadow-btn hover:bg-blue-deep hover:shadow-[0_10px_26px_-8px_rgba(22,104,227,0.5)]",
  secondary:
    "bg-surface/70 text-ink border border-line backdrop-blur-sm hover:border-[#A9C7F2] hover:shadow-card-hover",
  ghost: "bg-transparent text-blue hover:bg-fog/70",
};

export function Button({
  variant = "primary",
  loading = false,
  disabled,
  className = "",
  children,
  ...rest
}: ButtonProps) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-control px-5 py-2.5 text-sm font-semibold transition-all duration-150 disabled:cursor-not-allowed disabled:opacity-60";
  return (
    <button
      className={`${base} ${variantClass[variant]} ${className}`}
      disabled={disabled || loading}
      {...rest}
    >
      {loading && (
        <span
          aria-hidden="true"
          className="size-4 animate-spin rounded-full border-2 border-current border-t-transparent"
        />
      )}
      {children}
    </button>
  );
}
