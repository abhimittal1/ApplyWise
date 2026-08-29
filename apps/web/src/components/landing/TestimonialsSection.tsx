import { Star, Quote } from 'lucide-react';

const testimonials = [
  {
    name: 'Marcus Chen',
    role: 'Senior Full Stack Engineer',
    company: 'Ex-Amazon • Landed offer at Fintech Scaleup',
    initials: 'MC',
    avatarBg: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
    content:
      'The 5-factor match score completely changed how I apply. Instead of sending 50 blind resumes, I focused on 8 roles where I scored >90%. I got 5 callbacks and signed an offer in 3 weeks.',
    rating: 5,
  },
  {
    name: 'Sarah Jenkins',
    role: 'AI / Backend Engineer',
    company: 'Landed Staff Role at Series B AI Startup',
    initials: 'SJ',
    avatarBg: 'bg-purple-500/10 text-purple-600 dark:text-purple-400',
    content:
      'The Knowledge Chat feature is magical. Being able to ask "What specific numbers do I have for Redis caching optimization?" and getting cited snippets for interview questions was an incredible confidence booster.',
    rating: 5,
  },
  {
    name: 'David Rodriguez',
    role: 'Product & Solutions Architect',
    company: 'Landed Lead Role at Enterprise SaaS',
    initials: 'DR',
    avatarBg: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
    content:
      'The automated STAR interview prep generated questions that my actual interviewers asked verbatim. ApplyWise saved me at least 15 hours of manual resume tweaking every week.',
    rating: 5,
  },
];

export default function TestimonialsSection() {
  return (
    <section id="testimonials" className="py-24 bg-muted/30 border-y border-border/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="text-center max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3.5 py-1 text-xs font-semibold text-primary">
            Success Stories
          </div>
          <h2 className="mt-4 text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            Loved by Developers & Job Seekers
          </h2>
          <p className="mt-4 text-base sm:text-lg text-muted-foreground">
            See how professionals are accelerating their job applications and landing top-tier offers.
          </p>
        </div>

        {/* Testimonials Cards Grid */}
        <div className="mt-16 grid grid-cols-1 gap-8 md:grid-cols-3">
          {testimonials.map((t) => (
            <div
              key={t.name}
              className="relative flex flex-col justify-between rounded-2xl border border-border bg-card p-7 shadow-sm transition-all duration-300 hover:shadow-md"
            >
              <div>
                {/* Rating stars & quote icon */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1">
                    {[...Array(t.rating)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-amber-400 text-amber-400" />
                    ))}
                  </div>
                  <Quote className="h-6 w-6 text-muted-foreground/30" />
                </div>

                <p className="mt-5 text-sm text-foreground/90 leading-relaxed italic">
                  "{t.content}"
                </p>
              </div>

              {/* Author */}
              <div className="mt-6 pt-5 border-t border-border/50 flex items-center gap-3">
                <div
                  className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-xs font-bold ${t.avatarBg}`}
                >
                  {t.initials}
                </div>
                <div className="min-w-0">
                  <h4 className="text-sm font-bold text-foreground truncate">{t.name}</h4>
                  <p className="text-xs text-muted-foreground truncate">{t.role}</p>
                  <p className="text-[11px] text-primary/80 font-medium truncate">{t.company}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
