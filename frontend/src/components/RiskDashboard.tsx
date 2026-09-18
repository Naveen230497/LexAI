import type { RiskAnalysisResult, RiskEntry, RiskSeverity } from '../lib/api';
import { ShieldAlert, AlertTriangle, ArrowRight } from 'lucide-react';

interface RiskDashboardProps {
  riskAnalysis: RiskAnalysisResult;
}

// ─── Severity display configuration ─────────────────────────────────────────

interface SeverityConfig {
  /** Badge background and text colour classes. */
  badgeCls: string;
  /** Emoji icon — supplements colour for WCAG 1.4.1 compliance. */
  icon: string;
  /** Human-readable label. */
  label: string;
  /** Sort order (lower = higher priority). */
  order: number;
}

const SEVERITY_CONFIG: Record<RiskSeverity, SeverityConfig> = {
  CRITICAL: {
    badgeCls: 'bg-red-100 text-red-800 border-red-200',
    icon: '🔴',
    label: 'Critical',
    order: 0,
  },
  HIGH: {
    badgeCls: 'bg-orange-100 text-orange-800 border-orange-200',
    icon: '🟠',
    label: 'High',
    order: 1,
  },
  MEDIUM: {
    badgeCls: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    icon: '🟡',
    label: 'Medium',
    order: 2,
  },
  LOW: {
    badgeCls: 'bg-green-100 text-green-800 border-green-200',
    icon: '🟢',
    label: 'Low',
    order: 3,
  },
  INFO: {
    badgeCls: 'bg-blue-100 text-blue-800 border-blue-200',
    icon: '🔵',
    label: 'Info',
    order: 4,
  },
};

/** Returns the appropriate text colour class for the overall score (0-10). */
function scoreColour(score: number): string {
  if (score >= 8) return 'text-red-600';
  if (score >= 6) return 'text-orange-500';
  if (score >= 4) return 'text-yellow-500';
  return 'text-green-600';
}

function scoreBg(score: number): string {
  if (score >= 8) return 'bg-red-600';
  if (score >= 6) return 'bg-orange-500';
  if (score >= 4) return 'bg-yellow-500';
  return 'bg-green-600';
}

/** Returns a verbal severity label for the overall risk score. */
function scoreLabel(score: number): string {
  if (score >= 8) return 'Critical Risk';
  if (score >= 6) return 'High Risk';
  if (score >= 4) return 'Moderate Risk';
  return 'Low Risk';
}

// ─── Sub-components ──────────────────────────────────────────────────────────

interface RiskCardProps {
  risk: RiskEntry;
}

