import { useState } from 'react';

interface ReviewEditorProps {
  review: string;
  isGenerating: boolean;
  onRegenerate: () => void;
}

export function ReviewEditor({ review, isGenerating, onRegenerate }: ReviewEditorProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(review);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([review], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'literature-review.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="border-b px-4 py-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Generated Literature Review</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            disabled={!review || isGenerating}
            className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {copied ? 'Copied!' : 'Copy'}
          </button>
          <button
            onClick={handleDownload}
            disabled={!review || isGenerating}
            className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Download
          </button>
          <button
            onClick={onRegenerate}
            disabled={isGenerating}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? 'Generating...' : 'Regenerate'}
          </button>
        </div>
      </div>

      <div className="p-4">
        {isGenerating && !review ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full" />
            <span className="ml-3 text-gray-600">Generating literature review...</span>
          </div>
        ) : review ? (
          <div className="prose max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed bg-gray-50 p-4 rounded-lg overflow-auto max-h-[600px]">
              {review}
            </pre>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-12">
            Complete the analysis to generate a literature review.
          </p>
        )}
      </div>
    </div>
  );
}
