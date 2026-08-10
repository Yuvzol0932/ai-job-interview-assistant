import type { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  hover?: boolean;
}

export function Card({ children, hover = false, className = "", ...rest }: CardProps) {
  return (
    <div
      className={`rounded-card border border-line bg-surface p-5 shadow-card transition-all duration-180 ${
        hover ? "hover:-translate-y-0.5 hover:shadow-card-hover" : ""
      } ${className}`}
      {...rest}
    >
      {children}
    </div>
  );
}
