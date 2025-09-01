import { useState } from 'react';
import { FileUpload } from '@/components/FileUpload';
import { AgentPipeline, type Agent } from '@/components/AgentPipeline';
import { RiskDashboard, type RiskCounts, type FlaggedClause, type Artifact } from '@/components/RiskDashboard';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Separator } from '@/components/ui/separator';



const Index = () => {
  const [convertedMarkdown, setConvertedMarkdown] = useState<string | null>(null);
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

  const handleFileConvert = async (file: File) => {
    try {
      setIsProcessing(true);
      setConvertedMarkdown(null);
      setSelectedFile(file);
      const formData = new FormData();
      formData.append("file", file);
      const convertRes = await fetch("/convert", {
        method: "POST",
        body: formData,
      });
      
      if (!convertRes.ok) throw new Error(`Conversion failed: ${convertRes.status}`);
      const markdown = await convertRes.text();   
      setConvertedMarkdown(markdown)
      toast({
        title: "File converted",
        description: "Markdown version is ready. Click Start Analysis to continue.",
      });
      setIsProcessing(false);
      return markdown;            
    } catch (err) {
      console.error(err);
      toast({
        title: "Error",
        description: "File conversion failed. See console for details.",
      });
      return null;
    }
  };

  const AnalyzeProcessing = async () => {
    if (!convertedMarkdown) return;

    setIsProcessing(true);

    const simulateAgents = async () => {
        for (let i = 0; i < agents.length; i++) {
          setAgents(prev =>
            prev.map((agent, index) =>
              index === i ? { ...agent, status: "processing", progress: 0 } : agent
            )
          );

          for (let progress = 0; progress <= 100; progress += 15) {
            await new Promise(resolve => setTimeout(resolve, 600));
            setAgents(prev =>
              prev.map((agent, index) =>
                index === i ? { ...agent, progress } : agent
              )
            );
          }

          setAgents(prev =>
            prev.map((agent, index) =>
              index === i ? { ...agent, status: "completed", progress: 100 } : agent
            )
          );
        }
    };

    try {
      // Start both fetch and agent animation concurrently
      const analyzePromise = fetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "text/markdown" },
        body: convertedMarkdown,
      });

      // Start agent animation without awaiting yet
      const simulationPromise = simulateAgents();

      // Wait for backend response
      const analyzeRes = await analyzePromise;
      if (!analyzeRes.ok) throw new Error(`Analysis failed: ${analyzeRes.status}`);
      const analysisResult = await analyzeRes.json();

      // Wait for agent simulation to finish (if it hasn’t already)
      await simulationPromise;

      setDashboardData(analysisResult);

      toast({
        title: "Processing Complete",
        description: "Your tenant agreement has been analyzed successfully.",
      });

    } catch (err) {
      console.error(err);
      toast({
        title: "Error",
        description: "Analysis failed. See console for details.",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const resetProcess = () => {
    setSelectedFile(null);
    setConvertedMarkdown(null)
    setIsProcessing(false);
    setAgents(prev => prev.map(agent => ({ ...agent, status: 'pending', progress: undefined })));
    setDashboardData(null);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border bg-gradient-hero relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-primary/5"></div>
        <div className="container mx-auto px-4 py-12 relative">
          <div className="text-center animate-fade-in">
            <h1 className="text-5xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-4">
              Tenant Agreement Analyzer
            </h1>
            <p className="mt-4 text-muted-foreground max-w-3xl mx-auto text-xl leading-relaxed">
              AI-powered multi-agent system for analyzing tenant agreements, identifying risks, and generating actionable insights
            </p>
            <div className="mt-6 flex justify-center space-x-4">
              <div className="px-4 py-2 bg-primary/10 rounded-full text-sm font-medium text-primary">
                ✨ Advanced AI Analysis
              </div>
              <div className="px-4 py-2 bg-success/10 rounded-full text-sm font-medium text-success">
                🔒 Secure Processing
              </div>
              <div className="px-4 py-2 bg-accent/10 rounded-full text-sm font-medium text-accent">
                ⚡ Real-time Results
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
          {!selectedFile ? (
            /* Upload Section */
            <div className="max-w-2xl mx-auto">
              <FileUpload onFileSelect={handleFileConvert} isProcessing={isProcessing} />
            </div>
          ) : !convertedMarkdown ? (
            <Card className="p-12 shadow-large bg-gradient-hero border-0 text-center">
              <div className="space-y-4">
                <div className="w-16 h-16 mx-auto bg-gradient-primary rounded-full flex items-center justify-center animate-glow">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-foreground"></div>
                </div>
                <p className="text-lg font-medium text-foreground">Processing your file...</p>
                <p className="text-muted-foreground">Please wait while we process your document</p>
              </div>
            </Card>
        ) : (
          /* Processing & Results */
          <div className="space-y-8">
            {/* File Info & Controls */}
            <Card className="p-8 shadow-large bg-gradient-surface border-0 animate-fade-in">
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  <h2 className="text-2xl font-bold text-foreground">Processing: {selectedFile.name}</h2>
                  <p className="text-muted-foreground text-lg">
                    {(selectedFile.size / 1024).toFixed(1)} KB • {selectedFile.type}
                  </p>
                  <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                    <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                    <span>File uploaded successfully</span>
                  </div>
                </div>
                <div className="space-x-3">
                  {!isProcessing && !dashboardData && (
                    <Button onClick={AnalyzeProcessing} className="px-8 py-3 text-lg font-semibold bg-gradient-primary hover:opacity-90 shadow-medium hover:shadow-large transition-all duration-300">
                      Start Analysis
                    </Button>
                  )}
                  <Button variant="outline" onClick={resetProcess} className="px-6 py-3 font-medium">
                    Reset
                  </Button>
                </div>
              </div>
            </Card>

            <div className="grid lg:grid-cols-2 gap-12">
              {/* Agent Pipeline */}
              <div className="animate-slide-up">
                <h2 className="text-2xl font-bold text-foreground mb-6 bg-gradient-primary bg-clip-text text-transparent">Processing Pipeline</h2>
                <AgentPipeline agents={agents} />
              </div>

              {/* Dashboard Results */}
              <div className="animate-slide-up" style={{ animationDelay: '200ms' }}>
                <h2 className="text-2xl font-bold text-foreground mb-6 bg-gradient-primary bg-clip-text text-transparent">Analysis Results</h2>
                {dashboardData ? (
                  <RiskDashboard 
                    riskCounts={dashboardData.riskCounts}
                    flaggedClauses={dashboardData.flaggedClauses}
                    artifacts={dashboardData.artifacts}
                  />
                ) : (
                  <Card className="p-12 shadow-large bg-gradient-hero border-0">
                    <div className="text-center">
                      {isProcessing ? (
                        <div className="space-y-4">
                          <div className="w-16 h-16 mx-auto bg-gradient-primary rounded-full flex items-center justify-center animate-glow">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-foreground"></div>
                          </div>
                          <p className="text-lg font-medium text-foreground">Analysis in progress...</p>
                          <p className="text-muted-foreground">Our AI agents are working hard to analyze your document</p>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          <div className="w-16 h-16 mx-auto bg-gradient-surface rounded-full flex items-center justify-center border-2 border-dashed border-border">
                            <span className="text-2xl">📄</span>
                          </div>
                          <p className="text-lg font-medium text-foreground">Ready to analyze</p>
                          <p className="text-muted-foreground">Click "Start Analysis" to begin processing your document</p>
                        </div>
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