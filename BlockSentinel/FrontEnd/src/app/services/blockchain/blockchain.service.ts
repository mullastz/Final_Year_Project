import { Injectable } from '@angular/core';
import { JsonRpcProvider, Contract } from 'ethers';
// Update the path below to the actual location of your ABI JSON file
import contractABI from '../../../app/abi/LedgerABI.json';

const CONTRACT_ADDRESS = '0x8EA9b457437Ce332421b06bD8A8E5B7579920b14';
const PROVIDER_URL = 'http://127.0.0.1:7545'; // Ganache

@Injectable({
  providedIn: 'root'
})
export class BlockchainService {
  private provider: JsonRpcProvider;
  private contract: Contract;

  constructor() {
    this.provider = new JsonRpcProvider(PROVIDER_URL);
    this.contract = new Contract(CONTRACT_ADDRESS, contractABI, this.provider);
  }

  async getLedgerEntries(): Promise<any[]> {
    const count = await this.contract['getEntryCount']();
    const entries = [];

    for (let i = 0; i < count; i++) {
      const [sourceId, payload, timestamp] = await this.contract['getEntry'](i);
      entries.push({
        sourceId,
        payload: JSON.parse(payload),
        timestamp: new Date(Number(timestamp) * 1000).toLocaleString()
      });
    }

    return entries;
  }
}
