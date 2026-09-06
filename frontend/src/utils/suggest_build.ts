import type{ CPUResponse, MotherboardResponse, RAMResponse } from '../types/api';

export type CompatibilityStatus = 'COMPATIBLE' | 'INCOMPATIBLE' | 'NEUTRAL';

export const checkComponentCompatibility = (
    item: any, 
    category: string,
    currentBuild: { cpu?: CPUResponse | null, motherboard?: MotherboardResponse | null, ram?: RAMResponse | null}
): CompatibilityStatus => {
    const cat = category.toUpperCase();
     if (cat === 'CPU') {
        if (currentBuild.motherboard) {
            return item.socket === currentBuild.motherboard.socket 
                ? 'COMPATIBLE' 
                : 'INCOMPATIBLE';
        }

    }

    if(cat == 'MOTHERBOARD'){
        let isSocketOk = true;
        let isDdrOk = true;
        let hasAnythingToCompare = false; 
        if (currentBuild.cpu) {
            hasAnythingToCompare = true;
            isSocketOk = item.socket === currentBuild.cpu.socket;
        }
        
        if (currentBuild.ram) {
            hasAnythingToCompare = true;
            isDdrOk = item.ddr_generation === currentBuild.ram.ddr_generation;
        }
        if (hasAnythingToCompare) {
            return (isSocketOk && isDdrOk) ? 'COMPATIBLE' : 'INCOMPATIBLE';
        }
    }
     if (cat === 'RAM') {
        if (currentBuild.motherboard) {
            return item.ddr_generation === currentBuild.motherboard.ddr_generation 
                ? 'COMPATIBLE' 
                : 'INCOMPATIBLE';
        }
    }
    return 'NEUTRAL';
}