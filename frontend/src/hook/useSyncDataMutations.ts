import useSyncSignageMutation from "./useSyncSignageMutation"
import useSyncInterventionMutation from "./useSyncInterventionMutation"
import useSyncInfrastructureMutation from "./useSyncInfrastructureMutation"
import useSyncReportMutation from "./useSyncReportMutation"

export default function useSyncDataMutations() {
  const mutations = {
    signageMutation: useSyncSignageMutation(),
    interventionMutation: useSyncInterventionMutation(),
    infrastructureMutation: useSyncInfrastructureMutation(),
    reportMutation: useSyncReportMutation(),
  }

  return mutations
}
