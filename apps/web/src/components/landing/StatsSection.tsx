import { Zap, Target, BookOpen, ShieldCheck } from 'lucide-react';

const stats = [
  {
    value: '5x',
    label: 'Faster Application Cycles',
    description: 'Create customized resumes, cover letters, and outreach emails in under 30 seconds.',
    icon: Zap,
    color: 'text-amber-500',
    bg: 'bg-amber-500/10',
  },
  {
    value: '94%',
    label: 'ATS Screen Pass Rate',
    description: 'Algorithmic 5-factor scoring highlights key strengths and closes critical skill gaps.',
    icon: Target,
    color: 'text-emerald-500',
    bg: 'bg-emerald-500/10',
  },
  {
    value: '10,000+',
    label: 'Interview Questions Prepared',
    description: 'Technical challenges, STAR-method scenarios, and system design tailored to the exact role.',
    icon: BookOpen,
    color: 'text-blue-500',
    bg: 'bg-blue-500/10',
  },
  {
    value: '100%',
    label: 'Private & Secure Storage',
    description: 'Your career records, documents, and notes are indexed exclusively in your secure workspace.',
    icon: ShieldCheck,
    color: 'text-purple-500',
    bg: 'bg-purple-500/10',
  },
];

export default function StatsSection() {
  return (
    <section className="relative border-y border-border/60 bg-card/40 py-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="relative flex flex-col justify-between rounded-2xl border border-border/80 bg-card p-6 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-md"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
                    {stat.value}
                  </span>
                  <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${stat.bg}`}>
                    <stat.icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                </div>
                <h3 className="mt-3 text-base font-semibold text-foreground">{stat.label}</h3>
                <p className="mt-1.5 text-xs text-muted-foreground leading-relaxed">
                  {stat.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
