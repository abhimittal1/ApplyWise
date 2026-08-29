import {
  FileText,
  MessageSquare,
  Target,
  Sparkles,
  Kanban,
  GraduationCap,
  ArrowUpRight,
} from 'lucide-react';
import { Link } from 'react-router-dom';

const features = [
  {
    icon: FileText,
    title: 'Document Intelligence',
    subtitle: 'Layer A: Knowledge Engine',
    description:
      'Upload resumes (PDF/DOCX), project notes, and certifications. Our AI extracts verified skills, past impact metrics, and project timelines into structured vector embeddings.',
    color: 'text-blue-500',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/20',
  },
  {
    icon: MessageSquare,
    title: 'Knowledge Chat (RAG)',
    subtitle: 'Conversational Career Search',
    description:
      'Chat directly with your career history. Query your achievements: "What projects demonstrate high-concurrency systems?" and receive cited evidence for applications.',
    color: 'text-purple-500',
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/20',
  },
  {
    icon: Target,
    title: '5-Factor Job Match Scoring',
    subtitle: 'Layer C: Matching Engine',
    description:
      'Evaluate job postings with transparent algorithmic weights: Skills (40%), Semantic Fit (30%), Projects (15%), Education (10%), and Location (5%). Zero guesswork.',
    color: 'text-emerald-500',
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/20',
  },
  {
    icon: Sparkles,
    title: 'Tailored Content Generator',
    subtitle: 'Instant Application Materials',
    description:
      'Generate targeted resume bullet points, persuasive cover letters, and recruiter outreach emails in seconds, tailored to the specific job description and company context.',
    color: 'text-amber-500',
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/20',
  },
  {
    icon: Kanban,
    title: 'Visual Application Tracker',
    subtitle: '6-Stage Kanban Pipeline',
    description:
      'Track every opportunity from Saved to Applying, Applied, Interview, Offer, and Decision. Monitor deadlines, response times, and follow-up alerts in one visual dashboard.',
    color: 'text-indigo-500',
    bg: 'bg-indigo-500/10',
    border: 'border-indigo-500/20',
  },
  {
    icon: GraduationCap,
    title: 'Role-Specific Interview Prep',
    subtitle: 'Technical & Behavioral Coaching',
    description:
      'Generate technical drill questions, STAR-method behavioral scenarios, system design architectures, and company deep-dives custom-tailored to the target role.',
    color: 'text-rose-500',
    bg: 'bg-rose-500/10',
    border: 'border-rose-500/20',
  },
];

export default function FeaturesSection() {
  return (
    <section id="features" className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="text-center max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3.5 py-1 text-xs font-semibold text-primary">
            Platform Capabilities
          </div>
          <h2 className="mt-4 text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            Everything You Need to Command Your Job Search
          </h2>
          <p className="mt-4 text-base sm:text-lg text-muted-foreground leading-relaxed">
            ApplyWise connects your personal career documents with advanced AI retrieval to give you an unfair advantage at every stage of the hiring pipeline.
          </p>
        </div>

        {/* Feature Grid */}
        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group relative flex flex-col justify-between rounded-2xl border border-border bg-card p-7 shadow-sm transition-all duration-300 hover:-translate-y-1.5 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5"
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${feature.bg} ${feature.border} border`}>
                    <feature.icon className={`h-6 w-6 ${feature.color}`} />
                  </div>
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                    {feature.subtitle}
                  </span>
                </div>

                <h3 className="mt-5 text-xl font-bold tracking-tight text-foreground group-hover:text-primary transition-colors">
                  {feature.title}
                </h3>
                <p className="mt-2.5 text-sm text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-border/50 flex items-center justify-between text-xs font-medium text-primary">
                <Link to="/register" className="inline-flex items-center gap-1 hover:underline">
                  Try feature <ArrowUpRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
