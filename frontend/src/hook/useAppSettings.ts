import type { AppConfigSchemaProps } from "@/schemas/settings"
import { useQueryClient } from "@tanstack/react-query"

export const APP_SETTINGS_QUERY_KEY = ["appsettings"]

export function useAppSettings() {
  const queryClient = useQueryClient()
  const data = queryClient.getQueryData<AppConfigSchemaProps>(
    APP_SETTINGS_QUERY_KEY
  )

  return {
    data,
    setData: (nextData: Partial<AppConfigSchemaProps>) =>
      queryClient.setQueryData(
        APP_SETTINGS_QUERY_KEY,
        (prevData: AppConfigSchemaProps) => ({
          ...prevData,
          ...nextData,
          syncData: {
            ...prevData?.syncData,
            ...nextData.syncData,
          },
          list: {
            ...prevData?.list,
            ...nextData.list,
          },
        })
      ),
  }
}
