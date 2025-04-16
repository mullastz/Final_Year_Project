export interface RegisteredSystem {
  id: string;
  name: string;
  logoUrl: string;
  url: string;
  type: string;
  dataType: string;
  status: 'active' | 'inactive';
  alert: string;
  health: 'Good' | 'Bad';
  admins: {
    name: string;
    email: string;
  }[];
}
