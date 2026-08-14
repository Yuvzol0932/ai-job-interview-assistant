import type { JobPosting, MatchedJob } from "../types";

interface JobCardProps {
  job: JobPosting | MatchedJob;
}

function isMatched(job: JobPosting | MatchedJob): job is MatchedJob {
  return "match_score" in job;
}

export function JobCard({ job }: JobCardProps) {
  const matched = isMatched(job) ? job : null;
  const requirements = job.requirements.slice(0, 3);

  return (
    <article className="card-surface flex h-full flex-col p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-fog px-2.5 py-1 text-xs font-semibold text-blue">
              {job.category}
            </span>
            {matched ? (
              <span
                className={`rounded-full px-2.5 py-1 text-xs font-bold tabular-nums ${
                  matched.match_score >= 70
                    ? "bg-blue/10 text-blue-deep"
                    : matched.match_score >= 50
                      ? "bg-gold-soft text-gold"
                      : "bg-canvas text-muted"
                }`}
              >
                匹配度 {matched.match_score}
              </span>
            ) : null}
          </div>
          <h3 className="mt-2 text-base font-bold text-ink">{job.title}</h3>
          <p className="mt-1 text-sm text-muted">{job.company}</p>
        </div>
        <span className="whitespace-nowrap text-sm font-semibold text-ink">
          {job.salary}
        </span>
      </div>

      <div className="mt-3 flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted">
        <span>{job.location || "地点待定"}</span>
        {job.education ? <span>{job.education}</span> : null}
        {job.experience ? <span>{job.experience}</span> : null}
      </div>

      {requirements.length ? (
        <ul className="mt-3 space-y-1.5 text-sm leading-relaxed text-muted">
          {requirements.map((item) => (
            <li key={item} className="flex gap-2">
              <span className="text-gold" aria-hidden="true">
                ·
              </span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : null}

      {job.description ? (
        <p className="mt-3 text-sm leading-relaxed text-ink">{job.description}</p>
      ) : null}

      {matched && matched.match_reasons.length ? (
        <div className="mt-3 rounded-control bg-fog/70 px-3 py-2">
          <p className="text-xs font-semibold text-blue-deep">推荐理由</p>
          <ul className="mt-1 space-y-1 text-xs leading-relaxed text-ink">
            {matched.match_reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {matched && matched.gap_hints.length ? (
        <p className="mt-3 text-xs leading-relaxed text-muted">
          简历差距：{matched.gap_hints.join("；")}
        </p>
      ) : null}

      <footer className="mt-auto flex flex-wrap items-center justify-between gap-2 border-t border-line/70 pt-3 text-xs text-muted">
        <span>
          {job.source_label}
          {job.deadline ? ` · 截止 ${job.deadline}` : ""}
        </span>
        {job.url ? (
          <a
            href={job.url}
            target="_blank"
            rel="noreferrer"
            className="font-semibold text-blue underline-offset-4 hover:underline"
          >
            查看详情
          </a>
        ) : (
          <span>投递方式待补充</span>
        )}
      </footer>
    </article>
  );
}
