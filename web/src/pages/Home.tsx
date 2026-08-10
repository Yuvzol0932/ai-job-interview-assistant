import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Card } from "../components/Card";

const journeyNodes = [
  { label: "01 简历诊断", left: "14%" },
  { label: "02 模拟面试", left: "50%" },
  { label: "03 面试复盘", left: "86%" },
];

function Journey() {
  const trackRef = useRef<HTMLDivElement>(null);
  const dotRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const track = trackRef.current;
    const dot = dotRef.current;
    if (!track || !dot) return;
    const update = () => {
      const range = track.clientWidth - dot.offsetWidth;
      track.style.setProperty("--journey-range", `${range}px`);
    };
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  return (
    <div
      ref={trackRef}
      aria-label="三步求职旅程：简历诊断、模拟面试、面试复盘"
      className="journey-track relative h-72 overflow-hidden rounded-card border border-line bg-gradient-to-br from-surface via-fog to-[#FCFAF3] shadow-card"
    >
      <div
        aria-hidden="true"
        className="absolute inset-[-40%] opacity-60"
        style={{
          backgroundImage:
            "repeating-linear-gradient(135deg, rgba(22,104,227,0.06) 0 1px, transparent 1px 44px)",
        }}
      />
      <div ref={dotRef} className="journey-dot" aria-hidden="true" />
      {journeyNodes.map((node, index) => (
        <div
          key={node.label}
          className="absolute top-1/2 -translate-x-1/2 -translate-y-1/2 text-center"
          style={{ left: node.left }}
        >
          <span
            className={`journey-ring mx-auto flex size-4 items-center justify-center rounded-full border-2 border-gold bg-surface ${
              index === 1 ? "[animation-delay:0.8s]" : index === 2 ? "[animation-delay:1.6s]" : ""
            }`}
            aria-hidden="true"
          />
          <span className="mt-3 inline-block whitespace-nowrap rounded-full border border-line bg-surface/90 px-3 py-1.5 text-xs font-semibold text-ink shadow-sm">
            {node.label}
          </span>
        </div>
      ))}
    </div>
  );
}

export function Home() {
  return (
    <div>
      <section className="pb-10 pt-4 md:pt-8">
        <h1 className="max-w-3xl text-4xl font-extrabold leading-tight tracking-tight text-ink md:text-6xl">
          把每一次练习，都变成下一次面试的底气。
        </h1>
        <p className="mt-4 max-w-2xl text-base text-muted md:text-lg">
          校园求职 · AI 求职面试助手 —— 诊断简历 → 模拟面试 → 拿到面试官手记。
        </p>
      </section>

      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
      >
        <Journey />
      </motion.section>

      <section className="mt-8 grid gap-5 md:grid-cols-3">
        {[
          {
            to: "/resume",
            title: "① 简历诊断",
            desc: "上传或粘贴简历，AI 先问清缺失信息，再给出专属优化方案。",
          },
          {
            to: "/interview",
            title: "② 模拟面试",
            desc: "选择岗位方向，像真实面试官一样逐题问答，答完还可以被追问细节。",
          },
          {
            to: "/review",
            title: "③ 面试复盘",
            desc: "面试官手记：五维评分、逐题点评、成长建议，历史随时回看。",
          },
        ].map((entry, index) => (
          <motion.div
            key={entry.to}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.08 * index, ease: [0.16, 1, 0.3, 1] }}
          >
            <Card hover className="flex h-full flex-col">
              <h2 className="text-lg font-bold text-ink">{entry.title}</h2>
              <p className="mt-2 flex-1 text-sm leading-relaxed text-muted">{entry.desc}</p>
              <Link
                to={entry.to}
                className="mt-5 inline-flex items-center justify-center rounded-control bg-blue px-4 py-2.5 text-sm font-semibold text-white shadow-btn transition-all duration-150 hover:bg-blue-deep"
              >
                开始
              </Link>
            </Card>
          </motion.div>
        ))}
      </section>

      <section className="mt-14">
        <h2 className="text-xl font-bold text-ink">适合谁用</h2>
        <div className="mt-5 grid gap-5 md:grid-cols-3">
          {[
            ["正在准备校招、实习面试的同学", "投递前先发现简历问题，面试前先熟悉节奏。"],
            ["简历投出没有回音的同学", "用岗位对照找出证据缺口，知道改哪里。"],
            ["想练习表达、提升临场的同学", "逐题作答 + 追问，复盘里看到真实进步。"],
          ].map(([title, desc]) => (
            <div key={title} className="rounded-card border border-line bg-surface p-5 shadow-card">
              <h3 className="font-semibold text-ink">{title}</h3>
              <p className="mt-1.5 text-sm text-muted">{desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
