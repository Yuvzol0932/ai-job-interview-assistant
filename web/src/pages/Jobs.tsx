import { useEffect, useState } from "react";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { Field } from "../components/Field";
import { JobCard } from "../components/JobCard";
import { PageHeader } from "../components/PageHeader";
import { api } from "../lib/api";
import type { JobFilters, JobPosting } from "../types";

export function Jobs() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [filters, setFilters] = useState<JobFilters>({
    categories: [],
    locations: [],
    sources: [],
  });
  const [category, setCategory] = useState("");
  const [location, setLocation] = useState("");
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const res = await api.jobs({
        category: category || undefined,
        location: location || undefined,
        keyword: keyword.trim() || undefined,
      });
      setJobs(res.jobs);
      setFilters(res.filters);
    } catch (err) {
      setError(err instanceof Error ? err.message : "岗位加载失败，请重试。");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [category, location, keyword]);

  async function handleRefresh() {
    setRefreshing(true);
    setNotice("");
    setError("");
    try {
      const res = await api.refreshJobs();
      setNotice(
        res.errors.length
          ? `已更新 ${res.fetched} 条，${res.errors.length} 个数据源更新失败`
          : `已更新 ${res.fetched} 条，当前共 ${res.total} 条岗位`,
      );
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "岗位更新失败，请稍后重试。");
    } finally {
      setRefreshing(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="企业招聘"
        caption="浏览可投递岗位，按岗位方向、城市与关键词筛选。"
      />

      <Card className="mb-6">
        <div className="grid gap-4 md:grid-cols-3">
          <Field label="岗位方向">
            <select
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              className="w-full rounded-control border border-line bg-surface px-4 py-2.5 text-sm text-ink transition-colors duration-150 focus:border-blue focus:ring-2 focus:ring-blue/20"
            >
              <option value="">全部方向</option>
              {filters.categories.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </Field>
          <Field label="工作地点">
            <select
              value={location}
              onChange={(event) => setLocation(event.target.value)}
              className="w-full rounded-control border border-line bg-surface px-4 py-2.5 text-sm text-ink transition-colors duration-150 focus:border-blue focus:ring-2 focus:ring-blue/20"
            >
              <option value="">全部城市</option>
              {filters.locations.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </Field>
          <Field label="关键词">
            <input
              value={keyword}
              onChange={(event) => setKeyword(event.target.value)}
              placeholder="例如：公众号、数据分析…"
              className="w-full rounded-control border border-line bg-surface px-4 py-2.5 text-sm text-ink transition-colors duration-150 focus:border-blue focus:ring-2 focus:ring-blue/20"
            />
          </Field>
        </div>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-muted">
            共 {loading ? "…" : jobs.length} 条岗位
            {notice ? ` · ${notice}` : ""}
          </p>
          <Button variant="secondary" onClick={() => void handleRefresh()} loading={refreshing}>
            更新岗位
          </Button>
        </div>
      </Card>

      {error ? (
        <div
          role="alert"
          className="mb-6 rounded-control border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {error}
        </div>
      ) : null}

      {loading ? (
        <p className="py-10 text-center text-sm text-muted">正在加载岗位…</p>
      ) : jobs.length ? (
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      ) : (
        <div className="rounded-control border border-dashed border-line bg-surface/60 px-6 py-12 text-center">
          <p className="font-semibold text-ink">没有找到符合条件的岗位</p>
          <p className="mt-1 text-sm text-muted">试试清空筛选条件或更换关键词。</p>
        </div>
      )}
    </div>
  );
}
