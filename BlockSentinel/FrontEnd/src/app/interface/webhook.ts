export interface Webhook {
  id: number;
  url: string;
  event: string;
  status: string;
  showMenu?: boolean; // Optional property to avoid initialization errors
}