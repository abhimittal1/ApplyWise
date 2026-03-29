import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, AlertCircle, Loader2 } from 'lucide-react';
import { uploadDocument, type DocumentInfo } from '@/lib/api/documents';

interface DocumentUploadProps {
  onUploadComplete: (doc: DocumentInfo) => void;
}

export default function DocumentUpload({ onUploadComplete }: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      setError(null);
      for (const file of acceptedFiles) {
        setUploading(true);
        try {
          const doc = await uploadDocument(file);
          onUploadComplete(doc);
        } catch (err: any) {
          setError(err.response?.data?.detail || 'Upload failed');
        } finally {
          setUploading(false);
        }
      }
    },
    [onUploadComplete]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxSize: 20 * 1024 * 1024,
    disabled: uploading,
  });

  return (
    <div>
      <div
        {...getRootProps()}
        className={`group cursor-pointer rounded-xl border-2 border-dashed p-10 text-center transition-all duration-200 ${
          isDragActive
            ? 'border-primary bg-primary/5 scale-[1.01]'
            : 'border-border hover:border-primary/50 hover:bg-primary/[0.02]'
        } ${uploading ? 'pointer-events-none opacity-50' : ''}`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Processing your document...</p>
              <p className="mt-1 text-xs text-muted-foreground">This may take a moment</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className={`flex h-12 w-12 items-center justify-center rounded-full transition-colors ${
              isDragActive ? 'bg-primary/20' : 'bg-muted group-hover:bg-primary/10'
            }`}>
              <Upload className={`h-6 w-6 transition-colors ${
                isDragActive ? 'text-primary' : 'text-muted-foreground group-hover:text-primary'
              }`} />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">
                {isDragActive ? 'Drop files here' : 'Drag & drop files, or click to browse'}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                PDF, DOCX, or TXT (max 20MB)
              </p>
            </div>
          </div>
        )}
      </div>
      {error && (
        <div className="mt-3 flex items-center gap-2 rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}
    </div>
  );
}
