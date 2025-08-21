import { AlertTriangle, CheckCircle, AlertCircle, Download } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

export interface RiskCounts {
  high: number;
  medium: number;
  ok: number;
}

export interface FlaggedClause {
  id: string;
  category: 'Unfair Clauses' | 'Stamp Duty' | 'Your Rights';
  risk: 'HIGH' | 'MEDIUM' | 'OK';
  title: string;
  description: string;
  anchor?: string;
}

export interface Artifact {
  id: string;
  name: string;
  type: 'ics' | 'email' | 'rider' | 'pdf';
  url: string;
}

interface RiskDashboardProps {
  riskCounts: RiskCounts;
  flaggedClauses: FlaggedClause[];
  artifacts: Artifact[];
}

const RiskIcon = ({ risk }: { risk: 'HIGH' | 'MEDIUM' | 'OK' }) => {
  switch (risk) {
    case 'HIGH':
      return <AlertTriangle className="w-4 h-4 text-destructive" />;
    case 'MEDIUM':
      return <AlertCircle className="w-4 h-4 text-warning" />;
    default:
      return <CheckCircle className="w-4 h-4 text-success" />;
  }
};

const RiskBadge = ({ risk }: { risk: 'HIGH' | 'MEDIUM' | 'OK' }) => {
  const variants = {
    HIGH: 'destructive',
    MEDIUM: 'default',
    OK: 'default'
  } as const;

  return (
    <Badge 
      variant={variants[risk]}
      className={risk === 'MEDIUM' ? 'bg-warning text-warning-foreground hover:bg-warning/80' : 
                 risk === 'OK' ? 'bg-success text-success-foreground hover:bg-success/80' : ''}
    >
      {risk}
    </Badge>
  );
};

export const RiskDashboard = ({ riskCounts, flaggedClauses, artifacts }: RiskDashboardProps) => {
  const totalIssues = riskCounts.high + riskCounts.medium;

  return (
    <div className="space-y-6">
      {/* Risk Summary */}
      <Card className="p-6 bg-gradient-surface shadow-medium">
        <h2 className="text-xl font-semibold text-foreground mb-4">Risk Assessment Summary</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-destructive">{riskCounts.high}</div>
            <div className="text-sm text-muted-foreground">High Risk</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-warning">{riskCounts.medium}</div>
            <div className="text-sm text-muted-foreground">Medium Risk</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-success">{riskCounts.ok}</div>
            <div className="text-sm text-muted-foreground">No Issues</div>
          </div>
        </div>
        
        {totalIssues > 0 && (
          <div className="mt-4 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
            <div className="flex items-center space-x-2 text-destructive">
              <AlertTriangle className="w-4 h-4" />
              <span className="font-medium">
                {totalIssues} issue{totalIssues > 1 ? 's' : ''} require{totalIssues === 1 ? 's' : ''} attention
              </span>
            </div>
          </div>
        )}
      </Card>

      {/* Flagged Clauses */}
      {flaggedClauses.length > 0 && (
        <Card className="p-6 shadow-soft">
          <h3 className="text-lg font-semibold text-foreground mb-4">Flagged Clauses</h3>
          <div className="space-y-4">
            {flaggedClauses.map((clause) => (
              <div key={clause.id} className="border border-border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <RiskIcon risk={clause.risk} />
                    <h4 className="font-medium text-foreground">{clause.title}</h4>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline">{clause.category}</Badge>
                    <RiskBadge risk={clause.risk} />
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">{clause.description}</p>
                {clause.anchor && (
                  <div className="mt-2">
                    <Button variant="link" size="sm" className="p-0 h-auto">
                      View in document →
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Generated Artifacts */}
      {artifacts.length > 0 && (
        <Card className="p-6 shadow-soft">
          <h3 className="text-lg font-semibold text-foreground mb-4">Generated Documents</h3>
          <div className="grid gap-3">
            {artifacts.map((artifact) => (
              <div key={artifact.id} className="flex items-center justify-between p-3 border border-border rounded-lg">
                <div className="flex items-center space-x-3">
                  <Download className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm font-medium text-foreground">{artifact.name}</span>
                  <Badge variant="outline" className="text-xs">
                    {artifact.type.toUpperCase()}
                  </Badge>
                </div>
                <Button variant="outline" size="sm">
                  Download
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};