import { useState, useCallback } from 'react';
import { DEMO_SCENARIOS } from '../data/demoCases';
import { DemoScenario } from '../types/agent';

export interface UseDemoCasesReturn {
  scenarios: DemoScenario[];
  selectedScenario: DemoScenario;
  selectScenario: (scenarioId: string) => DemoScenario | undefined;
}

export const useDemoCases = (): UseDemoCasesReturn => {
  const [selectedScenario, setSelectedScenario] = useState<DemoScenario>(DEMO_SCENARIOS[0]);

  const selectScenario = useCallback((scenarioId: string) => {
    const found = DEMO_SCENARIOS.find((s) => s.id === scenarioId);
    if (found) {
      setSelectedScenario(found);
      return found;
    }
    return undefined;
  }, []);

  return {
    scenarios: DEMO_SCENARIOS,
    selectedScenario,
    selectScenario,
  };
};
