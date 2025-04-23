export interface Admin {
    [x: string]: string | number;
    id: number;
    name: string;
    email: string;
    role: string;
    status: 'Active' | 'Inactive';
  }
  