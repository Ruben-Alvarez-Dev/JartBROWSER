import { create } from 'zustand';

interface AppState {
  currentStep: number;
  isAdvancedMode: boolean;
  config: any;
  setCurrentStep: (step: number) => void;
  setAdvancedMode: (advanced: boolean) => void;
  setConfig: (config: any) => void;
}

export const useAppStore = create<AppState>((set) => ({
  currentStep: 0,
  isAdvancedMode: false,
  config: {},
  setCurrentStep: (step) => set({ currentStep: step }),
  setAdvancedMode: (advanced) => set({ isAdvancedMode: advanced }),
  setConfig: (config) => set({ config })
}));
