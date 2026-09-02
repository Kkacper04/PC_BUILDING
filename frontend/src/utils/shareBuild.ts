import type { ComponentType } from '../types/api';

const COMPONENT_KEYS: ComponentType[] = [
  'cpu', 'motherboard', 'ram', 'gpu', 'psu', 'case', 'cooler', 'storage',
];

interface BuildIds {
  cpu?: number;
  motherboard?: number;
  ram?: number;
  gpu?: number;
  psu?: number;
  case?: number;
  cooler?: number;
  storage?: number;
}

export function encodeBuildToUrl(ids: BuildIds): string {
  const params = new URLSearchParams();
  for (const key of COMPONENT_KEYS) {
    const id = ids[key];
    if (id != null) {
      params.set(key, String(id));
    }
  }
  return `${window.location.origin}/?${params.toString()}`;
}

export function decodeBuildFromUrl(search: string): BuildIds {
  const params = new URLSearchParams(search);
  const ids: BuildIds = {};
  for (const key of COMPONENT_KEYS) {
    const val = params.get(key);
    if (val != null) {
      const parsed = parseInt(val, 10);
      if (!isNaN(parsed)) {
        ids[key] = parsed;
      }
    }
  }
  return ids;
}

export function hasBuildParams(search: string): boolean {
  const params = new URLSearchParams(search);
  return COMPONENT_KEYS.some((key) => params.has(key));
}
