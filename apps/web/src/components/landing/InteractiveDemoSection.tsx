import { useState } from 'react';
import {
  Target,
  MessageSquare,
  Kanban,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  FileText,
  Building2,
  MapPin,
  DollarSign,
  Send,
  Bot,
  User,
  ArrowRight,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export default function InteractiveDemoSection() {
  const [activeTab, setActiveTab] = useState<'match' | 'chat' | 'kanban'>('match');

  // Chat simulator state
  const [chatMessages, setChatMessages] = useState<Array<{ role: 'user' | 'assistant'; text: string; source?: string }>>([
    {
      role: 'user',
      text: 'What are my strongest achievements in scaling distributed backend systems?',
    },
    {
      role: 'assistant',
      text: 'Based on your uploaded resume (Resume_2026.pdf) and project notes (Distributed_RAG.docx):\n\n1. Built a high-throughput vector search pipeline serving 10,000+ queries/sec with sub-50ms p95 latency using FastAPI & pgvector.\n2. Scaled distributed worker queues with Celery & Redis, reducing document ingestion lag by 78%.\n3. Architected multi-region PostgreSQL database with read replicas and automated failover.',
      source: 'Resume_2026.pdf • Page 1',
    },
  ]);

  const presetQuestions = [
    'What skills are missing for a Staff Engineer role?',
    'Summarize my experience with Python & PostgreSQL',
    'Draft a 30-second elevator pitch for tech interviews',
  ];

  const handleSendPreset = (question: string) => {
    const responses: Record<string, string> = {
      'What skills are missing for a Staff Engineer role?':
        'Based on your target jobs and profile, your technical execution is in the 95th percentile. The primary gaps are:\n• Experience leading cross-team architectural RFCs\n• Public cloud FinOps / cloud cost optimization track record\n• Managing team mentorship & hiring pipelines.',
      'Summarize my experience with Python & PostgreSQL':
        'You have 5+ years building production systems in Python (FastAPI, AsyncIO, SQLAlchemy) and PostgreSQL (pgvector, query optimization, connection pooling, complex migrations).',
      'Draft a 30-second elevator pitch for tech interviews':
        '"I am a backend & AI engineer specializing in high-throughput distributed systems and semantic search architectures. Recently, I built end-to-end RAG pipelines scaling to 10k QPS while slashing processing lag by 78%."',
    };

    setChatMessages((prev) => [
      ...prev,
      { role: 'user', text: question },
      {
        role: 'assistant',
        text: responses[question] || 'Synthesized answer based on your knowledge base.',
        source: 'Profile_Verified_Skills.json',
      },
    ]);
  };

  return (
    <section id="demo" className="py-20 bg-muted/40 border-y border-border/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="text-center max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3.5 py-1 text-xs font-semibold text-primary">
            Interactive Product Preview
          </div>
          <h2 className="mt-4 text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            See ApplyWise in Action
          </h2>
          <p className="mt-3 text-base text-muted-foreground">
            Explore how our AI engine analyzes jobs, answers complex career queries, and organizes your application pipeline.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="mt-10 flex justify-center">
          <div className="inline-flex rounded-xl bg-card border border-border p-1.5 shadow-sm">
            <button
              onClick={() => setActiveTab('match')}
              className={`flex items-center gap-2 rounded-lg px-4 py-2.5 text-xs sm:text-sm font-semibold transition-all ${
                activeTab === 'match'
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Target className="h-4 w-4" />
              1. Job Match Engine
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center gap-2 rounded-lg px-4 py-2.5 text-xs sm:text-sm font-semibold transition-all ${
                activeTab === 'chat'
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <MessageSquare className="h-4 w-4" />
              2. Knowledge Chat (RAG)
            </button>
            <button
              onClick={() => setActiveTab('kanban')}
              className={`flex items-center gap-2 rounded-lg px-4 py-2.5 text-xs sm:text-sm font-semibold transition-all ${
                activeTab === 'kanban'
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Kanban className="h-4 w-4" />
              3. Application Pipeline
            </button>
          </div>
        </div>

        {/* Tab Content Display Container */}
        <div className="mt-8 rounded-2xl border border-border bg-card p-6 sm:p-8 shadow-xl">
          {/* TAB 1: Job Match Engine */}
          {activeTab === 'match' && (
            <div className="grid gap-8 lg:grid-cols-12">
              {/* Job Header & Details */}
              <div className="lg:col-span-7 space-y-6">
                <div className="flex flex-wrap items-start justify-between gap-4 border-b border-border pb-5">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="rounded-md bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">
                        Full-Time
                      </span>
                      <span className="text-xs text-muted-foreground">Scraped via LinkedIn URL</span>
                    </div>
                    <h3 className="mt-2 text-2xl font-bold text-foreground">Lead AI Platform Engineer</h3>
                    <div className="mt-2 flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Building2 className="h-3.5 w-3.5 text-primary" /> Anthropic / Scale AI
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5 text-primary" /> San Francisco, CA (Hybrid)
                      </span>
                      <span className="flex items-center gap-1">
                        <DollarSign className="h-3.5 w-3.5 text-primary" /> $190k - $240k + Equity
                      </span>
                    </div>
                  </div>
                  <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-center">
                    <span className="text-2xl font-black text-emerald-600 dark:text-emerald-400">92%</span>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                      Strong Fit
                    </p>
                  </div>
                </div>

                {/* Skills Analysis */}
                <div>
                  <h4 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
                    Required Skills Breakdown
                  </h4>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {[
                      { name: 'Python 3.11 / AsyncIO', match: true },
                      { name: 'FastAPI & REST APIs', match: true },
                      { name: 'PostgreSQL + pgvector', match: true },
                      { name: 'RAG Pipeline Architecture', match: true },
                      { name: 'Docker & Microservices', match: true },
                      { name: 'Redis Caching & Celery', match: true },
                      { name: 'Kubernetes Cluster Ops', match: false },
                      { name: 'Prometheus & Grafana', match: false },
                    ].map((skill) => (
                      <span
                        key={skill.name}
                        className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium ${
                          skill.match
                            ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
                        }`}
                      >
                        {skill.match ? (
                          <CheckCircle2 className="h-3.5 w-3.5" />
                        ) : (
                          <AlertCircle className="h-3.5 w-3.5" />
                        )}
                        {skill.name}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Key Insights */}
                <div className="rounded-xl bg-accent/40 p-4 border border-border">
                  <div className="flex items-center gap-2 text-xs font-bold text-accent-foreground uppercase tracking-wide">
                    <Sparkles className="h-4 w-4 text-primary" />
                    AI Resume Customization Recommendation
                  </div>
                  <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
                    "Emphasize your pgvector indexing optimization and sub-50ms retrieval benchmarks in Bullet Point 2 of your resume. Mention self-hosted Redis caching to offset Kubernetes experience."
                  </p>
                </div>
              </div>

              {/* 5-Factor Scoring Breakdown */}
              <div className="lg:col-span-5 rounded-xl border border-border bg-card/60 p-6 flex flex-col justify-between">
                <div>
                  <h4 className="font-bold text-base text-foreground">5-Factor Algorithmic Score</h4>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Calculated by comparing your verified knowledge base against the JD.
                  </p>

                  <div className="mt-6 space-y-4">
                    {[
                      { label: 'Technical Skills (40%)', score: 95, color: 'bg-emerald-500' },
                      { label: 'Semantic Experience (30%)', score: 90, color: 'bg-blue-500' },
                      { label: 'Project Portfolio (15%)', score: 92, color: 'bg-purple-500' },
                      { label: 'Education & Certs (10%)', score: 88, color: 'bg-amber-500' },
                      { label: 'Location & Work Auth (5%)', score: 100, color: 'bg-teal-500' },
                    ].map((item) => (
                      <div key={item.label}>
                        <div className="flex justify-between text-xs font-semibold">
                          <span>{item.label}</span>
                          <span>{item.score}%</span>
                        </div>
                        <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-muted">
                          <div
                            className={`h-full rounded-full ${item.color}`}
                            style={{ width: `${item.score}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-6 pt-5 border-t border-border flex flex-col gap-2">
                  <Link
                    to="/register"
                    className="flex items-center justify-center gap-2 rounded-lg bg-primary py-2.5 text-xs font-semibold text-primary-foreground shadow-sm hover:bg-primary/90"
                  >
                    <Sparkles className="h-3.5 w-3.5" />
                    Generate Tailored Application Package
                  </Link>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Knowledge Chat (RAG) */}
          {activeTab === 'chat' && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-border pb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400">
                    <Bot className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold">Personal Knowledge Chat</h3>
                    <p className="text-xs text-muted-foreground">
                      Retrieving directly from 3 indexed documents with pgvector
                    </p>
                  </div>
                </div>
                <div className="hidden sm:flex items-center gap-2">
                  <span className="flex items-center gap-1 rounded-md bg-muted px-2 py-1 text-[11px] font-medium text-muted-foreground">
                    <FileText className="h-3 w-3" /> Resume_2026.pdf
                  </span>
                  <span className="flex items-center gap-1 rounded-md bg-muted px-2 py-1 text-[11px] font-medium text-muted-foreground">
                    <FileText className="h-3 w-3" /> Distributed_RAG.docx
                  </span>
                </div>
              </div>

              {/* Chat Messages Stream */}
              <div className="space-y-4 max-h-80 overflow-y-auto pr-1">
                {chatMessages.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex items-start gap-3 ${
                      msg.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {msg.role === 'assistant' && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <Bot className="h-4 w-4" />
                      </div>
                    )}
                    <div
                      className={`max-w-xl rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
                        msg.role === 'user'
                          ? 'bg-primary text-primary-foreground rounded-tr-none'
                          : 'bg-muted/80 text-foreground border border-border rounded-tl-none whitespace-pre-line'
                      }`}
                    >
                      <p>{msg.text}</p>
                      {msg.source && (
                        <div className="mt-2.5 pt-2 border-t border-border/40 text-[10px] font-medium text-muted-foreground flex items-center gap-1">
                          <FileText className="h-3 w-3 text-primary" />
                          Source: {msg.source}
                        </div>
                      )}
                    </div>
                    {msg.role === 'user' && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                        <User className="h-4 w-4" />
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Preset suggestion chips */}
              <div className="pt-2">
                <p className="text-xs font-semibold text-muted-foreground mb-2">Try asking:</p>
                <div className="flex flex-wrap gap-2">
                  {presetQuestions.map((q) => (
                    <button
                      key={q}
                      onClick={() => handleSendPreset(q)}
                      className="rounded-lg border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:border-primary hover:text-primary"
                    >
                      "{q}"
                    </button>
                  ))}
                </div>
              </div>

              {/* Chat Input Bar */}
              <div className="relative flex items-center">
                <input
                  type="text"
                  readOnly
                  placeholder="Ask anything about your background, skills, or achievements..."
                  className="w-full rounded-xl border border-input bg-background py-3 pl-4 pr-12 text-sm focus:outline-none"
                />
                <button
                  type="button"
                  className="absolute right-2 rounded-lg bg-primary p-2 text-primary-foreground transition-opacity hover:opacity-90"
                  aria-label="Send"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}

          {/* TAB 3: Application Pipeline */}
          {activeTab === 'kanban' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-border pb-4">
                <div>
                  <h3 className="text-lg font-bold">6-Stage Visual Kanban Pipeline</h3>
                  <p className="text-xs text-muted-foreground">
                    Organize your job search with automated deadline tracking & stage progression
                  </p>
                </div>
                <Link
                  to="/register"
                  className="hidden sm:inline-flex items-center gap-1.5 text-xs font-semibold text-primary hover:underline"
                >
                  Start Tracking <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>

              {/* Kanban columns preview */}
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:grid-cols-4">
                {/* Column 1: Saved */}
                <div className="rounded-xl border border-border bg-muted/30 p-3">
                  <div className="flex items-center justify-between font-semibold text-xs text-muted-foreground mb-3">
                    <span className="flex items-center gap-1.5">
                      <span className="h-2 w-2 rounded-full bg-blue-500" /> Saved (2)
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div className="rounded-lg border border-border bg-card p-3 shadow-xs">
                      <span className="text-[10px] font-semibold text-emerald-600 dark:text-emerald-400">
                        94% Match
                      </span>
                      <h5 className="font-bold text-xs mt-0.5">Staff Backend Architect</h5>
                      <p className="text-[11px] text-muted-foreground">OpenAI • Remote</p>
                    </div>
                    <div className="rounded-lg border border-border bg-card p-3 shadow-xs">
                      <span className="text-[10px] font-semibold text-blue-600 dark:text-blue-400">
                        89% Match
                      </span>
                      <h5 className="font-bold text-xs mt-0.5">Senior AI Engineer</h5>
                      <p className="text-[11px] text-muted-foreground">Linear • San Francisco</p>
                    </div>
                  </div>
                </div>

                {/* Column 2: Applied */}
                <div className="rounded-xl border border-border bg-muted/30 p-3">
                  <div className="flex items-center justify-between font-semibold text-xs text-muted-foreground mb-3">
                    <span className="flex items-center gap-1.5">
                      <span className="h-2 w-2 rounded-full bg-amber-500" /> Applied (1)
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div className="rounded-lg border border-border bg-card p-3 shadow-xs">
                      <span className="text-[10px] font-semibold text-emerald-600 dark:text-emerald-400">
                        92% Match
                      </span>
                      <h5 className="font-bold text-xs mt-0.5">Lead Systems Engineer</h5>
                      <p className="text-[11px] text-muted-foreground">Stripe • Applied 2d ago</p>
                    </div>
                  </div>
                </div>

                {/* Column 3: Interviewing */}
                <div className="rounded-xl border border-border bg-muted/30 p-3">
                  <div className="flex items-center justify-between font-semibold text-xs text-muted-foreground mb-3">
                    <span className="flex items-center gap-1.5">
                      <span className="h-2 w-2 rounded-full bg-purple-500" /> Interview (1)
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div className="rounded-lg border-2 border-primary/40 bg-card p-3 shadow-sm">
                      <div className="flex justify-between items-center">
                        <span className="text-[10px] font-semibold text-purple-600 dark:text-purple-400">
                          Round 2: System Design
                        </span>
                      </div>
                      <h5 className="font-bold text-xs mt-0.5">Principal Software Engineer</h5>
                      <p className="text-[11px] text-muted-foreground">Vercel • Tomorrow, 2:00 PM</p>
                      <div className="mt-2 rounded-md bg-purple-500/10 px-2 py-1 text-[10px] font-medium text-purple-600 dark:text-purple-400">
                        Prep Guide Generated
                      </div>
                    </div>
                  </div>
                </div>

                {/* Column 4: Offer */}
                <div className="rounded-xl border border-border bg-muted/30 p-3 hidden lg:block">
                  <div className="flex items-center justify-between font-semibold text-xs text-muted-foreground mb-3">
                    <span className="flex items-center gap-1.5">
                      <span className="h-2 w-2 rounded-full bg-emerald-500" /> Offer (1)
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/5 p-3 shadow-xs">
                      <span className="text-[10px] font-bold uppercase text-emerald-600 dark:text-emerald-400">
                        $215,000 / yr Base
                      </span>
                      <h5 className="font-bold text-xs mt-0.5">Staff Platform Engineer</h5>
                      <p className="text-[11px] text-muted-foreground">TechCorp • Decision by Friday</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
