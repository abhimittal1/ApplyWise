import { Upload, Target, CheckCircle2, FileText, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const steps = [
  {
    number: '01',
    title: 'Upload & Build Your Knowledge Base',
    subtitle: 'Extract skills & verified experience',
    description:
      'Upload your resume (PDF/DOCX), projects, and work history. ApplyWise automatically parses and indexes your achievements into high-dimensional vector embeddings.',
    icon: Upload,
    color: 'text-blue-500',
    bg: 'bg-blue-500/10',
    points: [
      'Automatic skill and metric extraction',
      'Supports PDFs, DOCX, and text notes',
      '100% private, self-contained storage',
    ],
  },
  {
    number: '02',
    title: 'Import & Score Any Job Posting',
    subtitle: 'Transparent 5-factor ATS matching',
    description:
      'Paste any job link from LinkedIn, Greenhouse, Lever, or raw text. The AI calculates your exact match percentage across skills, semantics, projects, education, and location.',
    icon: Target,
    color: 'text-primary',
    bg: 'bg-primary/10',
    points: [
      'Multi-source import (URL, text, search)',
      'Identifies critical missing skills & gaps',
      'Ranks roles by real qualification score',
    ],
  },
  {
    number: '03',
    title: 'Generate Materials & Ace Interviews',
    subtitle: 'Tailor applications & practice drills',
    description:
      'Generate customized resume bullets, cover letters, and recruiter emails. Practice with role-tailored technical questions, STAR behavioral frameworks, and system design drills.',
    icon: FileText,
    color: 'text-emerald-500',
    bg: 'bg-emerald-500/10',
    points: [
      'Job-specific resume bullet recommendations',
      'Persuasive custom cover letters',
      'STAR-method behavioral interview prep',
    ],
  },
];

export default function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="text-center max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3.5 py-1 text-xs font-semibold text-primary">
            Step-By-Step Workflow
          </div>
          <h2 className="mt-4 text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            How ApplyWise Transforms Your Career Trajectory
          </h2>
          <p className="mt-4 text-base sm:text-lg text-muted-foreground">
            From raw resume to accepted offer in three simple, automated steps.
          </p>
        </div>

        {/* Steps Grid */}
        <div className="mt-16 grid grid-cols-1 gap-8 lg:grid-cols-3">
          {steps.map((step, index) => (
            <div
              key={step.number}
              className="relative flex flex-col justify-between rounded-2xl border border-border bg-card p-8 shadow-sm transition-all duration-300 hover:border-primary/40 hover:shadow-md"
            >
              {/* Step indicator header */}
              <div>
                <div className="flex items-center justify-between">
                  <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${step.bg}`}>
                    <step.icon className={`h-6 w-6 ${step.color}`} />
                  </div>
                  <span className="text-3xl font-black text-muted-foreground/30 font-mono">
                    {step.number}
                  </span>
                </div>

                <h3 className="mt-6 text-xl font-bold tracking-tight text-foreground">
                  {step.title}
                </h3>
                <p className="text-xs font-semibold text-primary mt-1">{step.subtitle}</p>

                <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
                  {step.description}
                </p>

                {/* Bullets */}
                <div className="mt-6 space-y-2.5 pt-4 border-t border-border/50">
                  {step.points.map((point) => (
                    <div key={point} className="flex items-center gap-2 text-xs text-foreground/80">
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                      <span>{point}</span>
                    </div>
                  ))}
                </div>
              </div>

              {index === 2 && (
                <div className="mt-8 pt-4">
                  <Link
                    to="/register"
                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-primary py-3 text-xs font-semibold text-primary-foreground shadow-sm hover:bg-primary/90"
                  >
                    Start Free in 2 Minutes <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
