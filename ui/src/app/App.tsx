import { useState, useCallback, useEffect } from "react";
import { ChevronLeft, ChevronRight, BookOpen, Calendar, LayoutDashboard } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

// ─── Types ───────────────────────────────────────────────────────────────────

type TransactionType = "expense" | "income";

interface Transaction {
  id: string;
  type: TransactionType;
  amount: number;
  category: string;
  memo: string;
  date: string; // YYYY-MM-DD
}

// ─── Constants ───────────────────────────────────────────────────────────────

const EXPENSE_CATEGORIES = [
  { label: "食費",   icon: "🍽️" },
  { label: "日用品", icon: "🛒" },
  { label: "交通費", icon: "🚃" },
  { label: "その他", icon: "📌" },
];

const INCOME_CATEGORIES = [
  { label: (import.meta.env.VITE_INCOME_P1 as string) || "Person1", icon: "👨" },
  { label: (import.meta.env.VITE_INCOME_P2 as string) || "Person2", icon: "👩" },
];

const WEEKDAYS = ["日", "月", "火", "水", "木", "金", "土"];

const todayStr = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};

// ─── Seed data ───────────────────────────────────────────────────────────────

const SEED: Transaction[] = [
  { id: "1", type: "expense", amount: 880,    category: "食費",   memo: "ランチ",     date: "2026-07-06" },
  { id: "2", type: "expense", amount: 2000,   category: "その他", memo: "公共料金",   date: "2026-07-06" },
  { id: "3", type: "expense", amount: 8000,   category: "その他", memo: "友人の誕生日", date: "2026-07-05" },
  { id: "4", type: "expense", amount: 2500,   category: "その他", memo: "美容室",     date: "2026-07-05" },
  { id: "5", type: "expense", amount: 1000,   category: "食費",   memo: "コンビニ",   date: "2026-07-04" },
  { id: "6", type: "income",  amount: 350000, category: (import.meta.env.VITE_INCOME_P1 as string) || "Person1", memo: "7月分", date: "2026-07-01" },
  { id: "7", type: "expense", amount: 10500,  category: "その他", memo: "コンサート", date: "2026-07-10" },
  { id: "8", type: "expense", amount: 3500,   category: "交通費", memo: "定期券",     date: "2026-07-03" },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

function fmt(n: number) {
  return n.toLocaleString("ja-JP");
}

// ─── Category Picker Modal ────────────────────────────────────────────────────

function CategoryPicker({
  type,
  selected,
  onSelect,
  onClose,
}: {
  type: TransactionType;
  selected: string;
  onSelect: (c: string) => void;
  onClose: () => void;
}) {
  const cats = type === "expense" ? EXPENSE_CATEGORIES : INCOME_CATEGORIES;
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={onClose}>
      <div
        className="w-full max-w-md bg-card rounded-t-2xl pb-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <span className="text-base font-semibold text-card-foreground">カテゴリーを選択</span>
          <button
            onClick={onClose}
            className="text-sm text-primary font-medium px-2 py-1 rounded hover:bg-secondary transition-colors"
          >
            閉じる
          </button>
        </div>
        <div className="grid grid-cols-3 gap-2 px-4 pt-4">
          {cats.map((c) => (
            <button
              key={c.label}
              onClick={() => { onSelect(c.label); onClose(); }}
              className={`flex flex-col items-center gap-1 py-3 rounded-xl border transition-all text-sm font-medium
                ${selected === c.label
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border bg-secondary text-card-foreground hover:border-primary/40"
                }`}
            >
              <span className="text-xl">{c.icon}</span>
              <span>{c.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Register Screen ──────────────────────────────────────────────────────────

function RegisterScreen({ onSave }: { onSave: (t: Transaction) => void }) {
  const [type, setType] = useState<TransactionType>("expense");
  const [amountStr, setAmountStr] = useState("0");
  const [category, setCategory] = useState("食費");
  const [memo, setMemo] = useState("");
  const [date, setDate] = useState(todayStr());
  const [showCatPicker, setShowCatPicker] = useState(false);

  const handlePad = useCallback((key: string) => {
    if (key === "←") {
      setAmountStr((s) => (s.length <= 1 ? "0" : s.slice(0, -1)));
    } else if (key === ".") {
      // ignore decimals for JPY
    } else {
      setAmountStr((s) => {
        if (s === "0") return key;
        if (s.length >= 10) return s;
        return s + key;
      });
    }
  }, []);

  const handleSave = () => {
    const amount = parseInt(amountStr, 10);
    if (!amount) return;
    onSave({
      id: Date.now().toString(),
      type,
      amount,
      category,
      memo,
      date,
    });
    setAmountStr("0");
    setMemo("");
  };

  const cats = type === "expense" ? EXPENSE_CATEGORIES : INCOME_CATEGORIES;
  const catIcon = cats.find((c) => c.label === category)?.icon ?? "📌";

  const PAD = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    [".", "0", "←"],
  ];

  return (
    <div className="flex flex-col h-full bg-secondary">
      {/* Type toggle */}
      <div className="flex gap-0 mx-4 mt-4 rounded-lg overflow-hidden border border-border bg-card shadow-sm">
        {(["expense", "income"] as TransactionType[]).map((t) => (
          <button
            key={t}
            onClick={() => {
              setType(t);
              setCategory(t === "expense" ? "食費" : INCOME_CATEGORIES[0].label);
            }}
            className={`flex-1 py-2.5 text-sm font-semibold transition-colors
              ${type === t ? "bg-primary text-primary-foreground" : "bg-card text-muted-foreground hover:bg-muted"}`}
          >
            {t === "expense" ? "支出" : "収入"}
          </button>
        ))}
      </div>

      {/* Amount display */}
      <div className="mx-4 mt-3 bg-card rounded-xl shadow-sm border border-border px-5 py-4 flex items-center justify-between">
        <span className="text-xl text-muted-foreground font-medium">¥</span>
        <span
          className={`flex-1 text-right text-4xl font-bold tracking-tight ${
            type === "expense" ? "text-red-500" : "text-emerald-600"
          }`}
        >
          {fmt(parseInt(amountStr, 10) || 0)}
        </span>
        <span className="text-xl text-muted-foreground font-medium ml-1">円</span>
      </div>

      {/* Fields */}
      <div className="mx-4 mt-3 bg-card rounded-xl shadow-sm border border-border divide-y divide-border overflow-hidden">
        <div
          className="flex items-center justify-between px-5 py-3.5 cursor-pointer hover:bg-secondary/60 transition-colors"
          onClick={() => setShowCatPicker(true)}
        >
          <span className="text-sm font-medium text-muted-foreground">カテゴリー</span>
          <div className="flex items-center gap-1.5 text-sm font-medium text-card-foreground">
            <span>{catIcon}</span>
            <span>{category}</span>
            <ChevronRight className="w-4 h-4 text-muted-foreground" />
          </div>
        </div>
        <div className="flex items-center justify-between px-5 py-3">
          <span className="text-sm font-medium text-muted-foreground">メモ</span>
          <input
            type="text"
            value={memo}
            onChange={(e) => setMemo(e.target.value)}
            placeholder="メモを入力"
            className="text-right text-sm font-medium bg-transparent outline-none text-card-foreground placeholder:text-muted-foreground/60 w-40"
          />
        </div>
        <div className="flex items-center justify-between px-5 py-3">
          <span className="text-sm font-medium text-muted-foreground">日付</span>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="text-right text-sm font-medium bg-transparent outline-none text-card-foreground"
          />
        </div>
      </div>

      {/* Save */}
      <button
        onClick={handleSave}
        className="mx-4 mt-3 py-3 rounded-xl bg-primary text-primary-foreground font-semibold text-base shadow-sm hover:bg-primary/90 active:scale-[0.98] transition-all"
      >
        保存
      </button>

      {/* Numpad */}
      <div className="mt-auto mx-4 mb-4 grid grid-cols-3 gap-2">
        {PAD.flat().map((key) => (
          <button
            key={key}
            onClick={() => handlePad(key)}
            className={`py-4 rounded-xl text-lg font-semibold transition-all active:scale-95
              ${key === "←"
                ? "bg-muted text-muted-foreground hover:bg-muted/80"
                : "bg-card text-card-foreground shadow-sm border border-border hover:bg-secondary active:bg-muted"
              }`}
          >
            {key}
          </button>
        ))}
      </div>

      {showCatPicker && (
        <CategoryPicker
          type={type}
          selected={category}
          onSelect={setCategory}
          onClose={() => setShowCatPicker(false)}
        />
      )}
    </div>
  );
}

// ─── Calendar Screen ──────────────────────────────────────────────────────────

function CalendarScreen({ transactions }: { transactions: Transaction[] }) {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1); // 1-12

  const prevMonth = () => {
    if (month === 1) { setYear(y => y - 1); setMonth(12); }
    else setMonth(m => m - 1);
  };
  const nextMonth = () => {
    if (month === 12) { setYear(y => y + 1); setMonth(1); }
    else setMonth(m => m + 1);
  };

  // Build day map for current month
  const monthStr = `${year}-${String(month).padStart(2, "0")}`;
  const monthTx = transactions.filter((t) => t.date.startsWith(monthStr));

  const byDate: Record<string, { income: number; expense: number }> = {};
  for (const t of monthTx) {
    if (!byDate[t.date]) byDate[t.date] = { income: 0, expense: 0 };
    if (t.type === "income") byDate[t.date].income += t.amount;
    else byDate[t.date].expense += t.amount;
  }

  const totalIncome = monthTx.filter(t => t.type === "income").reduce((s, t) => s + t.amount, 0);
  const totalExpense = monthTx.filter(t => t.type === "expense").reduce((s, t) => s + t.amount, 0);
  const totalBalance = totalIncome - totalExpense;

  // Calendar grid
  const firstDay = new Date(year, month - 1, 1).getDay(); // 0=Sun
  const daysInMonth = new Date(year, month, 0).getDate();
  const cells: (number | null)[] = [
    ...Array(firstDay).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ];
  // pad to full rows
  while (cells.length % 7 !== 0) cells.push(null);

  // Grouped transaction list (sorted by date desc)
  const sortedDates = Object.keys(byDate).sort((a, b) => b.localeCompare(a));

  return (
    <div className="flex flex-col h-full bg-secondary overflow-y-auto">
      {/* Month nav */}
      <div className="flex items-center justify-between px-5 py-4 bg-primary text-primary-foreground">
        <button onClick={prevMonth} className="p-1 rounded-full hover:bg-white/20 transition-colors">
          <ChevronLeft className="w-5 h-5" />
        </button>
        <div className="text-center">
          <span className="text-base font-bold">{year}年{month}月</span>
        </div>
        <button onClick={nextMonth} className="p-1 rounded-full hover:bg-white/20 transition-colors">
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Weekday headers */}
      <div className="grid grid-cols-7 bg-primary/80">
        {WEEKDAYS.map((d, i) => (
          <div
            key={d}
            className={`py-1.5 text-center text-xs font-semibold
              ${i === 0 ? "text-red-200" : i === 6 ? "text-blue-200" : "text-primary-foreground/80"}`}
          >
            {d}
          </div>
        ))}
      </div>

      {/* Calendar cells */}
      <div className="grid grid-cols-7 border-l border-t border-border bg-card">
        {cells.map((day, idx) => {
          const col = idx % 7;
          const dateStr = day
            ? `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`
            : "";
          const info = dateStr ? byDate[dateStr] : undefined;
          const isToday = dateStr === todayStr();

          return (
            <div
              key={idx}
              className="border-r border-b border-border min-h-[60px] p-1 flex flex-col"
            >
              {day !== null && (
                <>
                  <span
                    className={`text-[11px] font-semibold w-5 h-5 flex items-center justify-center rounded-full mb-0.5
                      ${isToday ? "bg-primary text-primary-foreground" : ""}
                      ${col === 0 && !isToday ? "text-red-500" : ""}
                      ${col === 6 && !isToday ? "text-blue-500" : ""}
                      ${col > 0 && col < 6 && !isToday ? "text-card-foreground" : ""}`}
                  >
                    {day}
                  </span>
                  {info?.income ? (
                    <span className="text-[9px] font-medium text-emerald-600 leading-tight">
                      {fmt(info.income)}円
                    </span>
                  ) : null}
                  {info?.expense ? (
                    <span className="text-[9px] font-medium text-red-500 leading-tight">
                      {fmt(info.expense)}円
                    </span>
                  ) : null}
                </>
              )}
            </div>
          );
        })}
      </div>

      {/* Monthly summary */}
      <div className="grid grid-cols-3 divide-x divide-border bg-card border-b border-border mx-0">
        <div className="py-3 px-2 text-center">
          <p className="text-[10px] text-muted-foreground font-medium">収入</p>
          <p className="text-xs font-bold text-emerald-600">{fmt(totalIncome)}円</p>
        </div>
        <div className="py-3 px-2 text-center">
          <p className="text-[10px] text-muted-foreground font-medium">支出</p>
          <p className="text-xs font-bold text-red-500">{fmt(totalExpense)}円</p>
        </div>
        <div className="py-3 px-2 text-center">
          <p className="text-[10px] text-muted-foreground font-medium">合計</p>
          <p className={`text-xs font-bold ${totalBalance >= 0 ? "text-emerald-600" : "text-red-500"}`}>
            {fmt(totalBalance)}円
          </p>
        </div>
      </div>

      {/* Transaction list */}
      <div className="pb-4">
        {sortedDates.map((dateKey) => {
          const [y, m, d] = dateKey.split("-");
          const label = `${y}年${parseInt(m)}月${parseInt(d)}日`;
          const dayTx = transactions
            .filter((t) => t.date === dateKey)
            .sort((a, b) => b.id.localeCompare(a.id));

          return (
            <div key={dateKey}>
              <div className="px-4 py-2 bg-muted border-b border-border">
                <span className="text-xs font-semibold text-muted-foreground">{label}</span>
              </div>
              {dayTx.map((t) => {
                const cats = t.type === "expense" ? EXPENSE_CATEGORIES : INCOME_CATEGORIES;
                const icon = cats.find((c) => c.label === t.category)?.icon ?? "📌";
                return (
                  <div
                    key={t.id}
                    className="flex items-center justify-between px-4 py-3 bg-card border-b border-border"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-lg">{icon}</span>
                      <div>
                        <p className="text-sm font-medium text-card-foreground">{t.category}</p>
                        {t.memo ? (
                          <p className="text-xs text-muted-foreground">{t.memo}</p>
                        ) : null}
                      </div>
                    </div>
                    <span
                      className={`text-sm font-bold ${
                        t.type === "income" ? "text-emerald-600" : "text-red-500"
                      }`}
                    >
                      {t.type === "income" ? "+" : "-"}{fmt(t.amount)}円
                    </span>
                  </div>
                );
              })}
            </div>
          );
        })}
        {sortedDates.length === 0 && (
          <div className="py-12 text-center text-muted-foreground text-sm">
            この月の取引はありません
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Dashboard Screen ─────────────────────────────────────────────────────────

interface WeeklySummary {
  period: { start: string; end: string };
  food: { 自炊: number; 外食: number; その他: number };
  food_total: number;
  withdrawal: Record<string, number>;
  withdrawal_total: number;
}

const CHART_COLORS = ["#667eea", "#764ba2", "#ed64a6", "#ff9a9e", "#fad0c4", "#a1c4fd"];

function DashboardScreen() {
  const [stats, setStats] = useState<{ total: number; categories: number } | null>(null);
  const [chartData, setChartData] = useState<{ category: string; count: number }[]>([]);
  const [weekly, setWeekly] = useState<WeeklySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const apiUrl = (import.meta.env.VITE_API_URL as string | undefined) ?? "";

  useEffect(() => {
    if (!apiUrl) {
      setError("API URLが設定されていません");
      setLoading(false);
      return;
    }
    Promise.all([
      fetch(`${apiUrl}/api/data`).then((r) => r.json()),
      fetch(`${apiUrl}/api/weekly-summary`).then((r) => r.json()),
    ])
      .then(([data, summary]) => {
        const categoryCount: Record<string, number> = {};
        (data.items as { category?: string }[]).forEach((item) => {
          const cat = item.category ?? "未分類";
          categoryCount[cat] = (categoryCount[cat] ?? 0) + 1;
        });
        setStats({ total: data.items.length, categories: Object.keys(categoryCount).length });
        const CHART_DISPLAY = ["食費", "日用品", "交通費"] as const;
        setChartData([
          ...CHART_DISPLAY.map((cat) => ({ category: cat, count: categoryCount[cat] ?? 0 })),
          {
            category: "拠出",
            count: (categoryCount["拠出"] ?? 0) + (categoryCount["入金"] ?? 0),
          },
        ]);
        setWeekly(summary as WeeklySummary);
      })
      .catch(() => setError("データの取得に失敗しました"))
      .finally(() => setLoading(false));
  }, [apiUrl]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-secondary">
        <p className="text-muted-foreground text-sm">読み込み中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-secondary px-8">
        <p className="text-red-500 text-sm text-center">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-secondary overflow-y-auto">
      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 mx-4 mt-4">
        <div className="bg-primary text-primary-foreground rounded-xl p-4 text-center shadow-sm">
          <p className="text-xs font-medium opacity-80 mb-1">総アイテム数</p>
          <p className="text-3xl font-bold">{stats?.total ?? 0}</p>
        </div>
        <div className="bg-primary text-primary-foreground rounded-xl p-4 text-center shadow-sm">
          <p className="text-xs font-medium opacity-80 mb-1">カテゴリ数</p>
          <p className="text-3xl font-bold">{stats?.categories ?? 0}</p>
        </div>
      </div>

      {/* Chart */}
      <div className="mx-4 mt-4 bg-card rounded-xl shadow-sm border border-border p-4">
        <p className="text-sm font-semibold text-card-foreground mb-3">カテゴリ別件数</p>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 20 }}>
            <XAxis dataKey="category" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" />
            <YAxis tick={{ fontSize: 10 }} allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {chartData.map((_, i) => (
                <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Weekly summary */}
      {weekly && (
        <div className="mx-4 mt-4 mb-4">
          <p className="text-xs font-semibold text-muted-foreground mb-2">
            先週の詳細（{weekly.period.start} 〜 {weekly.period.end}）
          </p>
          <div className="grid grid-cols-1 gap-3">
            <div className="bg-card rounded-xl shadow-sm border border-border p-4">
              <p className="text-sm font-semibold text-primary mb-3">食費</p>
              {(["自炊", "外食", "その他"] as const).map((key) => (
                <div key={key} className="flex justify-between py-2 border-b border-border last:border-0">
                  <span className="text-sm text-muted-foreground">{key}</span>
                  <span className="text-sm font-medium text-card-foreground">
                    ¥{(weekly.food[key] ?? 0).toLocaleString()}
                  </span>
                </div>
              ))}
              <div className="flex justify-between pt-2 mt-1 border-t-2 border-primary">
                <span className="text-sm font-semibold text-primary">合計</span>
                <span className="text-sm font-bold text-primary">
                  ¥{weekly.food_total.toLocaleString()}
                </span>
              </div>
            </div>
            <div className="bg-card rounded-xl shadow-sm border border-border p-4">
              <p className="text-sm font-semibold text-primary mb-3">拠出金額</p>
              {Object.entries(weekly.withdrawal).map(([person, amount]) => (
                <div key={person} className="flex justify-between py-2 border-b border-border last:border-0">
                  <span className="text-sm text-muted-foreground">{person}</span>
                  <span className="text-sm font-medium text-card-foreground">
                    ¥{(amount as number).toLocaleString()}
                  </span>
                </div>
              ))}
              <div className="flex justify-between pt-2 mt-1 border-t-2 border-primary">
                <span className="text-sm font-semibold text-primary">合計</span>
                <span className="text-sm font-bold text-primary">
                  ¥{weekly.withdrawal_total.toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────

export default function App() {
  const [screen, setScreen] = useState<"register" | "calendar" | "dashboard">("register");
  const [transactions, setTransactions] = useState<Transaction[]>(SEED);
  const [savedMsg, setSavedMsg] = useState(false);

  const handleSave = (t: Transaction) => {
    setTransactions((prev) => [t, ...prev]);
    setSavedMsg(true);
    setTimeout(() => setSavedMsg(false), 1800);
  };

  return (
    <div
      className="flex flex-col size-full max-w-md mx-auto overflow-hidden bg-background shadow-2xl"
      style={{ fontFamily: "'Noto Sans JP', 'Inter', sans-serif" }}
    >
      {/* Header */}
      <div className="bg-primary text-primary-foreground px-5 py-3.5 flex items-center justify-between shrink-0">
        <h1 className="text-lg font-bold tracking-tight">KakeiBot</h1>
        <span className="text-xs font-medium opacity-80">
          {new Date().getFullYear()}年{new Date().getMonth() + 1}月
        </span>
      </div>

      {/* Save toast */}
      {savedMsg && (
        <div className="absolute top-14 left-1/2 -translate-x-1/2 z-50 bg-emerald-600 text-white text-sm font-medium px-4 py-2 rounded-full shadow-lg">
          ✓ 保存しました
        </div>
      )}

      {/* Screen content */}
      <div className="flex-1 overflow-hidden relative">
        <div className={`absolute inset-0 overflow-hidden transition-opacity duration-200 ${screen === "register" ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"}`}>
          <RegisterScreen onSave={handleSave} />
        </div>
        <div className={`absolute inset-0 overflow-hidden transition-opacity duration-200 ${screen === "calendar" ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"}`}>
          <CalendarScreen transactions={transactions} />
        </div>
        <div className={`absolute inset-0 overflow-hidden transition-opacity duration-200 ${screen === "dashboard" ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"}`}>
          <DashboardScreen />
        </div>
      </div>

      {/* Bottom tab bar */}
      <div className="grid grid-cols-3 border-t border-border bg-card shrink-0">
        {(["register", "calendar", "dashboard"] as const).map((s) => (
          <button
            key={s}
            onClick={() => setScreen(s)}
            className={`flex flex-col items-center gap-1 py-2.5 transition-colors
              ${screen === s ? "text-primary" : "text-muted-foreground hover:text-card-foreground"}`}
          >
            {s === "register" && <BookOpen className="w-5 h-5" />}
            {s === "calendar" && <Calendar className="w-5 h-5" />}
            {s === "dashboard" && <LayoutDashboard className="w-5 h-5" />}
            <span className="text-[10px] font-semibold">
              {s === "register" ? "登録" : s === "calendar" ? "カレンダー" : "ダッシュボード"}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
