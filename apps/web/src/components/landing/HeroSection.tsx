import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Sparkles,
  CheckCircle2,
  TrendingUp,
  FileCheck2,
  Bot,
  Zap,
  Target,
  Layers,
} from 'lucide-react';

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden pt-12 pb-20 md:pt-20 md:pb-28">
      {/* Background glowing gradients */}
      <div className="pointer-events-none absolute -top-40 left-1/2 -z-10 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-primary/15 blur-[120px] dark:bg-primary/20" />
      <div className="pointer-events-none absolute top-1/2 -right-40 -z-10 h-[400px] w-[500px] rounded-full bg-accent/30 blur-[100px] dark:bg-primary/10" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-12 lg:gap-8">
          {/* Left Column: Copy & CTAs */}
          <div className="text-center lg:col-span-7 lg:text-left">
            {/* Pill Badge */}
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-xs font-semibold text-primary shadow-sm backdrop-blur-sm">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Next-Gen AI Career Operating System</span>
              <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
            </div>

            {/* Main Headline */}
            <h1 className="mt-6 text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl text-foreground">
              Land Your Dream Job{' '}
              <span className="bg-gradient-to-r from-primary via-purple-500 to-indigo-500 bg-clip-text text-transparent">
                5x Faster
              </span>{' '}
              with AI Career Intelligence
            </h1>

            {/* Subtitle */}
            <p className="mt-5 text-lg text-muted-foreground sm:text-xl leading-relaxed">
              Turn your resumes, projects, and work history into a private career knowledge base. Get transparent 5-factor ATS job matching, custom resume tailoring, and role-specific interview coaching.
            </p>

            {/* CTA Buttons */}
            <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:justify-center lg:justify-start">
              <Link
                to="/register"
                className="group inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-7 py-3.5 text-base font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-all hover:bg-primary/90 hover:shadow-xl hover:shadow-primary/30 hover:-translate-y-0.5"
              >
                Get Started Free
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
              <a
                href="#demo"
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-border bg-card px-6 py-3.5 text-base font-semibold text-foreground shadow-sm transition-all hover:bg-accent hover:border-border/80"
              >
                <Zap className="h-4 w-4 text-primary" />
                Explore Interactive Demo
              </a>
            </div>

            {/* Trust Badges */}
            <div className="mt-8 flex flex-wrap items-center justify-center gap-y-2 gap-x-6 text-xs text-muted-foreground lg:justify-start">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                <span>Transparent 5-factor scoring</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                <span>100% data privacy</span>
              </div>
            </div>
          </div>

          {/* Right Column: Hero Visual Preview Card */}
          <div className="lg:col-span-5">
            <div className="relative mx-auto max-w-lg rounded-2xl border border-border/80 bg-card/90 p-6 shadow-2xl backdrop-blur-xl transition-all duration-300 hover:shadow-primary/10">
              {/* Header of preview card */}
              <div className="flex items-start justify-between border-b border-border/60 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Target Match Analysis
                    </span>
                    <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-600 dark:text-emerald-400">
                      Live Preview
                    </span>
                  </div>
                  <h3 className="mt-1 text-lg font-bold">Staff Full Stack Engineer</h3>
                  <p className="text-xs text-muted-foreground">Stripe • Remote / San Francisco</p>
                </div>

                {/* Score badge */}
                <div className="flex flex-col items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-purple-500/10 p-3 border border-primary/30">
                  <span className="text-2xl font-black text-primary">94%</span>
                  <span className="text-[10px] font-semibold uppercase text-primary/80">Match</span>
                </div>
              </div>

              {/* Score breakdown metrics */}
              <div className="mt-4 space-y-3">
                <div>
                  <div className="flex justify-between text-xs font-medium">
                    <span className="flex items-center gap-1.5 text-muted-foreground">
                      <Target className="h-3.5 w-3.5 text-primary" /> Required Skills (40%)
                    </span>
                    <span className="font-semibold text-emerald-600 dark:text-emerald-400">96% Match</span>
                  </div>
                  <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-muted">
                    <div className="h-full rounded-full bg-emerald-500 transition-all duration-1000" style={{ width: '96%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs font-medium">
                    <span className="flex items-center gap-1.5 text-muted-foreground">
                      <Layers className="h-3.5 w-3.5 text-blue-500" /> Semantic Experience Fit (30%)
                    </span>
                    <span className="font-semibold text-blue-600 dark:text-blue-400">92% Match</span>
                  </div>
                  <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-muted">
                    <div className="h-full rounded-full bg-blue-500 transition-all duration-1000" style={{ width: '92%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs font-medium">
                    <span className="flex items-center gap-1.5 text-muted-foreground">
                      <TrendingUp className="h-3.5 w-3.5 text-amber-500" /> Project Portfolio (15%)
                    </span>
                    <span className="font-semibold text-amber-600 dark:text-amber-400">90% Match</span>
                  </div>
                  <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-muted">
                    <div className="h-full rounded-full bg-amber-500 transition-all duration-1000" style={{ width: '90%' }} />
                  </div>
                </div>
              </div>

              {/* Skills matched chips */}
              <div className="mt-4 pt-3 border-t border-border/60">
                <p className="text-xs font-medium text-muted-foreground mb-2">Extracted Match Highlights:</p>
                <div className="flex flex-wrap gap-1.5">
                  <span className="rounded-md bg-emerald-500/10 px-2 py-1 text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
                    ✓ React 19 & TypeScript
                  </span>
                  <span className="rounded-md bg-emerald-500/10 px-2 py-1 text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
                    ✓ FastAPI & Python
                  </span>
                  <span className="rounded-md bg-emerald-500/10 px-2 py-1 text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
                    ✓ Vector Search (pgvector)
                  </span>
                  <span className="rounded-md bg-amber-500/10 px-2 py-1 text-[11px] font-medium text-amber-600 dark:text-amber-400">
                    ⚡ Kubernetes (Gap to bridge)
                  </span>
                </div>
              </div>

              {/* AI action recommendations */}
              <div className="mt-4 rounded-xl bg-accent/40 p-3 border border-border/50">
                <div className="flex items-center gap-2 text-xs font-semibold text-accent-foreground">
                  <Bot className="h-4 w-4 text-primary" />
                  <span>AI Action Plan Ready</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                  "Your background in distributed RAG architectures gives you a top 5% edge. Generated 3 tailored resume bullets & STAR interview story."
                </p>
                <div className="mt-2.5 flex items-center gap-2">
                  <Link
                    to="/register"
                    className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg bg-primary py-1.5 px-2.5 text-xs font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                  >
                    <FileCheck2 className="h-3.5 w-3.5" />
                    Tailor Resume
                  </Link>
                  <Link
                    to="/register"
                    className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg border border-border bg-card py-1.5 px-2.5 text-xs font-medium hover:bg-accent"
                  >
                    <Sparkles className="h-3.5 w-3.5 text-primary" />
                    Interview Prep
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
