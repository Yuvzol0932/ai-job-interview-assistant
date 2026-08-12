import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { api } from "../lib/api";

const navItems = [
  { to: "/", label: "首页" },
  { to: "/resume", label: "简历诊断" },
  { to: "/interview", label: "模拟面试" },
  { to: "/review", label: "面试复盘" },
];

export function Layout() {
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    api
      .health()
      .then(() => mounted && setOnline(true))
      .catch(() => mounted && setOnline(false));
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="relative min-h-screen">
      <div className="app-bg" aria-hidden="true" />
      <header className="glass-header">
        <div className="mx-auto flex w-full max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6 lg:px-8">
          <NavLink to="/" className="text-lg font-extrabold tracking-tight text-ink">
            AI 求职面试助手
          </NavLink>
          <nav className="flex items-center gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  `relative rounded-full px-3 py-1.5 text-sm font-semibold transition-colors duration-150 sm:px-4 ${
                    isActive
                      ? "bg-fog text-blue"
                      : "text-muted hover:bg-fog/60 hover:text-blue"
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    {item.label}
                    {isActive ? (
                      <span
                        className="absolute inset-x-3 -bottom-0.5 h-px bg-gold"
                        aria-hidden="true"
                      />
                    ) : null}
                  </>
                )}
              </NavLink>
            ))}
          </nav>
          <div
            className={`flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium ${
              online === null
                ? "border-gold/30 bg-gold-soft text-gold"
                : online
                  ? "border-blue/20 bg-fog text-blue-deep"
                  : "border-line bg-surface text-muted"
            }`}
          >
            <span
              className={`size-1.5 rounded-full ${
                online === null ? "bg-gold" : online ? "bg-blue" : "bg-muted"
              }`}
              aria-hidden="true"
            />
            {online === null
              ? "正在连接服务…"
              : online
                ? "服务已连接"
                : "服务未连接，请先启动后端"}
          </div>
        </div>
      </header>
      <main className="relative z-10 mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 md:py-12 lg:px-8">
        <Outlet />
      </main>
      <footer className="relative z-10 border-t border-line/70 py-6 text-center text-xs text-muted">
        校园求职 · AI 求职面试助手 —— 诊断简历 → 模拟面试 → 拿到面试官手记
      </footer>
    </div>
  );
}