/** Renders a single risk entry as an accessible article card. */
function RiskCard({ risk }: RiskCardProps): JSX.Element {
  const cfg = SEVERITY_CONFIG[risk.severity];

  return (
    <article
      role="article"
      aria-label={`${cfg.label} risk: ${risk.section}`}
      className="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 transition-all hover:shadow-md hover:ring-slate-300"
    >
      <div className={`absolute top-0 left-0 h-full w-1.5 ${cfg.badgeCls.split(' ')[0]}`} />
      
      {/* Header: severity badge + section */}
      <div className="flex flex-wrap items-start justify-between gap-4 mb-4 pl-2">
        <div className="flex items-center gap-3">
          <span
            aria-label={`Risk severity: ${cfg.label}`}
            className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold border ${cfg.badgeCls}`}
          >
            <span aria-hidden="true">{cfg.icon}</span>
            {cfg.label}
          </span>
          <span className="text-sm font-semibold text-slate-700 uppercase tracking-wider">
            {risk.section}
          </span>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500">
          {risk.category}
        </span>
      </div>

      <div className="pl-2 space-y-5">
        {/* Explanation */}
        <div>
          <h3 className="mb-2 text-sm font-bold text-slate-900 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-slate-400" />
            Identified Issue
          </h3>
          <p className="text-sm text-slate-600 leading-relaxed">{risk.explanation}</p>
        </div>

        {/* Clause text */}
        <blockquote className="relative rounded-lg border-l-2 border-slate-200 bg-slate-50/50 p-4 font-mono text-xs text-slate-500 leading-relaxed whitespace-pre-wrap">
          {risk.clause_text}
        </blockquote>

        {/* Recommendation */}
        <div className="rounded-xl bg-indigo-50/50 p-4 border border-indigo-100/50">
          <h3 className="mb-2 text-sm font-bold text-indigo-900 flex items-center gap-2">
            <ArrowRight className="h-4 w-4 text-indigo-500" />
            Recommended Action
          </h3>
          <p className="text-sm text-indigo-700/90 leading-relaxed">{risk.recommendation}</p>
        </div>
      </div>
    </article>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function RiskDashboard({ riskAnalysis }: RiskDashboardProps): JSX.Element {
  const { risks, overall_risk_score, summary } = riskAnalysis;

  const sortedRisks = [...risks].sort(
    (a, b) => SEVERITY_CONFIG[a.severity].order - SEVERITY_CONFIG[b.severity].order,
  );

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Overall risk score card */}
      <section
        aria-labelledby="risk-score-heading"
        className="overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-slate-200"
      >
        <div className="p-8 sm:p-10">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-4">
                <div className={`p-3 rounded-2xl ${scoreColour(overall_risk_score).replace('text-', 'bg-').replace('600', '100').replace('500', '100')} bg-opacity-50`}>
                  <ShieldAlert aria-hidden="true" className={`h-8 w-8 ${scoreColour(overall_risk_score)}`} />
                </div>
                <h2 id="risk-score-heading" className="text-2xl font-bold text-slate-900 tracking-tight">
                  Risk Assessment
                </h2>
              </div>
              <p className="text-base text-slate-600 leading-relaxed max-w-2xl">{summary}</p>
            </div>
            
            <div className="flex flex-col items-end shrink-0">
              <div className="flex items-baseline gap-2">
                <span
                  aria-label={`Overall risk score: ${overall_risk_score} out of 10`}
                  className={`text-6xl font-black tabular-nums tracking-tighter ${scoreColour(overall_risk_score)}`}
                >
                  {overall_risk_score.toFixed(1)}
                </span>
                <span className="text-xl font-bold text-slate-400">/ 10</span>
              </div>
              <span className={`mt-2 text-sm font-bold uppercase tracking-widest ${scoreColour(overall_risk_score)}`}>
                {scoreLabel(overall_risk_score)}
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-8 pt-8 border-t border-slate-100">
            <div className="flex justify-between text-xs font-bold text-slate-400 mb-3 uppercase tracking-wider">
              <span>Safe (0-3)</span>
              <span>Moderate (4-5)</span>
              <span>High (6-7)</span>
              <span>Critical (8-10)</span>
            </div>
            <div className="h-3 w-full rounded-full bg-slate-100 overflow-hidden flex">
              <div 
                className={`h-full rounded-full transition-all duration-1000 ease-out ${scoreBg(overall_risk_score)}`}
                style={{ width: `${(overall_risk_score / 10) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Risk entries */}
      <section aria-labelledby="risk-entries-heading">
        <div className="flex items-center justify-between mb-6">
          <h2 id="risk-entries-heading" className="text-xl font-bold text-slate-900 tracking-tight">
            Detailed Findings
          </h2>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-bold text-slate-600">
            {risks.length} {risks.length === 1 ? 'Issue' : 'Issues'}
          </span>
        </div>

        {sortedRisks.length === 0 ? (
          <div className="rounded-2xl border-2 border-dashed border-slate-200 p-12 text-center">
            <ShieldAlert className="mx-auto h-12 w-12 text-slate-300 mb-4" />
            <h3 className="text-lg font-semibold text-slate-900">No Risks Identified</h3>
            <p className="text-slate-500 mt-2">This document appears to be standard and low-risk.</p>
          </div>
        ) : (
          <div className="space-y-5">
            {sortedRisks.map((risk, i) => (
              <div key={risk.id} className="animate-in fade-in slide-in-from-bottom-4" style={{ animationDelay: `${i * 100}ms`, animationFillMode: 'both' }}>
                <RiskCard risk={risk} />
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
