import type { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  hover?: boolean;
}

export function Card({ children, hover = false, className = "", ...rest }: CardProps) {
  return (
    <div
      className={`card-surface p-5 ${hover ? "card-surface-hover" : ""} ${className}`}
      {...rest}
    >
      {children}
    </div>
  );
}
