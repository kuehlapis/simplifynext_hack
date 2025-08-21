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
      return <CheckCircle className="w-5 h-5 text-success" />;
    case 'processing':
      return <Loader2 className="w-5 h-5 text-primary animate-spin" />;
    case 'error':
      return <AlertCircle className="w-5 h-5 text-destructive" />;
    default:
      return <Clock className="w-5 h-5 text-muted-foreground" />;
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
    <div className="space-y-4">
      {agents.map((agent, index) => (
        <Card key={agent.id} className="p-6 shadow-soft hover:shadow-medium transition-shadow">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <StatusIcon status={agent.status} />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">{agent.name}</h3>
                <p className="text-sm text-muted-foreground">{agent.description}</p>
              </div>
            </div>
            <StatusBadge status={agent.status} />
          </div>
          
          {agent.status === 'processing' && agent.progress !== undefined && (
            <Progress value={agent.progress} className="w-full" />
          )}
          
          {agent.output && (
            <div className="mt-4 p-4 bg-secondary rounded-lg">
              <pre className="text-sm text-secondary-foreground whitespace-pre-wrap">
                {typeof agent.output === 'string' ? agent.output : JSON.stringify(agent.output, null, 2)}
              </pre>
            </div>
          )}
        </Card>
      ))}
    </div>
  );
};