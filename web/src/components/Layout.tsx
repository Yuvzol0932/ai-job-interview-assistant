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
    <div className="min-h-screen">
      <div className="h-0.5 bg-gradient-to-r from-blue via-[#7FB0F5] to-gold" />
      <header className="sticky top-0 z-40 border-b border-line bg-surface/90 backdrop-blur">
        <div className="mx-auto flex w-full max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6 lg:px-8">
          <NavLink to="/" className="text-lg font-extrabold tracking-tight text-ink">
            AI 求职面试助手
          </NavLink>
          <nav className="flex items-center gap-1 rounded-full border border-line bg-surface p-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  `rounded-full px-3 py-1.5 text-sm font-semibold transition-colors duration-150 sm:px-4 ${
                    isActive
                      ? "bg-blue text-white shadow-btn"
                      : "text-muted hover:bg-fog hover:text-blue"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="flex items-center gap-2 text-xs text-muted">
            <span
              className={`size-2 rounded-full ${
                online === null
                  ? "bg-gold"
                  : online
                    ? "bg-blue"
                    : "bg-muted"
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
      <main className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 md:py-12 lg:px-8">
        <Outlet />
      </main>
      <footer className="border-t border-line py-6 text-center text-xs text-muted">
        校园求职 · AI 求职面试助手 —— 诊断简历 → 模拟面试 → 拿到面试官手记
      </footer>
    </div>
  );
}
