"use client";

interface StatusBlockProps {
  title: string;
  message: string;
  actionLabel?: string;
  className?: string;
  onAction?: () => void;
  tone?: "neutral" | "error";
}

interface SkeletonBlockProps {
  className?: string;
  rows?: number;
}

export function StatusBlock({
  title,
  message,
  actionLabel,
  className = "",
  onAction,
  tone = "neutral"
}: StatusBlockProps) {
  return (
    <div className={`state-block ${tone} ${className}`}>
      <strong>{title}</strong>
      <p>{message}</p>
      {actionLabel && onAction ? (
        <button className="state-button" onClick={onAction} type="button">
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}

export function SkeletonBlock({ className = "", rows = 3 }: SkeletonBlockProps) {
  return (
    <div className={`skeleton-block ${className}`} aria-label="Loading" role="status">
      {Array.from({ length: rows }).map((_, index) => (
        <span className="skeleton-line" key={index} />
      ))}
    </div>
  );
}

export function SkeletonValue() {
  return <span className="skeleton-value" aria-label="Loading" role="status" />;
}
