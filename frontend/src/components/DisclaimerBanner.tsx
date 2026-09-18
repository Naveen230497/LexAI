import { AlertTriangle } from 'lucide-react';

/**
 * DisclaimerBanner — persistent legal disclaimer shown on all pages.
 *
 * Marked with role="note" so screen readers announce it as supplementary
 * information. Required by the challenge brief: solutions must clarify
 * they provide information, not legal advice.
 */
export default function DisclaimerBanner(): JSX.Element {
  return (
    <aside
      role="note"
      aria-label="Legal disclaimer"
      className="w-full bg-amber-50 border-l-4 border-amber-400 px-4 py-3 flex items-start gap-3"
    >
      <AlertTriangle
        aria-hidden="true"
        className="mt-0.5 h-5 w-5 flex-shrink-0 text-amber-500"
      />
      <p className="text-sm text-amber-800 leading-snug">
        <span className="font-semibold">Important:</span> LexAI provides general legal
        information only — not legal advice. Always consult a qualified legal professional
        for advice specific to your situation.
      </p>
    </aside>
  );
}
