import { CheckCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

export type AgentStatus = 'pending' | 'processing' | 'completed' | 'error';

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: AgentStatus;
  progress?: number;
  output?: any;
}

interface AgentPipelineProps {
  agents: Agent[];
}

const StatusIcon = ({ status }: { status: AgentStatus }) => {
  switch (status) {
    case 'completed':
      return (
        <div className="relative p-2 bg-success/20 rounded-full">
          <CheckCircle className="w-5 h-5 text-success" />
          <div className="absolute inset-0 bg-success/20 rounded-full animate-ping"></div>
        </div>
      );
    case 'processing':
      return (
        <div className="p-2 bg-primary/20 rounded-full">
          <Loader2 className="w-5 h-5 text-primary animate-spin" />
        </div>
      );
    case 'error':
      return (
        <div className="p-2 bg-destructive/20 rounded-full">
          <AlertCircle className="w-5 h-5 text-destructive" />
        </div>
      );
    default:
      return (
        <div className="p-2 bg-muted/50 rounded-full">
          <Clock className="w-5 h-5 text-muted-foreground" />
        </div>
      );
  }
};

const StatusBadge = ({ status }: { status: AgentStatus }) => {
  const variants = {
    pending: 'secondary',
    processing: 'default',
    completed: 'default',
    error: 'destructive'
  } as const;

  const labels = {
    pending: 'Pending',
    processing: 'Processing',
    completed: 'Completed',
    error: 'Error'
  };

  return (
    <Badge 
      variant={variants[status]} 
      className={status === 'completed' ? 'bg-success text-success-foreground hover:bg-success/80' : ''}
    >
      {labels[status]}
    </Badge>
  );
};

export const AgentPipeline = ({ agents }: AgentPipelineProps) => {
  return (
    <div className="space-y-6">
      {agents.map((agent, index) => (
        <Card key={agent.id} className="p-6 shadow-medium hover:shadow-large transition-all duration-300 bg-gradient-surface border-0 animate-slide-up" style={{ animationDelay: `${index * 100}ms` }}>
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                <StatusIcon status={agent.status} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground">{agent.name}</h3>
                <p className="text-muted-foreground leading-relaxed">{agent.description}</p>
              </div>
            </div>
            <StatusBadge status={agent.status} />
          </div>
          
          {agent.status === 'processing' && agent.progress !== undefined && (
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Processing...</span>
                <span className="font-medium text-primary">{agent.progress}%</span>
              </div>
              <div className="w-full bg-muted rounded-full h-3 overflow-hidden">
                <div 
                  className="bg-gradient-primary h-3 rounded-full transition-all duration-500 relative" 
                  style={{ width: `${agent.progress}%` }}
                >
                  <div className="absolute inset-0 bg-white/30 animate-pulse"></div>
                </div>
              </div>
            </div>
          )}
          
          {agent.output && (
            <div className="mt-6 p-4 bg-card/50 border border-border/50 rounded-xl">
              <pre className="text-sm text-card-foreground whitespace-pre-wrap leading-relaxed">
                {typeof agent.output === 'string' ? agent.output : JSON.stringify(agent.output, null, 2)}
              </pre>
            </div>
          )}
        </Card>
      ))}
    </div>
  );
};