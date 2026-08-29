import { useState } from 'react';
import { ChevronDown, HelpCircle } from 'lucide-react';

const faqs = [
  {
    question: 'How does ApplyWise calculate my job match score?',
    answer:
      'ApplyWise uses a transparent 5-dimensional scoring model: Technical Skills match (40%), Semantic experience fit (30%), Projects relevance (15%), Education alignment (10%), and Location / work authorization fit (5%). Unlike black-box screening tools, we show you the exact breakdown and identify specific missing keywords or skills.',
  },
  {
    question: 'Is my resume and career information secure and private?',
    answer:
      'Yes, 100%. Your uploaded documents and personal career history are stored in an encrypted database and isolated workspace. We never sell your data, share your documents with recruiters without permission, or train public foundational models on your personal materials.',
  },
  {
    question: 'Can I import jobs from LinkedIn, Indeed, or Greenhouse links?',
    answer:
      'Yes. ApplyWise allows you to import job listings in three ways: paste a live job URL to automatically scrape details, copy/paste raw job description text, or search and add roles manually.',
  },
  {
    question: 'How is ApplyWise different from generic ChatGPT prompts?',
    answer:
      'ChatGPT does not know your full career history, lacks vector-indexed retrieval of your projects, cannot compute transparent 5-factor ATS mathematical scores, and does not provide an integrated 6-stage Kanban application tracker. ApplyWise gives you a dedicated career intelligence platform tailored specifically to your background.',
  },
  {
    question: 'What materials can I generate with the AI assistant?',
    answer:
      'You can generate job-specific tailored resume bullet points, customized cover letters matching the company culture, professional recruiter outreach/follow-up emails, and custom interview prep guides covering technical drills and behavioral STAR responses.',
  },
  {
    question: 'Is ApplyWise free to get started?',
    answer:
      'Yes! You can create an account, upload your documents, index your skills, and start analyzing job postings for free with zero credit card required.',
  },
];

export default function FaqSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const toggleFaq = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section id="faq" className="py-24 sm:py-32">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3.5 py-1 text-xs font-semibold text-primary">
            <HelpCircle className="h-3.5 w-3.5" />
            Frequently Asked Questions
          </div>
          <h2 className="mt-4 text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            Everything You Need to Know
          </h2>
          <p className="mt-3 text-base text-muted-foreground">
            Have questions about how ApplyWise works? Find quick answers below.
          </p>
        </div>

        {/* FAQ Accordion List */}
        <div className="mt-14 space-y-4">
          {faqs.map((faq, index) => {
            const isOpen = openIndex === index;
            return (
              <div
                key={faq.question}
                className="overflow-hidden rounded-2xl border border-border bg-card transition-all duration-200"
              >
                <button
                  onClick={() => toggleFaq(index)}
                  className="flex w-full items-center justify-between p-5 sm:p-6 text-left font-semibold text-foreground hover:bg-accent/40 transition-colors"
                  aria-expanded={isOpen}
                >
                  <span className="text-base sm:text-lg pr-4">{faq.question}</span>
                  <div
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-border bg-background transition-transform duration-200 ${
                      isOpen ? 'rotate-180 bg-accent text-primary' : 'text-muted-foreground'
                    }`}
                  >
                    <ChevronDown className="h-4 w-4" />
                  </div>
                </button>

                {isOpen && (
                  <div className="px-5 sm:px-6 pb-6 pt-1 text-sm text-muted-foreground leading-relaxed border-t border-border/40">
                    <p>{faq.answer}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
