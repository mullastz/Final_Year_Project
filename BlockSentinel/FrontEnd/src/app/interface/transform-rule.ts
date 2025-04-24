export interface TransformRule {
    id: string;
    sourceField: string;
    targetField: string;
    transformRule: 'No Transformation' | 'Numeric Rule' | 'Date Rule' | 'String Rule' | 'Mapping Rule';
    detail?: string; // optional for rule details
  }
  
