import { create } from 'zustand';
import type {
  CPUResponse,
  GPUResponse,
  MotherboardResponse,
  RAMResponse,
  PSUResponse,
  CaseResponse,
  StorageResponse,
  CPUCoolerResponse,
  ComponentType,
  AnyComponent,
} from '../types/api';

export interface BuildState {
  cpu: CPUResponse | null;
  gpu: GPUResponse | null;
  motherboard: MotherboardResponse | null;
  ram: RAMResponse | null;
  psu: PSUResponse | null;
  pcCase: CaseResponse | null;
  cooler: CPUCoolerResponse | null;
  storage: StorageResponse | null;

  setComponent: (type: ComponentType, component: AnyComponent | null) => void;
  removeComponent: (type: ComponentType) => void;
  clearBuild: () => void;
  getTotalPrice: () => number;
}

export const useBuildStore = create<BuildState>()((set, get) => ({
  cpu: null,
  gpu: null,
  motherboard: null,
  ram: null,
  psu: null,
  pcCase: null,
  cooler: null,
  storage: null,

  setComponent: (type: ComponentType, component: AnyComponent | null) => {
    switch (type) {
      case 'cpu':
        set({ cpu: component as CPUResponse | null });
        break;
      case 'gpu':
        set({ gpu: component as GPUResponse | null });
        break;
      case 'motherboard':
        set({ motherboard: component as MotherboardResponse | null });
        break;
      case 'ram':
        set({ ram: component as RAMResponse | null });
        break;
      case 'psu':
        set({ psu: component as PSUResponse | null });
        break;
      case 'case':
        set({ pcCase: component as CaseResponse | null });
        break;
      case 'cooler':
        set({ cooler: component as CPUCoolerResponse | null });
        break;
      case 'storage':
        set({ storage: component as StorageResponse | null });
        break;
      default:
        break;
    }
  },

  removeComponent: (type: ComponentType) => {
    switch (type) {
      case 'cpu':
        set({ cpu: null });
        break;
      case 'gpu':
        set({ gpu: null });
        break;
      case 'motherboard':
        set({ motherboard: null });
        break;
      case 'ram':
        set({ ram: null });
        break;
      case 'psu':
        set({ psu: null });
        break;
      case 'case':
        set({ pcCase: null });
        break;
      case 'cooler':
        set({ cooler: null });
        break;
      case 'storage':
        set({ storage: null });
        break;
      default:
        break;
    }
  },

  clearBuild: () => {
    set({
      cpu: null,
      gpu: null,
      motherboard: null,
      ram: null,
      psu: null,
      pcCase: null,
      cooler: null,
      storage: null,
    });
  },

  getTotalPrice: () => {
    const { cpu, gpu, motherboard, ram, psu, pcCase, cooler, storage } = get();
    const items = [cpu, gpu, motherboard, ram, psu, pcCase, cooler, storage];
    return items.reduce((sum, item) => {
      if (item && item.price != null) {
        return sum + Number(item.price);
      }
      return sum;
    }, 0);
  },
}));

export default useBuildStore;
