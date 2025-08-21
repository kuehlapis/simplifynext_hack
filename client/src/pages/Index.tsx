import { useState } from 'react';
import { FileUpload } from '@/components/FileUpload';
import { AgentPipeline, type Agent } from '@/components/AgentPipeline';
import { RiskDashboard, type RiskCounts, type FlaggedClause, type Artifact } from '@/components/RiskDashboard';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Separator } from '@/components/ui/separator';

const Index = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: 'intake',
      name: 'Intake Agent',
      description: 'Convert input into normalized Markdown and generate anchors for key clauses',
      status: 'pending'
    },
    {
      id: 'analyzer',
      name: 'Analyzer Agent',
      description: 'Extract content against YAML rulebook and flag issues by category and risk level',
      status: 'pending'
    },
    {
      id: 'planner',
      name: 'Planner & Drafter Agent',
      description: 'Generate task lists, ICS events, and draft email summaries with key issues',
      status: 'pending'
    },
    {
      id: 'qa',
      name: 'QA Guardrails Agent',
      description: 'Check disclaimers, ensure no PII leaks, and run consistency checks',
      status: 'pending'
    },
    {
      id: 'packager',
      name: 'Packager Agent',
      description: 'Output final JSON dashboard with risk counts and artifact links',
      status: 'pending'
    }
  ]);
  const [dashboardData, setDashboardData] = useState<{
    riskCounts: RiskCounts;
    flaggedClauses: FlaggedClause[];
    artifacts: Artifact[];
  } | null>(null);

  const { toast } = useToast();

  const simulateProcessing = async () => {
    setIsProcessing(true);
    
    // Simulate agent processing with delays
    for (let i = 0; i < agents.length; i++) {
      setAgents(prev => prev.map((agent, index) => 
        index === i ? { ...agent, status: 'processing', progress: 0 } : agent
      ));

      // Simulate processing progress
      for (let progress = 0; progress <= 100; progress += 20) {
        await new Promise(resolve => setTimeout(resolve, 200));
        setAgents(prev => prev.map((agent, index) => 
          index === i ? { ...agent, progress } : agent
        ));
      }

      setAgents(prev => prev.map((agent, index) => 
        index === i ? { ...agent, status: 'completed', progress: 100 } : agent
      ));
    }

    // Generate mock dashboard data
    const mockData = {
      riskCounts: {
        high: 3,
        medium: 5,
        ok: 12
      },
      flaggedClauses: [
        {
          id: '1',
          category: 'Unfair Clauses' as const,
          risk: 'HIGH' as const,
          title: 'Excessive Security Deposit',
          description: 'Security deposit exceeds 2 months rent, which may be unenforceable',
          anchor: 'clause-7.2'
        },
        {
          id: '2',
          category: 'Your Rights' as const,
          risk: 'HIGH' as const,
          title: 'Waived Maintenance Rights',
          description: 'Tenant waives right to request timely repairs and maintenance',
          anchor: 'clause-12.1'
        },
        {
          id: '3',
          category: 'Stamp Duty' as const,
          risk: 'MEDIUM' as const,
          title: 'Unclear Stamp Duty Allocation',
          description: 'Agreement does not clearly specify who bears stamp duty costs',
          anchor: 'clause-15.3'
        }
      ],
      artifacts: [
        {
          id: '1',
          name: 'Task Schedule',
          type: 'ics' as const,
          url: '#'
        },
        {
          id: '2',
          name: 'Summary Email Draft',
          type: 'email' as const,
          url: '#'
        },
        {
          id: '3',
          name: 'Amendment Rider',
          type: 'rider' as const,
          url: '#'
        },
        {
          id: '4',
          name: 'Annotated Agreement',
          type: 'pdf' as const,
          url: '#'
        }
      ]
    };

    setDashboardData(mockData);
    setIsProcessing(false);
    
    toast({
      title: "Processing Complete",
      description: "Your tenant agreement has been analyzed successfully.",
    });
  };

  const resetProcess = () => {
    setSelectedFile(null);
    setIsProcessing(false);
    setAgents(prev => prev.map(agent => ({ ...agent, status: 'pending', progress: undefined })));
    setDashboardData(null);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border bg-gradient-surface">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              Tenant Agreement Analyzer
            </h1>
            <p className="mt-2 text-muted-foreground max-w-2xl mx-auto">
              AI-powered multi-agent system for analyzing tenant agreements, identifying risks, and generating actionable insights
            </p>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {!selectedFile ? (
          /* Upload Section */
          <div className="max-w-2xl mx-auto">
            <FileUpload onFileSelect={setSelectedFile} isProcessing={isProcessing} />
          </div>
        ) : (
          /* Processing & Results */
          <div className="space-y-8">
            {/* File Info & Controls */}
            <Card className="p-6 shadow-soft">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-foreground">Processing: {selectedFile.name}</h2>
                  <p className="text-sm text-muted-foreground">
                    {(selectedFile.size / 1024).toFixed(1)} KB • {selectedFile.type}
                  </p>
                </div>
                <div className="space-x-2">
                  {!isProcessing && !dashboardData && (
                    <Button onClick={simulateProcessing} className="bg-gradient-primary hover:opacity-90">
                      Start Analysis
                    </Button>
                  )}
                  <Button variant="outline" onClick={resetProcess}>
                    Reset
                  </Button>
                </div>
              </div>
            </Card>

            <div className="grid lg:grid-cols-2 gap-8">
              {/* Agent Pipeline */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4">Processing Pipeline</h2>
                <AgentPipeline agents={agents} />
              </div>

              {/* Dashboard Results */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4">Analysis Results</h2>
                {dashboardData ? (
                  <RiskDashboard 
                    riskCounts={dashboardData.riskCounts}
                    flaggedClauses={dashboardData.flaggedClauses}
                    artifacts={dashboardData.artifacts}
                  />
                ) : (
                  <Card className="p-8 shadow-soft">
                    <div className="text-center text-muted-foreground">
                      {isProcessing ? (
                        <p>Analysis in progress...</p>
                      ) : (
                        <p>Click "Start Analysis" to begin processing your document.</p>
                      )}
                    </div>
                  </Card>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Index;