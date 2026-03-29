import { useState, type FormEvent } from 'react';
import { X, Loader2, Search, ExternalLink } from 'lucide-react';
import {
  createJob,
  importJobFromText,
  confirmTextImport,
  importJobFromURL,
  confirmUrlImport,
  searchJobs,
  saveSearchResult,
  type JobPreview,
  type JobSearchResponse,
} from '@/lib/api/jobs';

interface AddJobModalProps {
  isOpen: boolean;
  onClose: () => void;
  onJobAdded: () => void;
}

type Tab = 'manual' | 'paste' | 'url' | 'search';

export default function AddJobModal({ isOpen, onClose, onJobAdded }: AddJobModalProps) {
  const [tab, setTab] = useState<Tab>('manual');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Manual form
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [location, setLocation] = useState('');
  const [description, setDescription] = useState('');
  const [url, setUrl] = useState('');
  const [remote, setRemote] = useState(false);

  // Paste import
  const [rawText, setRawText] = useState('');
  const [preview, setPreview] = useState<JobPreview | null>(null);

  // URL import
  const [urlInput, setUrlInput] = useState('');
  const [urlPreview, setUrlPreview] = useState<JobPreview | null>(null);

  // Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLocation, setSearchLocation] = useState('');
  const [searchResults, setSearchResults] = useState<JobSearchResponse | null>(null);
  const [savingId, setSavingId] = useState<number | null>(null);

  if (!isOpen) return null;

  const resetForm = () => {
    setTitle(''); setCompany(''); setLocation(''); setDescription('');
    setUrl(''); setRemote(false); setRawText(''); setPreview(null);
    setUrlInput(''); setUrlPreview(null);
    setSearchQuery(''); setSearchLocation(''); setSearchResults(null);
    setError(''); setSavingId(null);
  };

  const handleManualSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await createJob({ title, company, location: location || undefined, description: description || undefined, url: url || undefined, remote });
      resetForm();
      onJobAdded();
      onClose();
    } catch {
      setError('Failed to create job');
    } finally {
      setLoading(false);
    }
  };

  const handleParse = async () => {
    if (!rawText.trim()) return;
    setError('');
    setLoading(true);
    try {
      const parsed = await importJobFromText(rawText);
      setPreview(parsed);
    } catch {
      setError('Failed to parse job description');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmPaste = async () => {
    if (!preview) return;
    setLoading(true);
    try {
      await confirmTextImport({
        title: preview.title,
        company: preview.company,
        location: preview.location || undefined,
        description: preview.description || undefined,
      });
      resetForm();
      onJobAdded();
      onClose();
    } catch {
      setError('Failed to save job');
    } finally {
      setLoading(false);
    }
  };

  const handleUrlParse = async () => {
    if (!urlInput.trim()) return;
    setError('');
    setLoading(true);
    try {
      const parsed = await importJobFromURL(urlInput);
      setUrlPreview(parsed);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to fetch job from URL');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmUrl = async () => {
    if (!urlPreview) return;
    setLoading(true);
    try {
      await confirmUrlImport({
        title: urlPreview.title,
        company: urlPreview.company,
        location: urlPreview.location || undefined,
        description: urlPreview.description || undefined,
        url: urlPreview.url || urlInput || undefined,
      });
      resetForm();
      onJobAdded();
      onClose();
    } catch {
      setError('Failed to save job');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setError('');
    setLoading(true);
    setSearchResults(null);
    try {
      const results = await searchJobs(searchQuery, searchLocation);
      setSearchResults(results);
      if (results.total === 0) {
        setError('No jobs found. Try different keywords or check that API keys are configured.');
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Search failed. Make sure job search API keys are configured.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSearchResult = async (result: JobPreview, index: number) => {
    setSavingId(index);
    try {
      await saveSearchResult({
        title: result.title,
        company: result.company,
        location: result.location || undefined,
        description: result.description || undefined,
        url: result.url || undefined,
      });
      onJobAdded();
      // Remove saved result from list
      if (searchResults) {
        setSearchResults({
          ...searchResults,
          results: searchResults.results.filter((_, i) => i !== index),
          total: searchResults.total - 1,
        });
      }
    } catch {
      setError('Failed to save job');
    } finally {
      setSavingId(null);
    }
  };

  const tabButton = (t: Tab, label: string) => (
    <button
      onClick={() => { setTab(t); setPreview(null); setUrlPreview(null); setError(''); }}
      className={`relative px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-colors ${
        tab === t
          ? 'text-primary'
          : 'text-muted-foreground hover:text-foreground'
      }`}
    >
      {label}
      {tab === t && (
        <span className="absolute inset-x-0 bottom-0 h-0.5 rounded-full bg-primary" />
      )}
    </button>
  );

  const inputClasses =
    'mt-1.5 block w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground shadow-sm placeholder:text-muted-foreground transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20';

  const primaryBtnClasses =
    'w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground shadow-sm transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 disabled:opacity-50';

  const renderPreview = (p: JobPreview, onBack: () => void, onConfirm: () => void) => (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-foreground">Extracted Information</h3>
      <div className="rounded-xl border border-border bg-muted/50 p-4 space-y-2.5 text-sm">
        <p><span className="font-medium text-foreground">Title:</span> <span className="text-muted-foreground">{p.title}</span></p>
        <p><span className="font-medium text-foreground">Company:</span> <span className="text-muted-foreground">{p.company}</span></p>
        {p.location && <p><span className="font-medium text-foreground">Location:</span> <span className="text-muted-foreground">{p.location}</span></p>}
        {p.description && <p><span className="font-medium text-foreground">Summary:</span> <span className="text-muted-foreground">{p.description}</span></p>}
        {p.requirements.length > 0 && (
          <div>
            <span className="font-medium text-foreground">Requirements:</span>
            <ul className="mt-1.5 list-disc list-inside space-y-0.5 text-muted-foreground">
              {p.requirements.map((r, i) => <li key={i}>{r}</li>)}
            </ul>
          </div>
        )}
      </div>
      <div className="flex gap-3">
        <button
          onClick={onBack}
          className="flex-1 rounded-lg border border-border px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-accent"
        >
          Back
        </button>
        <button
          onClick={onConfirm}
          disabled={loading}
          className={`flex-1 ${primaryBtnClasses}`}
          style={{ width: 'auto' }}
        >
          {loading ? <Loader2 className="mx-auto h-4 w-4 animate-spin" /> : 'Save Job'}
        </button>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="relative w-full max-w-lg rounded-xl border border-border bg-background shadow-xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-5 py-4">
          <h2 className="text-lg font-semibold text-foreground">Add Job</h2>
          <button
            onClick={() => { resetForm(); onClose(); }}
            className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border px-5">
          {tabButton('manual', 'Manual')}
          {tabButton('paste', 'Paste')}
          {tabButton('url', 'URL')}
          {tabButton('search', 'Search')}
        </div>

        {/* Content */}
        <div className="p-5 space-y-4">
          {error && (
            <div className="rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-600 dark:text-red-400">
              {error}
            </div>
          )}

          {/* Manual Tab */}
          {tab === 'manual' && (
            <form onSubmit={handleManualSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground">Title *</label>
                <input
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className={inputClasses}
                  placeholder="Software Engineer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground">Company *</label>
                <input
                  required
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className={inputClasses}
                  placeholder="Google"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground">Location</label>
                <input
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className={inputClasses}
                  placeholder="San Francisco, CA"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={4}
                  className={inputClasses}
                  placeholder="Paste job description..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground">URL</label>
                <input
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className={inputClasses}
                  placeholder="https://..."
                />
              </div>
              <label className="flex items-center gap-2.5 text-sm text-foreground">
                <input
                  type="checkbox"
                  checked={remote}
                  onChange={(e) => setRemote(e.target.checked)}
                  className="h-4 w-4 rounded border-input text-primary focus:ring-primary/30"
                />
                Remote
              </label>
              <button type="submit" disabled={loading} className={primaryBtnClasses}>
                {loading ? <Loader2 className="mx-auto h-4 w-4 animate-spin" /> : 'Add Job'}
              </button>
            </form>
          )}

          {/* Paste Tab */}
          {tab === 'paste' && !preview && (
            <div className="space-y-4">
              <textarea
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                rows={10}
                className={inputClasses}
                placeholder="Paste the full job description here..."
              />
              <button
                onClick={handleParse}
                disabled={loading || !rawText.trim()}
                className={primaryBtnClasses}
              >
                {loading ? <Loader2 className="mx-auto h-4 w-4 animate-spin" /> : 'Parse Job Description'}
              </button>
            </div>
          )}
          {tab === 'paste' && preview && renderPreview(preview, () => setPreview(null), handleConfirmPaste)}

          {/* URL Tab */}
          {tab === 'url' && !urlPreview && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground">Job Posting URL</label>
                <input
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  className={inputClasses}
                  placeholder="https://company.com/careers/job-id"
                />
              </div>
              <button
                onClick={handleUrlParse}
                disabled={loading || !urlInput.trim()}
                className={primaryBtnClasses}
              >
                {loading ? <Loader2 className="mx-auto h-4 w-4 animate-spin" /> : 'Import from URL'}
              </button>
            </div>
          )}
          {tab === 'url' && urlPreview && renderPreview(urlPreview, () => setUrlPreview(null), handleConfirmUrl)}

          {/* Search Tab */}
          {tab === 'search' && (
            <div className="space-y-4">
              <div className="flex gap-3">
                <div className="flex-1">
                  <input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    className={`${inputClasses} mt-0`}
                    placeholder="Job title or keywords..."
                  />
                </div>
                <div className="w-36">
                  <input
                    value={searchLocation}
                    onChange={(e) => setSearchLocation(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    className={`${inputClasses} mt-0`}
                    placeholder="Location"
                  />
                </div>
              </div>
              <button
                onClick={handleSearch}
                disabled={loading || !searchQuery.trim()}
                className={primaryBtnClasses}
              >
                {loading ? <Loader2 className="mx-auto h-4 w-4 animate-spin" /> : (
                  <span className="flex items-center justify-center gap-2">
                    <Search className="h-4 w-4" /> Search Jobs
                  </span>
                )}
              </button>

              {searchResults && (
                <div className="space-y-3">
                  <p className="text-xs text-muted-foreground">
                    Found {searchResults.total} results
                    {searchResults.apis_used.length > 0 && ` from ${searchResults.apis_used.join(', ')}`}
                  </p>
                  <div className="max-h-[300px] space-y-2 overflow-y-auto pr-1">
                    {searchResults.results.map((result, i) => (
                      <div
                        key={i}
                        className="rounded-xl border border-border bg-card p-4 shadow-sm transition-all hover:shadow-md hover:border-primary/30"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0 flex-1">
                            <p className="font-medium text-sm text-foreground truncate">{result.title}</p>
                            <p className="mt-0.5 text-xs text-muted-foreground">
                              {result.company}{result.location ? ` · ${result.location}` : ''}
                            </p>
                          </div>
                          <button
                            onClick={() => handleSaveSearchResult(result, i)}
                            disabled={savingId === i}
                            className="shrink-0 rounded-lg bg-primary px-3.5 py-1.5 text-xs font-medium text-primary-foreground shadow-sm transition-colors hover:bg-primary/90 disabled:opacity-50"
                          >
                            {savingId === i ? <Loader2 className="h-3 w-3 animate-spin" /> : 'Save'}
                          </button>
                        </div>
                        {result.description && (
                          <p className="mt-2 text-xs leading-relaxed text-muted-foreground line-clamp-2">
                            {result.description}
                          </p>
                        )}
                        {result.url && (
                          <a
                            href={result.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
                          >
                            <ExternalLink className="h-3 w-3" /> View posting
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
