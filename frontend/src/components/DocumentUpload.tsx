import { useCallback } from 'react';
import { useDropzone, type FileRejection } from 'react-dropzone';
import { UploadCloud, Loader2 } from 'lucide-react';
import { useDocumentUpload } from '../hooks/useDocumentUpload';

/** Maximum accepted file size: 10 MB in bytes. */
const MAX_SIZE_BYTES = 10 * 1024 * 1024;

const ACCEPTED_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt'],
};

/**
 * DocumentUpload — drag-and-drop file upload zone.
 * Accepts PDF, DOCX, and plain text files up to 10 MB.
 *
 * On successful drop/selection, immediately calls the upload API and
 * navigates to the workspace. Keyboard operable via react-dropzone.
 */
export default function DocumentUpload(): JSX.Element {
  const { upload, isUploading, error } = useDocumentUpload();

  const onDrop = useCallback(
    (acceptedFiles: File[], rejections: FileRejection[]) => {
      if (rejections.length > 0) return; // validation errors shown via getRejectedMsg
      if (acceptedFiles.length > 0) {
        void upload(acceptedFiles[0]);
      }
    },
    [upload],
  );

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: MAX_SIZE_BYTES,
    multiple: false,
    disabled: isUploading,
  });

  /** Build a human-readable rejection message from react-dropzone errors. */
  const rejectionMessage =
    fileRejections.length > 0
      ? fileRejections[0].errors.map((e) => e.message).join('. ')
      : null;

  const displayError = error ?? rejectionMessage;

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        aria-label="Upload legal document, accepts PDF, DOCX, or text files up to 10 megabytes"
        className={[
          'relative flex flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed p-12 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2',
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-slate-300 bg-slate-50 hover:border-blue-400 hover:bg-blue-50',
          isUploading ? 'pointer-events-none opacity-60' : '',
        ].join(' ')}
      >
        <input {...getInputProps()} />

        {isUploading ? (
          <Loader2
            aria-hidden="true"
            className="h-12 w-12 animate-spin text-blue-500"
          />
        ) : (
          <UploadCloud
            aria-hidden="true"
            className={`h-12 w-12 ${isDragActive ? 'text-blue-500' : 'text-slate-400'}`}
          />
        )}

        <div className="text-center">
          {isUploading ? (
            <p className="text-base font-medium text-blue-600">Uploading document…</p>
          ) : isDragActive ? (
            <p className="text-base font-medium text-blue-600">Drop your document here</p>
          ) : (
            <>
              <p className="text-base font-medium text-slate-700">
                Drag &amp; drop your legal document here
              </p>
              <p className="mt-1 text-sm text-slate-500">
                or{' '}
                <span className="text-blue-600 underline underline-offset-2">
                  click to browse
                </span>
              </p>
            </>
          )}
        </div>

        <p className="text-xs text-slate-400">PDF · DOCX · TXT — up to 10 MB</p>
      </div>

      {/* Accessible error region — announced by screen readers when content changes */}
      <div aria-live="polite" aria-atomic="true" className="mt-3 min-h-[1.25rem]">
        {displayError && (
          <p role="alert" className="text-sm font-medium text-red-600">
            {displayError}
          </p>
        )}
      </div>
    </div>
  );
}
