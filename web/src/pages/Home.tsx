import { Link } from "react-router-dom";
import { motion } from "framer-motion";

const ease: [number, number, number, number] = [0.16, 1, 0.3, 1];

const steps = [
  {
    title: "简历诊断",
    oneLine: "粘贴或上传简历，先找出没写清楚的地方。",
    detail: "AI 先问清缺失信息，再对照目标岗位与当地市场，给出专属优化方案。",
    to: "/resume",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="size-5">
        <path d="M6 3h9l4 4v14H6z" strokeLinejoin="round" />
        <path d="M14 3v5h5" strokeLinejoin="round" />
        <path d="M9 12h7M9 16h5" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: "模拟面试",
    oneLine: "选择岗位方向，像真实面试官一样逐题作答。",
    detail: "回答空泛时 AI 会追问细节，帮你把每一次练习变成下一次的底气。",
    to: "/interview",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="size-5">
        <path d="M4 5h16v11H9l-5 4z" strokeLinejoin="round" />
        <path d="M8 10h8M8 13h5" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: "面试复盘",
    oneLine: "五维评分 + 面试官手记，进步看得见。",
    detail: "逐题点评、成长建议与收尾鼓励，历史复盘随时回看、可删除。",
    to: "/review",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="size-5">
        <path d="M4 20V10M10 20V4M16 20v-7M21 20H3" strokeLinecap="round" />
      </svg>
    ),
  },
];

function DialPanel() {
  const ticks = Array.from({ length: 60 }, (_, index) => index * 6);
  const stations = [
    { angle: 150, label: "诊断", active: true },
    { angle: 90, label: "面试", active: false },
    { angle: 30, label: "复盘", active: false },
  ];

  function polar(angle: number, radius: number) {
    const rad = (angle * Math.PI) / 180;
    return { x: 100 + radius * Math.cos(rad), y: 100 - radius * Math.sin(rad) };
  }

  const needle = polar(150, 58);

  return (
    <div className="card-surface card-surface-hover relative mx-auto w-full max-w-md p-8 shadow-dial">
      <div className="hairline-gold mb-8" aria-hidden="true" />
      <svg viewBox="0 0 200 200" role="img" aria-label="求职备战三步校准：诊断、面试、复盘">
        <circle className="dial-ring" cx="100" cy="100" r="88" />
        <circle className="dial-ring" cx="100" cy="100" r="70" strokeOpacity="0.55" />
        {ticks.map((angle) => {
          const major = angle % 30 === 0;
          const outer = polar(angle, major ? 80 : 84);
          const inner = polar(angle, major ? 70 : 75);
          return (
            <line
              key={angle}
              className={major ? "dial-tick-major" : "dial-tick"}
              x1={outer.x}
              y1={outer.y}
              x2={inner.x}
              y2={inner.y}
            />
          );
        })}
        {stations.map((station) => {
          const point = polar(station.angle, 60);
          return (
            <g key={station.label}>
              <circle
                className="dial-station"
                cx={point.x}
                cy={point.y}
                r={station.active ? 5 : 4}
              />
            </g>
          );
        })}
        <line
          className="dial-needle"
          x1="100"
          y1="100"
          x2={needle.x}
          y2={needle.y}
        />
        <circle cx="100" cy="100" r="4.5" fill="#12213A" />
      </svg>
      <div className="mt-8 grid grid-cols-3 gap-3 text-center">
        {stations.map((station, index) => (
          <div key={station.label}>
            <span
              className={`text-xs font-semibold ${
                station.active ? "text-blue" : "text-muted"
              }`}
            >
              第 {index + 1} 步
            </span>
            <p className={`text-sm font-semibold ${station.active ? "text-ink" : "text-muted"}`}>
              {station.label}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export function Home() {
  return (
    <div>
      <section className="grid items-center gap-12 py-8 lg:grid-cols-[1.05fr_0.95fr] lg:py-16">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, ease }}
        >
          <h1 className="hero-title max-w-xl text-4xl font-extrabold leading-[1.12] tracking-tight text-ink md:text-6xl">
            把每一次练习，都变成下一次面试的底气。
          </h1>
          <p className="mt-6 max-w-lg text-base leading-relaxed text-muted md:text-lg">
            面向校园求职的 AI 面试教练：先诊断简历，再模拟面试，最后拿到一份面试官口吻的复盘。
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-3">
            <Link
              to="/resume"
              className="inline-flex items-center justify-center rounded-control bg-blue px-5 py-2.5 text-sm font-semibold text-white shadow-btn transition-all duration-150 hover:bg-blue-deep hover:shadow-[0_10px_26px_-8px_rgba(22,104,227,0.5)]"
            >
              开始简历诊断
            </Link>
            <Link
              to="/review"
              className="inline-flex items-center justify-center rounded-control border border-line bg-surface/70 px-5 py-2.5 text-sm font-semibold text-ink backdrop-blur-sm transition-all duration-150 hover:border-[#A9C7F2] hover:shadow-card-hover"
            >
              查看面试复盘
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.1, ease }}
        >
          <DialPanel />
        </motion.div>
      </section>

      <section className="py-12 lg:py-16">
        <div className="mb-10 max-w-2xl">
          <h2 className="text-2xl font-bold tracking-tight text-ink md:text-3xl">
            三步走完求职备战
          </h2>
          <div className="hairline-gold mt-4 w-16" aria-hidden="true" />
        </div>
        <div className="grid gap-5 md:grid-cols-3">
          {steps.map((step, index) => (
            <motion.article
              key={step.title}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ duration: 0.45, delay: 0.06 * index, ease }}
              className="group"
            >
              <Link to={step.to} className="block h-full">
                <div className="card-surface card-surface-hover flex h-full flex-col p-6">
                  <div className="flex items-start justify-between">
                    <span className="flex size-11 items-center justify-center rounded-control bg-fog text-blue transition-colors duration-180 group-hover:bg-blue group-hover:text-white">
                      {step.icon}
                    </span>
                    <span className="text-xs font-semibold tabular-nums text-gold">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                  </div>
                  <h3 className="mt-5 text-lg font-bold text-ink">{step.title}</h3>
                  <p className="mt-1.5 text-sm text-muted">{step.oneLine}</p>
                  <p className="mt-3 text-sm leading-relaxed text-muted opacity-0 transition-all duration-200 group-hover:opacity-100">
                    {step.detail}
                  </p>
                  <span className="mt-auto pt-5 text-sm font-semibold text-blue">
                    开始 →
                  </span>
                </div>
              </Link>
            </motion.article>
          ))}
        </div>
      </section>

      <section className="border-t border-line/70 py-12 lg:py-16">
        <h2 className="text-xl font-bold text-ink">适合谁用</h2>
        <div className="mt-8 grid gap-8 md:grid-cols-3">
          {[
            ["正在准备校招、实习面试的同学", "投递前先发现简历问题，面试前先熟悉节奏。"],
            ["简历投出没有回音的同学", "用岗位对照找出证据缺口，知道该改哪里。"],
            ["想练习表达、提升临场的同学", "逐题作答 + 追问，在复盘里看到真实进步。"],
          ].map(([title, desc]) => (
            <div key={title} className="border-t border-line pt-5">
              <h3 className="font-semibold text-ink">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted">{desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
