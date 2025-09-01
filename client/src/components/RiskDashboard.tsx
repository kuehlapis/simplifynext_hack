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
  description?: string;
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
      <Card className="p-8 bg-gradient-surface shadow-large border-0 animate-fade-in">
        <h2 className="text-2xl font-bold text-foreground mb-6 bg-gradient-primary bg-clip-text text-transparent">Risk Assessment Summary</h2>
        <div className="grid grid-cols-3 gap-6">
          <div className="text-center p-4 rounded-xl bg-destructive/5 border border-destructive/20 hover:bg-destructive/10 transition-all duration-300">
            <div className="text-4xl font-bold text-destructive mb-2 animate-glow">{riskCounts.high}</div>
            <div className="text-sm font-medium text-destructive/80">High Risk</div>
          </div>
          <div className="text-center p-4 rounded-xl bg-warning/5 border border-warning/20 hover:bg-warning/10 transition-all duration-300">
            <div className="text-4xl font-bold text-warning mb-2">{riskCounts.medium}</div>
            <div className="text-sm font-medium text-warning/80">Medium Risk</div>
          </div>
          <div className="text-center p-4 rounded-xl bg-success/5 border border-success/20 hover:bg-success/10 transition-all duration-300">
            <div className="text-4xl font-bold text-success mb-2">{riskCounts.ok}</div>
            <div className="text-sm font-medium text-success/80">No Issues</div>
          </div>
        </div>
        
        {totalIssues > 0 && (
          <div className="mt-6 p-6 bg-gradient-to-r from-destructive/10 to-destructive/5 border border-destructive/20 rounded-xl shadow-medium">
            <div className="flex items-center space-x-3 text-destructive">
              <div className="p-2 bg-destructive/20 rounded-full">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <span className="font-semibold text-lg">
                {totalIssues} issue{totalIssues > 1 ? 's' : ''} require{totalIssues === 1 ? 's' : ''} immediate attention
              </span>
            </div>
          </div>
        )}
      </Card>

      {/* Flagged Clauses */}
      {flaggedClauses.length > 0 && (
        <Card className="p-8 shadow-large border-0 bg-gradient-surface animate-slide-up">
          <h3 className="text-2xl font-bold text-foreground mb-6 bg-gradient-primary bg-clip-text text-transparent">Flagged Clauses</h3>
          <div className="space-y-6">
            {flaggedClauses.map((clause, index) => (
              <div key={clause.id} className="border border-border/50 rounded-xl p-6 bg-card hover:shadow-medium transition-all duration-300 animate-fade-in" style={{ animationDelay: `${index * 150}ms` }}>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-full bg-gradient-primary/10">
                      <RiskIcon risk={clause.risk} />
                    </div>
                    <h4 className="font-semibold text-foreground text-lg">{clause.title}</h4>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Badge variant="outline" className="bg-muted/50 border-border/50">{clause.category}</Badge>
                    <RiskBadge risk={clause.risk} />
                  </div>
                </div>
                <p className="text-muted-foreground leading-relaxed mb-4">{clause.description}</p>
                {clause.anchor && (
                  <div className="mt-4">
                    <Button variant="link" size="sm" className="p-0 h-auto font-medium text-primary hover:text-primary-glow transition-colors">
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
        <Card className="p-8 shadow-large border-0 bg-gradient-surface animate-slide-up">
          <h3 className="text-2xl font-bold text-foreground mb-6 bg-gradient-primary bg-clip-text text-transparent">Generated Documents</h3>
          <div className="grid gap-4">
            {artifacts.map((artifact, index) => (
              <div key={artifact.id} className="flex items-center justify-between p-5 border border-border/50 rounded-xl bg-card hover:shadow-medium transition-all duration-300 animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                <div className="flex items-center space-x-4">
                  <div className="p-3 rounded-xl bg-gradient-primary/10">
                    <Download className="w-5 h-5 text-primary" />
                  </div>
                                      <div>
                      <span className="font-semibold text-foreground text-lg">{artifact.name}</span>
                      <Badge variant="outline" className="ml-3 bg-muted/50 border-border/50 text-xs font-medium">
                        {artifact.type.toUpperCase()}
                      </Badge>
                      {artifact.description && (
                        <p className="text-sm text-muted-foreground mt-1 max-w-md">{artifact.description}</p>
                      )}
                    </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="px-6 py-2 font-medium bg-gradient-primary text-primary-foreground border-0 hover:opacity-90 shadow-soft hover:shadow-medium transition-all duration-300"
                  onClick={() => {
                    // Create a proper download link for the artifact
                    const link = document.createElement('a');
                    link.href = artifact.url;
                    
                    // Add appropriate file extensions based on type
                    let filename = artifact.name;
                    if (!filename.includes('.')) {
                      const extension = artifact.type === 'ics' ? '.ics' : 
                                     artifact.type === 'email' ? '.json' : 
                                     artifact.type === 'rider' ? '.json' : '.pdf';
                      filename = filename.toLowerCase().replace(/\s+/g, '_') + extension;
                    }
                    
                    link.download = filename;
                    link.click();
                  }}
                >
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